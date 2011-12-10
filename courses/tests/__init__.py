"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from shortcuts import ShortcutTestCase
from yacs.courses import models, utils, managers
from yacs.courses.views import SELECTED_COURSES_SESSION_KEY
from yacs.courses.tests.factories import (SemesterFactory, SemesterDepartmentFactory,
        OfferedForFactory, CourseFactory, SemesterSectionFactory, SectionFactory,
        DepartmentFactory, PeriodFactory, SectionPeriodFactory)
from collections import namedtuple
from mock import Mock, patch
import datetime
import sys

# utils
def course(name):
    return models.Course.objects.get(name=name)
# end utils

class SemesterBasedQuerySetTest(TestCase):
    def setUp(self):
        self.sem = SemesterFactory.create(year=2011, month=1)
        self.sd1 = SemesterDepartmentFactory.create(semester=self.sem)
        self.sd2 = SemesterDepartmentFactory.create(semester=self.sem)

    def test_semester_based_queryset_for_a_semester(self):
        departments = models.Department.objects.by_semester(2011, 1)
        self.assertEqual([self.sd1.department, self.sd2.department], list(departments))

    def test_semester_based_queryset_is_empty_for_another_semester(self):
        departments = models.Department.objects.by_semester(2010, 1)
        self.assertEqual([], list(departments))

    def test_no_semester_filtering_if_none(self):
        departments = models.Department.objects.by_semester(None, None)
        self.assertEqual([self.sd1.department, self.sd2.department], list(departments))

class SerializableQuerySetTest(TestCase):
    def setUp(self):
        self.sem = SemesterFactory.create(year=2011, month=1)
        dept1 = DepartmentFactory.create(name='depart1', code='dept1')
        self.sd1 = SemesterDepartmentFactory.create(semester=self.sem, department=dept1)
        dept2 = DepartmentFactory.create(name='depart2', code='dept2')
        self.sd2 = SemesterDepartmentFactory.create(semester=self.sem, department=dept2)

    def test_serializable_queryset(self):
        departments = models.Department.objects.all().toJSON()
        self.assertEqual([{
            'name': 'depart1',
            'code': 'dept1',
        }, {
            'name': 'depart2',
            'code': 'dept2',
        }], departments)

class SectionPeriodQuerySetTest(TestCase):
    def setUp(self):
        self.sem = SemesterFactory.create(year=2011, month=1)
        self.dept = DepartmentFactory.create(code='CSCI')
        SemesterDepartmentFactory.create(department=self.dept, semester=self.sem)

        self.course = CourseFactory.create(number=2222, department=self.dept)
        OfferedForFactory.create(course=self.course, semester=self.sem)

        self.section = SectionFactory.create(course=self.course)
        SemesterSectionFactory.create(semester=self.sem, section=self.section)
        SectionPeriodFactory.create(section=self.section)

    def test_filter_by_course_code(self):
        sps = models.SectionPeriod.objects.by_course_code('CSCI', 2222)
        self.assertEqual([self.section], [sp.section for sp in sps])

    def test_filter_by_course(self):
        c = models.Course.objects.all()[0]
        sps = models.SectionPeriod.objects.by_course(c)
        self.assertEqual([self.section], [sp.section for sp in sps])

    def test_filter_by_sections(self):
        sps = models.SectionPeriod.objects.by_sections([self.section])
        self.assertEqual([self.section], [sp.section for sp in sps])

    def test_filter_by_courses(self):
        sps = models.SectionPeriod.objects.by_courses([self.course])
        self.assertEqual([self.section], [sp.section for sp in sps])

class CourseQuerySetTest(TestCase):
    def setUp(self):
        self.sem = SemesterFactory.create()
        self.dept1 = DepartmentFactory.create(code='CSCI')
        self.dept2 = DepartmentFactory.create()

        self.course1 = CourseFactory.create(department=self.dept1, name='the course')
        OfferedForFactory.create(course=self.course1, semester=self.sem)

        self.course2 = CourseFactory.create(department=self.dept2)
        OfferedForFactory.create(course=self.course2, semester=self.sem)

        self.course3 = CourseFactory.create(department=self.dept1, name='another course')
        OfferedForFactory.create(course=self.course3, semester=self.sem)

    def test_filter_by_department(self):
        courses = models.Course.objects.by_department(self.dept1)
        self.assertEqual([self.course1, self.course3], list(courses))

    def test_search_by_department(self):
        courses = models.Course.objects.search(dept='CSCI')
        self.assertEqual([self.course1, self.course3], list(courses))

    def test_search_by_query(self):
        courses = models.Course.objects.search('another').get()
        self.assertEqual(self.course3, courses)

