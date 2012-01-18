from django.conf.urls.defaults import patterns, include, url

from yacs.courses import views


urlpatterns = patterns('',
    url(r'^$', views.RedirectToLatestSemesterRedirectView.as_view(), name='index'),

    # courses
    url(r'^(?P<year>[1-9]\d*)/(?P<month>[1-9]\d*)/$', views.DepartmentListView.as_view(), name='departments'),
    url(r'^(?P<year>[1-9]\d*)/(?P<month>[1-9]\d*)/search/$', views.SearchCoursesListView.as_view(), name='search-all-courses'),
    url(r'^(?P<year>[1-9]\d*)/(?P<month>[1-9]\d*)/(?P<code>[A-Z]+)/$', views.CourseByDeptListView.as_view(), name='courses-by-dept'),
    url(r'^(?P<year>[1-9]\d*)/(?P<month>[1-9]\d*)/(?P<code>[A-Z]+)/(?P<number>[1-9]\d*)/$', views.CourseDetailView.as_view(), name='course'),

    url(r'^(?P<year>[1-9]\d*)/(?P<month>[1-9]\d*)/selected/$', views.SelectedCoursesListView.as_view(), name='selected-courses'),
    # actions
    url(r'^(?P<year>[1-9]\d*)/(?P<month>[1-9]\d*)/select/$', views.SelectCoursesView.as_view(), name='select-courses'),
    url(r'^(?P<year>[1-9]\d*)/(?P<month>[1-9]\d*)/deselect/$', views.DeselectCoursesView.as_view(), name='deselect-courses'),
    # other possible urls to have:
    # /semesters/ => view all past semesters
    # /<year>/ => view semesters for a given year
    # /<year>/<month>/<code>/<number>/ => view course by number
    # /<year>/<month>/course-<id>/ => view course by id
    # /<year>/<month>/sections/<crn>/ => view section by crn
)
