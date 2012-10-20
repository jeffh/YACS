from yacs.settings.base import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': '',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}

# === django-pipeline ===
STATICFILES_STORAGE = 'pipeline.storage.PipelineStorage'
