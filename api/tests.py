"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.core.urlresolvers import reverse
from django_dynamic_fixture import new, get, DynamicFixture as F
from timetable.courses import models

class ShortcutTestCase(TestCase):
    def get(self, url_name, *args, **kwargs):
        status = kwargs.pop('status_code', None)
        params = kwargs.pop('get', '')
        response = self.client.get(reverse(url_name, args=args, kwargs=kwargs) + params)
        if status is not None:
            self.assertEqual(response.status_code, status, response.content)
        return response

    def post(self, url_name, *args, **kwargs):
        status = kwargs.pop('status_code', None)
        data = kwargs.pop("data", None)
        params = kwargs.pop('get', '')
        response = self.client.post(reverse(url_name, args=args, kwargs=kwargs) + params, data)
        if status is not None:
            self.assertEqual(response.status_code, status)
        return response


class TestAPIAvailability(ShortcutTestCase):
    urls = 'timetable.api.urls'
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
        get(models.SemesterDepartment, department=get(models.Department), semester=semester)

        course = get(models.Course, department=cs_dept, number=4230)
        get(models.OfferedFor, course=course, semester=semester)

    def test_get_semesters(self):
        "/api/"
        self.get('semesters', status_code=200)
    
    def test_get_semesters_by_year(self):
        "/api/2011/"
        self.get('semesters-by-year', year=2011, status_code=200)

    def test_get_courses(self):
        "/api/2011/1/"
        self.get('courses-by-semester', year=2011, month=1, status_code=200)

    def test_get_courses_by_id(self):
        "/api/2011/1/2/"
        self.get('course-by-id', year=2011, month=1, cid=2, status_code=200)
    
    def test_get_sections_by_number(self):
        "/api/2011/1/2/1/"
        self.get('sections-by-number', year=2011, month=1, cid=2, number=1, status_code=200)
    
    def test_get_sections_by_studying_abroad(self):
        "/api/2011/1/2/study-abroad/"
        self.get('sections-by-study-abroad', year=2011, month=1, cid=2, status_code=200)

    def test_get_sections_by_crn(self):
        self.get('sections-by-crn', year=2011, month=1, cid=2, crn=13337, status_code=200)

    def test_get_departments(self):
        self.get('departments', year=2011, month=1)

    def test_get_courses_by_department(self):
        self.get('courses-by-department', year=2011, month=1, code='CSCI', status_code=200)

    def test_get_courses_by_subject(self):
        self.get('courses-by-subject', year=2011, month=1, code='CSCI', number=4230, status_code=200)

    def test_get_schedules_via_crns(self):
        "/api/2011/1/schedules/?crns=13337"
        self.get('scheduler', year=2011, month=1, get='?crns=13337', status_code=200)

    def test_get_schedules_via_course_ids(self):
        "/api/2011/1/schedules/?cids=13337"
        self.get('scheduler', year=2011, month=1, get='?cids=2', status_code=200)
    