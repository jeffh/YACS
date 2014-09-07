from datetime import time
from json import loads
import sys

from django.core.urlresolvers import reverse
from shortcuts import ShortcutTestCase

from courses import models
from courses.tests.factories import (
    SemesterFactory, CourseFactory, PeriodFactory,
    SectionFactory, SectionPeriodFactory, OfferedForFactory
)
from scheduler.models import cache_conflicts


# TODO: convert this (and the tests that use this) to use factories
def create_section(**kwargs):
    periods = kwargs.pop('periods', [])
    section = models.Section.objects.create(**kwargs)
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


class ICSViewTest(ShortcutTestCase):
    urls = 'yacs.urls'

    def test_ics(self):
        # FIXME: remove http request dependency
        semester = SemesterFactory.create(year=2012, month=9)
        sections = SectionFactory.create_batch(3, semester=semester)
        crns = [str(s.crn) for s in sections]
        response = self.get('ics', get='?crn=' + '&crn='.join(crns), status_code=200)


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
            id=1,
            course=self.course1,
            crn=1000,
            number=1,
            seats_taken=3,
            seats_total=10,
            semester=self.semester,
            periods=[
                dict(period=self.periods[0], semester=self.semester),
                dict(period=self.periods[4], semester=self.semester),
            ],
        )
        self.section2 = create_section(
            id=2,
            course=self.course1,
            crn=1001,
            number=2,
            seats_taken=4,
            seats_total=5,
            semester=self.semester,
            periods=[
                dict(period=self.periods[1], semester=self.semester),
            ],
        )
        self.section3 = create_section(
            id=3,
            course=self.course2,
            crn=1002,
            number=1,
            seats_taken=4,
            seats_total=6,
            semester=self.semester,
            periods=[
                dict(period=self.periods[4], semester=self.semester),
            ],
        )
        self.section4 = create_section(
            id=4,
            course=self.course2,
            crn=1003,
            number=2,
            seats_taken=7,
            seats_total=6,
            semester=self.semester,
            periods=[
                dict(period=self.periods[5], semester=self.semester),
            ]
        )
        cache_conflicts(semester=self.semester)

    def test_get_schedules(self):
        "/2011/1/schedules/"
        response = self.get('schedules', year=2011, month=1)
        self.assertEqual(response.status_code, 302)
        # redirects to url below

    def test_get_schedules(self):
        "/2011/1/schedules/1/"
        response = self.get('schedules', year=2011, month=1, id=1)
        self.assertEqual(response.status_code, 302)
        # redirects to url below

    def test_get_schedules(self):
        "/2011/1/schedules/1/1/"
        response = self.get('schedules', year=2011, month=1, id=1, index=1)
        self.assertEqual(response.status_code, 200)
