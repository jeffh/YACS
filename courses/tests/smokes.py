"""
Smokes - Contains all smoke tests.

Most of these tests simply check if all the views do not return unexpected server errors.
"""
import datetime
import sys

from shortcuts import ShortcutTestCase

from courses import models
from courses.views import SELECTED_COURSES_SESSION_KEY
from courses.tests.factories import (SemesterFactory, SemesterDepartmentFactory,
        OfferedForFactory, CourseFactory, SectionFactory, DepartmentFactory,
        PeriodFactory, SectionPeriodFactory)


class BasicSchema(ShortcutTestCase):
    urls = 'yacs.urls'
    def setUp(self):
        semester = SemesterFactory.create(year=2011, month=1)
        course = CourseFactory.create(pk=2)
        OfferedForFactory.create(semester=semester, course=course)

        section = SectionFactory.create(number=1, course=course, semester=semester)
        sa_section = SectionFactory.create(number=models.Section.STUDY_ABROAD, course=course, semester=semester)
        crn_section = SectionFactory.create(crn=13337, course=course, semester=semester)

        cs_dept = DepartmentFactory.create(code='CSCI')
        SemesterDepartmentFactory.create(semester=semester, department=cs_dept)

        ecse_dept = DepartmentFactory.create(code='ECSE')
        SemesterDepartmentFactory.create(semester=semester, department=ecse_dept)

        self.semester, self.course, self.cs_dept, self.ecse_dept = semester, course, cs_dept, ecse_dept


class ListDepartmentsIntegrationTests(BasicSchema):
    def test_list_departments(self):
        response = self.get('departments', year=2011, month=1, status_code=200)
        self.assertIn(self.cs_dept, response.context['departments'])
        self.assertIn(self.ecse_dept, response.context['departments'])


class SearchTest(BasicSchema):
    def setUp(self):
        super(SearchTest, self).setUp()
        course = CourseFactory.create(department=self.cs_dept, number=4230, name='Intro to Computing')
        OfferedForFactory.create(course=course, semester=self.semester)

        course2 = CourseFactory.create(department=self.cs_dept, number=4231, name='Skynet 101')
        OfferedForFactory.create(course=course2, semester=self.semester)

        # another department
        course3 = CourseFactory.create(department=self.ecse_dept, number=4230, name='Imaginary Power')
        OfferedForFactory.create(course=course3, semester=self.semester)

        section = SectionFactory.create(course=course, semester=self.semester)
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
        self.assertIn('courses/_course_list.html', [t.name for t in response.template])
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



