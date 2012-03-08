from django.conf.urls.defaults import patterns, include, url

from api import views

api4 = dict(version=4)
meta = {
    'version': api4['version'],
    'data': {
        'objects': ('semesters', 'departments', 'courses', 'sections'),
        'supported_formats': ['json', 'xml', 'plist', 'bplist'],
        'default_format': 'json',
    },
}

urlpatterns = patterns('',
    url(r'^/$', views.raw_data, meta, name='metadata'),
    url(r'^\.(?P<ext>[a-z]+)$', views.raw_data, meta, name='metadata'),

    url(r'^/semesters/$', views.semesters, api4, name='semesters'),
    url(r'^/semesters\.(?P<ext>[a-z]+)$', views.semesters, api4, name='semesters'),
    url(r'^/semesters/(?P<id>\d+)/$', views.semesters, api4, name='semesters'),
    url(r'^/semesters/(?P<id>\d+)\.(?P<ext>[a-z]+)$', views.semesters, api4, name='semesters'),
    url(r'^/departments/$', views.departments, api4, name='departments'),
    url(r'^/departments\.(?P<ext>[a-z]+)$', views.departments, api4, name='departments'),
    url(r'^/departments/(?P<id>\d+)/$', views.departments, api4, name='departments'),
    url(r'^/departments/(?P<id>\d+)\.(?P<ext>[a-z]+)$', views.departments, api4, name='departments'),
    url(r'^/courses/$', views.courses, api4, name='courses'),
    url(r'^/courses/(?P<id>\d+)/$', views.courses, api4, name='courses'),
    url(r'^/courses/(?P<id>\d+)\.(?P<ext>[a-z]+)$', views.courses, api4, name='courses'),
    url(r'^/sections/$', views.sections, api4, name='sections'),
    url(r'^/sections/(?P<id>\d+)/$', views.sections, api4, name='sections'),
    url(r'^/sections/(?P<id>\d+)\.(?P<ext>[a-z]+)$', views.sections, api4, name='sections'),
)

