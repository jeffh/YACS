from icalendar import Calendar, Event, UTC, vText
from datetime import datetime
from json import dumps
import urllib

from django.db.models import F, Q
from django.views.generic import ListView
from django.http import HttpResponse, Http404, HttpResponseNotFound
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext
from django.conf import settings
from django.core.cache import cache
from django.core.urlresolvers import reverse

from yacs.courses.views import SemesterBasedMixin, SELECTED_COURSES_SESSION_KEY
from yacs.courses.models import Semester, SectionPeriod, Course, Section, Department
from yacs.courses.utils import dict_by_attr, ObjectJSONEncoder
from yacs.scheduler import models
from yacs.scheduler.scheduler import compute_schedules

import time

class Timer():
   def __enter__(self): self.start = time.time()
   def __exit__(self, *args): print time.time() - self.start

ICAL_PRODID = getattr(settings, 'SCHEDULER_ICAL_PRODUCT_ID', '-//Jeff Hui//YACS Export 1.0//EN')

DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
def sorted_daysofweek(dow):
    "Sorts list of days of the week to what we're expected."
    return [d for d in DAYS if d in dow]

def period_stats(periods):
    if len(periods) < 1:
        return range(8, 20), DAYS[:5]
    min_time, max_time, dow_used = None, None, set()
    for period in periods:
        min_time = min(min_time or period.start, period.start)
        max_time = max(max_time or period.end, period.end)
        dow_used = dow_used.union(period.days_of_week)

    timerange = range(min_time.hour -1 , max_time.hour + 2)
    return timerange, sorted_daysofweek(dow_used)

def section_ids_to_periods(sections_and_periods):
    secid_to_periods = {}
    for snp in sections_and_periods:
        secid_to_periods[snp.section_id] = secid_to_periods.get(snp.section_id, []) + [snp]
    return secid_to_periods

def take(amount, generator):
    result = []
    for i, g in enumerate(generator):
        result.append(g)
        if i + 1 >= amount:
            return result
    return result

def build_section_mapping(schedules):
    "Build a data structure specifically for the template to hammer away at."
    sections = {} # [schedule-index][dow][starting-hour]
    for i, schedule in enumerate(schedules):
        dows = sections[i+1] = {}
        for secs in schedule.values():
            for sp in secs.all_section_periods:
                for dow in sp.period.days_of_week:
                    dows[dow] = dows.get(dow, {})
                    dows[dow][sp.period.start.hour] = sp
    return sections

def build_color_mapping(courses, max=9):
    colors = {}
    for i, course in enumerate(courses):
        colors[course] = (i % max) + 1
    return colors

def build_conflict_mapping(conflicts):
    result = {} # section_id => [section_ids]
    for conflict in conflicts:
        s = result[conflict.section1.id] = result.get(conflict.section1.id, set())
        s.add(conflict.section2.id)
        s = result[conflict.section2.id] = result.get(conflict.section2.id, set())
        s.add(conflict.section1.id)
    return result

def schedules_bootloader(request, year, month):
    crns = request.GET.get('crns')
    if crns is not None:
        crns = [c for c in crns.split('-') if c.strip() != '']
    if crns is None:
        selected_courses = request.session.get(SELECTED_COURSES_SESSION_KEY, {})
        return redirect(reverse('schedules', kwargs=dict(year=year, month=month)) + '?crns=' + urllib.quote('-'.join(str(crn) for sections in selected_courses.values() for crn in sections)))

    prefix = 'crn='
    crns = prefix + ('&'+prefix).join(urllib.quote(str(crn)) for crn in crns)

    single_schedule = ''
    # disabled for now... use JS
    #schedule_offset = request.GET.get('at', '')
    #if schedule_offset:
    #    single_schedule = "&from=%s&limit=1" % urllib.quote(schedule_offset)
    return render_to_response('scheduler/placeholder_schedule_list.html', {
        'ajax_url': reverse('ajax-schedules', kwargs=dict(year=year, month=month)) + '?' + crns + single_schedule,
        'sem_year': year,
        'sem_month': month,
    }, RequestContext(request))

