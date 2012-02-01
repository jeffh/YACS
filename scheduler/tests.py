from datetime import time
from json import loads

from django.core.urlresolvers import reverse
from shortcuts import ShortcutTestCase

from courses import models
from courses.tests.factories import (SemesterFactory, CourseFactory, PeriodFactory,
        SemesterSectionFactory, SectionFactory, SectionPeriodFactory, OfferedForFactory)
from models import cache_conflicts
from views import SELECTED_COURSES_SESSION_KEY


# TODO: convert this (and the tests that use this) to use factories
def create_section(**kwargs):
    semesters = kwargs.pop('semesters', [])
    periods = kwargs.pop('periods', [])
    section = models.Section.objects.create(**kwargs)
    for semester in semesters:
        models.SemesterSection.objects.create(semester=semester, section=section)
    for period in periods:
        models.SectionPeriod.objects.create(section=section, **period)
    return section


def create_periods(*ranges):
    periods = []
    for start, end, dow in ranges:
        periods.append(PeriodFactory.create(
            start=time(*start),
            end=time(*end),
            days_of_week_flag=dow,
        ))
    return periods


class ScheduleViewsSmokeTests(ShortcutTestCase):
    urls = 'yacs.urls'

    def setUp(self):
        self.semester = SemesterFactory.create(year=2011, month=1)

        self.course1 = CourseFactory.create(id=1, min_credits=4, max_credits=4)
        OfferedForFactory.create(course=self.course1, semester=self.semester)
        self.course2 = CourseFactory.create(id=2, min_credits=4, max_credits=4)
        OfferedForFactory.create(course=self.course2, semester=self.semester)

        self.periods = create_periods(
            ((10, 0), (11, 50), models.Period.MONDAY | models.Period.THURSDAY),  # 0
            ((10, 0), (10, 50), models.Period.MONDAY | models.Period.THURSDAY),  # 1
            ((11, 0), (11, 50), models.Period.TUESDAY | models.Period.FRIDAY),  # 2
            ((12, 0), (13, 50), models.Period.TUESDAY | models.Period.FRIDAY),  # 3
            ((14, 0), (16, 50), models.Period.WEDNESDAY),  # 4
            ((10, 0), (10, 50), models.Period.TUESDAY | models.Period.FRIDAY),  # 5
            ((10, 0), (11, 50), models.Period.TUESDAY | models.Period.FRIDAY),  # 6
        )
        # conflicts: (0, 1), (2, 3), (5, 6)

        self.section1 = create_section(
            course=self.course1,
            crn=1000,
            number=1,
            seats_taken=3,
            seats_total=10,
            semesters=[self.semester],
            periods=[
                dict(period=self.periods[0], semester=self.semester),
                dict(period=self.periods[4], semester=self.semester),
            ],
        )
        self.section2 = create_section(
            course=self.course1,
            crn=1001,
            number=2,
            seats_taken=4,
            seats_total=5,
            semesters=[self.semester],
            periods=[
                dict(period=self.periods[1], semester=self.semester),
            ],
        )
        self.section3 = create_section(
            course=self.course2,
            crn=1003,
            number=1,
            seats_taken=4,
            seats_total=6,
            semesters=[self.semester],
            periods=[
                dict(period=self.periods[4], semester=self.semester),
            ],
        )
        self.section4 = create_section(
            course=self.course2,
            crn=1004,
            number=2,
            seats_taken=7,
            seats_total=6,
            semesters=[self.semester],
            periods=[
                dict(period=self.periods[5], semester=self.semester),
            ]
        )
        # can't figure out where the other semester objects get created
        # its do to get(models.Section, ...) but not sure where
        #models.Semester.objects.filter(id__gt=self.semester.id).delete()
        cache_conflicts(semester=self.semester)

    def set_selected(self, value):
        return self.set_session({SELECTED_COURSES_SESSION_KEY: value})

    def get_ajax_schedules_from_crns(self, crns):
        return self.get('ajax-schedules', year=2011, month=1, get='?crn=' + '&crn='.join(map(str, crns)))

    def test_get_ajax_check(self):
        "/2012/1/schedules/ajax/?check=1&crn=95069&_=132124919995"
        pass # TODO

    def test_get_ajax_schedules_for_full_sections(self):
        "/2011/1/schedules/ajax/?crn=1004"
        response = self.get_ajax_schedules_from_crns([1004])
        self.assertEqual(response.status_code, 200)

        obj = loads(response.content)
        schedules = obj['schedules']
        self.assertEqual(len(schedules), 1)
        self.assertEqual(schedules[0], {'2': 1004})

    def test_get_schedules(self):
        "/2011/1/schedules/"
        self.set_selected({1: [1000, 1001], 2: [1003]})
        response = self.get('schedules', year=2011, month=1)
        self.assertEqual(response.status_code, 302)

    def test_get_ajax_schedules(self):
        "/2011/1/schedules/ajax/?crn=1000&crn=1001&crn=1003"
        response = self.get_ajax_schedules_from_crns([1000, 1001, 1003])
        self.assertEqual(response.status_code, 200)

        obj = loads(response.content)
        schedules = obj['schedules']
        self.assertEqual(len(schedules), 1)
        self.assertEqual(schedules[0], {'1': 1001, '2': 1003})

