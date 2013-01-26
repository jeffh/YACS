from yacs.settings.base import *

DEBUG = True

DATABASES = {
    'default': {
        #'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'yacs.db',
        'USER': 'timetable',
        'PASSWORD': 'thereisn0sp00n',
        'HOST': 'localhost',
        'PORT': '',
        'OPTIONS': {
            #'autocommit': True,
        }
    }
}

INSTALLED_APPS += (
    'jasmine',
)
