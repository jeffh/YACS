from yacs.settings.base import *

DEBUG = True
TEMPLATE_DEBUG = DEBUG

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        'VERSION': CACHE_VERSION,
    }
}
