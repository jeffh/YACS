from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings
from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView

from django.contrib import admin
admin.autodiscover()

from courses.sitemaps import sitemaps
from courses.views.newviews import redirect_to_latest_semester

urlpatterns = patterns('',
    url(r'^robots\.txt$', 'courses.views.newviews.robots_txt'),
    url(r'^sitemap\.xml$', 'django.contrib.sitemaps.views.sitemap', {'sitemaps': sitemaps}, name='sitemap'),

    #url(r'^$', redirect_to_latest_semester, name='index'),
    url(r'^$', TemplateView.as_view(template_name='angular/index.html'), name='index'),

    url(r'^semesters/', include('courses.urls')),
    url(r'^semesters/', include('scheduler.urls')),
    url(r'^api/', include('api.urls', namespace='api')),
    url(r'^visuals/', include('courses_viz.urls', namespace='courses_viz')),

    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
)


if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += patterns('',
        url(r'^jasmine/$', TemplateView.as_view(template_name='jasmine/runner.html'), name='index'),
    )
