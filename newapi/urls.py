from django.conf.urls.defaults import patterns, include, url
from yacs.newapi import views


urlpatterns = patterns('',
    # courses app
    url(r'^v1/$', views.SemesterListView.as_view(), name='semesters'),
    url(r'^v1/(?P<year>[1-9]\d*)/$', views.SemesterListView.as_view(), name='semesters-by-year'),
    url(r'^v1/(?P<year>[1-9]\d*)/(?P<month>[1-9]\d*)/$', views.SemesterDetailView.as_view(), name='semester'),
    url(r'^v1/(?P<year>[1-9]\d*)/(?P<month>[1-9]\d*)/departments/$', views.DepartmentListView.as_view(), name='departments'),
    url(r'^v1/(?P<year>[1-9]\d*)/(?P<month>[1-9]\d*)/departments/(?P<code>[A-Z]+)/$', views.CourseByDeptListView.as_view(), name='courses-by-dept'),
    url(r'^v1/(?P<year>[1-9]\d*)/(?P<month>[1-9]\d*)/search/$', views.SearchCoursesListView.as_view(), name='search-all-courses'),
    url(r'^v1/(?P<year>[1-9]\d*)/(?P<month>[1-9]\d*)/courses/$', views.CourseListView.as_view(), name='courses'),
    url(r'^v1/(?P<year>[1-9]\d*)/(?P<month>[1-9]\d*)/courses/(?P<cid>\d+)/$', views.CourseDetailView.as_view(), name='course'),
    url(r'^v1/(?P<year>[1-9]\d*)/(?P<month>[1-9]\d*)/departments/(?P<code>[A-Z]+)/(?P<number>[1-9]\d*)/$', views.CourseDetailView.as_view(), name='course-by-code'),
    url(r'^v1/(?P<year>[1-9]\d*)/(?P<month>[1-9]\d*)/departments/(?P<code>[A-Z]+)/(?P<number>[1-9]\d*)/sections/$', views.SectionListView.as_view(), name='sections'),
    url(r'^v1/(?P<year>[1-9]\d*)/(?P<month>[1-9]\d*)/departments/(?P<code>[A-Z]+)/(?P<number>[1-9]\d*)/sections/(?P<secnum>\d+)/$', views.SectionDetailView.as_view(), name='section'),
    url(r'^v1/(?P<year>[1-9]\d*)/(?P<month>[1-9]\d*)/sections/$', views.SectionListView.as_view(), name='sections'),
    url(r'^v1/(?P<year>[1-9]\d*)/(?P<month>[1-9]\d*)/sections/(?P<crn>\d+)/$', views.SectionDetailView.as_view(), name='section'),
    # auto fetch latest semester
    url(r'^v1/latest/$', views.SemesterDetailView.as_view(), name='semester'),
    url(r'^v1/latest/departments/$', views.DepartmentListView.as_view(), name='departments'),
    url(r'^v1/latest/departments/(?P<code>[A-Z]+)/$', views.CourseByDeptListView.as_view(), name='courses-by-dept'),
    url(r'^v1/latest/search/$', views.SearchCoursesListView.as_view(), name='search-all-courses'),
    url(r'^v1/latest/courses/$', views.CourseListView.as_view(), name='courses'),
    url(r'^v1/latest/courses/(?P<cid>\d+)/$', views.CourseDetailView.as_view(), name='course'),
    url(r'^v1/latest/departments/(?P<code>[A-Z]+)/(?P<number>[1-9]\d*)/$', views.CourseDetailView.as_view(), name='course-by-code'),
    url(r'^v1/latest/departments/(?P<code>[A-Z]+)/(?P<number>[1-9]\d*)/sections/$', views.SectionListView.as_view(), name='sections'),
    url(r'^v1/latest/departments/(?P<code>[A-Z]+)/(?P<number>[1-9]\d*)/sections/(?P<secnum>\d+)/$', views.SectionDetailView.as_view(), name='section'),
    url(r'^v1/latest/sections/$', views.SectionListView.as_view(), name='sections'),
    url(r'^v1/latest/sections/(?P<crn>\d+)/$', views.SectionDetailView.as_view(), name='section'),

)
