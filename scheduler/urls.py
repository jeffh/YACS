from django.conf.urls.defaults import patterns, include, url
from timetable.scheduler import views

urlpatterns = patterns('',
    # selecting courses
    url(r'^(?P<year>[1-9]\d*)/(?P<month>[1-9]\d*)/schedules/$', views.schedules, name='schedules'),
    # 
    #url(r'^schools/(?P<school>[a-z0-9]+)/schedules/$', 'timetable.scheduler.views.schedules', name='courses'),
    # Examples:
    # url(r'^$', 'timetable.views.home', name='home'),
    # url(r'^timetable/', include('timetable.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
