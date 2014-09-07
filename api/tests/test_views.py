from datetime import time, datetime

from shortcuts import ShortcutTestCase

from courses import models
from courses.tests.factories import (
    SemesterFactory, DepartmentFactory, SemesterDepartmentFactory,
    CourseFactory, OfferedForFactory, SectionPeriodFactory,
    SectionFactory
)
from scheduler.models import SavedSelection
from scheduler.factories import SavedSelectionFactory


class TestAPI4Docs(ShortcutTestCase):
    urls = 'yacs.urls'

    def setUp(self):
        self.s = SemesterFactory.create(year=2012)
        self.d = DepartmentFactory.create()
        SemesterDepartmentFactory(department=self.d, semester=self.s)

    def test_it_should_not_blow_up(self):
        self.get('api:v4:docs', status_code=200)


class TestAPI4Schedules(ShortcutTestCase):
    urls = 'api.urls'

    def test_schedules(self):
        pass


class TestAPI4Semesters(ShortcutTestCase):
    urls = 'api.urls'

    def setUp(self):
        self.s1 = SemesterFactory.create(year=2011)
        self.s2 = SemesterFactory.create(year=2012, month=9)

    def as_dict(self, sem):
        return {
            u"name": sem.name,
            u"ref": sem.ref,
            u"year": sem.year,
            u"date_updated": unicode(sem.date_updated.isoformat())[:-7],
            u"date_created": unicode(sem.date_created.isoformat()),
            u"id": sem.id,
            u"month": sem.month,
        }

    def test_get_semester_by_id(self):
        s3 = SemesterFactory.create()
        json = self.json_get('v4:semesters', id=s3.id)

        # for some odd reason, accuracy is lost for datetimes.
        json['result']['date_updated'] = json['result']['date_updated'][:-7]

        self.assertEqual(json, {
            u"version": 4,
            u"success": True,
            u"result": self.as_dict(s3),
        })

    def test_get_semesters_by_ids(self):
        s3 = SemesterFactory.create()
        json = self.json_get(
            'v4:semesters', get='?id=%d&id=%d' % (s3.id, self.s2.id))

        # for some odd reason, accuracy is lost for datetimes.
        for row in json['result']:
            row['date_updated'] = row['date_updated'][:-7]

        self.assertEqual(json, {
            u"version": 4,
            u"success": True,
            u"result": [
                self.as_dict(s3),
                self.as_dict(self.s2),
            ]
        })

    def test_get_semester_by_course(self):
        c1, c2 = CourseFactory.create_batch(2)
        OfferedForFactory.create(semester=self.s1, course=c1)
        OfferedForFactory.create(semester=self.s2, course=c2)
        json = self.json_get('v4:semesters', get='?course_id=%d' % c2.id)

        # for some odd reason, accuracy is lost for datetimes.
        for row in json['result']:
            row['date_updated'] = row['date_updated'][:-7]

        self.assertEqual(json, {
            u"version": 4,
            u"success": True,
            u"result": [self.as_dict(self.s2)],
        })

    def test_get_semester_by_dept(self):
        d1 = DepartmentFactory.create()
        d2 = DepartmentFactory.create()
        SemesterDepartmentFactory.create(semester=self.s1, department=d1)
        SemesterDepartmentFactory.create(semester=self.s2, department=d2)
        json = self.json_get('v4:semesters', get='?department_id=%d' % d1.id)

        # for some odd reason, accuracy is lost for datetimes.
        for row in json['result']:
            row['date_updated'] = row['date_updated'][:-7]

        self.assertEqual(json, {
            u"version": 4,
            u"success": True,
            u"result": [self.as_dict(self.s1)],
        })

    def test_get_semester_by_month(self):
        json = self.json_get('v4:semesters', get='?month=1')

        # for some odd reason, accuracy is lost for datetimes.
        for row in json['result']:
            row['date_updated'] = row['date_updated'][:-7]

        self.assertEqual(json, {
            u"version": 4,
            u"success": True,
            u"result": [self.as_dict(self.s1)],
        })

    def test_get_semester_by_year(self):
        json = self.json_get('v4:semesters', get='?year=2012')

        # for some odd reason, accuracy is lost for datetimes.
        for row in json['result']:
            row['date_updated'] = row['date_updated'][:-7]

        self.assertEqual(json, {
            u"version": 4,
            u"success": True,
            u"result": [self.as_dict(self.s2)],
        })

    def test_get_semester(self):
        self.maxDiff = None
        json = self.json_get('v4:semesters', status_code=200)

        # for some odd reason, accuracy is lost for datetimes.
        for row in json['result']:
            row['date_updated'] = row['date_updated'][:-7]

        self.assertEqual(json, {
            u"version": 4,
            u"success": True,
            u"result": [
                self.as_dict(self.s2),
                self.as_dict(self.s1),
            ],
        })

    def test_get_semester_by_ext(self):
        json = self.json_get('v4:semesters', ext='json', status_code=200)

        # for some odd reason, accuracy is lost for datetimes.
        for row in json['result']:
            row['date_updated'] = row['date_updated'][:-7]

        self.assertEqual(json, {
            u"version": 4,
            u"success": True,
            u"result": [
                self.as_dict(self.s2),
                self.as_dict(self.s1),
            ],
        })


