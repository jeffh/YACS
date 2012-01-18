from datetime import time

from django.core.urlresolvers import reverse
from django.utils.simplejson import loads
from shortcuts import ShortcutTestCase

from yacs.courses import models
from yacs.courses.tests import factories


class TestLatestAPI(ShortcutTestCase):
    fixtures = ['semesters.json', 'courses/fixtures/calc1.json', 'courses/fixtures/intro-to-cs.json', 'courses/fixtures/data-structures.json']
    urls = 'yacs.newapi.urls'
    def fields(self, dicts, field):
        return list(d[field] for d in dicts)

    def test_get_semester(self):
        json = self.json_get('semester', status_code=200)
        self.assertEqual(json['status'], 'OK')
        sem = json['payload']
        self.assertEqual(sem['year'], 2011)
        self.assertEqual(sem['month'], 9)

    def test_get_departments(self):
        json = self.json_get('departments', status_code=200)
        self.assertEqual(json['status'], 'OK')
        self.assertEqual(len(json['payload']), 3)
        self.assertEqual(self.fields(json['payload'], 'code'), ['CSCI', 'ECSE', 'MATH'])
        self.assertEqual(self.fields(json['payload'], 'name'), ['Computer Science', 'Electrical, Computer, and Systems Engineering', 'Mathematics'])

    def test_get_courses_by_dept(self):
        json = self.json_get('courses-by-dept', code='CSCI', status_code=200)
        self.assertEqual(json['status'], 'OK')
        dept = json['payload']
        self.assertEqual(dept['code'], 'CSCI')
        self.assertEqual(dept['name'], 'Computer Science')
        self.assertEqual(len(dept['courses']), 2)

    def test_get_courses_via_search(self):
        json = self.json_get('search-all-courses', get='?q=CSCI', status_code=200)
        self.assertEqual(json['status'], 'OK')
        results = json['payload']
        self.assertEqual(len(results), 2)
        self.assertEqual([r['name'] for r in results], ['INTRO TO COMPUTER PROGRAMMING', 'DATA STRUCTURES'])

        json = self.json_get('search-all-courses', get='?q=CALCULUS', status_code=200)
        self.assertEqual(json['status'], 'OK')
        results = json['payload']
        self.assertEqual(len(results), 1)
        self.assertEqual([r['name'] for r in results], ['CALCULUS I'])

    def test_get_courses(self):
        json = self.json_get('courses', status_code=200)
        self.assertEqual(json['status'], 'OK')
        self.assertEqual(len(json['payload']), 3)
        self.assertSetEqual(set(c['name'] for c in json['payload']), set(['CALCULUS I', 'INTRO TO COMPUTER PROGRAMMING', 'DATA STRUCTURES']))

    def test_get_course(self):
        json = self.json_get('course', cid=96, status_code=200)
        self.assertEqual(json['status'], 'OK')
        obj = json['payload']
        self.assertEqual(obj['name'], 'CALCULUS I')
        self.assertEqual(obj['department'], dict(code=u'MATH', name=u'Mathematics'))
        self.assertEqual(obj['number'], 1010)
        self.assertEqual(obj['min_credits'], 4)
        self.assertEqual(obj['max_credits'], 4)

    def test_get_course_by_code(self):
        json = self.json_get('course-by-code', code='CSCI', number=1010, status_code=200)
        self.assertEqual(json['status'], 'OK')
        obj = json['payload']
        self.assertEqual(obj['name'], 'INTRO TO COMPUTER PROGRAMMING')
        self.assertEqual(obj['number'], 1010)
        self.assertEqual(obj['min_credits'], 4)
        self.assertEqual(obj['max_credits'], 4)

    # TODO: make more comprehensive
    def test_get_course_sections_by_code(self):
        json = self.json_get('sections', code='CSCI', number=1010, status_code=200)

    # TODO: make more comprehensive
    def test_get_course_sections_by_course_id(self):
        json = self.json_get('sections', cid=224, status_code=200)

    def test_get_section_through_code(self):
        json = self.json_get('section', code='CSCI', number=1010, secnum=1, status_code=200)
        self.assertEqual(json['status'], 'OK')
        obj = json['payload']
        self.assertEqual(obj['number'], '1')
        self.assertEqual(obj['seats_taken'], 48)
        self.assertEqual(obj['seats_left'], 2)
        self.assertEqual(obj['seats_total'], 50)
        self.assertEqual(obj['crn'], 85723)
        # TODO: self.assertEqual(obj['periods'], ...)

    def test_get_section_through_cid(self):
        json = self.json_get('section', cid=224, secnum=1, status_code=200)
        self.assertEqual(json['status'], 'OK')
        obj = json['payload']
        self.assertEqual(obj['number'], '1')
        self.assertEqual(obj['seats_taken'], 48)
        self.assertEqual(obj['seats_left'], 2)
        self.assertEqual(obj['seats_total'], 50)
        self.assertEqual(obj['crn'], 85723)
        # TODO: self.assertEqual(obj['periods'], ...)

    # TODO: make more comprehensive
    def test_get_sections(self):
        json = self.json_get('sections', status_code=200)

    def test_get_section_by_crn(self):
        json = self.json_get('section', crn=85723, status_code=200)
        self.assertEqual(json['status'], 'OK')
        obj = json['payload']
        self.assertEqual(obj['number'], '1')
        self.assertEqual(obj['seats_taken'], 48)
        self.assertEqual(obj['seats_left'], 2)
        self.assertEqual(obj['seats_total'], 50)
        self.assertEqual(obj['crn'], 85723)
        # TODO: self.assertEqual(obj['periods'], ...)


# yeah, I know, not the best practice to be doing this.. but I'm short on time!
class TestLatestAPIViaYearAndMonth(TestLatestAPI):
    def json_get(self, *args, **kwargs):
        return super(TestLatestAPIViaYearAndMonth, self).json_get(*args, year=2011, month=9, **kwargs)


# TODO: make more comprehensive
class TestSemesterAPI(ShortcutTestCase):
    fixtures = ['semesters.json']
    urls = 'yacs.newapi.urls'

    def test_get_semesters(self):
        json = self.json_get('semesters', status_code=200)
        obj = json['payload']
        self.assertEqual(models.Semester.objects.count(), len(obj))

    def test_get_semesters_by_year(self):
        json = self.json_get('semesters-by-year', year=2011, status_code=200)


class TestSemesterAPIWithFactory(ShortcutTestCase):
    urls = 'yacs.newapi.urls'
    def test_get_semesters_with_one_semester(self):
        semester = factories.SemesterFactory.create()
        json = self.json_get('semesters', status_code=200)
        obj = json['payload']
        expected_item = semester.toJSON()
        expected_item['date_updated'] = expected_item['date_updated'].isoformat()
        self.assertEqual([expected_item], obj)
