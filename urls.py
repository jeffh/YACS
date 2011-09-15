from django.conf.urls.defaults import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    #url(r'^$', include('timetable.courses.urls')),
    url(r'^$', include('timetable.scheduler.urls')),
    # Examples:
    # url(r'^$', 'timetable.views.home', name='home'),
    # url(r'^timetable/', include('timetable.foo.urls')),

    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
)
