from yacs.settings.base import settings

__all__ = ['settings']

with settings as s:
    s.DEBUG = True

    s.DATABASES = {
        'default': {
            #'ENGINE': 'django.db.backends.postgresql_psycopg2',
            #'NAME': 'yacs.db',
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

    s.INSTALLED_APPS += (
        'jasmine',
    )
