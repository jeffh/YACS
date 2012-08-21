import unittest

import rpi_courses.scheduler as s
from rpi_courses.parser import CourseCatalog
from pyconstraints import Problem

from constants import XML_SCHEDULE_TEST_FILE, XML_SCHEDULE_TEST_CONFLICT_FILE


with open(XML_SCHEDULE_TEST_FILE) as f:
    SCHEDULE_CONTENTS = f.read()

with open(XML_SCHEDULE_TEST_CONFLICT_FILE) as f:
    CONFLICT_CONTENTS = f.read()


class TestTimeRange(unittest.TestCase):
    "Time range of [1200, 1300]"
    def setUp(self):
        self.tr = s.TimeRange(start=1200, end=1300, dow=(0,))

    def assertIn(self, item, collection):
        if hasattr(super(TestTimeRange, self), 'assertIn'):
            super(TestTimeRange, self).assertIn(item, collection)
        else:
            assert item in collection

    def assertNotIn(self, item, collection):
        if hasattr(super(TestTimeRange, self), 'assertNotIn'):
            super(TestTimeRange, self).assertNotIn(item, collection)
        else:
            assert item not in collection

    def test_time_range_does_contain(self):
        "should contain time range of [1100, 1250]."
        self.assertIn(((0,), 1100, 1250), self.tr)

    def test_time_range_does_not_contain(self):
        "should not contain time range of [1100, 1150]."
        self.assertNotIn(((0,), 1100, 1150), self.tr)


class TestMakeSchedules(unittest.TestCase):
    "Scheduler from XML fixture"
    # TODO: make instances themselves instead of using this XML files.
    def setUp(self):
        catalog = CourseCatalog.from_string(SCHEDULE_CONTENTS)
        course_names = (
            'graph theory math',
            'learning',
            'intro to philosophy',
            'software design & doc',
            'multivar calc',
        )
        self.courses = {}
        for n in course_names:
            self.courses[n] = catalog.find_courses(n)[0]

    def assertIn(self, item, collection):
        if hasattr(super(TestMakeSchedules, self), 'assertIn'):
            super(TestMakeSchedules, self).assertIn(item, collection)
        else:
            assert item in collection

    def dump(self, schedules):
        results = []
        for schedule in schedules:
            result = {}
            for course, section in schedule.items():
                result[course.name] = section.num
            results.append(result)
        for result in results:
            from pprint import pprint
            pprint(result.values())

    def test_compute_schedules(self):
        "Should have 36 solutions for all courses."
        result = s.compute_schedules(self.courses.values())
        # RPI scheduler lists 12 schedules but:
        # - MATH 2010 has two sections for all the 12 schedules
        # - Software Design & Docs has 2 sections for 6 of the schedules
        self.assertEqual(len(result), 36)

    def test_schedules_with_no_conflicts(self):
        "Should have 2 solutions for graph theory & intro to philosophy."
        courses = (
            self.courses['graph theory math'], self.courses['intro to philosophy']
        )
        result = s.compute_schedules(courses)
        expected = [{
            courses[0]: courses[0].sections[0],
            courses[1]: courses[1].sections[1],
        }, {
            courses[0]: courses[0].sections[0],
            courses[1]: courses[1].sections[0],
        }]

        self.assertIn(result[0], expected)
        self.assertIn(result[1], expected)
        self.assertNotEqual(result[0], result[1])

    def test_schedules_with_restricting_times_and_no_conflicts(self):
        "Should have 1 solution for graph theory & intro to philosophy with time restriction."
        courses = (
            self.courses['graph theory math'], self.courses['intro to philosophy']
        )
        restrictions = []
        for p in courses[1].sections[0].periods:
            restrictions.append(
                s.TimeRange(*p.time_range, dow=(0,))
            )
        result = s.compute_schedules(courses, restrictions)
        expected = [{
            courses[0]: courses[0].sections[0],
            courses[1]: courses[1].sections[1],
        }]
        self.assertEqual(list(result), expected)


class TestMakeConflictableSchedules(unittest.TestCase):
    # TODO: make instances themselves instead of using this XML files.
    def setUp(self):
        catalog = CourseCatalog.from_string(CONFLICT_CONTENTS)
        course_names = (
            'BEGINNING PROG FOR ENG',
            'COMPUTER SCIENCE I',
        )
        self.courses = {}
        for n in course_names:
            self.courses[n] = catalog.find_courses(n)[0]

    def assertIn(self, item, collection):
        if hasattr(super(TestMakeConflictableSchedules, self), 'assertIn'):
            super(TestMakeConflictableSchedules, self).assertIn(item, collection)
        else:
            assert item in collection

    def test_schedules_with_conflicts(self):
        "Should schedule courses with some conflicts."
        result = s.compute_schedules(self.courses.values())
        c = (
            self.courses['BEGINNING PROG FOR ENG'],
            self.courses['COMPUTER SCIENCE I'],
        )
        expected = []
        for s1 in c[0].sections:
            for s2 in c[1].sections:
                if not s1.conflicts_with(s2):
                    expected.append({c[0]: s1, c[1]: s2})

        self.assertEqual(len(result), len(expected))
        for r in result:
            self.assertIn(r, expected)
            for r2 in result:
                if r != r2:
                    self.assertNotEqual(r, r2)

    def test_schedules_with_conflicts_and_restricted_times(self):
        "Should schedule courses with some conflicts and time restrictions"
        result = s.compute_schedules(self.courses.values())
        c = (
            self.courses['BEGINNING PROG FOR ENG'],
            self.courses['COMPUTER SCIENCE I']
        )

        restrictions = [s.TimeRange(start=1000, end=1100, dow=(0,))]

        expected = []
        for s1 in c[0].sections:
            if restrictions[0].conflicts_with(s1):
                continue
            for s2 in c[1].sections:
                if not s1.conflicts_with(s2):
                    expected.append({c[0]: s1, c[1]: s2})

        self.assertEquals(len(result), len(expected))
        for r in result:
            self.assertIn(r, expected)
            for r2 in result:
                if r != r2:
                    self.assertNotEqual(r, r2)


if __name__ == '__main__':
    unittest.main()
