from django.conf.urls.defaults import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^', include('yacs.courses.urls')),
    url(r'^', include('yacs.scheduler.urls')),
    url(r'^api/', include('yacs.api.urls', namespace='api')),
    # Examples:
    # url(r'^$', 'yacs.views.home', name='home'),
    # url(r'^timetable/', include('yacs.foo.urls')),

    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
)
