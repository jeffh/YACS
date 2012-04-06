from rpi_courses.sis_parser import CourseCatalog
from rpi_courses import models
from test.rpi_courses.utils import TestCaseForModel

from mock import Mock

import os
import unittest
from time import mktime
from constants import SIS_FILE_SPRING2012

with open(SIS_FILE_SPRING2012) as f:
    CONTENTS_SPRING2012 = f.read()
catalog_spring2012 = None


class TestCatalogSpring2012(TestCaseForModel):
    def setUp(self):
        global catalog_spring2012
        if catalog_spring2012 is None:
            catalog_spring2012 = CourseCatalog.from_string(CONTENTS_SPRING2012)
        self.catalog = catalog_spring2012

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

    def get_section_by_crn(self, crn):
        for course in self.catalog.get_courses():
            for section in course.sections:
                if crn == section.crn:
                    return section
        raise KeyError("Section with CRN of " + str(crn) + " does not exist.")

    def test_time_period_from_11_to_1pm(self):
        "When period lists 11 - 1:50pm..."
        section = self.get_section_by_crn(96688)
        expected_section = models.Section(
            crn=96688, num='03', taken=0, total=23, notes=[],
            periods=[models.Period(
                type='LAB', instructor='Morris',
                start=1100, end=1250,
                location='', int_days=(3,)
            )]
        )
        self.assertSectionEquals(section, expected_section)

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
                    location='', int_days=(),
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

    def test_creative_writing_poetry(self):
        # Bug: this class was not detected by the parser
        course = self.catalog.find_courses('CREATIVE WRITING: POETRY')[0]
        expected_course = models.Course(
            'CREATIVE WRITING: POETRY', 'LITR', num=2961, credmin=4, credmax=4,
            grade_type='', sections=[models.Section(
                crn=96438, num='01', taken=0, total=22,
                periods=[models.Period(
                    type='LEC', instructor='Gutmann',
                    start=1200, end=1350, location='',
                    int_days=(1, 4),
                )],
                notes=['COMMUNICATION INTENSIVE'],
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
                    int_days=(1, 4),
                )],
                notes=['MEETS WITH COGS 4967']
            )]
        )
        self.assertCourseEquals(course, expected_course)

    def test_get_psych_course_count(self):
        courses = self.catalog.find_courses('PSYC')
        expected_names = (
            'GENERAL PSYCHOLOGY',
            'CRITICAL THINKING',
            'INTRO. TO COGNITIVE SCIEN',
            'HUMAN FACTORS IN DESIGN',
            'SOCIAL PSYCHOLOGY',
            'THINKING',
            'DEMOCRACY: SOCIAL VS POLI',
            'HEROES OF THE HUDSON VALL',
            'ANARCHISM: ETHICAL SOCIET',
            'MOTIVATION & PERFORMANCE',
            'PROFESSIONAL DEVELOPMENT',
            'ORGANIZATIONAL PSYCHOLOGY',
            'ADV EXPER METHODS & STATI',
            'BEHAVIORAL NEUROSCIENCE',
            'COGNITIVE PSYCHOLOGY',
            'PERSONALITY',
            'LEARNING',
            'DRUGS SOCIETY & BEHAVIOR',
            'ABNORMAL PSYCHOLOGY',
            'FORENSIC PSYCHOLOGY',
            'PSYCHOPHARM & BEH TOXICO',
            'SPORTS PSYCHOLOGY SEMINAR',
            'READINGS IN PSYC',
            'ADVANCED TOPICS IN MOTIVA',
            'COG SCI & ECONOMICS',
            'INTRO TO COG NEUROSCIENCE',
            'STRESS & THE BRAIN',
            'UNDERGRADUATE THESIS',
        )
        self.assertEqual(set(c.name for c in courses), set(expected_names))

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
                        int_days=(0, 3)
                    )],
                    notes=[]
                ),
                models.Section(
                    crn=95481, num='02', taken=0, total=35,
                    periods=[models.Period(
                        type='LEC', instructor='Carcasole',
                        start=1000, end=1150, location='',
                        int_days=(1, 4)
                    )],
                    notes=[]
                ),
                models.Section(
                    crn=98420, num='03', taken=0, total=27,
                    periods=[models.Period(
                        type='LEC', instructor='Thero',
                        start=1200, end=1350, location='',
                        int_days=(0, 3)
                    )],
                    notes=[]
                )
            ],
        )

        self.assertCourseEquals(course, expected_course)

    def test_digital_control_systems(self):
        course = self.catalog.find_courses('DIGITAL CONTROL SYSTEMS')[0]
        expected_course = models.Course(
            'DIGITAL CONTROL SYSTEMS', 'ECSE', num=4510, credmin=3, credmax=3,
            grade_type='', sections=[
                models.Section(
                    crn=95474, num='01', taken=0, total=40,
                    periods=[models.Period(
                        type='LEC', instructor='Chow',
                        start=1200, end=1320, location='',
                        int_days=(1, 4)
                    )],
                    notes=[]
                )
            ]
        )

        self.assertCourseEquals(course, expected_course)

    def test_digital_communications(self):
        course = self.catalog.find_courses('DIGITAL COMMUNICATIONS')[0]
        expected_course = models.Course(
            'DIGITAL COMMUNICATIONS', 'ECSE', num=4560, credmin=3, credmax=3,
            grade_type='', sections=[
                models.Section(
                    crn=97975, num='01', taken=0, total=40,
                    periods=[models.Period(
                        type='LEC', instructor='Saulnier',
                        start=1600, end=1720, location='',
                        int_days=(0, 3)
                    )],
                    notes=['MEETS WITH ECSE 6560']
                )
            ]
        )

        self.assertCourseEquals(course, expected_course)


if __name__ == '__main__':
    unittest.main()
