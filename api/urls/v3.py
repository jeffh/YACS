from django.conf.urls.defaults import patterns, include, url

from api import views

api3 = dict(version=3, objects=(
    'semesters', 'departments', 'courses', 'sections',
))

urlpatterns = patterns('',
    # version 3
    url(r'^$', views.ObjectList.as_view(), api3, name='objects'),
    url(r'^semesters/$', views.SemesterListView.as_view(), api3, name='semesters'),
    url(r'^semesters/(?P<year>[1-9]\d*)/$', views.SemesterListView.as_view(), api3, name='semesters-by-year'),
    url(r'^semesters/(?P<year>[1-9]\d*)/(?P<month>[1-9]\d*)/$', views.SemesterDetailView.as_view(), api3, name='semester'),
    url(r'^departments/$', views.DepartmentListView.as_view(), api3, name='departments'),
    url(r'^departments/(?P<code>[A-Z]+)/$', views.CourseByDeptListView.as_view(), api3, name='courses-by-dept'),
    url(r'^courses/search/$', views.SearchCoursesListView.as_view(), api3, name='search-all-courses'),
    url(r'^courses/$', views.CourseListView.as_view(), api3, name='courses'),
    url(r'^courses/(?P<cid>\d+)/$', views.CourseDetailView.as_view(), api3, name='course'),
    url(r'^courses/(?P<cid>\d+)/sections/$', views.SectionListView.as_view(), api3, name='sections'),
    url(r'^courses/(?P<cid>\d+)/sections/(?P<secnum>\d+|study-abroad)/$', views.SectionDetailView.as_view(), api3, name='section'),
    url(r'^departments/(?P<code>[A-Z]+)/(?P<number>[1-9]\d*)/$', views.CourseDetailView.as_view(), api3, name='course-by-code'),
    url(r'^departments/(?P<code>[A-Z]+)/(?P<number>[1-9]\d*)/sections/$', views.SectionListView.as_view(), api3, name='sections'),
    url(r'^departments/(?P<code>[A-Z]+)/(?P<number>[1-9]\d*)/sections/(?P<secnum>[\da-zA-Z]+)/$', views.SectionDetailView.as_view(), api3, name='section'),
    url(r'^sections/$', views.SectionListView.as_view(), api3, name='sections'),
    url(r'^sections/(?P<crn>\d+)/$', views.SectionDetailView.as_view(), api3, name='section'),
)
