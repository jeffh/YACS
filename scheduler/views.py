from datetime import datetime
from json import dumps
import urllib
import time

from django.db.models import F, Q
from django.views.generic import ListView, TemplateView, View
from django.http import HttpResponse, Http404, HttpResponseNotFound, HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext
from django.conf import settings
from django.core.cache import cache
from django.core.urlresolvers import reverse
from icalendar import Calendar, Event, vText

from courses.views import SemesterBasedMixin, SELECTED_COURSES_SESSION_KEY, AjaxJsonResponseMixin
from courses.models import Semester, SectionPeriod, Course, Section, Department
from courses.utils import dict_by_attr, ObjectJSONEncoder, sorted_daysofweek, DAYS
from scheduler import models
from scheduler.scheduling import compute_schedules


ICAL_PRODID = getattr(settings, 'SCHEDULER_ICAL_PRODUCT_ID', '-//Jeff Hui//YACS Export 1.0//EN')
SECTION_LIMIT = getattr(settings, 'SECTION_LIMIT', 60)


class ResponsePayloadException(Exception):
    "This exception is raised if a special form of HttpResponse is wanted to be returned (eg - JSON error response)."
    def __init__(self, response):
        self.response = response
        super(ResponsePayloadException, self).__init__('')


class ExceptionResponseMixin(object):
    """Handles ResponsePayloadExceptions appropriately.

    If the view throws a ResponsePayloadException, then the raise Response is used instead of the traditional
    HttpResponse object.
    """
    def dispatch(self, *args, **kwargs):
        try:
            return super(ExceptionResponseMixin, self).dispatch(*args, **kwargs)
        except ResponsePayloadException as e:
            return e.response


class ConflictMixin(SemesterBasedMixin):
    "Provides the view with helper methods to acquire the conflicted sections."
    def conflict_mapping(self, conflicts):
        """Returns a dictionary of section id to a frozen set of section ids
        that conflict with the given section.
        """
        result = {} # section_id => [section_ids]
        for conflict in conflicts:
            result.setdefault(conflict.section1.id, set()).add(conflict.section2.id)
            result.setdefault(conflict.section2.id, set()).add(conflict.section1.id)
        # freeze all sets
        for key in result.keys():
            result[key] = frozenset(result[key])
        return result

    def get_sections_by_crns(self, crns):
        "Returns all sections with the provided CRNs."
        year, month = self.get_year_and_month()
        queryset = models.SectionProxy.objects.by_crns(crns, year=year, month=month)
        queryset = queryset.select_related('course', 'course__department')
        return queryset.by_semester(year, month).prefetch_periods() #queryset.full_select(year, month)

    def inject_conflict_mapping_in_sections(self, sections):
        """Givens the collection of section objects, attaches a conflict attr
        to each which is a frozen set of all section ids that conflict with
        the given section.
        """
        section_ids = set(s.id for s in sections)
        conflicts = models.SectionConflict.objects.by_sections(section_ids)
        conflict_mapping = self.conflict_mapping(conflicts)
        empty_set = frozenset() # saves memory
        for section in sections:
            section.conflicts = conflict_mapping.get(section.id) or empty_set


