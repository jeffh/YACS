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
            'NAME': 'mydata',
            'USER': 'postgreuser',
            'PASSWORD': 'postgre',
            'HOST': 'localhost',
            'PORT': '',
            'OPTIONS': {
                'autocommit': True,
            }
        }
    }
