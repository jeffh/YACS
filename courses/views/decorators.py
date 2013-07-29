import sys
from functools import wraps

from django.conf import settings
from django.http import HttpResponse, Http404
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.contrib.auth.decorators import login_required

__all__ = ['Renderer', 'login_required', 'staff_required']


def staff_required(fn):
    @login_required
    @wraps(fn)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_staff:
            raise PermissionDenied("You are not an admin")
        return fn(request, *args, **kwargs)
    return wrapper


class AlternativeResponse(Exception):
    def __init__(self, response):
        self.response = response


class Renderer(object):
    def __init__(self, **settings):
        self.settings = {
            'error_handler': self.handle_error,
            'template_prefix': '',
            'template_name': 'template.html',
            'context': {},
            'mimetype': None,
            'headers': {},
            'encoder': None,
            'posthook': None,
        }
        self.settings.update(settings)

    def __repr__(self):
        return "Renderer(settings=%r)" % (self.settings,)

    def __call__(self, **custom_settings):
        "Behaves like a decorator"
        def decorator(fn):
            @wraps(fn)
            def decorated(request, *args, **kwargs):
                settings_instance = {}
                settings_instance.update(self.settings)
                settings_instance.update(custom_settings)
                try:
                    result = fn(request, *args, **kwargs)
                    settings_instance.update(result)
                    if callable(settings_instance['posthook']):
                        settings_instance = settings_instance['posthook'](settings_instance, request, *args, **kwargs)
                    response = self.create_response(request, settings_instance)
                    return self.assign_headers(response, settings_instance['headers'])
                except AlternativeResponse as altresponse:
                    return altresponse.response
            decorated.raw_view = fn
            decorated.decorator = self
            return decorated
        return decorator

    def handle_error(self, error, traceback):
        if settings.DEBUG:
            raise (error, None, traceback)  # remove tuple, if this is broken
        raise Http404

    def extract_view(self, decorated_view, original=False):
        if not original:
            return decorated_view.raw_view
        v = decorated_view
        while hasattr(v, 'raw_view'):
            v = v.raw_view
        return v

    def assign_headers(self, response, headers):
        for name, value in headers.items():
            response[name] = value
        return response

    def process_context(self, context, encoder):
        if encoder is None:
            return context
        for key in context.keys():
            context[key] = encoder(context[key])
        return context

    def create_response(self, request, settings):
        context = self.process_context(settings['context'], settings['encoder'])
        full_template_path = settings['template_prefix'] + settings['template_name']
        return render_to_response(full_template_path,
                context,
                context_instance=RequestContext(request),
                mimetype=settings['mimetype'])