class SemesterTest(TestCase):
    def setUp(self):
        self.now = datetime.datetime.now().replace(microsecond=0)
        self.sem = SemesterFactory.create(year=2011, month=2, name='foo', date_updated=self.now)

    def test_to_json(self):
        expected = {
            'year': 2011,
            'month': 2,
            'name': 'foo',
            'date_updated': self.now,
        }
        result = self.sem.toJSON()
        result['date_updated'] = result['date_updated'].replace(microsecond=0)
        self.assertEquals(expected, result)

    @patch.object(models, 'has_model', lambda *a, **k: True)
    @patch.object(models.Semester, 'departments', Mock())
    def test_to_json_with_department(self):
        m = models.Semester.departments.all.return_value = Mock()
        m.toJSON.return_value = {'foobar': 1}
        expected = {
            'year': 2011,
            'month': 2,
            'name': 'foo',
            'date_updated': self.now,
            'departments': {'foobar': 1}
        }
        result = self.sem.toJSON()
        result['date_updated'] = result['date_updated'].replace(microsecond=0)
        self.assertEquals(expected, result)

class DepartmentTest(TestCase):
    def setUp(self):
        self.dept = DepartmentFactory.create(name='foo', code='CSCI')

    def test_to_json(self):
        expected = {
            'name': 'foo',
            'code': 'CSCI',
        }
        result = self.dept.toJSON()
        self.assertEqual(expected, result)

    @patch.object(models, 'has_model', lambda *a, **k: True)
    @patch.object(models.Department, 'semesters', Mock())
    def test_to_json_with_semesters(self):
        m = models.Department.semesters.all.return_value = Mock()
        m.toJSON.return_value = {'foobar': 1}
        expected = {
            'name': 'foo',
            'code': 'CSCI',
            'semesters': {'foobar': 1},
        }
        result = self.dept.toJSON()
        self.assertEqual(expected, result)

class PeriodTest(TestCase):
    def setUp(self):
        self.start = datetime.time(hour=7)
        self.end = datetime.time(hour=7, minute=50)
        self.period = PeriodFactory.create(start=self.start, end=self.end, days_of_week_flag=1)

    def test_to_json(self):
        expected = {
            'start_time': self.start,
            'end_time': self.end,
            'days_of_the_week': ['Monday']
        }
        result = self.period.toJSON()
        self.assertEqual(expected, result)

    def test_is_not_tba(self):
        self.assertFalse(self.period.is_to_be_announced)

    def test_days_of_week(self):
        self.assertEqual(['Monday'], self.period.days_of_week)

    def test_does_not_conflicts_with(self):
        p = PeriodFactory.build(
            start=datetime.time(hour=8),
            end=datetime.time(hour=9),
            days_of_week_flag=1
        )
        self.assertFalse(self.period.conflicts_with(p))

    def test_conflicts_with(self):
        p = PeriodFactory.build(
            start=datetime.time(hour=7),
            end=datetime.time(hour=9),
            days_of_week_flag=1
        )
        self.assertTrue(self.period.conflicts_with(p))

    def test_days_of_week_setter(self):
        self.period.days_of_week = ['Tuesday']
        self.assertEqual(self.period.days_of_week_flag, 2)

    def test_period_to_tuple(self):
        expected = (self.start, self.end, 1)
        self.assertEqual(expected, self.period.to_tuple())

    def test_period_is_on_monday(self):
        self.assertTrue(self.period.is_on_day(models.Period.MONDAY))

    def test_period_is_not_on_tuesday(self):
        self.assertFalse(self.period.is_on_day(models.Period.TUESDAY))

class TBAPeriodTest(TestCase):
    def setUp(self):
        self.period = PeriodFactory.create(start=None, end=None, days_of_week_flag=1)

    def test_is_tba(self):
        self.assertTrue(self.period.is_to_be_announced)

