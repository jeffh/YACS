from django.core.urlresolvers import reverse
from yacs.courses import models
from shortcuts import ShortcutTestCase
from django.utils.simplejson import loads
from datetime import time

class TestAPI(ShortcutTestCase):
    fixtures = ['semesters.json', 'courses/fixtures/calc1.json', 'courses/fixtures/intro-to-cs.json', 'courses/fixtures/data-structures.json']
    urls = 'yacs.newapi.urls'
    def json_get(self, *args, **kwargs):
        response = self.get(*args, **kwargs)
        return loads(response.content)

    def test_get_latest_semester(self):
        json = self.json_get('latest-semester', status_code=200)
        self.assertEqual(json['status'], 'OK')
        sem = json['payload']
        self.assertEqual(sem['year'], 2011)
        self.assertEqual(sem['month'], 9)

    def test_get_latest_departments(self):
        json = self.json_get('latest-departments', status_code=200)
        self.assertEqual(json['status'], 'OK')
        self.assertEqual(len(json['payload']), 3)
        self.assertEqual([d['code'] for d in json['payload']], ['CSCI', 'ECSE', 'MATH'])
        self.assertEqual([d['name'] for d in json['payload']], ['Computer Science', 'Electrical, Computer, and Systems Engineering', 'Mathematics'])

    def test_get_latest_courses_by_dept(self):
        json = self.json_get('latest-courses-by-dept', code='CSCI', status_code=200)
        self.assertEqual(json['status'], 'OK')
        dept = json['payload']
        self.assertEqual(dept['code'], 'CSCI')
        self.assertEqual(dept['name'], 'Computer Science')
        self.assertEqual(len(dept['courses']), 2)

    def test_get_courses_via_search(self):
        json = self.json_get('latest-search-all-courses', get='?q=CSCI', status_code=200)
        self.assertEqual(json['status'], 'OK')
        results = json['payload']
        self.assertEqual(len(results), 2)
        self.assertEqual([r['name'] for r in results], ['INTRO TO COMPUTER PROGRAMMING', 'DATA STRUCTURES'])


