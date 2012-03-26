import re

from django.contrib.sessions.middleware import SessionMiddleware as SessionMW
from django.contrib.auth.middleware import AuthenticationMiddleware as AuthMW
from django.contrib.messages.middleware import MessageMiddleware as MessageMW
from django.conf import settings

from debug_toolbar.middleware import DebugToolbarMiddleware as DebugToolbarMW


EXCLUDED = [
    re.compile(url) for url in getattr(settings, 'SESSION_EXCLUDED_URLS', [])
]


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


class SessionMiddleware(WrapRequestResponse, SessionMW):
    pass


class AuthenticationMiddleware(WrapRequestResponse, AuthMW):
    pass


class MessageMiddleware(WrapRequestResponse, MessageMW):
    pass


class DebugToolbarMiddleware(WrapRequestResponse, DebugToolbarMW):
    pass