class SectionTest(TestCase):
    def test_to_json(self):
        section = SectionFactory.build(
            number=1, crn=2, seats_taken=3, seats_total=4
        )
        expected = {
            'number': 1,
            'crn': 2,
            'seats_taken': 3,
            'seats_total': 4,
            'seats_left': 1,
        }
        result = section.toJSON()
        self.assertEqual(expected, result)

    def test_is_not_study_abroad(self):
        section = SectionFactory.build()
        self.assertFalse(section.is_study_abroad)

    def test_is_study_abroad(self):
        section = SectionFactory.build(number=models.Section.STUDY_ABROAD)
        self.assertTrue(section.is_study_abroad)

    def test_is_not_full(self):
        section = SectionFactory.build()
        self.assertFalse(section.is_full)

    def test_is_full(self):
        section = SectionFactory.build(seats_taken=2, seats_total=2)
        self.assertTrue(section.is_full)

    def test_seats_left(self):
        section = SectionFactory.build(seats_taken=4, seats_total=5)
        self.assertEqual(section.seats_left, 1)

    def test_seats_left_should_never_be_negative(self):
        section = SectionFactory.build(seats_taken=7, seats_total=5)
        self.assertEqual(section.seats_left, 0)

    @patch.object(sys, 'stdout', Mock())
    def test_days_of_week(self):
        section = SectionFactory.create()
        period1 = PeriodFactory.create(days_of_week_flag=models.Period.TUESDAY)
        period2 = PeriodFactory.create(days_of_week_flag=models.Period.MONDAY)
        SectionPeriodFactory.create(period=period1, section=section)
        SectionPeriodFactory.create(period=period2, section=section)

        expected = ['Monday', 'Tuesday']
        self.assertEqual(expected, section.days_of_week)

    @patch.object(sys, 'stdout', Mock())
    def test_instructors(self):
        section = SectionFactory.create()
        SectionPeriodFactory.create(section=section, instructor='foo')
        SectionPeriodFactory.create(section=section, instructor='bar')

        expected = set(['foo', 'bar'])
        self.assertEqual(expected, section.instructors)

    @patch.object(sys, 'stdout', Mock())
    def test_get_period_section_from_db(self):
        section = SectionFactory.build()
        self.assertEqual(set([]), section.get_period_sections())

    def test_get_period_section_from_cache(self):
        section = SectionFactory.build()
        section.all_section_periods = [1,2]

        self.assertEqual(set([1,2]), section.get_period_sections())

    def test_get_periods_from_db(self):
        section = SectionFactory.build()
        section.get_period_sections = Mock()
        section_periods = [SectionPeriodFactory.create() for i in range(3)]
        section.get_period_sections.return_value = set(section_periods)

        self.assertEqual(set([sp.period for sp in section_periods]), section.get_periods())

    def test_conflicts_with_self(self):
        section = SectionFactory.build()
        self.assertTrue(section.conflicts_with(section))

    def test_does_not_conflict_with_section_with_nonconflicting_periods(self):
        def period():
            m = Mock()
            m.conflicts_with = Mock(return_value=False)
            return m
        section1, section2 = SectionFactory.create(), SectionFactory.create()
        section1.get_periods = Mock(return_value=[period(), period()])
        section2.get_periods = Mock(return_value=[period(), period()])

        self.assertFalse(section1.conflicts_with(section2))

    def test_conflicts_with_section_with_conflicting_periods(self):
        def period():
            m = Mock()
            m.conflicts_with = Mock(return_value=True)
            return m
        section1, section2 = SectionFactory.create(), SectionFactory.create()
        section1.get_periods = Mock(return_value=[period()])
        section2.get_periods = Mock(return_value=[period()])

        self.assertTrue(section1.conflicts_with(section2))

    def test_conflicts_with_using_cache(self):
        section1, section2 = SectionFactory.create(), SectionFactory.create()
        section1.conflicts = set([section2.id])
        self.assertTrue(section1.conflicts_with(section2))

    def test_no_conflicts_using_cache(self):
        section1, section2 = SectionFactory.create(), SectionFactory.create()
        section1.conflicts = set()
        self.assertFalse(section1.conflicts_with(section2))


class CourseTest(TestCase):
    def test_to_json(self):
        course = CourseFactory.create(
                pk=1, name='foo', number=5050, min_credits=4, max_credits=5
        )
        expected = {
            'id': 1,
            'name': 'foo',
            'number': 5050,
            'min_credits': 4,
            'max_credits': 5,
        }
        self.assertEqual(expected, course.toJSON())

    def test_code(self):
        dept = DepartmentFactory.build(code='CSCI')
        course = CourseFactory.build(department=dept, number=1100)
        self.assertEqual('CSCI 1100', course.code)

    def test_credits_display_for_equivalent_min_and_max_credits(self):
        course = CourseFactory.build(min_credits=4, max_credits=4)
        self.assertEqual('4 credits', course.credits_display)

    def test_credits_display_for_equivalent_min_and_max_credits_as_one_credit(self):
        course = CourseFactory.build(min_credits=1, max_credits=1)
        self.assertEqual('1 credit', course.credits_display)

    def test_credits_display_for_range(self):
        course = CourseFactory.build(min_credits=1, max_credits=8)
        self.assertEqual('1 - 8 credits', course.credits_display)

    @patch.object(models.Course, 'sections', Mock())
    def test_available_sections(self):
        course = CourseFactory.build()
        queryset = models.Course.sections.by_availability = Mock(return_value='foobar')
        self.assertEqual('foobar', course.available_sections)
        queryset.assert_called_with()

    def test_crns(self):
        course = CourseFactory.create()
        section1 = SectionFactory.create(crn=123, course=course)
        section2 = SectionFactory.create(crn=124, course=course)
        SectionPeriodFactory.create(section=section1)
        SectionPeriodFactory.create(section=section2)

        self.assertEqual([123, 124], list(course.crns))

    def test_full_crns(self):
        course = CourseFactory.create()
        section1 = SectionFactory.create(crn=123, course=course)
        section2 = SectionFactory.create(crn=124, course=course, seats_total=1)
        SectionPeriodFactory.create(section=section1)
        SectionPeriodFactory.create(section=section2)

        self.assertEqual([123], list(course.full_crns))

    def test_instructors(self):
        course = CourseFactory.create()
        section1 = SectionFactory.create(crn=123, course=course)
        section2 = SectionFactory.create(crn=124, course=course, seats_total=1)
        SectionPeriodFactory.create(section=section1, instructor='foo')
        SectionPeriodFactory.create(section=section1, instructor='foobar')
        SectionPeriodFactory.create(section=section1, instructor='fizzbuzz')
        SectionPeriodFactory.create(section=section2, instructor='fizz')

        self.assertEqual(set(['foo', 'foobar', 'fizzbuzz', 'fizz']), set(course.instructors))

    def test_kinds(self):
        course = CourseFactory.create()
        section1 = SectionFactory.create(crn=123, course=course)
        section2 = SectionFactory.create(crn=124, course=course, seats_total=1)
        SectionPeriodFactory.create(section=section1, kind='foo')
        SectionPeriodFactory.create(section=section1, kind='foobar')
        SectionPeriodFactory.create(section=section1, kind='fizzbuzz')
        SectionPeriodFactory.create(section=section2, kind='fizz')

        self.assertEqual(set(['foo', 'foobar', 'fizzbuzz', 'fizz']), set(course.kinds))