class TestAPI4SavedSelections(ShortcutTestCase):
    urls = 'api.urls'

    def test_saving_and_loading(self):
        course1 = CourseFactory.create()
        course2 = CourseFactory.create()
        section1 = SectionFactory.create(course=course1)
        section2 = SectionFactory.create(course=course1)
        section3 = SectionFactory.create(course=course2)

        json = self.json_post('v4:saved-selections', data={
            'section_ids': ','.join([
                str(section1.id),
                str(section2.id),
                str(section3.id),
            ]),
            'blocked_times': ','.join(['Wednesday_12:0:0', 'Thursday_14:0:0'])
        }, status_code=200)

        selection = SavedSelection.objects.all()[0]

        expected_json = {
            u"version": 4,
            u"success": True,
            u"result": {
                u'id': selection.id,
                u'selection': {
                    unicode(course1.id): [
                        section1.id,
                        section2.id,
                    ],
                    unicode(course2.id): [
                        section3.id
                    ]
                },
                u'blocked_times': [
                    u'Thursday_14:0:0',
                    u'Wednesday_12:0:0',
                ]
            }
        }

        self.assertEqual(json, expected_json)
        json = self.json_post('v4:saved-selection', id=selection.id, status_code=200)
        self.assertEqual(json, expected_json)


class TestAPI4Departments(ShortcutTestCase):
    urls = 'api.urls'

    def as_dict(self, dept):
        return {
            u"code": dept.code,
            u"id": dept.id,
            u"name": dept.name,
        }

    def test_get_department_by_id(self):
        d1, d2, d3 = DepartmentFactory.create_batch(3)
        json = self.json_get('v4:departments', id=d1.id, status_code=200)

        self.assertEqual(json, {
            u"version": 4,
            u"success": True,
            u"result": self.as_dict(d1)
        })

    def test_get_departments_by_ids(self):
        d1, d2, d3 = DepartmentFactory.create_batch(3)
        json = self.json_get(
            'v4:departments', get='?id=%d&id=%d' % (d1.id, d2.id),
            status_code=200)

        self.assertEqual(json, {
            u"version": 4,
            u"success": True,
            u"result": [
                self.as_dict(d1),
                self.as_dict(d2),
            ]
        })

    def test_get_departments_by_code(self):
        d1, d2, d3 = DepartmentFactory.create_batch(3)
        d4 = DepartmentFactory.create(code='FOO')

        json = self.json_get(
            'v4:departments', get='?code=FOO', status_code=200)

        self.assertEqual(json, {
            u"version": 4,
            u"success": True,
            u"result": [self.as_dict(d4)]
        })

    def test_get_departments_by_courses(self):
        d1, d2, d3 = DepartmentFactory.create_batch(3)
        c1 = CourseFactory.create(department=d1)
        c2 = CourseFactory.create(department=d2)
        c3 = CourseFactory.create(department=d3)

        json = self.json_get(
            'v4:departments',
            get='?course_id=%d&course_id=%d' % (c1.id, c2.id),
            status_code=200)

        self.assertEqual(json, {
            u"version": 4,
            u"success": True,
            u"result": [
                self.as_dict(d1),
                self.as_dict(d2),
            ]
        })

    def test_get_departments_by_semester(self):
        s1, s2 = SemesterFactory.create_batch(2)
        d1, d2, d3 = DepartmentFactory.create_batch(3)
        SemesterDepartmentFactory.create(semester=s1, department=d1)
        SemesterDepartmentFactory.create(semester=s1, department=d2)
        SemesterDepartmentFactory.create(semester=s2, department=d3)

        json = self.json_get(
            'v4:departments',
            get='?semester_id=%d' % s1.id,
            status_code=200)

        self.assertEqual(json, {
            u"version": 4,
            u"success": True,
            u"result": [
                self.as_dict(d1),
                self.as_dict(d2),
            ]
        })

    def test_get_departments(self):
        d1, d2, d3, d4 = DepartmentFactory.create_batch(4)
        json = self.json_get('v4:departments', status_code=200)

        self.assertEqual(json, {
            u"version": 4,
            u"success": True,
            u"result": [
                self.as_dict(d1),
                self.as_dict(d2),
                self.as_dict(d3),
                self.as_dict(d4),
            ]
        })

    def test_get_departments_by_ext(self):
        d1, d2, d3, d4 = DepartmentFactory.create_batch(4)
        json = self.json_get('v4:departments', ext='json', status_code=200)
        self.maxDiff = None

        self.assertEqual(json, {
            u"version": 4,
            u"success": True,
            u"result": [
                self.as_dict(d1),
                self.as_dict(d2),
                self.as_dict(d3),
                self.as_dict(d4),
            ]
        })


