from yacs.settings.base import *

DEBUG = True
TEMPLATE_DEBUG = DEBUG

STATICFILES_DIRS += (relative_path('static', 'specs'), )
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        'VERSION': CACHE_VERSION,
    }
}
