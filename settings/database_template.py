
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