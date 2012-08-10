from django.conf.urls.defaults import patterns, include, url

from jasmine import views

urlpatterns = patterns('',
    url(r'^specs/$', views.JasmineView.as_view(), name='specs'),
)
