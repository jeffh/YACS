from django.db.models import F
from django.views.generic import ListView
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from timetable.courses.views import SemesterBasedMixin, SELECTED_COURSES_SESSION_KEY
from timetable.courses.models import Semester, SectionPeriod, Course, Section
from timetable.scheduler import models
from timetable.scheduler.scheduler import compute_schedules

from pprint import pprint

def build_schedule_object_graph(schedules, sections_and_periods):
    schedules = list(set(schedules))

    secid_to_periods = {}
    for snp in sections_and_periods:
        secid_to_periods[snp.section_id] = secid_to_periods.get(snp.section_id, []) + [snp.period]

    crn_to_section = {}
    for snp in sections_and_periods:
        snp.section.all_periods = secid_to_periods[snp.section_id]
        crn_to_section[snp.section.crn] = snp.section

    sid_to_sections = {}
    for schedule in schedules:
        sections = []
        print repr(schedule.crns)
        for crn in schedule.crns:
            sections.append(crn_to_section[crn])
        sid_to_sections[schedule.id] = sections

    for schedule in schedules:
        schedule.all_sections = sid_to_sections[schedule.id]

    return schedules

def sorted_daysofweek(dow):
    "Sorts list of days of the week to what we're expected."
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    return [d for d in days if d in dow]

def period_stats(periods):
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

def force_compute_schedules(request, year, month):
    selected_courses = request.session.get(SELECTED_COURSES_SESSION_KEY, {})
    crns = [crn for sections in selected_courses.values() for crn in sections]

    sections = Section.objects.filter(
        crn__in=crns, semesters__year__contains=year, semesters__month__contains=month
    ).select_related('course').distinct()

    sections_and_periods = SectionPeriod.objects.filter(
        semester__year__contains=year,
        semester__month__contains=month,
        section__crn__in=crns,
        #section__seats_taken__lt=F('section__seats_total'),
    ).select_related('section', 'period', 'section__course', 'section__course__department')

    sid_to_periods = section_ids_to_periods(sections_and_periods)

    periods = [snp.period for snp in sections_and_periods]

    selected_courses = {}
    for section in sections:
        section.all_section_periods = sid_to_periods[section.id]
        selected_courses[section.course] = selected_courses.get(section.course, []) + [section]

    schedules = compute_schedules(selected_courses)

    pprint(schedules)

    timerange, dows = period_stats(periods)

    return render_to_response('scheduler/schedule_list.html', {
        'schedules': schedules,
        'time_range': timerange,
        'dows': dows,
        'sem_year': year,
        'sem_month': month,
    }, RequestContext(request))

# scrapped... it's a lot more complicated to cache this data. Do it some other time.
def schedules(request, year, month):
    selected_courses = request.session.get(SELECTED_COURSES_SESSION_KEY, {})
    crns = [crn for sections in selected_courses.values() for crn in sections]

    semester = get_object_or_404(Semester, year=year, month=month)
    # we just need objects to be created
    schedules = models.Schedule.objects.get_or_create_all_from_crns(crns, semester)

    pprint(schedules)

    sections_and_periods = SectionPeriod.objects.filter(
        semester=semester,
        section__crn__in=crns,
        #section__seats_taken__lt=F('section__seats_total'),
    ).select_related('section', 'period', 'section__course', 'section__course__department')

    # build the entire schedule object tree
    schedules = build_schedule_object_graph(schedules, sections_and_periods)

    return render_to_response('scheduler/schedule_list.html', {
        'schedules': schedules,
        'sem_year': year,
        'sem_month': month,
    }, RequestContext(request))