class TestAPI4Courses(ShortcutTestCase):
    urls = 'api.urls'

    def to_dict(self, obj):
        return {
            u"name": obj.name,
            u"number": obj.number,
            u"department_id": obj.department_id,
            u"min_credits": obj.min_credits,
            u"max_credits": obj.max_credits,
            u"grade_type": obj.grade_type,
            u"description": obj.description,
            u"prereqs": obj.prereqs,
            u"is_comm_intense": obj.is_comm_intense,
            u"id": obj.id,
        }

    def test_fetch_should_not_exclude_comm_intense(self):
        c1 = CourseFactory.create(is_comm_intense=True)
        c1.save()
        json = self.json_get('v4:courses', id=int(c1.id), status_code=200)
        self.maxDiff = None
        self.assertEqual(json, {
            u"version": 4,
            u"success": True,
            u"result": self.to_dict(c1),
        })

    def test_search_department_name(self):
        c1, c2 = CourseFactory.create_batch(2)
        d = DepartmentFactory.create(name='Computer Science')
        c3, c4 = CourseFactory.create_batch(2, department=d)
        json = self.json_get(
            'v4:courses', get='?search=Computer', status_code=200)
        self.maxDiff = None
        self.assertEqual(json, {
            u"version": 4,
            u"success": True,
            u"result": [
                self.to_dict(c3),
                self.to_dict(c4),
            ],
        })

    def test_search_department_code(self):
        c1, c2 = CourseFactory.create_batch(2)
        d = DepartmentFactory.create(code='CSCI')
        c3 = CourseFactory.create(department=d)
        json = self.json_get(
            'v4:courses', get='?search=CSCI', status_code=200)
        self.maxDiff = None
        self.assertEqual(json, {
            u"version": 4,
            u"success": True,
            u"result": [self.to_dict(c3)],
        })

    def test_search_name(self):
        c1, c2 = CourseFactory.create_batch(2)
        c3 = CourseFactory.create(name="Cakes for Dummies")
        json = self.json_get(
            'v4:courses', get='?search=cakes dum', status_code=200)
        self.maxDiff = None
        self.assertEqual(json, {
            u"version": 4,
            u"success": True,
            u"result": [self.to_dict(c3)],
        })

    def test_search_instructor(self):
        c1, c2 = CourseFactory.create_batch(2)
        c3 = CourseFactory.create()
        sec = SectionFactory.create(course=c3)
        sp = SectionPeriodFactory.create(section=sec, instructor='Moorthy')
        json = self.json_get('v4:courses', get='?search=moor', status_code=200)
        self.maxDiff = None
        self.assertEqual(json, {
            u"version": 4,
            u"success": True,
            u"result": [
                self.to_dict(c3),
            ]
        })

    def test_get_courses(self):
        c1, c2, c3 = CourseFactory.create_batch(3)
        json = self.json_get('v4:courses', status_code=200)
        self.maxDiff = None
        self.assertEqual(json, {
            u"version": 4,
            u"success": True,
            u"result": [
                self.to_dict(c1),
                self.to_dict(c2),
                self.to_dict(c3),
            ]
        })

    def test_get_courses_by_dept_code(self):
        d = DepartmentFactory.create(code='CSCI')
        c1, c2 = CourseFactory.create_batch(2, department=d)
        c3, c4 = CourseFactory.create_batch(2)
        json = self.json_get(
            'v4:courses', get='?department_code=%s' % d.code, status_code=200)
        self.maxDiff = None
        self.assertEqual(json, {
            u"version": 4,
            u"success": True,
            u"result": [
                self.to_dict(c1),
                self.to_dict(c2),
            ]
        })

    def test_get_courses_by_dept_id(self):
        d = DepartmentFactory.create(code='CSCI')
        c1, c2 = CourseFactory.create_batch(2, department=d)
        c3, c4 = CourseFactory.create_batch(2)
        json = self.json_get(
            'v4:courses', get='?department_id=%s' % d.id, status_code=200)
        self.assertEqual(json, {
            u"version": 4,
            u"success": True,
            u"result": [
                self.to_dict(c1),
                self.to_dict(c2),
            ]
        })

    def test_get_courses_by_number(self):
        c1, c2 = CourseFactory.create_batch(2, number=1337)
        c3, c4 = CourseFactory.create_batch(2)
        json = self.json_get('v4:courses', get='?number=1337', status_code=200)
        self.assertEqual(json, {
            u"version": 4,
            u"success": True,
            u"result": [
                self.to_dict(c1),
                self.to_dict(c2),
            ]
        })

    def test_get_course_by_id(self):
        c1, c2 = CourseFactory.create_batch(2)
        json = self.json_get('v4:courses', id=c1.id, status_code=200)
        self.assertEqual(json, {
            u"version": 4,
            u"success": True,
            u"result": self.to_dict(c1),
        })

    def test_get_courses_by_ids(self):
        c1, c2, c3, c4 = CourseFactory.create_batch(4)
        json = self.json_get(
            'v4:courses',
            get='?id=%d&id=%d' % (c1.id, c3.id),
            status_code=200)
        self.assertEqual(json, {
            u"version": 4,
            u"success": True,
            u"result": [
                self.to_dict(c1),
                self.to_dict(c3),
            ]
        })


