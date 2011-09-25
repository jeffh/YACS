from django.test import TestCase
from django.core.urlresolvers import reverse

class ShortcutTestCase(TestCase):
    def get(self, url_name, *args, **kwargs):
        status = kwargs.pop('status_code', None)
        params = kwargs.pop('get', '')
        response = self.client.get(reverse(url_name, args=args, kwargs=kwargs) + params)
        if status is not None:
            self.assertEqual(response.status_code, status)
        return response

    def post(self, url_name, *args, **kwargs):
        status = kwargs.pop('status_code', None)
        data = kwargs.pop("data", None)
        params = kwargs.pop('get', '')
        response = self.client.post(reverse(url_name, args=args, kwargs=kwargs) + params, data)
        if status is not None:
            self.assertEqual(response.status_code, status)
        return response