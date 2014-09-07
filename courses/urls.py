from django.conf.urls import patterns, include, url

from courses import views
from courses.views import newviews as nviews


urlpatterns = patterns(
    '',
    url(r'^$', nviews.semester_list, name='semesters'),
    url(r'^(?P<year>[1-9]\d*)/$', nviews.semester_list, name='semesters'),

    url(r'^(?P<year>[1-9]\d*)/(?P<month>[1-9]\d*)/$', nviews.department_list, name='departments'),
    url(r'^(?P<year>[1-9]\d*)/(?P<month>[1-9]\d*)/search/$', nviews.course_list_by_dept, {'is_search': True}, name='search-all-courses'),
    url(r'^(?P<year>[1-9]\d*)/(?P<month>[1-9]\d*)/(?P<code>[A-Z]+)/$', nviews.course_list_by_dept, name='courses-by-dept'),

    # courses
    url(r'^(?P<year>[1-9]\d*)/(?P<month>[1-9]\d*)/(?P<code>[A-Z]+)/(?P<number>[1-9]\d*)/$', views.CourseDetailView.as_view(), name='course'),

    # pretty much a static page..
    url(r'^(?P<year>[1-9]\d*)/(?P<month>[1-9]\d*)/selected/$', nviews.selected_courses_view, name='selected-courses'),
    # actions
    # url(r'^(?P<year>[1-9]\d*)/(?P<month>[1-9]\d*)/select/$', views.SelectCoursesView.as_view(), name='select-courses'),
    # url(r'^(?P<year>[1-9]\d*)/(?P<month>[1-9]\d*)/deselect/$', views.DeselectCoursesView.as_view(), name='deselect-courses'),
    # other possible urls to have:
    # /semesters/ => view all past semesters
    # /<year>/ => view semesters for a given year
    # /<year>/<month>/<code>/<number>/ => view course by number
    # /<year>/<month>/course-<id>/ => view course by id
    # /<year>/<month>/sections/<crn>/ => view section by crn
)
