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

ext_re = r'\.(?P<ext>[a-z]+)$'

urlpatterns = patterns('',
    url(r'^/$', views.raw_data, meta, name='metadata'),
    url(r'^' + ext_re, views.raw_data, meta, name='metadata'),

    url(r'^/semesters/$', views.semesters, api4, name='semesters'),
    url(r'^/semesters' + ext_re, views.semesters, api4, name='semesters'),
    url(r'^/semesters/(?P<id>\d+)/$', views.semesters, api4, name='semesters'),
    url(r'^/semesters/(?P<id>\d+)' + ext_re, views.semesters, api4, name='semesters'),

    url(r'^/departments/$', views.departments, api4, name='departments'),
    url(r'^/departments' + ext_re, views.departments, api4, name='departments'),
    url(r'^/departments/(?P<id>\d+)/$', views.departments, api4, name='departments'),
    url(r'^/departments/(?P<id>\d+)' + ext_re, views.departments, api4, name='departments'),

    url(r'^/courses/$', views.courses, api4, name='courses'),
    url(r'^/courses' + ext_re, views.courses, api4, name='courses'),
    url(r'^/courses/(?P<id>\d+)/$', views.courses, api4, name='courses'),
    url(r'^/courses/(?P<id>\d+)' + ext_re, views.courses, api4, name='courses'),

    url(r'^/sections/$', views.sections, api4, name='sections'),
    url(r'^/sections' + ext_re, views.sections, api4, name='sections'),
    url(r'^/sections/(?P<id>\d+)/$', views.sections, api4, name='sections'),
    url(r'^/sections/(?P<id>\d+)' + ext_re, views.sections, api4, name='sections'),

    url(r'^/conflicts/$', views.section_conflicts, api4, name='conflicts'),
    url(r'^/conflicts' + ext_re, views.section_conflicts, api4, name='conflicts'),
    url(r'^/conflicts/(?P<id>\d+)/$', views.section_conflicts, api4, name='conflicts'),
    url(r'^/conflicts/(?P<id>\d+)' + ext_re, views.section_conflicts, api4, name='conflicts'),

    url(r'^/schedules/$', views.schedules, api4, name='schedules'),
    url(r'^/schedules' + ext_re, views.schedules, api4, name='schedules'),
    url(r'^/schedules/(?P<slug>[A-Za-z0-9_-]+)/$', views.schedules, api4, name='schedules'),
    url(r'^/schedules/(?P<slug>[A-Za-z0-9_-]+)' + ext_re, views.schedules, api4, name='schedules'),
)
