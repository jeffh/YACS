from django.conf.urls.defaults import patterns, include, url
from timetable.scheduler import views

urlpatterns = patterns('',
    # selecting courses
    url(r'^(?P<year>[1-9]\d*)/(?P<month>[1-9]\d*)/schedules/$', views.force_compute_schedules, name='schedules'),

)
