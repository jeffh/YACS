from django.core.urlresolvers import reverse
from django_dynamic_fixture import new, get, DynamicFixture as F
from yacs.courses import models
from shortcuts import ShortcutTestCase
from django.utils.simplejson import loads
from datetime import time

class TestAPI(ShortcutTestCase):
    urls = 'yacs.api.urls'
    def setUp(self):
        # dynamic fixtures doesn't create intermediary models when automatically generating,
        # so we have to create them manually.
        self.semester = semester = get(models.Semester, year=2011, month=1)

        cs_dept = get(models.Department, code='CSCI')
        get(models.SemesterDepartment, department=cs_dept, semester=semester, persist_dependencies=False)
        get(models.SemesterDepartment, department=get(models.Department), semester=semester, persist_dependencies=False)

        self.course = course = get(models.Course, id=2, department=cs_dept, name='course1', persist_dependencies=False)
        get(models.OfferedFor, course=course, semester=semester, persist_dependencies=False)

        section = get(models.Section, number=1, course=course, persist_dependencies=False)
        get(models.SemesterSection, semester=semester, section=section, persist_dependencies=False)

        crn_section = get(models.Section, crn=13337, course=course, persist_dependencies=False)
        get(models.SemesterSection, semester=semester, section=crn_section, persist_dependencies=False)

        course = get(models.Course, department=cs_dept, number=4230, name='course2', persist_dependencies=False)
        get(models.OfferedFor, course=course, semester=semester, persist_dependencies=False)

    def json_get(self, *args, **kwargs):
        response = self.get(*args, **kwargs)
        return loads(response.content)

    def test_get_semesters(self):
        "/api/"
        json = self.json_get('semesters', status_code=200)
        self.assertEqual(len(json), 1)

    def test_get_semesters_by_year(self):
        "/api/2011/"
        get(models.Semester, n=10)
        get(models.Semester, year=2011, month=9)

        json = self.json_get('semesters-by-year', year=2011, status_code=200)

        self.assertEqual(len(json), 2)
        self.assertEqual(json[0]['year'], 2011)
        self.assertEqual(json[1]['year'], 2011)

    def test_get_semester(self):
        "/api/2011/1/"
        json = self.json_get('semester', year=2011, month=1, status_code=200)
        self.assertEqual(json['year'], 2011)
        self.assertEqual(json['month'], 1)

    def test_get_courses(self):
        "/api/2011/1/courses/"
        s = get(models.Semester)
        for c in get(models.Course, n=10):
            get(models.OfferedFor, course=c, semester=s)

        json = self.json_get('courses-by-semester', year=2011, month=1, status_code=200)
        self.assertEqual(len(json), 2)
        self.assertEqual(json[0]['name'], 'course1')
        self.assertEqual(json[0]['id'], 2)
        self.assertEqual(json[1]['name'], 'course2')
        self.assertEqual(json[1]['number'], 4230)

    def test_get_courses_by_id(self):
        "/api/2011/1/courses/2/"
        json = self.json_get('course-by-id', year=2011, month=1, cid=2, status_code=200)
        self.assertEqual(json['id'], 2)
        self.assertEqual(json['department']['code'], 'CSCI')

    def test_get_sections_by_number(self):
        "/api/2011/1/courses/2/sections/1/"
        json = self.json_get('sections-by-number', year=2011, month=1, cid=2, number=1, status_code=200)
        self.assertEqual(len(json), 1)
        self.assertEqual(json[0]['number'], 1)

    def test_get_sections_by_studying_abroad(self):
        "/api/2011/1/courses/2/sections/study-abroad/"
        sa_section = get(models.Section, number=models.Section.STUDY_ABROAD, course=self.course, persist_dependencies=False)
        get(models.SemesterSection, semester=self.semester, section=sa_section, persist_dependencies=False)

        json = self.json_get('sections-by-study-abroad', year=2011, month=1, cid=2, status_code=200)
        self.assertEqual(len(json), 1)
        self.assertEqual(json[0]['number'], models.Section.STUDY_ABROAD)

    def test_get_sections_by_crn(self):
        "/api/2011/1/courses/2/sections/crn-13337/"
        json = self.json_get('sections-by-crn', year=2011, month=1, cid=2, crn=13337, status_code=200)
        self.assertEqual(len(json), 1)
        self.assertEqual(json[0]['crn'], 13337)

    def test_get_departments(self):
        "/api/2011/1/departments/"
        json = self.json_get('departments', year=2011, month=1)
        self.assertEqual(len(json), 2)

        # try with more ficticous departments
        depts = get(models.Department, n=10)
        for d in depts:
            get(models.SemesterDepartment, department=d, semester=self.semester, persist_dependencies=False)
        json = self.json_get('departments', year=2011, month=1)
        self.assertEqual(len(json), 12)

        # departments in another semester shouldn't affect us
        depts = get(models.Department, n=10)
        json = self.json_get('departments', year=2011, month=1)
        self.assertEqual(len(json), 12)

    def test_get_department(self):
        "/api/2011/1/departments/CSCI/"
        json = self.json_get('department', year=2011, month=1, code='CSCI', status_code=200)
        self.assertEqual(json['code'], 'CSCI')

    def test_get_periods(self):
        json = self.json_get('periods', status_code=200)

    def test_get_period(self):
        p = get(models.Period, id=1, start=time(), end=time())
        json = self.json_get('period', pid=p.id, status_code=200)

    def test_get_courses_by_department(self):
        "/api/2011/1/departments/CSCI/courses/"
        json = self.json_get('courses-by-department', year=2011, month=1, code='CSCI', status_code=200)
        self.assertEqual(len(json), 2)
        self.assertEqual(json[0]['name'], 'course1')
        self.assertEqual(json[1]['name'], 'course2')

    def test_get_courses_by_number(self):
        "/api/2011/1/departments/CSCI/4230/"
        json = self.json_get('courses-by-number', year=2011, month=1, code='CSCI', number=4230, status_code=200)
        self.assertEqual(json['number'], 4230)
        self.assertEqual(json['department']['code'], 'CSCI')

    def test_get_schedules_via_crns(self):
        "/api/2011/1/schedules/?crns=13337"
        json = self.json_get('scheduler', year=2011, month=1, get='?crns=13337', status_code=200)
        self.assertEqual(len(json), 1)

    def test_get_schedules_via_crns_with_complete(self):
        "/api/2011/1/schedules/?crns=13337&complete=1"
        json = self.json_get('scheduler', year=2011, month=1, get='?crns=13337&complete=1', status_code=200)
        self.assertEqual(len(json['schedules']), 1)
        self.assertTrue(json['courses'])
        self.assertTrue(json['sections'])

    def test_get_schedules_via_course_ids(self):
        "/api/2011/1/schedules/?cids=13337"
        json = self.json_get('scheduler', year=2011, month=1, get='?cids=2', status_code=200)

