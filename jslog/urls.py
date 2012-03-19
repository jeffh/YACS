from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('',
    url(r'^jslog/$', 'jslog.views.record', name='jslog'),
)
