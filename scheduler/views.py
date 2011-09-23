from django.db.models import F
from django.views.generic import ListView
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from timetable.courses.views import SemesterBasedMixin, SELECTED_COURSES_SESSION_KEY
from timetable.courses.models import Semester, SectionPeriod, Course
from timetable.scheduler import models

def build_schedule_object_graph(schedules_and_sections, sections_and_periods):
    schedules = []
    for sns in schedules_and_sections:
        schedules.append(sns.schedule)
    
    schedules = list(set(schedules))

    secid_to_periods = {}
    for snp in sections_and_periods:
        secid_to_periods[snp.section_id] = secid_to_periods.get(snp.section_id, []) + [snp.period]

    sid_to_sections = {}
    for sns in schedules_and_sections:
        sns.section.all_periods = secid_to_periods[sns.section_id]
        sid_to_sections[sns.schedule_id] = sid_to_sections.get(sns.schedule_id, []) + [sns.section]
    
    for schedule in schedules:
        schedule.all_sections = sid_to_sections[schedule.id]
    
    return schedules

def schedules(request, year, month):
    selected_courses = request.session.get(SELECTED_COURSES_SESSION_KEY, {})
    crns = [crn for sections in selected_courses.values() for crn in sections]

    semester = get_object_or_404(Semester, year=year, month=month)
    # we just need objects to be created
    schedules = models.Schedule.objects.get_or_create_all_from_crns(crns, semester)
    schedule_ids = [s.id for s in schedules]

    schedules_and_sections = models.SectionInSchedule.objects.filter(
        semester=semester,
        schedule__id__in=schedule_ids,
        #section__seats_taken__lt=F('section__seats_total'),
    ).select_related('section', 'schedule')

    sections_and_periods = SectionPeriod.objects.filter(
        semester=semester,
        section__crn__in=crns,
        #section__seats_taken__lt=F('section__seats_total'),
    ).select_related('section', 'period', 'section__course', 'section__course__department')

    # build the entire schedule object tree
    schedules = build_schedule_object_graph(schedules_and_sections, sections_and_periods)

    return render_to_response('scheduler/schedule_list.html', {
        'schedules': schedules,
    }, RequestContext(request))

