import re

from django.contrib.sessions.middleware import SessionMiddleware as OriginalSessionMiddleware
from django.contrib.auth.middleware import AuthenticationMiddleware as OriginalAuthenticationMiddleware
from django.contrib.messages.middleware import MessageMiddleware as OriginalMessageMiddleware
from django.conf import settings

from  debug_toolbar.middleware import DebugToolbarMiddleware as OriginalDebugToolbarMiddleware


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
        return getattr(super(WrapRequestResponse, self),
                'process_response',
                lambda req, rep: response)(request, response)

class SessionMiddleware(WrapRequestResponse, OriginalSessionMiddleware):
    pass

class AuthenticationMiddleware(WrapRequestResponse, OriginalAuthenticationMiddleware):
    pass

class MessageMiddleware(WrapRequestResponse, OriginalMessageMiddleware):
    pass

class DebugToolbarMiddleware(WrapRequestResponse, OriginalDebugToolbarMiddleware):
    pass
