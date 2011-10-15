from base import relative

DATABASES = {
    'default': {
        'ENGINE': '{{ databases.default.engine }}',
        'NAME': '{{ databases.default.name }}',
        'USER': '{{ databases.default.user }}',
        'PASSWORD': '{{ databases.default.password }}',
        'HOST': '{{ databases.default.host }}',
        'PORT': '{{ databases.default.port }}',
        'OPTIONS': {
            'autocommit': True,
        }
    }
}

DEBUG = {% if DEBUG %}True{% else %}False{% endif %}
TEMPLATE_DEBUG = DEBUG

# Things that require change when debug is changed
DJANGO_LOGGING = relative('logs', 'django.log')

# ==== Django Debug Toolbar ====
INTERNAL_IPS = ('127.0.0.1',)

def debug_toolbar_callback(request):
    return (DEBUG and request.META['REMOTE_ADDR'] in INTERNAL_IPS) or request.user.is_staff

DEBUG_TOOLBAR_CONFIG = {
    'INTERCEPT_REDIRECTS': False,
    'SHOW_TOOLBAR_CALLBACK': debug_toolbar_callback,
    'HIDE_DJANGO_SQL': False,
}

STATIC_URL = '{{ STATIC_URL }}'

# URL prefix for admin static files -- CSS, JavaScript and images.
# Make sure to use a trailing slash.
# Examples: "http://foo.com/static/admin/", "/static/admin/".
ADMIN_MEDIA_PREFIX = STATIC_URL + 'admin/'
