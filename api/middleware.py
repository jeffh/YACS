import re

import django.contrib.sessions.middleware
import django.contrib.auth.middleware
import django.contrib.messages.middleware
from django.conf import settings

import debug_toolbar.middleware


EXCLUDED = [re.compile(url) for url in getattr(settings, 'SESSION_EXCLUDED_URLS', [])]

def is_excluded(path):
    for regexp in EXCLUDED:
        if regexp.search(path):
            return True
    return False

class WrapRequestResponse(object):
    def process_request(self, request):
        if is_excluded(request.path_info):
            return None
        return super(WrapRequestResponse, self).process_request(request)

    def process_response(self, request, response):
        if is_excluded(request.path_info):
            return response
        return getattr(super(WrapRequestResponse, self), 'process_response', lambda req, rep: response)(request, response)

class SessionMiddleware(WrapRequestResponse, django.contrib.sessions.middleware.SessionMiddleware):
    pass

class AuthenticationMiddleware(WrapRequestResponse, django.contrib.auth.middleware.AuthenticationMiddleware):
    pass

class MessageMiddleware(WrapRequestResponse, django.contrib.messages.middleware.MessageMiddleware):
    pass

class DebugToolbarMiddleware(WrapRequestResponse, debug_toolbar.middleware.DebugToolbarMiddleware):
    pass