def json_compute_schedules_via_cache(request, year, month):
    requested_crns = request.GET.getlist('crn')
    savepoint = int(request.GET.get('from', 0))
    crns = []
    for crn in requested_crns:
        try:
            crns.append(int(crn))
        except (ValueError, TypeError):
            pass
    if len(crns) > 50:
        raise Http404

    sections = models.SectionProxy.objects.by_semester(year, month).filter(crn__in=crns).select_related('course', 'course__department').full_select(year, month)
    selected_courses = dict_by_attr(sections, 'course')
    section_ids = set(s.id for s in sections)
    conflicts = models.SectionConflict.objects.filter(
        section1__id__in=section_ids, section2__id__in=section_ids
    ).select_related('section1', 'section2')
    conflict_mapping = build_conflict_mapping(conflicts)
    for section in sections:
        section.conflicts = conflict_mapping.get(section.id) or set()

    # we should probably set some upper bound of computation and restrict number of sections used.
    #schedules = take(100, compute_schedules(selected_courses, generator=True))
    if request.GET.get('check'):
        for schedule in compute_schedules(selected_courses, generator=True):
            return HttpResponse('ok')
        return HttpResponseNotFound('conflicts')
    schedules = compute_schedules(selected_courses, start=savepoint, generator=True)

    try:
        limit = int(request.GET.get('limit'))
    except (ValueError, TypeError):
        limit = 0
    if limit > 0:
        print "limiting by", limit
        schedules = take(limit, schedules)
    else:
        schedules = list(schedules)

    periods = set(p for s in sections for p in s.all_periods)
    timerange, dows = period_stats(periods)
    section_mapping = {} # [schedule-index][dow][starting-hour]
    for i, schedule in enumerate(schedules):
        the_dows = section_mapping[i+1] = {}
        for secs in schedule.values():
            for j, sp in enumerate(secs.all_section_periods):
                for dow in sp.period.days_of_week:
                    the_dows[dow] = the_dows.get(dow, {})
                    the_dows[dow][sp.period.start.hour] = {
                        'cid': sp.section.course.id,
                        'crn': sp.section.crn,
                        'pindex': j,
                    }
    #color_mapping = build_color_mapping(selected_courses)

    courses_output, sections_output = {}, {}
    for course, sections in selected_courses.items():
        courses_output[course.id] = course.toJSON(select_related=((Department._meta.db_table, 'code'),))
        for section in sections:
            sections_output[section.crn] = section.toJSON()

    schedules_output = [{ str(course.id): section.crn for course, section in schedule.items() } for schedule in schedules]

    if len(schedules_output):
        context = {
            'schedules': schedules_output,
            'courses': courses_output,
            'sections': sections_output,
            'section_mapping': section_mapping,
            'time_range': timerange,
            'dows': dows,
            'sem_year': year,
            'sem_month': month,
        }
    else:
        context = {
            'schedules': [],
            'sem_year': year,
            'sem_month': month,
        }

    return HttpResponse(ObjectJSONEncoder(indent=4).encode(context))

def compute_schedules_via_cache(request, year, month):
    with Timer():
        selected_courses = request.session.get(SELECTED_COURSES_SESSION_KEY, {})
        crns = [crn for sections in selected_courses.values() for crn in sections]
        savepoint = int(request.GET.get('from', 0))

        sections = models.SectionProxy.objects.filter(crn__in=crns).select_related('course', 'course__department').full_select(year, month)
        selected_courses = dict_by_attr(sections, 'course')
        section_ids = set(s.id for s in sections)
        conflicts = models.SectionConflict.objects.filter(
            section1__id__in=section_ids, section2__id__in=section_ids
        ).select_related('section1', 'section2')
        conflict_mapping = build_conflict_mapping(conflicts)
        for section in sections:
            section.conflicts = conflict_mapping.get(section.id) or set()

        periods = set(p for s in sections for p in s.all_periods)

        # we should probably set some upper bound of computation and restrict number of sections used.
        #schedules = take(100, compute_schedules(selected_courses, generator=True))
        schedules = compute_schedules(selected_courses, start=savepoint)
        timerange, dows = period_stats(periods)
        sections_mapping = build_section_mapping(schedules)
        color_mapping = build_color_mapping(selected_courses)

        context = {
            'schedules': schedules,
            'sections':sections_mapping,
            'time_range': timerange,
            'selected_courses': selected_courses,
            'color_mapping': color_mapping,
            'dows': dows,
            'sem_year': year,
            'sem_month': month,
        }

        if request.GET.get('ajax'):
            return HttpResponse(dumps([{ course.id: section.crn for course, section in schedule.items() } for schedule in schedules]))

        return render_to_response('scheduler/schedule_list.html', context, RequestContext(request))

def force_compute_schedules(request, year, month):
    with Timer():
        selected_courses = request.session.get(SELECTED_COURSES_SESSION_KEY, {})
        crns = [crn for sections in selected_courses.values() for crn in sections]
        savepoint = int(request.GET.get('from', 0))

        sections = Section.objects.filter(crn__in=crns).select_related('course', 'course__department').full_select(year, month)

        selected_courses = dict_by_attr(sections, 'course')

        periods = set(p for s in sections for p in s.all_periods)

        # we should probably set some upper bound of computation and restrict number of sections used.
        #schedules = take(100, compute_schedules(selected_courses, return_generator=True))
        schedules = compute_schedules(selected_courses, start=savepoint)
        timerange, dows = period_stats(periods)
        sections_mapping = build_section_mapping(schedules)
        color_mapping = build_color_mapping(selected_courses)


        context = {
            'schedules': schedules,
            'sections':sections_mapping,
            'time_range': timerange,
            'selected_courses': selected_courses,
            'color_mapping': color_mapping,
            'dows': dows,
            'sem_year': year,
            'sem_month': month,
        }

        if request.GET.get('ajax'):
            return HttpResponse(dumps([{ course.id: section.crn for course, section in schedule.items() } for schedule in schedules]))

        return render_to_response('scheduler/schedule_list.html', context, RequestContext(request))


def icalendar(request, year, month, crns):
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
