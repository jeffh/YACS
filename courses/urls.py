from django.conf.urls.defaults import patterns, include, url
from timetable.courses import views


urlpatterns = patterns('',
    url(r'^$', views.RedirectToLatestSemesterRedirectView.as_view(), name='index'),

    # courses
    url(r'^(?P<year>[1-9]\d*)/(?P<month>[1-9]\d*)/$', views.DepartmentListView.as_view(), name='departments'),
    #url(r'^(?P<year>[1-9]\d*)/(?P<month>[1-9]\d*)/selected_courses/$', 'timetable.scheduler.views.selected_courses', name='selected-courses'),
    url(r'^(?P<year>[1-9]\d*)/(?P<month>[1-9]\d*)/(?P<code>[A-Z]+)/$', views.CourseByDeptListView.as_view(), name='courses-by-dept'),

    # actions
    url(r'^(?P<year>[1-9]\d*)/(?P<month>[1-9]\d*)/selection/$', views.select_courses, name='select-courses'),

    # other possible urls to have:
    # /semesters/ => view all past semesters
    # /<year>/ => view semesters for a given year
    # /<year>/<month>/<code>/<number>/ => view course by number
    # /<year>/<month>/course-<id>/ => view course by id
    # /<year>/<month>/sections/<crn>/ => view section by crn
)
