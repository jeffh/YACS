from django.test import TestCase

from courses import models
from courses.tests.factories import (SemesterFactory, SemesterDepartmentFactory,
        OfferedForFactory, CourseFactory, SemesterSectionFactory, SectionFactory,
        DepartmentFactory, PeriodFactory, SectionPeriodFactory)


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

