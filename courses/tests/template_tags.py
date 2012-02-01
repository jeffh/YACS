from datetime import time

from django.test import TestCase
from mock import Mock

from courses.templatetags.courses import remove_zero_prefix, get, display_period, dow_short
from courses.tests.factories import PeriodFactory



__all__ = ['RemoveZeroPrefixTest', 'GetTest', 'DowShortTest']


class RemoveZeroPrefixTest(TestCase):
    def test_remove_zero_prefix_with_zero_prefix(self):
        self.assertEqual(remove_zero_prefix('01'), '1')

    def test_remove_zero_prefix_with_no_zero_prefix(self):
        self.assertEqual(remove_zero_prefix('21'), '21')


class GetTest(TestCase):
    def test_get_with_object(self):
        obj = Mock()
        obj.lol = 342
        self.assertEqual(get(obj, 'lol'), 342)

    def test_get_with_index(self):
        obj = [1, 2, 3]
        self.assertEqual(get(obj, 1), 2)

    def test_get_with_key_index(self):
        obj = {'lol': 'rofl'}
        self.assertEqual(get(obj, 'lol'), 'rofl')

    def test_get_should_return_None_on_invalid_access(self):
        obj = []
        self.assertEqual(get(obj, 4), None)


class DisplayPeriodTest(TestCase):
    def test_display_period_of_4_to_5(self):
        period = PeriodFactory.build(start=time(hour=4), end=time(hour=5))
        self.assertEqual(display_period(period), '4:00-5:00 am')

    def test_display_period_with_minutes(self):
        period = PeriodFactory.build(start=time(hour=4), end=time(hour=4, minute=50))
        self.assertEqual(display_period(period), '4:00-4:50 am')

    def test_display_period_in_the_afternoon(self):
        period = PeriodFactory.build(start=time(hour=14), end=time(hour=14, minute=50))
        self.assertEqual(display_period(period), '2:00-2:50 pm')

    def test_display_period_from_morning_to_afternoon(self):
        period = PeriodFactory.build(start=time(hour=10), end=time(hour=14, minute=50))
        self.assertEqual(display_period(period), '10:00 am-2:50 am')


class DowShortTest(TestCase):
    def test_monday(self):
        self.assertEqual(dow_short('Monday'), 'Mo')

    def test_tuesday(self):
        self.assertEqual(dow_short('Tuesday'), 'Tu')

    def test_wednesday(self):
        self.assertEqual(dow_short('Wednesday'), 'We')

    def test_thursday(self):
        self.assertEqual(dow_short('Thursday'), 'Th')

    def test_friday(self):
        self.assertEqual(dow_short('Friday'), 'Fr')

    def test_saturday(self):
        self.assertEqual(dow_short('Saturday'), 'Sa')

    def test_sunday(self):
        self.assertEqual(dow_short('Sunday'), 'Su')

    def test_return_None_otherwise(self):
        self.assertEqual(dow_short('foobar'), None)

    def test_convert_list(self):
        collection = ['Monday', 'Wednesday', 'Thursday']
        self.assertEqual(dow_short(collection), ('Mo', 'We', 'Th'))

    def test_convert_tuple(self):
        collection = ('Monday', 'Wednesday', 'Thursday')
        self.assertEqual(dow_short(collection), ('Mo', 'We', 'Th'))

