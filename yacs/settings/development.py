from yacs.settings.base import *

DEBUG = True
TEMPLATE_DEBUG = DEBUG

STATICFILES_DIRS += (relative_path('static', 'specs'), )
