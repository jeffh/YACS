from contextlib import contextmanager

from django.db import transaction
from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from json import loads


class ShortcutTestCase(TestCase):
    def get(self, url_name, *args, **kwargs):
        status = kwargs.pop('status_code', None)
        params = kwargs.pop('get', '')

        headers = kwargs.pop('headers', {})
        if kwargs.pop('ajax_request', False):
            headers['X_REQUESTED_WITH'] = 'XMLHttpRequest'
        headers = self._process_headers(headers)

        response = self.client.get(reverse(url_name, args=args, kwargs=kwargs) + params, **headers)
        if status is not None:
            self.assertEqual(response.status_code, status)
        return response

    def json_get(self, *args, **kwargs):
        prefix = kwargs.pop('prefix', '')
        response = self.get(*args, **kwargs)
        self.assertTrue(response.content.startswith(prefix))
        try:
            return loads(response.content[len(prefix):])
        except:
            print "Got:", response
            raise

    def post(self, url_name, *args, **kwargs):
        status = kwargs.pop('status_code', None)
        data = kwargs.pop("data", {})
        params = kwargs.pop('get', '')

        headers = kwargs.pop('headers', {})
        if kwargs.pop('ajax_request', False):
            headers['X_REQUESTED_WITH'] = 'XMLHttpRequest'
        headers = self._process_headers(headers)

        response = self.client.post(reverse(url_name, args=args, kwargs=kwargs) + params, data, **headers)
        if status is not None:
            self.assertEqual(response.status_code, status)
        return response

    def json_post(self, *args, **kwargs):
        prefix = kwargs.pop('prefix', '')
        response = self.post(*args, **kwargs)
        self.assertTrue(response.content.startswith(prefix))
        try:
            return loads(response.content[len(prefix):])
        except:
            print "Got:", response
            raise

    def _process_headers(self, kwargs):
        headers = {}
        for key, value in kwargs.items():
            if key.startswith('HTTP_'):
                headers[key.upper().replace('-', '_')] = value
            else:
                headers['HTTP_' + key.upper().replace('-', '_')] = value
        return headers