class SectionPeriodTest(TestCase):
    def test_to_json(self):
        period = PeriodFactory.build()
        period.toJSON = Mock(return_value={'lol': 1})
        sp = SectionPeriodFactory.build(
            instructor='foo',
            location='bar',
            kind='fizz',
            period=period
        )
        expected = {
            'instructor': 'foo',
            'location': 'bar',
            'kind': 'fizz',
            'lol': 1,
        }
        self.assertEqual(expected, sp.toJSON())

    def test_conflicts_with_uses_period_conflict(self):
        period1 = PeriodFactory.build()
        period1.conflicts_with = Mock(return_value=False)
        period2 = PeriodFactory.build()
        sp1 = SectionPeriodFactory.build(period=period1)
        sp2 = SectionPeriodFactory.build(period=period2)

        self.assertFalse(sp1.conflicts_with(sp2))
        period1.conflicts_with.assert_called_with(period2)

class BasicSchema(ShortcutTestCase):
    def setUp(self):
        semester = SemesterFactory.create(year=2011, month=1)
        course = CourseFactory.create(pk=2)
        OfferedForFactory.create(semester=semester, course=course)

        section = SectionFactory.create(number=1, course=course)
        SemesterSectionFactory.create(semester=semester, section=section)

        sa_section = SectionFactory.create(number=models.Section.STUDY_ABROAD, course=course)
        SemesterSectionFactory.create(semester=semester, section=sa_section)

        crn_section = SectionFactory.create(crn=13337, course=course)
        SemesterSectionFactory.create(semester=semester, section=crn_section)

        cs_dept = DepartmentFactory.create(code='CSCI')
        SemesterDepartmentFactory.create(semester=semester, department=cs_dept)

        ecse_dept = DepartmentFactory.create(code='ECSE')
        SemesterDepartmentFactory.create(semester=semester, department=ecse_dept)

        self.semester, self.course, self.cs_dept, self.ecse_dept = semester, course, cs_dept, ecse_dept

class ListDepartmentsIntegrationTests(BasicSchema):
    urls = 'yacs.urls'
    def test_list_departments(self):
        response = self.get('departments', year=2011, month=1, status_code=200)
        self.assertIn(self.cs_dept, response.context['departments'])
        self.assertIn(self.ecse_dept, response.context['departments'])

