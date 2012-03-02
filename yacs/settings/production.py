from yacs.settings.base import BaseSettings
import os
import json

__all__ = ['settings']

settings = BaseSettings()

with open(os.environ.get('YACS_SETTINGS', settings.relative_path('settings', 'production.json')), 'r') as handle:
    data = json.loads(handle.read())

with settings as s:
    s.DEBUG = False

    @s.lazy_eval
    def debug_toolbar_configs(s):
        def debug_toolbar_callback(request):
            return request.user.is_staff

        s.DEBUG_TOOLBAR_CONFIG = {
            'INTERCEPT_REDIRECTS': False,
            'SHOW_TOOLBAR_CALLBACK': debug_toolbar_callback,
            'HIDE_DJANGO_SQL': s.DEBUG
        }

    s.STATIC_URL = data['static_url']
    s.DATABASES = data['databases']

    @s.lazy_eval
    def set_admin_media(s):
        s.ADMIN_MEDIA_PREFIX = s.STATIC_URL + 'admin/'
