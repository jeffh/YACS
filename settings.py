# Django settings for timetable project.
import os
import sys
import djcelery
from datetime import timedelta
from celery.schedules import schedule

# setup
relative = lambda *x: os.path.join(os.path.abspath(os.path.dirname(__file__)), *x)

if relative('lib') not in sys.path:
    sys.path.append(relative('lib'))

djcelery.setup_loader()

# end setup

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Jeff Hui', 'huij@rpi.edu'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'sqlite3.db',                      # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/New_York'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = relative('uploads')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/uploads/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = relative('static', 'cache')

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# URL prefix for admin static files -- CSS, JavaScript and images.
# Make sure to use a trailing slash.
# Examples: "http://foo.com/static/admin/", "/static/admin/".
ADMIN_MEDIA_PREFIX = '/static/admin/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    relative('static', 'global')
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'ldbug$0pm8%@go!9yt+lg(@tn3yla3yd!x8nubld)e7ol-vdlu'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

ROOT_URLCONF = 'timetable.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    relative('templates'),
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # django admin
    'django.contrib.admin',
    'django.contrib.admindocs',
    # third-party apps
    'south',
    'django_extensions',
    'djcelery',
    'django_bcrypt',
    # local apps
    'timetable.courses',
    'timetable.scheduler',
)

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

# ==== CELERY CONFIG ====

# amqplib, pika, redis, beanstalk, sqlalchemy, django, mongodb, couchdb
BROKER_BACKEND = 'redis'
BROKER_HOST = "localhost"
BROKER_PORT = 6379
BROKER_VHOST = '0'
#BROKER_USER = "django"
#BROKER_PASSWORD = "django_development"
#BROKER_VHOST = "django_vhost"

# disables async results
CELERY_IGNORE_RESULT = False
# database, cache, mongodb, redis, tyrant, or amqp
CELERY_RESULT_BACKEND = "redis"
# configure redis backend
CELERY_REDIS_HOST = BROKER_HOST
CELERY_REDIS_PORT = BROKER_PORT
CELERY_REDIS_DB = 0
# when results are automatically deleted?
CELERY_TASK_RESULT_EXPIRES = timedelta(days=7)

#CELERY_IMPORTS = () # full module paths to tasks.py
# Worker settings
# If you're doing mostly I/O you can have more processes,
# but if mostly spending CPU, try to keep it close to the
# number of CPUs on your machine. If not set, the number of CPUs/cores
# available will be used.
CELERYD_CONCURRENCY = 1

CELERYBEAT_SCHEDULER = 'djcelery.schedulers.DatabaseScheduler'

# periodic schedules / cron jobs
CELERYBEAT_SCHEDULE = {
    # follows periodic intervals defined in feeds, so hitting this tasks as
    # a lot won't actually hit each feed.
    'source-checker': {
        'task': 'source.tasks.update_sources',
        'schedule': schedule(timedelta(minutes=1)),
    },
}

# ==== Django BCrypt ====
# The number of rounds determines the complexity of the bcrypt algorithm.
# The work factor is 2**log_rounds, and the default is 12
#
# This setting can be changed at any time without invalidating previously-generated hashes.
BCRYPT_LOG_ROUNDS = 12
