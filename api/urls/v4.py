from django.conf.urls.defaults import patterns, include, url
from django.views.decorators.cache import cache_page
from django.views.generic import TemplateView

from api import views

cache_duration = 60 * 10

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

    url(r'^/docs/$', TemplateView.as_view(template_name='api/4/docs.html'), name='docs'),

    url(r'^/semesters/$', cache_page(views.semesters, cache_duration), api4, name='semesters'),
    url(r'^/semesters' + ext_re, cache_page(views.semesters, cache_duration), api4, name='semesters'),
    url(r'^/semesters/(?P<id>\d+)/$', views.semesters, api4, name='semesters'),
    url(r'^/semesters/(?P<id>\d+)' + ext_re, views.semesters, api4, name='semesters'),

    url(r'^/departments/$', cache_page(views.departments, cache_duration), api4, name='departments'),
    url(r'^/departments' + ext_re, cache_page(views.departments, cache_duration), api4, name='departments'),
    url(r'^/departments/(?P<id>\d+)/$', views.departments, api4, name='departments'),
    url(r'^/departments/(?P<id>\d+)' + ext_re, views.departments, api4, name='departments'),

    url(r'^/courses/$', cache_page(views.courses, cache_duration), api4, name='courses'),
    url(r'^/courses' + ext_re, cache_page(views.courses, cache_duration), api4, name='courses'),
    url(r'^/courses/(?P<id>\d+)/$', views.courses, api4, name='courses'),
    url(r'^/courses/(?P<id>\d+)' + ext_re, views.courses, api4, name='courses'),

    url(r'^/sections/$', cache_page(views.sections, cache_duration), api4, name='sections'),
    url(r'^/sections' + ext_re, cache_page(views.sections, cache_duration), api4, name='sections'),
    url(r'^/sections/(?P<id>\d+)/$', views.sections, api4, name='sections'),
    url(r'^/sections/(?P<id>\d+)' + ext_re, views.sections, api4, name='sections'),

    url(r'^/conflicts/$', cache_page(views.section_conflicts, cache_duration), api4, name='conflicts'),
    url(r'^/conflicts' + ext_re, cache_page(views.section_conflicts, cache_duration), api4, name='conflicts'),
    url(r'^/conflicts/(?P<id>\d+)/$', views.section_conflicts, api4, name='conflicts'),
    url(r'^/conflicts/(?P<id>\d+)' + ext_re, views.section_conflicts, api4, name='conflicts'),

    url(r'^/schedules/$', cache_page(views.schedules, cache_duration), api4, name='schedules'),
    url(r'^/schedules' + ext_re, cache_page(views.schedules, cache_duration), api4, name='schedules'),
    url(r'^/schedules/(?P<slug>[A-Za-z0-9_-]+)/$', cache_page(views.schedules, cache_duration), api4, name='schedules'),
    url(r'^/schedules/(?P<slug>[A-Za-z0-9_-]+)' + ext_re, cache_page(views.schedules, cache_duration), api4, name='schedules'),
)
