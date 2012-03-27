import unittest


class TestCaseForModel(unittest.TestCase):
    def assertPeriodEquals(self, period1, period2):
        """
        Manually compares each property of two period instances.
        """
        self.assertEquals(period1.type, period2.type)
        self.assertEquals(period1.instructor, period2.instructor)
        self.assertEquals(period1.location, period2.location)
        self.assertEquals(period1.start, period2.start)
        self.assertEquals(period1.end, period2.end)
        self.assertEquals(period1.int_days, period2.int_days)

    def assertIn(self, item, collection):
        assert item in collection

    def assertPeriodEqual(self, period1, period2):
        self.assertPeriodEquals(period1, period2)

    def assertPeriodsEqual(self, periods1, periods2):
        """
        Invokes self.assertSectionEquals to two tuples of periods.
        """
        self.assertEquals(len(periods1), len(periods2))
        for i in range(len(periods1)):
            self.assertPeriodEquals(periods1[i], periods2[i])

    def assertPeriodsEquals(self, periods1, periods2):
        self.assertPeriodsEqual(period1, period2)

    def assertSectionEquals(self, section1, section2):
        """
        Manually compares each property of two section instances.
        """
        self.assertEquals(section1.crn, section2.crn)
        self.assertEquals(section1.num, section2.num)
        self.assertEquals(section1.seats_taken, section2.seats_taken)
        self.assertEquals(section1.seats_total, section2.seats_total)
        self.assertEquals(section1.notes, section2.notes)
        self.assertPeriodsEqual(section1.periods, section2.periods)

    def assertSectionEqual(self, section1, section2):
        self.assertSectionEquals(section1, section2)

    def assertSectionsEquals(self, sections1, sections2):
        """
        Invokes self.assertSectionEquals to two tuples of sections.
        """
        self.assertEquals(len(sections1), len(sections2))
        for i in range(len(sections1)):
            self.assertSectionEquals(sections1[i], sections2[i])

    def assertSectionsEqual(self, sections1, sections2):
        self.assertSectionsEquals(sections1, sections2)

    def assertCourseEquals(self, course1, course2):
        """
        Manually compares each property of two course instances.
        """
        self.assertEquals(course1.name, course2.name)
        self.assertEquals(course1.dept, course2.dept)
        self.assertEquals(course1.num, course2.num)
        self.assertEquals(course1.cred, course2.cred)
        # technically, we should compare grade_type
        # but we only want to know if the course is pass/fail anyway
        self.assertEquals(course1.is_pass_or_fail, course2.is_pass_or_fail)
        self.assertSectionsEqual(course1.sections, course2.sections)

    def assertCourseEqual(self, course1, course2):
        self.assertCourseEquals(course1, course2)
