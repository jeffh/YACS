from rpi_courses.parser import CourseCatalog
from rpi_courses import models
from test.rpi_courses.utils import TestCaseForModel

from mock import Mock

import os
import unittest
from time import mktime
from constants import XML_FILE, XML_PARSER_FILE


with open(XML_PARSER_FILE) as f:
    CONTENTS = f.read()


class TestCatalog(TestCaseForModel):
    def setUp(self):
        self.catalog = CourseCatalog.from_string(CONTENTS)

    def test_crosslisting(self):
        crns = self.catalog.crosslisted_with(76093)
        for e in (76097, 76098, 76099):
            self.assertIn(e, crns)

        crns = self.catalog.crosslisted_with(76097)
        for e in (76093, 76098, 76099):
            self.assertIn(e, crns)

        crns = self.catalog.crosslisted_with(76101)
        self.assertEquals(crns, (76106,))

    def test_get_timestamp(self):
        expected_timestamp = 1290023154
        timestamp = int(mktime(self.catalog.datetime.timetuple()))

        self.assertEquals(timestamp, expected_timestamp)

    def test_get_year(self):
        self.assertEquals(self.catalog.year, 2011)

    def test_get_semester(self):
        self.assertEquals(self.catalog.semester, 'Spring')

    def test_get_ta_training_seminar_with_no_time_periods(self):
        course = self.catalog.find_courses('TA TRAINING SEMINAR')[0]
        expected_course = models.Course(
            'TA TRAINING SEMINAR', 'ADMN', num=6800, credmin=0, credmax=0,
            grade_type='Satisfactory/Unsatisfactory',
            sections=[models.Section(
                crn=76285, num='01', taken=0, total=200,
                periods=[models.Period(
                    type='LEC', instructor='Gornic',
                    start='** TBA **', end='** TBA **',
                    location=' ', int_days=(),
                )],
                notes=[
                    'REQUIRED FOR ALL NEW OR CURRENT STUDENTS WHO WILL TA',
                    'MEETING ON THUR, 1/20 IN PM AND ALL DAY 1/21'
                ]
            )]
        )
        self.assertCourseEquals(course, expected_course)

    def test_get_intro_to_hci(self):
        course = self.catalog.find_courses('INTRODUCTION TO HCI')[0]
        expected_course = models.Course(
            'INTRODUCTION TO HCI', 'ITWS', num=2210, credmin=4, credmax=4,
            grade_type='', sections=[models.Section(
                crn=76041, num='01', taken=26, total=40,
                periods=[models.Period(
                    type='LEC', instructor='Grice',
                    start=1200, end=1350, location='LALLY 102',
                    int_days=(0, 3),
                )],
                notes=['RESTRICTED TO COMM, ITWS & EMAC MAJORS']
            )]
        )
        self.assertCourseEquals(course, expected_course)

    def test_get_intro_to_phil_with_two_sections(self):
        course = self.catalog.find_courses('INTRO TO PHILOSOPHY')[0]
        expected_course = models.Course(
            'INTRO TO PHILOSOPHY', 'PHIL', num=1110, credmin=4, credmax=4,
            grade_type='', sections=[
                models.Section(
                    crn=74447, num='01', taken=35, total=35,
                    periods=[models.Period(
                        type='LEC', instructor='Fahey',
                        start=1000, end=1150, location='CARNEG 206',
                        int_days=(0, 3)
                    )],
                    notes=[]
                ),
                models.Section(
                    crn=73498, num='02', taken=35, total=35,
                    periods=[models.Period(
                        type='LEC', instructor='Carcasole',
                        start=1000, end=1150, location='CARNEG 101',
                        int_days=(1, 4)
                    )],
                    notes=[]
                )
            ],
        )

        self.assertCourseEquals(course, expected_course)


if __name__ == '__main__':
    unittest.main()
