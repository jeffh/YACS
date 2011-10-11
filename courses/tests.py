"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django_dynamic_fixture import new, get, DynamicFixture as F
from testing_utils import ShortcutTestCase
from timetable.courses import models
from timetable.courses import utils

class BasicSchema(ShortcutTestCase):
    def setUp(self):
        semester = get(models.Semester, year=2011, month=1)
        course = get(models.Course, id=2)
        get(models.OfferedFor, course=course, semester=semester)

        section = get(models.Section, number=1, course=course)
        get(models.SemesterSection, semester=semester, section=section)

        sa_section = get(models.Section, number=models.Section.STUDY_ABROAD, course=course)
        get(models.SemesterSection, semester=semester, section=sa_section)

        crn_section = get(models.Section, crn=13337, course=course)
        get(models.SemesterSection, semester=semester, section=crn_section)

        cs_dept = get(models.Department, code='CSCI')
        get(models.SemesterDepartment, department=cs_dept, semester=semester)

        ecse_dept = get(models.Department, code='ECSE')
        get(models.SemesterDepartment, department=ecse_dept, semester=semester)

        self.semester, self.course, self.cs_dept, self.ecse_dept = semester, course, cs_dept, ecse_dept


class SearchTest(BasicSchema):
    def setUp(self):
        super(SearchTest, self).setUp()
        course = get(models.Course, department=self.cs_dept, number=4230, name='Intro to Computing')
        get(models.OfferedFor, course=course, semester=self.semester)

        course2 = get(models.Course, department=self.cs_dept, number=4231, name='Skynet 101')
        get(models.OfferedFor, course=course2, semester=self.semester)

        # another department
        course3 = get(models.Course, department=self.ecse_dept, number=4230, name='Imaginary Power')
        get(models.OfferedFor, course=course3, semester=self.semester)

        self.course1, self.course2, self.course3 = course, course2, course3

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

