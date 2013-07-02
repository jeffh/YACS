from django.conf.urls import patterns, include, url

from api import views

api2 = dict(version=2)

urlpatterns = patterns('',
    # courses app
    url(r'^$', views.SemesterListView.as_view(), api2, name='semesters'),
    url(r'^(?P<year>[1-9]\d*)/$', views.SemesterListView.as_view(), api2, name='semesters-by-year'),
    url(r'^(?P<year>[1-9]\d*)/(?P<month>[1-9]\d*)/$', views.SemesterDetailView.as_view(), api2, name='semester'),
    url(r'^(?P<year>[1-9]\d*)/(?P<month>[1-9]\d*)/departments/$', views.DepartmentListView.as_view(), api2, name='departments'),
    url(r'^(?P<year>[1-9]\d*)/(?P<month>[1-9]\d*)/departments/(?P<code>[A-Z]+)/$', views.CourseByDeptListView.as_view(), api2, name='courses-by-dept'),
    url(r'^(?P<year>[1-9]\d*)/(?P<month>[1-9]\d*)/search/$', views.SearchCoursesListView.as_view(), api2, name='search-all-courses'),
    url(r'^(?P<year>[1-9]\d*)/(?P<month>[1-9]\d*)/courses/$', views.CourseListView.as_view(), api2, name='courses'),
    url(r'^(?P<year>[1-9]\d*)/(?P<month>[1-9]\d*)/courses/(?P<cid>\d+)/$', views.CourseDetailView.as_view(), api2, name='course'),
    url(r'^(?P<year>[1-9]\d*)/(?P<month>[1-9]\d*)/courses/(?P<cid>\d+)/sections/$', views.SectionListView.as_view(), api2, name='sections'),
    url(r'^(?P<year>[1-9]\d*)/(?P<month>[1-9]\d*)/courses/(?P<cid>\d+)/sections/(?P<secnum>\d+|study-abroad)/$', views.SectionDetailView.as_view(), api2, name='section'),
    url(r'^(?P<year>[1-9]\d*)/(?P<month>[1-9]\d*)/departments/(?P<code>[A-Z]+)/(?P<number>[1-9]\d*)/$', views.CourseDetailView.as_view(), api2, name='course-by-code'),
    url(r'^(?P<year>[1-9]\d*)/(?P<month>[1-9]\d*)/departments/(?P<code>[A-Z]+)/(?P<number>[1-9]\d*)/sections/$', views.SectionListView.as_view(), api2, name='sections'),
    url(r'^(?P<year>[1-9]\d*)/(?P<month>[1-9]\d*)/departments/(?P<code>[A-Z]+)/(?P<number>[1-9]\d*)/sections/(?P<secnum>[\da-zA-Z]+)/$', views.SectionDetailView.as_view(), api2, name='section'),
    url(r'^(?P<year>[1-9]\d*)/(?P<month>[1-9]\d*)/sections/$', views.SectionListView.as_view(), api2, name='sections'),
    url(r'^(?P<year>[1-9]\d*)/(?P<month>[1-9]\d*)/sections/(?P<crn>\d+)/$', views.SectionDetailView.as_view(), api2, name='section'),
    # auto fetch latest semester
    url(r'^latest/$', views.SemesterDetailView.as_view(), api2, name='semester'),
    url(r'^latest/departments/$', views.DepartmentListView.as_view(), api2, name='departments'),
    url(r'^latest/departments/(?P<code>[A-Z]+)/$', views.CourseByDeptListView.as_view(), api2, name='courses-by-dept'),
    url(r'^latest/search/$', views.SearchCoursesListView.as_view(), api2, name='search-all-courses'),
    url(r'^latest/courses/$', views.CourseListView.as_view(), api2, name='courses'),
    url(r'^latest/courses/(?P<cid>\d+)/$', views.CourseDetailView.as_view(), api2, name='course'),
    url(r'^latest/courses/(?P<cid>\d+)/sections/$', views.SectionListView.as_view(), api2, name='sections'),
    url(r'^latest/courses/(?P<cid>\d+)/sections/(?P<secnum>\d+|study-abroad)/$', views.SectionDetailView.as_view(), api2, name='section'),
    url(r'^latest/departments/(?P<code>[A-Z]+)/(?P<number>[1-9]\d*)/$', views.CourseDetailView.as_view(), api2, name='course-by-code'),
    url(r'^latest/departments/(?P<code>[A-Z]+)/(?P<number>[1-9]\d*)/sections/$', views.SectionListView.as_view(), api2, name='sections'),
    url(r'^latest/departments/(?P<code>[A-Z]+)/(?P<number>[1-9]\d*)/sections/(?P<secnum>[\da-zA-Z]+)/$', views.SectionDetailView.as_view(), api2, name='section'),
    url(r'^latest/sections/$', views.SectionListView.as_view(), api2, name='sections'),
    url(r'^latest/sections/(?P<crn>\d+)/$', views.SectionDetailView.as_view(), api2, name='section'),
)
