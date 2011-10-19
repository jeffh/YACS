from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

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

    def set_session(self, *dicts, **kwargs):
        # bug: https://code.djangoproject.com/ticket/11475
        # we need to log in to get around this
        if not User.objects.filter(email='foo@foo.com').exists():
            User.objects.create_user(email='foo@foo.com', username='anon', password='bugme')
        self.client.login(username='anon', password='bugme')
        self.client.get('/')
        session = self.client.session
        for dic in dicts + (kwargs,):
            for key, value in dic.items():
                session[key] = value
        session.save()
        return session
