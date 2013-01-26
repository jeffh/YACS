from django.conf.urls.defaults import patterns, include, url
from django.views.decorators.cache import cache_page

from courses import views
from courses.views import newviews as nviews

cache_duration = 60 * 10

urlpatterns = patterns('',
    url(r'^$', nviews.semester_list, name='semesters'),
    url(r'^(?P<year>[1-9]\d*)/$', cache_page(nviews.semester_list, cache_duration), name='semesters'),

    url(r'^(?P<year>[1-9]\d*)/(?P<month>[1-9]\d*)/$', cache_page(nviews.department_list, cache_duration), name='departments'),
    url(r'^(?P<year>[1-9]\d*)/(?P<month>[1-9]\d*)/search/$', cache_page(nviews.course_list_by_dept, cache_duration), {'is_search': True}, name='search-all-courses'),
    url(r'^(?P<year>[1-9]\d*)/(?P<month>[1-9]\d*)/(?P<code>[A-Z]+)/$', cache_page(nviews.course_list_by_dept, cache_duration), name='courses-by-dept'),

    # courses
    url(r'^(?P<year>[1-9]\d*)/(?P<month>[1-9]\d*)/(?P<code>[A-Z]+)/(?P<number>[1-9]\d*)/$', views.CourseDetailView.as_view(), name='course'),

    # pretty much a static page..
    url(r'^(?P<year>[1-9]\d*)/(?P<month>[1-9]\d*)/selected/$', cache_page(nviews.selected_courses_view, 60 * 3600), name='selected-courses'),
    # actions
    #url(r'^(?P<year>[1-9]\d*)/(?P<month>[1-9]\d*)/select/$', views.SelectCoursesView.as_view(), name='select-courses'),
    #url(r'^(?P<year>[1-9]\d*)/(?P<month>[1-9]\d*)/deselect/$', views.DeselectCoursesView.as_view(), name='deselect-courses'),
    # other possible urls to have:
    # /semesters/ => view all past semesters
    # /<year>/ => view semesters for a given year
    # /<year>/<month>/<code>/<number>/ => view course by number
    # /<year>/<month>/course-<id>/ => view course by id
    # /<year>/<month>/sections/<crn>/ => view section by crn
)
