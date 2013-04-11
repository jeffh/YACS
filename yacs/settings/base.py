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

ADMINS = (
    ('Jeff Hui', 'jeff@jeffhui.net'),
)
MANAGERS = ADMINS

DATABASES = {
    'default': dj_database_url.parse(
        os.environ.get('YACS_DATABASE_URL',
                       'sqlite:////' + os.path.abspath('yacs.db')))
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
    #'django.contrib.sessions.middleware.SessionMiddleware',
    'api.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    #'django.contrib.auth.middleware.AuthenticationMiddleware',
    #'django.contrib.messages.middleware.MessageMiddleware',
    #'debug_toolbar.middleware.DebugToolbarMiddleware',
    'api.middleware.AuthenticationMiddleware',
    'api.middleware.MessageMiddleware',
    'api.middleware.DebugToolbarMiddleware',
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
    'south',
    'django_extensions',
    'debug_toolbar',
    'pipeline',
    # local apps
    'courses',
    'scheduler',
    'api',
    'courses_viz',
)

FROM_EMAIL = "no-reply@yacs.me"
EMAIL_BACKEND = 'django.core.mail.backends.dummy.EmailBackend'

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
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': relative_path('..', 'access.log'),
            'formatter': 'default',
            'filters': ['require_debug_false'],
        },
        'file-error': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': relative_path('..', 'error.log'),
            'formatter': 'default',
            'filters': ['require_debug_false'],
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['null'],
            'propagate': True,
            'level': 'INFO',
        },
        'django.request': {
            'handlers': ['console', 'file-error'],
            'level': 'ERROR',
            'propagate': True,
        },
        #'django.request': {
        #    'handlers': ['mail_admins'],
        #    'level': 'ERROR',
        #    'propagate': True,
        #},
        'yacs': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },
    }
}

# === Memory ===
CACHE_VERSION = 1
CACHES = {
    #'default': {
    #    'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    #    'VERSION': s.CACHE_VERSION,
    #}
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


def debug_toolbar_callback(request):
    return not RUNNING_TESTS and request.user.is_staff

DEBUG_TOOLBAR_PANELS = (
    'debug_toolbar.panels.version.VersionDebugPanel',
    'debug_toolbar.panels.timer.TimerDebugPanel',
    'debug_toolbar.panels.settings_vars.SettingsVarsDebugPanel',
    'debug_toolbar.panels.headers.HeaderDebugPanel',
    'debug_toolbar.panels.request_vars.RequestVarsDebugPanel',
    'debug_toolbar.panels.template.TemplateDebugPanel',
    'debug_toolbar.panels.sql.SQLDebugPanel',
    'debug_toolbar.panels.signals.SignalDebugPanel',
    'debug_toolbar.panels.logger.LoggingPanel',
    #'debug_profiling.ProfilingPanel'
)

DEBUG_TOOLBAR_CONFIG = {
    'INTERCEPT_REDIRECTS': False,
    'SHOW_TOOLBAR_CALLBACK': debug_toolbar_callback,
    'HIDE_DJANGO_SQL': False,
}

# ==== Django-Robots App ====
#s.ROBOTS_CACHE_TIMEOUT = 60*60*24 # 24-hour cache of robots file

# ==== api ====
# which urls require no sessions. This saves us at least one DB query.
# this is a collection of regular expressions
SESSION_EXCLUDED_URLS = (
    r'^/api/',
)

# ==== django-pipeline ====
STATICFILES_STORAGE = 'pipeline.storage.PipelineStorage'
PIPELINE_COMPILERS = (
    'pipeline.compilers.coffee.CoffeeScriptCompiler',
    'pipeline.compilers.sass.SASSCompiler',
)

#s.PIPELINE_COFFEE_SCRIPT_BINARY = 'coffee'

#s.PIPELINE_SASS_BINARY = 'sass'
PIPELINE_SASS_ARGUMENTS = '--scss'

PIPELINE_CSS_COMPRESSOR = 'pipeline.compressors.yui.YUICompressor'
PIPELINE_JS_COMPRESSOR = 'pipeline.compressors.yui.YUICompressor'

PIPELINE_YUI_BINARY = 'java -jar lib/yuicompressor-2.4.7.jar'
PIPELINE_YUI_CSS_ARGUMENTS = '--type css'
PIPELINE_YUI_JS_ARGUMENTS = '--type js'

PIPELINE_CSS = {
    'base+320': {
        'source_filenames': (
            'css/style.css',
            'css/320.css',
        ),
        'extra_context': {'media': 'screen'},
        'output_filename': 'core.css',
    },
    '480': {
        'source_filenames': ('css/480.css',),
        'extra_context': {'media': 'only screen and (min-width: 480px)'},
        'output_filename': '480.css',
    },
    '768': {
        'source_filenames': ('css/768.css',),
        'extra_context': {'media': 'only screen and (min-width: 768px)'},
        'output_filename': '768.css',
    },
    'ie': {
        'source_filenames': ('css/ie.css',),
        'output_filename': 'ie.css',
    },
    'ie': {
        'source_filenames': ('css/print.css',),
        'extra_context': {'media': 'print'},
        'output_filename': 'print.css',
    },
}

PIPELINE_JS = {
    'libs': {
        'source_filenames': (
            'js/libs/sessionstorage.1.4.js',
            'js/libs/json2.js',
            'js/libs/history.js',
            'js/libs/history.adapter.jquery.js',
            'js/libs/underscore-1.3.1.js',
            'js/libs/backbone-0.9.2.js',
            'js/320nu.js',
        ),
        'output_filename': 'l.js',
    },
    'application': {
        'source_filenames': (
            'js/v3/utilities.coffee',
            'js/v3/time.coffee',
            'js/v3/jquery.ext.coffee',
            'js/v3/api.coffee',
            'js/v3/summarizer.coffee',
            'js/v3/liveform.coffee',
            'js/v3/storage.coffee',
            'js/v3/templates.coffee',
            'js/v3/application.coffee',
        ),
        'output_filename': 'a.js',
    },
    'specs': {
        'source_filenames': (
            'specs/utilities_spec.coffee',
            'specs/time_spec.coffee',
            'specs/jquery_ext_spec.coffee',
            'specs/api_spec.coffee',
            'specs/summarizer_spec.coffee',
            'specs/liveform_spec.coffee',
            'specs/storage_spec.coffee',
            'specs/templates_spec.coffee',
        ),
        'output_filename': 's.js',
    }
}
