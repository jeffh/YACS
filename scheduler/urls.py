from django.conf.urls.defaults import patterns, include, url


urlpatterns = patterns('',
    # selecting courses
    url(r'^schools/(?P<school>[A-Za-z0-9]+)/schedules/$', 'timetable.scheduler.views.schedules', name='schedules'),
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
