from django.conf.urls.defaults import patterns, include, url
from yacs.scheduler import views

urlpatterns = patterns('',
    # selecting courses
    #url(r'^(?P<year>[1-9]\d*)/(?P<month>[1-9]\d*)/schedules/$', views.force_compute_schedules, name='schedules'),
    url(r'^(?P<year>[1-9]\d*)/(?P<month>[1-9]\d*)/schedules/ajax/$', views.JsonComputeSchedules.as_view(), name='ajax-schedules'),
    #url(r'^(?P<year>[1-9]\d*)/(?P<month>[1-9]\d*)/cached-schedules/$', views.compute_schedules_via_cache, name='schedules'),
    url(r'^(?P<year>[1-9]\d*)/(?P<month>[1-9]\d*)/schedules/$', views.SchedulesBootloader.as_view(), name='schedules'),
)
