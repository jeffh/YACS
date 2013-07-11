from yacs.settings.base import *
import os
import json
import dj_database_url

DEBUG = False
TEMPLATE_DEBUG = DEBUG
COURSES_WARN_EXTRA_QUERIES = not DEBUG and not RUNNING_TESTS
STATICFILES_STORAGE = 'pipeline.storage.PipelineCachedStorage'

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
        'VERSION': CACHE_VERSION,
    },
}

LOGGING['handlers']['file']['filename'] = '/www/yacs/logs/django.log'


def debug_toolbar_callback(request):
    return False

DEBUG_TOOLBAR_CONFIG = {
    'INTERCEPT_REDIRECTS': False,
    'SHOW_TOOLBAR_CALLBACK': debug_toolbar_callback,
    'HIDE_DJANGO_SQL': DEBUG
}

STATIC_URL = '/static/'

SECRET_KEY = os.environ['YACS_SECRET_KEY']

TEMPLATE_LOADERS = (
    ('django.template.loaders.cached.Loader', (
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
    )),
)

DEBUG_TOOLBAR_PANELS = (
    'debug_toolbar.panels.version.VersionDebugPanel',
    'debug_toolbar.panels.timer.TimerDebugPanel',
    'debug_toolbar.panels.settings_vars.SettingsVarsDebugPanel',
    'debug_toolbar.panels.headers.HeaderDebugPanel',
    'debug_toolbar.panels.request_vars.RequestVarsDebugPanel',
    'debug_toolbar.panels.template.TemplateDebugPanel',
    #'debug_toolbar.panels.sql.SQLDebugPanel',
    'debug_toolbar.panels.signals.SignalDebugPanel',
    'debug_toolbar.panels.logger.LoggingPanel',
    #'debug_profiling.ProfilingPanel'
)

#EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
#FROM_EMAIL = os.environ.get('YACS_EMAIL_FROM', 'robot@yacs.me')
#EMAIL_USE_TLS = os.environ.get('YACS_EMAIL_USE_TLS', 'yes').lower() in ['y', 'yes', 'true', 't', 'on']
#EMAIL_HOST = os.environ['YACS_EMAIL_HOST']
#EMAIL_USER = os.environ['YACS_EMAIL_USER']
#EMAIL_PASS = os.environ['YACS_EMAIL_PASS']
#EMAIL_PORT = int(os.environ.get('YACS_EMAIL_PORT', 587))
