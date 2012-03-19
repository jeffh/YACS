from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings
from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin
admin.autodiscover()

from courses.sitemaps import sitemaps
from courses.views.newviews import redirect_to_latest_semester

urlpatterns = patterns('',
    url(r'^robots\.txt$', 'courses.views.newviews.robots_txt'),
    url(r'^sitemap\.xml$', 'django.contrib.sitemaps.views.sitemap', {'sitemaps': sitemaps}, name='sitemap'),

    url(r'^$', redirect_to_latest_semester, name='index'),

    url(r'^semesters/', include('courses.urls')),
    url(r'^semesters/', include('scheduler.urls')),
    url(r'^api/', include('api.urls', namespace='api')),
    url(r'^visuals/', include('courses_viz.urls', namespace='courses_viz')),

    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^', include('jslog.urls')),
)


if settings.DEBUG:
    urlpatterns += patterns('',
        url(r'^tests/', include('django_jasmine.urls')),
    )

    urlpatterns += staticfiles_urlpatterns()