# warning: this view doesn't actually work by itself...
# mostly because the template doesn't expect the same context
class ComputeSchedules(ConflictMixin, ExceptionResponseMixin, TemplateView):
    template_name = 'scheduler/schedule_list.html'
    object_name = 'schedules'

    def get_crns(self):
        "Returns the list of CRNs the user currently selected."
        requested_crns = self.request.GET.getlist('crn')
        savepoint = int(self.request.GET.get('from', 0))
        crns = []
        for crn in requested_crns:
            try:
                crns.append(int(crn))
            except (ValueError, TypeError):
                pass
        return crns

    def get_sections(self):
        """Return the collection of section objects that
        correspond to the user's selection of CRNs.

        The section object has select_related and conflict maps.
        """
        year, month = self.get_year_and_month()
        sections = self.get_sections_by_crns(self.get_crns())

        if len(sections) > SECTION_LIMIT:
            raise ResponsePayloadException(HttpResponseForbidden('invalid'))

        self.inject_conflict_mapping_in_sections(sections)
        return sections

    def get_savepoint(self):
        "Returns the reference to a position in the scheduler generation."
        return int(self.request.GET.get('from', 0))

    def reformat_to_selected_courses(self, sections):
        "Returns a dictionary of a course mapped to its sections objects."
        return dict_by_attr(sections, 'course')

    def compute_schedules(self, selected_courses):
        # we should probably set some upper bound of computation and restrict number of sections used.
        #schedules = take(100, compute_schedules(selected_courses, generator=True))
        #
        # ideally, we should write the schedules to the database in bulk after
        # the first time we compute this for a bunch of benefits (short-linkable
        # urls, speed, etc.) But we'll have to wait for it to hit a release
        # version:
        # https://docs.djangoproject.com/en/dev/ref/models/querysets/#django.db.models.query.QuerySet.bulk_create
        if self.request.GET.get('check'):
            for schedule in compute_schedules(selected_courses, free_sections_only=False, generator=True):
                raise ResponsePayloadException(HttpResponse('ok'))
            raise ResponsePayloadException(HttpResponseNotFound('conflicts'))
        schedules = compute_schedules(selected_courses, start=self.get_savepoint(), free_sections_only=False, generator=True)

        try:
            limit = int(self.request.GET.get('limit'))
        except (ValueError, TypeError):
            limit = 0
        if limit > 0:
            print "limiting by", limit
            schedules = take(limit, schedules)
        else:
            schedules = list(schedules)

        return schedules

    def period_stats(self, periods):
        """Returns various statistics of the period objects provided..

        Currently only gives the minimum period time, maximium period
        time, and the days of the week all periods have.
        """
        if len(periods) < 1:
            return range(8, 20), DAYS[:5]
        min_time, max_time, dow_used = None, None, set()
        for period in periods:
            min_time = min(min_time or period.start, period.start)
            max_time = max(max_time or period.end, period.end)
            dow_used = dow_used.union(period.days_of_week)

        timerange = range(min_time.hour -1 , max_time.hour + 2)
        return timerange, sorted_daysofweek(dow_used)

    def get_is_thumbnail(self):
        """Returns logical true if the we need to provided thumbnail
        information.
        """
        return self.request.GET.get('thumbnail')

    def section_mapping(self, selected_courses, schedules, periods):
        "Builds the data structure of the data for faster display in the template (less looping)."
        timerange, dows = self.period_stats(periods)
        section_mapping = {} # [schedule-index][dow][starting-hour]
        dow_mapping = dict((d, i) for i, d in enumerate(DAYS))
        for i, schedule in enumerate(schedules):
            the_dows = section_mapping[i+1] = {}
            for section in schedule.values():
                for j, period in enumerate(section.get_periods()):
                    for dow in period.days_of_week:
                        dowi = dow_mapping.get(dow)
                        the_dows[dowi] = the_dows.get(dowi, {})
                        # saves 50% of request size by using tuple instead
                        # of dictionary
                        the_dows[dowi][period.start.hour] = (
                            section.course.id,
                            section.crn,
                            j,
                        )
        return section_mapping

    def section_mapping_for_thumbnails(self, selected_courses, schedules, periods):
        "Builds the data structure of the data for faster display in the template (less looping)."
        timerange, dows = self.period_stats(periods)
        section_mapping = {} # [schedule-index][hour][starting-hour]
        dow_mapping = dict((d, i) for i, d in enumerate(DAYS))
        # TODO: fixme -- change to new section_mapping
        for i, schedule in enumerate(schedules):
            the_dows = section_mapping[i+1] = {}
            for section in schedule.values():
                for j, period in enumerate(section.get_periods()):
                    for dow in period.days_of_week:
                        dowi = dow_mapping.get(dow)
                        the_dows[dowi] = the_dows.get(dowi, {})
                        the_dows[dowi][period.start.hour] = (
                            section.course.id,
                            section.crn,
                            j,
                        )
        return section_mapping

    def get_section_mapping(self, selected_courses, schedules, periods):
        "Preps the schedule data for display in the context."
        if self.get_is_thumbnail():
            return self.section_mapping_for_thumbnails(selected_courses, schedules, periods)
        else:
            return self.section_mapping(selected_courses, schedules, periods)

    def prep_schedules_for_context(self, schedules):
        """Returns the schedules in a JSON-friendly format.

        Returns a list of dictionary of course id to crns.
        """
        results = []
        for schedule in schedules:
            s = {}
            for course, section in schedule.items():
                s[str(course.id)] = section.crn
            results.append(s)
        return results
        # above is equivalent to below, but the one below is only for
        # python 2.7+, and not python 2.6
        #return [{ str(course.id): section.crn for course, section in schedule.items() } for schedule in schedules]

    def prep_courses_and_sections_for_context(self, selected_courses):
        """Returns all the database model objects for JSON-friendly output.

        Returns a tuple of courses and sections dictionary objects.
        """
        courses_output, sections_output = {}, {}
        for course, sections in selected_courses.items():
            courses_output[course.id] = course.toJSON(select_related=((Department._meta.db_table, 'code'),))
            for section in sections:
                sections_output[section.crn] = section.toJSON()
        return courses_output, sections_output

    def get_context_data(self, **kwargs):
        "Outputs all the context data used to render the view."
        data = super(ComputeSchedules, self).get_context_data(**kwargs)
        year, month = self.get_year_and_month()
        sections = self.get_sections()
        selected_courses = self.reformat_to_selected_courses(sections)
        schedules = self.compute_schedules(selected_courses)
        schedules_output = self.prep_schedules_for_context(schedules)

        if len(schedules_output):
            periods = set(p for s in sections for p in s.get_periods())
            timerange, dows = self.period_stats(periods)
            courses_output, sections_output = self.prep_courses_and_sections_for_context(selected_courses)
            context = {
                'time_range': timerange,
                'dows': DAYS,
                'schedules': schedules_output,
                'sem_year': year,
                'sem_month': month,
                'courses': courses_output,
                'sections': sections_output,
                'section_mapping': self.get_section_mapping(selected_courses, schedules, periods),
            }
        else:
            context = {
                'schedules': [],
                'sem_year': year,
                'sem_month': month,
            }
        data.update(context)
        return data