class SearchTest(BasicSchema):
    urls = 'yacs.urls'
    def setUp(self):
        super(SearchTest, self).setUp()
        course = CourseFactory.create(department=self.cs_dept, number=4230, name='Intro to Computing')
        OfferedForFactory.create(course=course, semester=self.semester)

        course2 = CourseFactory.create(department=self.cs_dept, number=4231, name='Skynet 101')
        OfferedForFactory.create(course=course2, semester=self.semester)

        # another department
        course3 = CourseFactory.create(department=self.ecse_dept, number=4230, name='Imaginary Power')
        OfferedForFactory.create(course=course3, semester=self.semester)

        section = SectionFactory.create(course=course)
        SemesterSectionFactory.create(semester=self.semester, section=section)
        period = PeriodFactory.create(start=datetime.time(hour=12), end=datetime.time(hour=13), days_of_week_flag=1)
        SectionPeriodFactory.create(section=section, period=period, instructor='Moorthy', semester=self.semester)

        self.course1, self.course2, self.course3 = course, course2, course3

    def test_search_by_professor(self):
        "/2011/1/search/?q=moor"
        response = self.get('search-all-courses', year=2011, month=1, get='?q=moor', status_code=200)
        courses = response.context['courses']
        self.assertIn(self.course1, courses)
        self.assertNotIn(self.course2, courses)
        self.assertNotIn(self.course3, courses)

    def test_searching_with_textfield_only_returning_partial(self):
        "/2011/1/search/?q=4230&partial=1"
        response = self.get('search-all-courses', year=2011, month=1, get='?q=4230&partial=1', status_code=200)
        self.assertEqual('courses/_course_list.html', response.template.name)
        courses = response.context['courses']
        self.assertIn(self.course1, courses)
        self.assertIn(self.course3, courses)
        self.assertNotIn(self.course2, courses)

    def test_searching_with_textfield_only(self):
        "/2011/1/search/?q=4230"
        response = self.get('search-all-courses', year=2011, month=1, get='?q=4230', status_code=200)
        courses = response.context['courses']
        self.assertIn(self.course1, courses)
        self.assertIn(self.course3, courses)
        self.assertNotIn(self.course2, courses)

    def test_search_course_name(self):
        response = self.get('search-all-courses', year=2011, month=1, get='?q=intro', status_code=200)
        courses = response.context['courses']
        self.assertIn(self.course1, courses)
        self.assertNotIn(self.course2, courses)
        self.assertNotIn(self.course3, courses)

    def test_searching_by_department_with_textfield(self):
        response = self.get('search-all-courses', year=2011, month=1, get='?q=csci', status_code=200)
        courses = response.context['courses']
        self.assertIn(self.course1, courses)
        self.assertIn(self.course2, courses)
        self.assertNotIn(self.course3, courses)

    def test_searching_by_department(self):
        "/2011/1/search/?d=CSCI"
        response = self.get('search-all-courses', year=2011, month=1, get='?d=CSCI', status_code=200)
        courses = response.context['courses']
        self.assertIn(self.course1, courses)
        self.assertIn(self.course2, courses)
        self.assertNotIn(self.course3, courses)

    def test_searching_by_department_and_textfield(self):
        "/2011/1/search/?d=CSCI&q=4230"
        response = self.get('search-all-courses', year=2011, month=1, get='?d=CSCI&q=4230', status_code=200)
        courses = response.context['courses']
        self.assertIn(self.course1, courses)
        self.assertNotIn(self.course2, courses)
        self.assertNotIn(self.course3, courses)


class TestSingleCourseSelecting(ShortcutTestCase):
    fixtures = ['intro-to-cs.json']
    urls = 'yacs.urls'

    def setUp(self):
        self.c = course('INTRO TO COMPUTER PROGRAMMING')

    def test_default_has_no_selection(self):
        "A new visitor should have no selected courses."
        response = self.get('departments', year=2011, month=9)
        self.assertFalse(self.client.session.get(SELECTED_COURSES_SESSION_KEY))

    def set_selected(self):
        self.set_session({SELECTED_COURSES_SESSION_KEY: {
            self.c.id: [85723, 86573]
        }})

    def test_selecting_a_course(self):
        "Selecting a course should populate the selected courses with the cid => crns."
        self.assertFalse(self.client.session.get(SELECTED_COURSES_SESSION_KEY))

        response = self.post('select-courses', year=2011, month=9, status_code=302, data={
            'course_' + str(self.c.id): 'selected',
        })

        selected = self.client.session.get(SELECTED_COURSES_SESSION_KEY)
        self.assertEqual(len(selected), 1)
        self.assertSequenceEqual(selected.keys(), [self.c.id])
        self.assertSequenceEqual(selected.get(self.c.id), [85723, 86573])

    def test_deselecting_course_via_course_list(self):
        "Deselect a course using the course_list view."
        self.set_selected()

        response = self.post('select-courses', year=2011, month=9, status_code=302, data={})
        selected = self.client.session.get(SELECTED_COURSES_SESSION_KEY)
        self.assertEqual(len(selected), 0)
        self.assertSequenceEqual(selected.keys(), [])

    def test_deselecting_course_via_selected(self):
        "Deselect a course using the selected courses view."
        self.set_selected()

        response = self.post('deselect-courses', year=2011, month=9, status_code=302, data={})
        selected = self.client.session.get(SELECTED_COURSES_SESSION_KEY)
        self.assertEqual(len(selected), 0)
        self.assertSequenceEqual(selected.keys(), [])

    def test_deselecting_section_via_selected(self):
        "Deselect a course's section using the selected courses view."
        self.set_selected()

        response = self.post('deselect-courses', year=2011, month=9, status_code=302, data={
            'selected_course_' + str(self.c.id): 'true',
            'selected_course_' + str(self.c.id) + '_85723': 'true'
        })
        selected = self.client.session.get(SELECTED_COURSES_SESSION_KEY)
        self.assertEqual(len(selected), 1)
        self.assertSequenceEqual(selected.keys(), [self.c.id])
        self.assertSequenceEqual(selected[self.c.id], [85723])

