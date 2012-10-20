import os
import sys

from django.core.exceptions import ImproperlyConfigured


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
