from django.conf.urls.defaults import patterns, include, url

from api import views

api4 = dict(version=4)

id_or_ids = r'/(?P<id>[\d,]+)'
ext_or_slash = r'((/)|([\./](?P<ext>[a-z]+)))$'

urlpatterns = patterns('',
    url(r'^' + ext_or_slash, views.raw_data, {
            'version': 4,
            'data': {
                'objects': ('semesters', 'departments', 'courses', 'sections'),
                'supported_formats': ['json', 'xml', 'plist', 'bplist'],
                'default_format': 'json',
            },
        }, name='semesters'),
    url(r'^/semesters' + ext_or_slash, views.semesters, api4, name='semesters'),
    url(r'^/semesters/(?P<id>\d+)' + ext_or_slash, views.semesters, api4, name='semesters'),
    url(r'^/departments' + ext_or_slash, views.departments, api4, name='departments'),
    url(r'^/departments/(?P<id>\d+)' + ext_or_slash, views.departments, api4, name='departments'),
    url(r'^/courses' + ext_or_slash, views.courses, api4, name='courses'),
    url(r'^/courses/(?P<id>\d+)' + ext_or_slash, views.courses, api4, name='courses'),
    url(r'^/sections' + ext_or_slash, views.sections, api4, name='sections'),
    url(r'^/sections/(?P<id>\d+)' + ext_or_slash, views.sections, api4, name='sections'),
)
