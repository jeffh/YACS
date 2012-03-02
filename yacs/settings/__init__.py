import os
import sys

from django.core.exceptions import ImproperlyConfigured

is_running_tests = 'test' in sys.argv
if is_running_tests:
    environment = 'test'
else:
    environment = os.environ.get('YACS_ENV', 'development')

if environment == 'development':
    from yacs.settings.development import settings
    #print 'using development'
elif environment == 'production':
    from yacs.settings.production import settings
    #print 'using production'
elif environment == 'test':
    from yacs.settings.test import settings
    #print 'using test'
else:
    raise ImproperlyConfigured('YACS_ENV environmental variable needs to be set, unless tests are running.')

settings.transfer(globals())

