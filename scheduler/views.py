from django.db.models import F
from django.views.generic import ListView
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from timetable.courses.views import SemesterBasedMixin, SELECTED_COURSES_SESSION_KEY
from timetable.courses.models import Semester, SectionPeriod, Course
from timetable.scheduler import models

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

def compute_schedules(request, year, month):
    pass

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
    }, RequestContext(request))

