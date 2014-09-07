from django.conf.urls import patterns, include, url

from courses_viz import views

urlpatterns = patterns(
    '',
    url(r'^$', views.DefaultRedirect.as_view()),
    url(r'^bubbles/$', views.render_template, {'template': 'bubble.html'}, name='bubble'),
    url(r'^timelines/$', views.render_template, {'template': 'timelines.html'}, name='timelines'),
    url(r'^treemap/$', views.render_template, {'template': 'treemap.html'}, name='treemap'),
)
