"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from timetable.courses.models import *
from timetable.courses import utils

class CapitalizationTest(TestCase):
    def test_capitalization_for_all_lowercase(self):
        self.assertEqual(capitalized("foobar"), "Foobar")

    def test_capitalization_for_all_uppercase(self):
        self.assertEqual(capitalized("FOOBAR"), "Foobar")

    def test_capitalization_for_mixed_case(self):
        self.assertEqual(capitalized("fOoBaR"), "Foobar")

    def test_capitalization_for_letter(self):
        self.assertEqual(capitalized("a"), "A")

    def test_capitalization_for_blank(self):
        self.assertEqual(capitalized(""), "")

    def test_capitalization_spaces(self):
        self.assertEqual(capitalized("   "), "   ")

class OptionsTest(TestCase):
    def test_returning_a_generator(self):
        g = utils.options()
        self.assertEqual(g.next(), 1)
        self.assertEqual(g.next(), 2)
        self.assertEqual(g.next(), 4)
        self.assertEqual(g.next(), 8)
        self.assertEqual(g.next(), 16)
        self.assertEqual(g.next(), 32)
        # this generator is infinite...

    def test_returning_a_list(self):
        g = utils.options(6)
        self.assertEqual(g, [1, 2, 4, 8, 16, 32])

