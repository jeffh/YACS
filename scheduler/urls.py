from django.conf.urls import patterns, include, url

import views


urlpatterns = patterns('',
    url(r'^schedules/ics/$', views.icalendar, name='ics'),
    # selecting courses
    url(r'^(?P<year>[1-9]\d*)/(?P<month>[1-9]\d*)/selected/(?P<id>\d+)/$', views.SelectionSelectedCoursesListView.as_view(), name='selected-courses'),
    url(r'^(?P<year>[1-9]\d*)/(?P<month>[1-9]\d*)/schedules/(?P<id>\d+)/$', views.schedules_bootloader, name='schedules'),
    url(r'^(?P<year>[1-9]\d*)/(?P<month>[1-9]\d*)/schedules/(?P<id>\d+)/(?P<index>\d+)/$', views.schedules_bootloader, name='schedules'),
    url(r'^(?P<year>[1-9]\d*)/(?P<month>[1-9]\d*)/schedules/$', views.schedules_bootloader, name='schedules'),
)
