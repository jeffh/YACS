from rpi_courses.sis_parser import CourseCatalog
from rpi_courses import models
from test.rpi_courses.utils import TestCaseForModel

from mock import Mock

import os
import unittest
from time import mktime
from constants import SIS_FILE

with open(SIS_FILE) as f:
    CONTENTS = f.read()
catalog = None

# from BeautifulSoup import BeautifulSoup; soup = BeautifulSoup(open('lib/test/rpi_courses/test_data/sis_courses.html').read())
# from rpi_courses.sis_parser import CourseCatalog; catalog = CourseCatalog.from_file('lib/test/rpi_courses/test_data/sis_courses.html')

class TestCatalog(TestCaseForModel):
    def setUp(self):
        global catalog
        if catalog is None:
            catalog = CourseCatalog.from_string(CONTENTS)
        self.catalog = catalog

#    def test_crosslisting(self):
#        crns = self.catalog.crosslisted_with(76093)
#        for e in (76097, 76098, 76099):
#            self.assertIn(e, crns)
#
#        crns = self.catalog.crosslisted_with(76097)
#        for e in (76093, 76098, 76099):
#            self.assertIn(e, crns)
#
#        crns = self.catalog.crosslisted_with(76101)
#        self.assertEquals(crns, (76106,))

    def test_get_year(self):
        self.assertEquals(self.catalog.year, 2012)

    def test_get_semester(self):
        self.assertEquals(self.catalog.semester, 'Spring')

    def test_get_ta_training_seminar_with_no_time_periods(self):
        course = self.catalog.find_courses('TA TRAINING SEMINAR')[0]
        expected_course = models.Course(
            'TA TRAINING SEMINAR', 'ADMN', num=6800, credmin=0, credmax=0,
            grade_type='Satisfactory/Unsatisfactory',
            sections=[models.Section(
                crn=97989, num='01', taken=0, total=200,
                periods=[models.Period(
                    type='LEC', instructor='Gornic',
                    start='** TBA **', end='** TBA **',
                    location=' ', int_days=(),
                )],
                notes=[]
            )]
        )
        self.assertCourseEquals(course, expected_course)

    def test_get_intro_to_hci(self):
        course = self.catalog.find_courses('INTRODUCTION TO HCI')[0]
        expected_course = models.Course(
            'INTRODUCTION TO HCI', 'ITWS', num=2210, credmin=4, credmax=4,
            grade_type='', sections=[models.Section(
                crn=97772, num='01', taken=0, total=40,
                notes=('RESTRICTED TO COMM, EMAC, ITWS MAJORS',),
                periods=[models.Period(
                    type='LEC', instructor='Grice',
                    start=1200, end=1350, location='',
                    int_days=(0, 3),
                )],
            )]
        )
        self.assertCourseEquals(course, expected_course)

    def test_crosslisted_courses(self):
        course = self.catalog.find_courses('INTRO TO COG NEUROSCIENCE')[1]
        expected_course = models.Course(
            'INTRO TO COG NEUROSCIENCE', 'PSYC', num=4968, credmin=4, credmax=4,
            grade_type='', sections=[models.Section(
                crn=98083, num='01', taken=0, total=10,
                periods=[models.Period(
                    type='LEC', instructor='Walf',
                    start=1400, end=1550, location='',
                    int_days=(1,4),
                )],
                notes=['MEETS WITH COGS 4967']
            )]
        )
        self.assertCourseEquals(course, expected_course)

    def test_courses_with_multiple_periods(self):
        course = self.catalog.find_courses('DATA STRUCTURES')[0]
        print course.sections[0].periods
        expected_course = models.Course(
            'DATA STRUCTURES', 'CSCI', num=1200, credmin=4, credmax=4,
            grade_type='', sections=[
                models.Section(
                    crn=95551, num='01', taken=0, total=33, notes=[],
                    periods=[
                        models.Period(
                            type='LEC', instructor='Stewart',
                            start=1200, end=1350, location='',
                            int_days=(0, 3)
                        ),
                        models.Period(
                            type='LAB', instructor='Staff',
                            start=1000, end=1150, location='',
                            int_days=(2,)
                        ),
                    ]
                ),
                models.Section(
                    crn=95552, num='02', taken=0, total=33, notes=[],
                    periods=[
                        models.Period(
                            type='LEC', instructor='Stewart',
                            start=1200, end=1350, location='',
                            int_days=(0, 3)
                        ),
                        models.Period(
                            type='LAB', instructor='Staff',
                            start=1000, end=1150, location='',
                            int_days=(2,)
                        ),
                    ]
                ),
                models.Section(
                    crn=95553, num='03', taken=0, total=33, notes=[],
                    periods=[
                        models.Period(
                            type='LEC', instructor='Stewart',
                            start=1200, end=1350, location='',
                            int_days=(0, 3)
                        ),
                        models.Period(
                            type='LAB', instructor='Staff',
                            start=1200, end=1350, location='',
                            int_days=(2,)
                        ),
                    ]
                ),
                models.Section(
                    crn=95554, num='04', taken=0, total=33, notes=[],
                    periods=[
                        models.Period(
                            type='LEC', instructor='Stewart',
                            start=1200, end=1350, location='',
                            int_days=(0, 3)
                        ),
                        models.Period(
                            type='LAB', instructor='Staff',
                            start=1400, end=1550, location='',
                            int_days=(2,)
                        ),
                    ]
                ),
                models.Section(
                    crn=95555, num='05', taken=0, total=33, notes=[],
                    periods=[
                        models.Period(
                            type='LEC', instructor='Stewart',
                            start=1200, end=1350, location='',
                            int_days=(0, 3)
                        ),
                        models.Period(
                            type='LAB', instructor='Staff',
                            start=1600, end=1750, location='',
                            int_days=(2,)
                        ),
                    ]
                ),
                models.Section(
                    crn=95556, num='06', taken=0, total=33, notes=[],
                    periods=[
                        models.Period(
                            type='LEC', instructor='Stewart',
                            start=1200, end=1350, location='',
                            int_days=(0, 3)
                        ),
                        models.Period(
                            type='LAB', instructor='Staff',
                            start=1800, end=1950, location='',
                            int_days=(2,)
                        ),
                    ]
                ),
                models.Section(
                    crn=95557, num='07', taken=0, total=33, notes=[],
                    periods=[
                        models.Period(
                            type='LEC', instructor='Stewart',
                            start=1200, end=1350, location='',
                            int_days=(0, 3)
                        ),
                        models.Period(
                            type='LAB', instructor='Staff',
                            start=1200, end=1350, location='',
                            int_days=(2,)
                        ),
                    ]
                ),
            ]
        )
        self.assertCourseEquals(course, expected_course)

    def test_get_intro_to_phil_with_three_sections(self):
        course = self.catalog.find_courses('INTRO TO PHILOSOPHY')[0]
        expected_course = models.Course(
            'INTRO TO PHILOSOPHY', 'PHIL', num=1110, credmin=4, credmax=4,
            grade_type='', sections=[
                models.Section(
                    crn=96407, num='01', taken=0, total=35,
                    periods=[models.Period(
                        type='LEC', instructor='Fahey',
                        start=1000, end=1150, location='',
                        int_days=(0,3)
                    )],
                    notes=[]
                ),
                models.Section(
                    crn=95481, num='02', taken=0, total=35,
                    periods=[models.Period(
                        type='LEC', instructor='Carcasole',
                        start=1000, end=1150, location='',
                        int_days=(1,4)
                    )],
                    notes=[]
                ),
                models.Section(
                    crn=98420, num='03', taken=0, total=27,
                    periods=[models.Period(
                        type='LEC', instructor='Thero',
                        start=1200, end=1350, location='',
                        int_days=(0,3)
                    )],
                    notes=[]
                )
            ],
        )

        self.assertCourseEquals(course, expected_course)

if __name__ == '__main__':
    unittest.main()
