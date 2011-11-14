"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django_dynamic_fixture import new, get, DynamicFixture as F
from shortcuts import ShortcutTestCase
from yacs.courses import models
from yacs.courses import utils
from yacs.courses.views import SELECTED_COURSES_SESSION_KEY
from collections import namedtuple
import datetime

# utils
def course(name):
    return models.Course.objects.get(name=name)
# end utils

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

class ListDepartmentsTest(BasicSchema):
    urls = 'yacs.urls'
    def test_list_departments(self):
        response = self.get('departments', year=2011, month=1, status_code=200)
        self.assertIn(self.cs_dept, response.context['departments'])
        self.assertIn(self.ecse_dept, response.context['departments'])

class SearchTest(BasicSchema):
    urls = 'yacs.urls'
    def setUp(self):
        super(SearchTest, self).setUp()
        course = get(models.Course, department=self.cs_dept, number=4230, name='Intro to Computing')
        get(models.OfferedFor, course=course, semester=self.semester)

        course2 = get(models.Course, department=self.cs_dept, number=4231, name='Skynet 101')
        get(models.OfferedFor, course=course2, semester=self.semester)

        # another department
        course3 = get(models.Course, department=self.ecse_dept, number=4230, name='Imaginary Power')
        get(models.OfferedFor, course=course3, semester=self.semester)

        section = get(models.Section, course=course)
        get(models.SemesterSection, semester=self.semester, section=section)
        period = get(models.Period, start=datetime.time(hour=12), end=datetime.time(hour=13), days_of_week_flag=1)
        get(models.SectionPeriod, section=section, period=period, instructor='Moorthy', semester=self.semester)

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


