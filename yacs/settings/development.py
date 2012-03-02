from yacs.settings.base import BaseSettings

__all__ = ['settings']

settings = BaseSettings()

with settings as s:
    s.DEBUG = True

    s.MIDDLEWARE_CLASSES += (
        'devserver.middleware.DevServerMiddleware',
    )

    @s.lazy_eval
    def debug_install_apps(s):
        if s.DEBUG:
            s.INSTALLED_APPS += (
                'django_jasmine',
                'devserver',
            )

    s.DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': 'yacs',
            'USER': 'timetable',
            'PASSWORD': 'thereisn0sp00n',
            'HOST': 'localhost',
            'PORT': '',
            'OPTIONS': {
                'autocommit': True,
            }
        }
    }
