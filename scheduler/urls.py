from django.conf.urls.defaults import patterns, include, url

import views


urlpatterns = patterns('',
    url(r'^(?P<year>[1-9]\d*)/(?P<month>[1-9]\d*)/schedules/ics/$', views.icalendar, name='ics'),
    # selecting courses
    url(r'^(?P<year>[1-9]\d*)/(?P<month>[1-9]\d*)/selected/(?P<slug>[A-Za-z0-9_-]+)/$', views.SelectionSelectedCoursesListView.as_view(), name='selected-courses'),
    #url(r'^(?P<year>[1-9]\d*)/(?P<month>[1-9]\d*)/schedules/ajax/$', views.JsonComputeSchedules.as_view(), name='ajax-schedules'),
    url(r'^(?P<year>[1-9]\d*)/(?P<month>[1-9]\d*)/schedules/(?P<slug>[A-Za-z0-9_-]+)/$', views.schedules_bootloader, name='schedules'),
    url(r'^(?P<year>[1-9]\d*)/(?P<month>[1-9]\d*)/schedules/(?P<slug>[A-Za-z0-9_-]+)/(?P<index>\d+)/$', views.schedules_bootloader, name='schedules'),
    #url(r'^(?P<year>[1-9]\d*)/(?P<month>[1-9]\d*)/cached-schedules/$', views.compute_schedules_via_cache, name='schedules'),
    url(r'^(?P<year>[1-9]\d*)/(?P<month>[1-9]\d*)/schedules/$', views.schedules_bootloader, name='schedules'),
)