class TestMultipleCourseSelecting(ShortcutTestCase):
    fixtures = ['intro-to-cs.json', 'intro-to-algorithms.json', 'calc1.json']
    urls = 'yacs.urls'

    def setUp(self):
        self.intro_cs_sections = [85723, 86573]
        self.intro_algos_sections = [85065, 85066, 85468, 86693, 85411, 85488]
        self.intro_algos_nonfull = [85065, 85468, 86693, 85411, 85488]
        self.calc1_nonfull = (85138, 85141, 85143, 85391, 85299, 85417, 85418, 85419, 86274, 85808, 86270, 85668, 85669, 85670)
        self.c, self.c2 = course('INTRO TO COMPUTER PROGRAMMING'), course('INTRODUCTION TO ALGORITHMS')
        self.c3 = course('CALCULUS I')

    def set_selected(self, calc=False):
        result = {
            self.c.id: self.intro_cs_sections,
            self.c2.id: self.intro_algos_nonfull
        }
        if calc:
            result[self.c3.id] = self.calc1_nonfull
        return self.set_session({SELECTED_COURSES_SESSION_KEY: result})

    def test_ajax_fetch_of_selected(self):
        self.set_selected()
        json = self.json_get('selected-courses', year=2011, month=9, status_code=200,
            ajax_request=True, prefix='for(;;); ',
        )
        self.assertEqual(json, {
            unicode(self.c.id): self.intro_cs_sections,
            unicode(self.c2.id): self.intro_algos_nonfull
        })

    def test_selecting_courses_via_ajax(self):
        "Simulate what a typical browser would hit when selecting courses."
        response = self.get('courses-by-dept', year=2011, month=9, code='CSCI', status_code=200)
        json = self.json_post('deselect-courses', year=2011, month=9,
            ajax_request=True, status_code=200, prefix='for(;;); ', data={
            'selected_course_' + str(self.c.id): 'checked',
            'selected_course_' + str(self.c.id) + '_85723': 'checked',
            'selected_course_' + str(self.c.id) + '_86573': 'checked',
        })
        selected = self.client.session.get(SELECTED_COURSES_SESSION_KEY)
        self.assertEqual(len(selected), 1)
        self.assertEqual(selected.get(self.c.id), self.intro_cs_sections)

        # apply to more sections
        json = self.json_post('deselect-courses', year=2011, month=9,
            ajax_request=True, status_code=200, prefix='for(;;); ', data={
            'selected_course_' + str(self.c.id): 'checked',
            'selected_course_' + str(self.c.id) + '_85723': 'checked',
            'selected_course_' + str(self.c.id) + '_86573': 'checked',
            'selected_course_' + str(self.c2.id): 'checked',
            'selected_course_' + str(self.c2.id) + '_85065': 'checked',
            'selected_course_' + str(self.c2.id) + '_85468': 'checked',
            'selected_course_' + str(self.c2.id) + '_86693': 'checked',
            'selected_course_' + str(self.c2.id) + '_85411': 'checked',
            'selected_course_' + str(self.c2.id) + '_85488': 'checked',
        })
        selected = self.client.session.get(SELECTED_COURSES_SESSION_KEY)
        self.assertEqual(len(selected), 2)
        self.assertEqual(selected.get(self.c.id), self.intro_cs_sections)
        self.assertSetEqual(set(selected.get(self.c2.id)), set(self.intro_algos_nonfull))

        # remove some sections via selected courses
        response = self.get('selected-courses', year=2011, month=9, status_code=200)
        json = self.json_post('deselect-courses', year=2011, month=9,
            ajax_request=True, status_code=200, prefix='for(;;);', data={
            'selected_course_' + str(self.c.id): 'checked',
            'selected_course_' + str(self.c.id) + '_85723': 'checked',
            'selected_course_' + str(self.c.id) + '_86573': 'checked',
            'selected_course_' + str(self.c2.id): 'checked',
            'selected_course_' + str(self.c2.id) + '_85065': 'checked',
            'selected_course_' + str(self.c2.id) + '_85468': 'checked',
            'selected_course_' + str(self.c2.id) + '_86693': 'checked',
        })
        selected = self.client.session.get(SELECTED_COURSES_SESSION_KEY)
        self.assertEqual(len(selected), 2)
        self.assertEqual(selected.get(self.c.id), self.intro_cs_sections)
        self.assertSetEqual(set(selected.get(self.c2.id)), set([85065, 85468, 86693]))

        # remove some course
        json = self.json_post('deselect-courses', year=2011, month=9,
            ajax_request=True, status_code=200, prefix='for(;;);', data={
            'selected_course_' + str(self.c2.id): 'checked',
            'selected_course_' + str(self.c2.id) + '_85065': 'checked',
            'selected_course_' + str(self.c2.id) + '_85468': 'checked',
            'selected_course_' + str(self.c2.id) + '_86693': 'checked',
        })
        selected = self.client.session.get(SELECTED_COURSES_SESSION_KEY)
        self.assertEqual(len(selected), 1)
        self.assertSetEqual(set(selected.get(self.c2.id)), set([85065, 85468, 86693]))

        # verify
        json = self.json_get('selected-courses', year=2011, month=9, status_code=200,
            ajax_request=True, prefix='for(;;); ',
        )
        self.assertEqual(json, {
            unicode(self.c2.id): [85065, 85468, 86693]
        })

    def test_selecting_courses(self):
        """Selecting a course should populate the selected courses with the cid => crns.
        Also should avoid full sections.
        """
        self.assertFalse(self.client.session.get(SELECTED_COURSES_SESSION_KEY))

        c, c2 = self.c, self.c2
        response = self.post('select-courses', year=2011, month=9, status_code=302, data={
            'course_' + str(c.id): 'selected',
            'course_' + str(c2.id): 'selected',
        })

        selected = self.client.session.get(SELECTED_COURSES_SESSION_KEY)
        self.assertEqual(len(selected), 2)
        self.assertSequenceEqual(selected.keys(), [c.id, c2.id])
        self.assertSequenceEqual(selected.get(c.id), self.intro_cs_sections)
        self.assertSequenceEqual(selected.get(c2.id), self.intro_algos_nonfull)

    def test_deselecting_all_courses_via_course_list(self):
        "Deselect a course using the course_list view."
        c = self.c
        self.set_selected()

        response = self.post('select-courses', year=2011, month=9, status_code=302, data={})
        selected = self.client.session.get(SELECTED_COURSES_SESSION_KEY)
        self.assertEqual(len(selected), 0)

    def test_deselecting_courses_only_for_department(self):
        "Deselect a course using the course_list view but don't deselect calculus."
        self.set_selected(calc=True)

        response = self.post('select-courses', year=2011, month=9, status_code=302, data={'dept': 'CSCI'})
        selected = self.client.session.get(SELECTED_COURSES_SESSION_KEY)
        self.assertEqual(type(selected), dict)
        self.assertEqual(len(selected), 1)
        self.assertSequenceEqual(selected.keys(), [self.c3.id])
        self.assertSequenceEqual(selected[self.c3.id], self.calc1_nonfull)

    def test_deselecting_course_via_selected(self):
        "Deselect a course using the selected courses view."
        self.set_selected()

        response = self.post('deselect-courses', year=2011, month=9, status_code=302, data={
            'selected_course_' + str(self.c.id): 'true',
            'selected_course_' + str(self.c.id) + '_85723': 'true',
            'selected_course_' + str(self.c.id) + '_86573': 'true',
            'selected_course_' + str(self.c2.id) + '_85065': 'true',
            'selected_course_' + str(self.c2.id) + '_85468': 'true',
        })
        selected = self.client.session.get(SELECTED_COURSES_SESSION_KEY)
        self.assertEqual(len(selected), 1)
        self.assertSequenceEqual(selected.keys(), [self.c.id])

    def test_deselecting_courses_via_selected(self):
        "Deselect a course using the selected courses view."
        self.set_selected()

        response = self.post('deselect-courses', year=2011, month=9, status_code=302, data={
            'selected_course_' + str(self.c.id) + '_85723': 'true',
            'selected_course_' + str(self.c.id) + '_86573': 'true',
        })
        selected = self.client.session.get(SELECTED_COURSES_SESSION_KEY)
        self.assertEqual(len(selected), 0)

    def test_deselecting_section_via_selected(self):
        "Deselect a course's section using the selected courses view."
        self.set_selected()

        response = self.post('deselect-courses', year=2011, month=9, status_code=302, data={
            'selected_course_' + str(self.c.id): 'true',
            'selected_course_' + str(self.c.id) + '_85723': 'true',
            'selected_course_' + str(self.c2.id): 'true',
            'selected_course_' + str(self.c2.id) + '_85065': 'true',
            'selected_course_' + str(self.c2.id) + '_85468': 'true',
        })
        selected = self.client.session.get(SELECTED_COURSES_SESSION_KEY)
        self.assertEqual(len(selected), 2)
        self.assertSequenceEqual(selected.keys(), [self.c.id, self.c2.id])
        self.assertSequenceEqual(selected[self.c.id], [85723])
        self.assertSequenceEqual(selected[self.c2.id], [85065, 85468])

