import os
import sys

from django.core.exceptions import ImproperlyConfigured

if 'ENV_DIR' in os.environ:
    print 'Detected buildpack environment. Loading environment vars from', os.environ['ENV_DIR']
    keys = (
        'YACS_ENV',
        'YACS_SECRET_KEY',
        'YACS_DATABASE_URL',
        'YACS_DISABLE_FILE_SYSTEM_LOGGING',
        'DATABASE_URL',
        'MEMCACHIER_SERVERS',
        'MEMCACHIER_USERNAMAE',
        'MEMCACHIER_PASSWORD',
        'MEMCACHE_SERVERS',
        'MEMCACHE_USERNAMAE',
        'MEMCACHE_PASSWORD',
    )
    for key in keys:
        os.environ[key] = open(os.path.join(os.environ['ENV_DIR'], key), 'r').read()


is_running_tests = 'test' in sys.argv
if is_running_tests:
    environment = 'test'
else:
    environment = os.environ.get('YACS_ENV', 'development')

if environment == 'development':
    from yacs.settings.development import *
    print 'Loading Development Environment...'
elif environment == 'production':
    from yacs.settings.production import *
    print 'Loading Production Environment...'
elif environment == 'test':
    from yacs.settings.test import *
    print 'Loading Test Environment...'
else:
    raise ImproperlyConfigured('YACS_ENV environmental variable needs to be set to development, test, or production - unless tests are running.')
