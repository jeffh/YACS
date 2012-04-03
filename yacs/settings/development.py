from yacs.settings.base import settings

__all__ = ['settings']

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
<<<<<<< HEAD
            'NAME': 'mydata',
            'USER': 'postgreuser',
            'PASSWORD': 'postgre',
=======
            'NAME': 'yacs',
            'USER': 'timetable',
            'PASSWORD': 'thereisn0sp00n',
>>>>>>> 923dc7751367ed6f1b06f49f519072b367b8e625
            'HOST': 'localhost',
            'PORT': '',
            'OPTIONS': {
                'autocommit': True,
            }
        }
    }