class CapitalizationTest(TestCase):
    def test_capitalization_for_all_lowercase(self):
        self.assertEqual(utils.capitalized("foobar"), "Foobar")

    def test_capitalization_for_all_uppercase(self):
        self.assertEqual(utils.capitalized("FOOBAR"), "Foobar")

    def test_capitalization_for_mixed_case(self):
        self.assertEqual(utils.capitalized("fOoBaR"), "Foobar")

    def test_capitalization_for_letter(self):
        self.assertEqual(utils.capitalized("a"), "A")

    def test_capitalization_for_blank(self):
        self.assertEqual(utils.capitalized(""), "")

    def test_capitalization_spaces(self):
        self.assertEqual(utils.capitalized("   "), "   ")

class OptionsTest(TestCase):
    def test_returning_a_generator(self):
        g = utils.options()
        self.assertEqual(g.next(), 1)
        self.assertEqual(g.next(), 2)
        self.assertEqual(g.next(), 4)
        self.assertEqual(g.next(), 8)
        self.assertEqual(g.next(), 16)
        self.assertEqual(g.next(), 32)
        # this generator is infinite...

    def test_returning_a_list(self):
        g = utils.options(6)
        self.assertEqual(g, [1, 2, 4, 8, 16, 32])

class ExtendedGetAttrTest(TestCase):
    SampleObject = namedtuple('SampleObject', ('a', 'b'))
    NestedSampleObject = namedtuple('NestedSampleObject', ('c', 'd'))
    def test_single_attr(self):
        o = self.SampleObject(1, 2)
        self.assertEqual(utils.extended_getattr(o, 'a'), 1)
        self.assertEqual(utils.extended_getattr(o, 'b'), 2)

    def test_nested_attr(self):
        o = self.SampleObject(self.NestedSampleObject(1, 2), 3)
        self.assertEqual(utils.extended_getattr(o, 'a.c'), 1)
        self.assertEqual(utils.extended_getattr(o, 'a.d'), 2)
        self.assertEqual(utils.extended_getattr(o, 'b'), 3)

    def test_attribute_error_on_invalid_attr(self):
        o = self.SampleObject(1, 2)
        self.assertRaises(utils.ExtendedAttributeError, utils.extended_getattr, o, 'f')

    def test_attribute_error_on_invalid_nested_attr(self):
        o = self.SampleObject(self.NestedSampleObject(1, 2), 3)
        self.assertRaises(utils.ExtendedAttributeError, utils.extended_getattr, o, 'a.f')

    def test_defaults_on_invalid_attr(self):
        o = self.SampleObject(1, 2)
        self.assertEqual(utils.extended_getattr(o, 'f', 3), 3)

    def test_defaults_on_invalid_nested_attr(self):
        o = self.SampleObject(self.NestedSampleObject(1, 2), 3)
        self.assertEqual(utils.extended_getattr(o, 'a.f', 9), 9)

