from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView

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

urlpatterns = patterns(
    '',
    url(r'^/$', views.raw_data, meta, name='metadata'),
    url(r'^' + ext_re, views.raw_data, meta, name='metadata'),

    url(r'^/docs/$', views.docs, dict(template_name='api/4/docs.html'), name='docs'),

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

    # not official API... this is actually deprecated and may
    # be removed at any point
    url(r'^/schedules/$', views.schedules, api4, name='schedules'),
    url(r'^/schedules' + ext_re, views.schedules, api4, name='schedules'),
    url(r'^/schedules/(?P<id>\d+)/$', views.schedules, api4, name='schedules'),
    url(r'^/schedules/(?P<id>\d+)' + ext_re, views.schedules, api4, name='schedules'),
    url(r'^/schedules/selection/(?P<id>\d+)/$', views.selections, api4, name='selection'),
    url(r'^/schedules/selection/(?P<id>\d+)' + ext_re, views.selections, api4, name='selection'),

    # new pending API
    url(r'^/selections/$', views.selections, api4, name='saved-selections'),
    url(r'^/selections/(?P<id>\d+)/$', views.selections, api4, name='saved-selection'),
)
