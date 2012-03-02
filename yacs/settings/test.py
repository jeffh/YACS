from yacs.settings.base import BaseSettings

__all__ = ['settings']

settings = BaseSettings()

with settings as s:
    s.DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': '',
            'USER': '',
            'PASSWORD': '',
            'HOST': '',
            'PORT': '',
        }
    }