class JsonComputeSchedules(AjaxJsonResponseMixin, ComputeSchedules):
    "Simply provides a JSON output format for the ComputeSchedules view."
    json_content_prefix = ''
    def get_is_ajax(self):
        return True

    def render_to_response(self, context):
        del context['template_base']
        return self.get_json_response(self.get_json_content_prefix() + self.convert_context_to_json(context))


def schedules_bootloader(request, year, month):
    """A simple view that loads the basic template and provides the
    URL for the javascript client to hit for the schedule computation.
    """
    #crns = request.GET.get('crns')
    #if crns is not None:
    #    crns = [c for c in crns.split('-') if c.strip() != '']
    #if crns is None:
    #    selected_courses = request.session.get(SELECTED_COURSES_SESSION_KEY, {})
    #    return redirect(reverse('schedules', kwargs=dict(year=year, month=month)) + '?crns=' + urllib.quote('-'.join(str(crn) for sections in selected_courses.values() for crn in sections)))

    #prefix = 'crn='
    #crns = prefix + ('&'+prefix).join(urllib.quote(str(crn)) for crn in crns)

    single_schedule = ''
    # disabled for now... use JS
    #schedule_offset = request.GET.get('at', '')
    #if schedule_offset:
    #    single_schedule = "&from=%s&limit=1" % urllib.quote(schedule_offset)
    return render_to_response('scheduler/placeholder_schedule_list.html', {
        'ajax_url': reverse('ajax-schedules', kwargs=dict(year=year, month=month)) + '?', # + crns + single_schedule,
        'sem_year': year,
        'sem_month': month,
    }, RequestContext(request))

## OBSOLETE -- should remove below when implemented as class-based view.

def icalendar(request, year, month):
    "Exports a given calendar into ics format."
    # TODO: gather all courses for schedule
    cal = Calendar()
    cal.add('prodid', ICAL_PRODID)
    cal.add('version', '2.0') # ical spec version

    # TODO: define instead of using placeholders
    sections = None # placeholder
    for section in sections:
        periods = None # placeholder
        for period in periods:
            event = Event()
            event.add('summary', '%s - %s (%s)' % (section.course.code, section.course.name, section.crn))

            # datetime of the first event occurrence
            event.add('dtstart', datetime.now())
            event.add('dtend', datetime.now())

            # recurrence rule
            event.add('rrule', dict(
                freq='weekly',
                interval=1, # every week
                byday='mo tu we th fr'.spit(' '),
                until=datetime.now()
            ))
            # dates to exclude
            #event.add('exdate', (datetime.now(),))

            event.add('location', section.section_period.location)
            event.add('uid', '%s_%s_%s' % (year, month, section.crn))


            cal.add_component(event)
    response = HttpResponse(cal.as_string())
    response['Content-Type'] = 'text/calendar'
    return response
