from django.conf.urls.defaults import patterns, include, url
from timetable.courses.views import DepartmentListView, RedirectToLatestSemesterRedirectView


urlpatterns = patterns('',
    url(r'^$', RedirectToLatestSemesterRedirectView.as_view(url='course-finder'), name='index'),

    # courses
    url(r'^(?P<year>[1-9]\d*)/(?P<month>[1-9]\d*)/$', DepartmentListView.as_view(), name='departments'),
    #url(r'^(?P<year>[1-9]\d*)/(?P<month>[1-9]\d*)/selected_courses/$', 'timetable.scheduler.views.selected_courses', name='selected-courses'),
    #url(r'^(?P<year>[1-9]\d*)/(?P<month>[1-9]\d*)/dept/(?P<code>[A-Za-z]+)/$', 'timetable.scheduler.views.courses_from_dept', name='courses-by-department'),

    # other possible urls to have:
    # /semesters/ => view all past semesters
    # /<year>/ => view semesters for a given year
    # /<year>/<month>/<code>/<number>/ => view course by number
    # /<year>/<month>/course-<id>/ => view course by id
    # /<year>/<month>/sections/<crn>/ => view section by crn
)
