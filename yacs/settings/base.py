import os
import sys
from datetime import timedelta
import dj_database_url

# To work with pypy
try:
    from psycopg2ct import compat
    compat.register()
except ImportError:
    pass


def relative_path(*path):
    return os.path.abspath(os.path.join(os.path.dirname(__file__), '..', *path))

# include lib
sys.path.insert(0, relative_path('..', 'lib'))

RUNNING_TESTS = 'test' in sys.argv
DEBUG = False
TEMPLATE_DEBUG = DEBUG

# it's ok, we don't send emails
ALLOWED_HOSTS = ['*']

ADMINS = (
    ('Jeff Hui', 'jeff@jeffhui.net'),
)
MANAGERS = ADMINS

DATABASES = {
    'default': dj_database_url.parse(
        os.environ.get('YACS_DATABASE_URL',
                       os.environ.get('DATABASE_URL',
                                      'sqlite:////' + os.path.abspath('yacs.db'))))
}

TEST_RUNNER = 'django.test.runner.DiscoverRunner'

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
MEDIA_ROOT = relative_path('uploads')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/uploads/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = relative_path('static', 'root')

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or
    # "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    relative_path('static', 'angular'),
    relative_path('static', 'global'),
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
)

PASSWORD_HASHERS = (
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.SHA1PasswordHasher',
)

# api middleware allows session middleware to be optional for
# specific urls. Other custom middleware simply respect the optional
# session middleware
MIDDLEWARE_CLASSES = (
    'django.middleware.gzip.GZipMiddleware',
    'django.middleware.common.CommonMiddleware',
    'api.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'api.middleware.AuthenticationMiddleware',
    'api.middleware.MessageMiddleware',
    # 'api.middleware.DebugToolbarMiddleware',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.contrib.messages.context_processors.messages",
    "django.core.context_processors.request",
)

ROOT_URLCONF = 'yacs.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    relative_path('templates'),
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',
    # django admin
    'django.contrib.admin',
    'django.contrib.admindocs',
    # third-party apps
    'django_extensions',
    'debug_toolbar',
    'pipeline',
    'gunicorn',
    'taggit',
    'colorful',
    # local apps
    'courses',
    'scheduler',
    'api',
    'courses_viz',
)

FROM_EMAIL = "no-reply@yacs.me"
EMAIL_BACKEND = 'django.core.mail.backends.dummy.EmailBackend'

SOUTH_MIGRATION_MODULES = {
    'taggit': 'taggit.south_migrations',
}

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            'format': '[%(asctime)s] %(levelname)s (%(module)s): %(message)s'
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
    },
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'django.utils.log.NullHandler',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'default',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['null'],
            'propagate': True,
            'level': 'INFO',
        },
        'django.request': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': True,
        },
        'yacs': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
    }
}

# === Memory ===
CACHE_VERSION = 1
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'VERSION': CACHE_VERSION,
    }
}

# ==== API App ====
# Return queries executed in json, only works when DEBUG = True
API_RETURN_QUERIES = True

# ==== Courses App ====
# full module path to the function that does all the importing
COURSES_COLLEGE_PARSER = 'courses.bridge.rpi.import_data'

# prints warnings to stdout about possible excuting extra queries
COURSES_WARN_EXTRA_QUERIES = not DEBUG and not RUNNING_TESTS

# ==== Scheduler App ====
SCHEDULER_ICAL_PRODUCT_ID = '-//Jeff Hui//YACS Export 1.0//EN'
# maximum number of sections to compute schedules for.
# more sections means it takes longer to compute. Until we have
# a good caching strategy, this is a hard upper bound. Default is 60.
SCHEDULER_SECTION_LIMIT = 60

# ==== Django Debug Toolbar ====
INTERNAL_IPS = ('127.0.0.1',)

DEBUG_TOOLBAR_PATCH_SETTINGS = False
DEBUG_TOOLBAR_CONFIG = {
    'INTERCEPT_REDIRECTS': False,
}

# ==== api ====
# which urls require no sessions. This saves us at least one DB query.
# this is a collection of regular expressions
SESSION_EXCLUDED_URLS = (
    r'^/api/',
)

# ==== django-pipeline ====
STATICFILES_STORAGE = 'pipeline.storage.PipelineStorage'

PIPELINE_CSS_COMPRESSOR = 'pipeline.compressors.yui.YUICompressor'
PIPELINE_JS_COMPRESSOR = 'pipeline.compressors.yui.YUICompressor'

PIPELINE_YUI_BINARY = 'lib/yuicompressor'
PIPELINE_YUI_CSS_ARGUMENTS = '--type css'
PIPELINE_YUI_JS_ARGUMENTS = '--type js'

PIPELINE_CLOSURE_BINARY = 'lib/closure'
PIPELINE_CLOSURE_ARGUMENTS = '--language_in=ECMASCRIPT5 --warning_level QUIET --third_party'

PIPELINE_CSS = {
    'angular': {
        'source_filenames': (
            'v4/css/reset.css',
            'v4/css/core.css',
            'v4/css/course_list.css',
            'v4/css/catalog.css',
            'v4/css/dept_list.css',
            'v4/css/schedules.css',
        ),
        'extra_context': {'media': 'screen,print'},
        'output_filename': 'ang.css',
    },
    'print': {
        'source_filenames': (
            'v4/css/reset.css',
            'v4/css/print.css',
        ),
        'extra_context': {'media': 'print'},
        'output_filename': 'print.css',
    },
}

PIPELINE_JS = {
    'angular': {
        'source_filenames': (
            'v4/js/lib/jquery.js',
            'v4/js/lib/angularjs/angular.min.js',
            'v4/js/lib/angularjs/angular-route.js',
            'v4/js/lib/angularjs/angular-cookies.js',
            'v4/js/lib/underscore.js',
            'v4/js/lib/angulartics/angulartics.min.js',
            'v4/js/lib/angulartics/angulartics-google-analytics.min.js',
            'v4/js/Application.js',
            'v4/js/Utils.js',
            'v4/js/DelayTrigger.js',
            'v4/js/Constants.js',
            'v4/js/Worker.js',
            'v4/js/worker/Namespace.js',
            'v4/js/worker/Utils.js',
            'v4/js/worker/ScheduleValidator.js',
            'v4/js/directives/schedule_block.js',
            'v4/js/domain/ModelFactory.js',
            'v4/js/domain/Tagger.js',
            'v4/js/domain/CourseFetcher.js',
            'v4/js/domain/CourseSearch.js',
            'v4/js/domain/ScheduleValidator.js',
            'v4/js/domain/Conflictor.js',
            'v4/js/domain/APIClient.js',
            'v4/js/domain/models/Semester.js',
            'v4/js/domain/models/Course.js',
            'v4/js/domain/models/Department.js',
            'v4/js/domain/models/Time.js',
            'v4/js/domain/models/SectionTime.js',
            'v4/js/domain/models/Section.js',
            'v4/js/domain/models/Conflict.js',
            'v4/js/domain/models/SavedSelection.js',
            'v4/js/domain/models/Selection.js',
            'v4/js/domain/models/SchedulePresenter.js',
            'v4/js/controllers/RootController.js',
            'v4/js/controllers/FooterController.js',
            'v4/js/controllers/NavigationController.js',
            'v4/js/controllers/SearchController.js',
            'v4/js/controllers/SearchResultsController.js',
            'v4/js/controllers/DepartmentController.js',
            'v4/js/controllers/CatalogController.js',
            'v4/js/controllers/IndexController.js',
            'v4/js/controllers/SelectionController.js',
        ),
        'output_filename': 'app.js'
    },
}