class TestAPI4Sections(ShortcutTestCase):
    urls = 'api.urls'

    def to_dict(self, obj):
        section = obj.section
        period = obj.period

        def time_format(t):
            return u"%02d:%02d:%02d" % (
                t.hour, t.minute, t.second
            )

        return {
            u"course_id": section.course_id,
            u"seats_total": section.seats_total,
            u"crosslisted_id": section.crosslisted_id,
            # obj.semester.id is another id
            u"semester_id": section.semester.id,
            u"id": obj.id,
            u"notes": unicode(section.notes),
            u"section_times": [
                {
                    u"start": time_format(period.start),
                    u"kind": obj.kind,
                    u"end": time_format(period.end),
                    u"instructor": obj.instructor,
                    u"location": obj.location,
                    u"days_of_the_week": period.days_of_week,
                    u"section_id": section.id,
                }
            ],
            u"crn": section.crn,
            u"number": section.number,
            u"seats_taken": section.seats_taken,
        }

    def test_get_sections(self):
        s1, s2, s3, s4 = SectionPeriodFactory.create_batch(4)
        json = self.json_get('v4:sections', status_code=200)
        self.assertEqual(json, {
            u"version": 4,
            u"success": True,
            u"result": [
                self.to_dict(s1),
                self.to_dict(s2),
                self.to_dict(s3),
                self.to_dict(s4),
            ]
        })

    def test_get_sections_by_semester(self):
        sem = SemesterFactory.create()
        s1, s2 = SectionPeriodFactory.create_batch(2, semester=sem)
        s3, s4 = SectionPeriodFactory.create_batch(2)
        json = self.json_get(
            'v4:sections', get='?semester_id=%d' % sem.id, status_code=200)
        self.assertEqual(json, {
            u"version": 4,
            u"success": True,
            u"result": [
                self.to_dict(s1),
                self.to_dict(s2),
            ]
        })

    def test_get_sections_by_course(self):
        c1 = CourseFactory.create()
        sec1, sec2 = SectionFactory.create_batch(2, course=c1)
        s1 = SectionPeriodFactory.create(section=sec1)
        s2 = SectionPeriodFactory.create(section=sec2)
        s3, s4 = SectionPeriodFactory.create_batch(2)
        json = self.json_get(
            'v4:sections', get='?course_id=%d' % c1.id, status_code=200)
        self.assertEqual(json, {
            u"version": 4,
            u"success": True,
            u"result": [
                self.to_dict(s1),
                self.to_dict(s2),
            ]
        })

    def test_get_section_by_id(self):
        s1, s2 = SectionPeriodFactory.create_batch(2)
        json = self.json_get('v4:sections', id=s1.id, status_code=200)
        self.maxDiff = None
        self.assertEqual(json, {
            u"version": 4,
            u"success": True,
            u"result": self.to_dict(s1),
        })

    def test_get_sections_by_ids(self):
        s1, s2, s3, s4 = SectionPeriodFactory.create_batch(4)
        json = self.json_get(
            'v4:sections',
            get='?id=%d&id=%d' % (s1.id, s3.id),
            status_code=200)
        self.assertEqual(json, {
            u"version": 4,
            u"success": True,
            u"result": [
                self.to_dict(s1),
                self.to_dict(s3),
            ]
        })

    def test_get_sections_by_crn(self):
        s1, s2, s3, s4 = SectionPeriodFactory.create_batch(4)
        json = self.json_get(
            'v4:sections',
            get='?crn=%d&crn=%d' % (s1.section.crn, s3.section.crn),
            status_code=200)
        self.assertEqual(json, {
            u"version": 4,
            u"success": True,
            u"result": [
                self.to_dict(s1),
                self.to_dict(s3),
            ]
        })


# TODO: we don't have any factories here...
class TestAPI4SectionConflicts(ShortcutTestCase):
    urls = 'api.urls'


class TestAPI4Selection(ShortcutTestCase):
    urls = 'api.urls'
