from django.core.urlresolvers import reverse
from django_dynamic_fixture import new, get, DynamicFixture as F
from yacs.courses import models
from yacs.scheduler.views import SELECTED_COURSES_SESSION_KEY
from shortcuts import ShortcutTestCase
from datetime import time

def create_section(**kwargs):
    semesters = kwargs.pop('semesters', [])
    periods = kwargs.pop('periods', [])
    section = get(models.Section, **kwargs)
    for semester in semesters:
        get(models.SemesterSection, semester=semester, section=section)
    for period in periods:
        get(models.SectionPeriod, section=section, **period)
    return section

def create_periods(*ranges):
    periods = []
    for start, end, dow in ranges:
        periods.append(get(
            models.Period,
            start=time(*start),
            end=time(*end),
            days_of_week_flag=dow,
        ))
    return periods

class TestScheduleViews(ShortcutTestCase):
    urls = 'yacs.urls'

    def setUp(self):
        semester = get(models.Semester, year=2011, month=1)

        course1 = get(models.Course, id=1, min_credits=4, max_credits=4, semesters=[semester])
        course2 = get(models.Course, id=2, min_credits=4, max_credits=4, semesters=[semester])

        periods = create_periods(
            ((10, 0), (11, 50), models.Period.MONDAY | models.Period.THURSDAY),  # 0
            ((10, 0), (10, 50), models.Period.MONDAY | models.Period.THURSDAY),  # 1
            ((11, 0), (11, 50), models.Period.TUESDAY | models.Period.FRIDAY),  # 2
            ((12, 0), (13, 50), models.Period.TUESDAY | models.Period.FRIDAY),  # 3
            ((14, 0), (16, 50), models.Period.WEDNESDAY),  # 4
            ((10, 0), (10, 50), models.Period.TUESDAY | models.Period.FRIDAY),  # 5
            ((10, 0), (11, 50), models.Period.TUESDAY | models.Period.FRIDAY),  # 6
        )
        # conflicts: (0, 1), (2, 3), (5, 6)

        section1 = create_section(
            course=course1,
            crn=1000,
            number=1,
            seats_taken=3,
            seats_total=10,
            periods=[
                dict(period=periods[0], semester=semester),
                dict(period=periods[4], semester=semester),
            ],
            semesters=[semester],
        )
        section2 = create_section(
            course=course1,
            crn=1001,
            number=2,
            seats_taken=4,
            seats_total=5,
            periods=[
                dict(period=periods[1], semester=semester),
            ],
            semesters=[semester],
        )
        section3 = create_section(
            course=course2,
            crn=1003,
            number=1,
            seats_taken=4,
            seats_total=6,
            periods=[
                dict(period=periods[4], semester=semester),
            ],
            semesters=[semester],
        )
        # can't figure out where the other semester objects get created
        # its do to get(models.Section, ...) but not sure where
        models.Semester.objects.filter(id__gt=semester.id).delete()

    def set_selected(self, value):
        session = self.client.session
        session[SELECTED_COURSES_SESSION_KEY] = value
        return session

    def test_get_schedules(self):
        self.set_selected({1: [1000, 1001], 2: [1003]})
        response = self.get('schedules', year=2011, month=1, status_code=200)

