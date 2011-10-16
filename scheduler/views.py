from icalendar import Calendar, Event, UTC, vText
from datetime import datetime

from django.db.models import F
from django.views.generic import ListView
from django.http import HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.conf import settings

from yacs.courses.views import SemesterBasedMixin, SELECTED_COURSES_SESSION_KEY
from yacs.courses.models import Semester, SectionPeriod, Course, Section
from yacs.courses.utils import dict_by_attr
from yacs.scheduler import models
from yacs.scheduler.scheduler import compute_schedules

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
            break
    return result

def force_compute_schedules(request, year, month):
    selected_courses = request.session.get(SELECTED_COURSES_SESSION_KEY, {})
    crns = [crn for sections in selected_courses.values() for crn in sections]

    #sections = Section.objects.filter(
    #    crn__in=crns, semesters__year__contains=year, semesters__month__contains=month
    #).select_related('course').distinct()

    #sections_and_periods = SectionPeriod.objects.filter(
    #    semester__year__contains=year,
    #    semester__month__contains=month,
    #    section__crn__in=crns,
    #    #section__seats_taken__lt=F('section__seats_total'),
    #).select_related('section', 'period', 'section__course', 'section__course__department')

    #sid_to_periods = section_ids_to_periods(sections_and_periods)

    print 'crns', crns
    sections = Section.objects.filter(crn__in=crns).select_related('course', 'course__department').full_select(year, month)

    selected_courses = dict_by_attr(sections, 'course')

    periods = set(p for s in sections for p in s.all_periods)
    print periods

    #selected_courses = {}
    #for section in sections:
    #    section.all_section_periods = sid_to_periods[section.id]
    #    selected_courses[section.course] = selected_courses.get(section.course, []) + [section]

    schedules = take(20, compute_schedules(selected_courses, return_generator=True))

    timerange, dows = period_stats(periods)

    return render_to_response('scheduler/schedule_list.html', {
        'schedules': schedules,
        'time_range': timerange,
        'dows': dows,
        'sem_year': year,
        'sem_month': month,
    }, RequestContext(request))


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