class DictByAttrTest(TestCase):
    SampleObject = namedtuple('SampleObject', ('a', 'b', 'c'))
    def test_mapping(self):
        items = [self.SampleObject(i, i+1, i+2) for i in range(10)]
        ordered = utils.dict_by_attr(items, 'a')
        self.assertEqual([0, 1, 2, 3, 4, 5, 6, 7, 8, 9], ordered.keys())
        self.assertEqual([(0, 1, 2)], ordered[0])
        self.assertEqual([(1, 2, 3)], ordered[1])
        self.assertEqual([(2, 3, 4)], ordered[2])
        self.assertEqual([(3, 4, 5)], ordered[3])
        self.assertEqual([(4, 5, 6)], ordered[4])
        self.assertEqual([(5, 6, 7)], ordered[5])
        self.assertEqual([(6, 7, 8)], ordered[6])
        self.assertEqual([(7, 8, 9)], ordered[7])
        self.assertEqual([(8, 9, 10)], ordered[8])
        self.assertEqual([(9, 10, 11)], ordered[9])

    def test_mapping_in_groups(self):
        items = [self.SampleObject(i % 3, i+1, i+2) for i in range(10)]
        ordered = utils.dict_by_attr(items, 'a')
        self.assertEqual([0, 1, 2], ordered.keys())
        self.assertEqual([(0, 1, 2), (0, 4, 5), (0, 7, 8), (0, 10, 11)], ordered[0])
        self.assertEqual([(1, 2, 3), (1, 5, 6), (1, 8, 9), ], ordered[1])
        self.assertEqual([(2, 3, 4), (2, 6, 7), (2, 9, 10), ], ordered[2])

    def test_mapping_with_lambda(self):
        items = [self.SampleObject(i, i+1, i+2) for i in range(10)]
        ordered = utils.dict_by_attr(items, lambda o: o.a)
        self.assertEqual([0, 1, 2, 3, 4, 5, 6, 7, 8, 9], ordered.keys())
        self.assertEqual([(0, 1, 2)], ordered[0])
        self.assertEqual([(1, 2, 3)], ordered[1])
        self.assertEqual([(2, 3, 4)], ordered[2])
        self.assertEqual([(3, 4, 5)], ordered[3])
        self.assertEqual([(4, 5, 6)], ordered[4])
        self.assertEqual([(5, 6, 7)], ordered[5])
        self.assertEqual([(6, 7, 8)], ordered[6])
        self.assertEqual([(7, 8, 9)], ordered[7])
        self.assertEqual([(8, 9, 10)], ordered[8])
        self.assertEqual([(9, 10, 11)], ordered[9])

    def test_mapping_with_value(self):
        items = [self.SampleObject(i, i+1, i+2) for i in range(10)]
        ordered = utils.dict_by_attr(items, 'a', 'b')
        self.assertEqual([0, 1, 2, 3, 4, 5, 6, 7, 8, 9], ordered.keys())
        self.assertEqual([1], ordered[0])
        self.assertEqual([2], ordered[1])
        self.assertEqual([3], ordered[2])
        self.assertEqual([4], ordered[3])
        self.assertEqual([5], ordered[4])
        self.assertEqual([6], ordered[5])
        self.assertEqual([7], ordered[6])
        self.assertEqual([8], ordered[7])
        self.assertEqual([9], ordered[8])
        self.assertEqual([10], ordered[9])


