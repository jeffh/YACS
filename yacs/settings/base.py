import os
import sys
from datetime import timedelta

__all__ = ['Settings']

class SettingsInterface(object):
    def __init__(self, settings_core):
        self.settings = settings_core

    def __getattr__(self, key):
        return self.settings[key]

    def __setattr__(self, key, value):
        if key not in ('settings', ):
            self.settings[key] = value
        else:
            super(SettingsInterface, self).__setattr__(key, value)

    def __getitem__(self, key):
        return self.settings[key]

    def __setitem__(self, key, value):
        self.settings[key] = value

    def keys(self):
        return self.settings.keys()

    def set_lazy(self, key, fn):
        def assign_key(settings):
            settings[key] = fn(settings)
        self.settings.lazy_fns.append(assign_key)

    def lazy_eval(self, fn):
        self.settings.lazy_fns.append(fn)

    def alias(self, key_src, key_dest, *more_key_dest):
        self.set_lazy(key_src, lambda s: key_dest)
        for key_dest in more_key_dest:
            self.set_lazy(key_src, lambda s: key_dest)

    def relative_path(self, *paths):
        return self.settings.relative_path(*paths)


class SettingsCore(object):
    def __init__(self):
        self.lazy_fns = []
        self.settings = {'RUNNING_TESTS': 'test' in sys.argv}
        self.init(SettingsInterface(self))

    def init(self, settings):
        pass # override by child

    def pretransfer(self):
        pass # override by child

    def relative_path(self, *paths):
        return os.path.normpath(os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', *paths))

    def __enter__(self):
        return SettingsInterface(self)

    def __exit__(self, type, instance, tb):
        pass

    def __getitem__(self, key):
        return self.settings[key]

    def __setitem__(self, key, value):
        self.settings[key] = value

    def __contains__(self, key):
        return key in self.settings

    def keys(self):
        return self.settings.keys()

    def extend(self, key, add_value):
        self.settings[key] += add_value

    def eval_lazy_values(self):
        setting_context = SettingsInterface(self)
        for fn in self.lazy_fns:
            fn(setting_context)
        self.lazy_fns = []

    def transfer(self, dictionary):
        self.eval_lazy_values()
        self.pretransfer()
        for key in self.keys():
            dictionary[key] = self.settings[key]

class BaseSettings(SettingsCore):
    DEBUG = True
    def init(self, settings):
        # include lib
        sys.path.insert(0, self.relative_path('..', 'lib'))

        settings.DEBUG = True
        settings.alias('DEBUG', 'TEMPLATE_DEBUG')

        settings.ADMINS = (
            ('Jeff Hui', 'huij@rpi.edu'),
        )
        settings.alias('ADMINS', 'MANAGERS')

        # Local time zone for this installation. Choices can be found here:
        # http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
        # although not all choices may be available on all operating systems.
        # On Unix systems, a value of None will cause Django to use the same
        # timezone as the operating system.
        # If running in a Windows environment this must be set to the same as your
        # system time zone.
        settings.TIME_ZONE = 'America/New_York'

        # Language code for this installation. All choices can be found here:
        # http://www.i18nguy.com/unicode/language-identifiers.html
        settings.LANGUAGE_CODE = 'en-us'

        settings.SITE_ID = 1

        # If you set this to False, Django will make some optimizations so as not
        # to load the internationalization machinery.
        settings.USE_I18N = True

        # If you set this to False, Django will not format dates, numbers and
        # calendars according to the current locale
        settings.USE_L10N = True

        # Absolute filesystem path to the directory that will hold user-uploaded files.
        # Example: "/home/media/media.lawrence.com/media/"
        settings.MEDIA_ROOT = settings.relative_path('uploads')

        # URL that handles the media served from MEDIA_ROOT. Make sure to use a
        # trailing slash.
        # Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
        settings.MEDIA_URL = '/uploads/'

        # Absolute path to the directory static files should be collected to.
        # Don't put anything in this directory yourself; store your static files
        # in apps' "static/" subdirectories and in STATICFILES_DIRS.
        # Example: "/home/media/media.lawrence.com/static/"
        settings.STATIC_ROOT = settings.relative_path('static', 'root')

        # URL prefix for static files.
        # Example: "http://media.lawrence.com/static/"
        settings.STATIC_URL = '/static/'

        # URL prefix for admin static files -- CSS, JavaScript and images.
        # Make sure to use a trailing slash.
        # Examples: "http://foo.com/static/admin/", "/static/admin/".
        settings.ADMIN_MEDIA_PREFIX = '/static/admin/'


        # List of finder classes that know how to find static files in
        # various locations.
        settings.STATICFILES_FINDERS = (
            'django.contrib.staticfiles.finders.FileSystemFinder',
            'django.contrib.staticfiles.finders.AppDirectoriesFinder',
        #    'django.contrib.staticfiles.finders.DefaultStorageFinder',
        )

        # Make this unique, and don't share it with anybody.
        settings.SECRET_KEY = 'ldbug$0pm8%@go!9yt+lg(@tn3yla3yd!x8nubld)e7ol-vdlu'

        # List of callables that know how to import templates from various sources.
        settings.TEMPLATE_LOADERS = (
            'django.template.loaders.filesystem.Loader',
            'django.template.loaders.app_directories.Loader',
        #     'django.template.loaders.eggs.Loader',
        )

        # api middleware allows session middleware to be optional for
        # specific urls. Other custom middleware simply respect the optional
        # session middleware
        settings.MIDDLEWARE_CLASSES = (
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

        settings.TEMPLATE_CONTEXT_PROCESSORS = (
            "django.contrib.auth.context_processors.auth",
            "django.core.context_processors.debug",
            "django.core.context_processors.i18n",
            "django.core.context_processors.media",
            "django.core.context_processors.static",
            "django.contrib.messages.context_processors.messages",
            "django.core.context_processors.request",
        )

        settings.ROOT_URLCONF = 'yacs.urls'

        settings.TEMPLATE_DIRS = (
            # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
            # Always use forward slashes, even on Windows.
            # Don't forget to use absolute paths, not relative paths.
            settings.relative_path('templates'),
        )

        settings.INSTALLED_APPS = (
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
            'robots',
            'debug_toolbar',
            'django_bcrypt',
            # local apps
            'courses',
            'scheduler',
            'api',
        )

        # A sample logging configuration. The only tangible logging
        # performed by this configuration is to send an email to
        # the site admins on every HTTP 500 error.
        # See http://docs.djangoproject.com/en/dev/topics/logging for
        # more details on how to customize your logging configuration.
        settings.LOGGING = {
            'version': 1,
            'disable_existing_loggers': True,
            'formatters':{
                'default': {
                    'format': '[%(asctime)s] %(levelname)s (%(module)s): %(message)s'
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
                #'file': {
                #    'level': 'DEBUG',
                #    'class': 'logging.FileHandler',
                #    'filename': settings.relative_path('django.log'),
                #    'formatter': 'default',
                #},
                'mail_admins': {
                    'level': 'ERROR',
                    'class': 'django.utils.log.AdminEmailHandler',
                },
            },
            'loggers': {
                'django': {
                    'handlers':['null'],
                    'propagate': True,
                    'level':'INFO',
                },
                'django.request': {
                    'handlers': ['mail_admins'],
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

        # ==== API App ====
        # Return queries executed in json, only works when DEBUG = True
        settings.API_RETURN_QUERIES = True

        # ==== Courses App ====
        # full module path to the function that does all the importing
        settings.COURSES_COLLEGE_PARSER = 'courses.bridge.rpi.import_data'

        # prints warnings to stdout about possible excuting extra queries
        @settings.lazy_eval
        def set_courses_query_warning(settings):
            settings.COURSES_WARN_EXTRA_QUERIES = not settings.DEBUG and not settings.RUNNING_TESTS

        # ==== Scheduler App ====
        settings.SCHEDULER_ICAL_PRODUCT_ID = '-//Jeff Hui//YACS Export 1.0//EN'
        # maximum number of sections to compute schedules for.
        # more sections means it takes longer to compute. Until we have
        # a good caching strategy, this is a hard upper bound. Default is 60.
        settings.SCHEDULER_SECTION_LIMIT = 60

        # ==== Django BCrypt ====
        # The number of rounds determines the complexity of the bcrypt algorithm.
        # The work factor is 2**log_rounds, and the default is 12
        #
        # This setting can be changed at any time without invalidating previously-generated hashes.
        settings.BCRYPT_LOG_ROUNDS = 12

        # ==== Django Debug Toolbar ====
        settings.INTERNAL_IPS = ('127.0.0.1',)

        def debug_toolbar_callback(request):
            return settings.RUNNING_TESTS and request.user.is_staff

        settings.DEBUG_TOOLBAR_PANELS = (
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

        settings.DEBUG_TOOLBAR_CONFIG = {
            'INTERCEPT_REDIRECTS': False,
            'SHOW_TOOLBAR_CALLBACK': debug_toolbar_callback,
            'HIDE_DJANGO_SQL': False,
        }

        # ==== Django-Robots App ====
        #settings.ROBOTS_CACHE_TIMEOUT = 60*60*24 # 24-hour cache of robots file

        # ==== Django-Jasmine ====
        settings.JASMINE_TEST_DIRECTORY = settings.relative_path('static', 'jasmine')

        # ==== api ====
        # which urls require no sessions. This saves us at least one DB query.
        # this is a collection of regular expressions
        settings.SESSION_EXCLUDED_URLS = (
            r'^/api/',
        )

        # ==== devserver ====
        @settings.lazy_eval
        def devserver_if_not_testing(settings):
            if not settings.RUNNING_TESTS:
                settings.DEVSERVER_AUTO_PROFILE = settings.DEBUG
                settings.DEVSERVER_MODULES = (
                    'devserver.modules.sql.SQLRealTimeModule',
                    'devserver.modules.sql.SQLSummaryModule',
                    'devserver.modules.profile.ProfileSummaryModule',
                )


