from yacs.settings.base import *

DEBUG = True
TEMPLATE_DEBUG = DEBUG

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        'VERSION': CACHE_VERSION,
    }
}

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'yacsdb',
        'USER': 'yacs',
        'PASSWORD': 'yacs',
        'HOST': '127.0.0.1',
        'PORT': '5432',
    }
}
