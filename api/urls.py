from django.conf.urls.defaults import patterns, include, url

from api import views


api3 = dict(version=3, objects=(
    'semesters', 'departments', 'courses', 'sections',
))
api2 = dict(version=2)

urlpatterns = patterns('',
    # version 3
    url(r'^v3/$', views.ObjectList.as_view(), api3, name='objects'),
    url(r'^v3/semesters/$', views.SemesterListView.as_view(), api3, name='semesters'),
    url(r'^v3/semesters/(?P<year>[1-9]\d*)/$', views.SemesterListView.as_view(), api3, name='semesters-by-year'),
    url(r'^v3/semesters/(?P<year>[1-9]\d*)/(?P<month>[1-9]\d*)/$', views.SemesterDetailView.as_view(), api3, name='semester'),
    url(r'^v3/departments/$', views.DepartmentListView.as_view(), api3, name='departments'),
    url(r'^v3/departments/(?P<code>[A-Z]+)/$', views.CourseByDeptListView.as_view(), api3, name='courses-by-dept'),
    url(r'^v3/courses/search/$', views.SearchCoursesListView.as_view(), api3, name='search-all-courses'),
    url(r'^v3/courses/$', views.CourseListView.as_view(), api3, name='courses'),
    url(r'^v3/courses/(?P<cid>\d+)/$', views.CourseDetailView.as_view(), api3, name='course'),
    url(r'^v3/courses/(?P<cid>\d+)/sections/$', views.SectionListView.as_view(), api3, name='sections'),
    url(r'^v3/courses/(?P<cid>\d+)/sections/(?P<secnum>\d+|study-abroad)/$', views.SectionDetailView.as_view(), api3, name='section'),
    url(r'^v3/departments/(?P<code>[A-Z]+)/(?P<number>[1-9]\d*)/$', views.CourseDetailView.as_view(), api3, name='course-by-code'),
    url(r'^v3/departments/(?P<code>[A-Z]+)/(?P<number>[1-9]\d*)/sections/$', views.SectionListView.as_view(), api3, name='sections'),
    url(r'^v3/departments/(?P<code>[A-Z]+)/(?P<number>[1-9]\d*)/sections/(?P<secnum>[\da-zA-Z]+)/$', views.SectionDetailView.as_view(), api3, name='section'),
    url(r'^v3/sections/$', views.SectionListView.as_view(), api3, name='sections'),
    url(r'^v3/sections/(?P<crn>\d+)/$', views.SectionDetailView.as_view(), api3, name='section'),

    # version 2
    # courses app
    url(r'^v2/$', views.SemesterListView.as_view(), api2, name='semesters'),
    url(r'^v2/(?P<year>[1-9]\d*)/$', views.SemesterListView.as_view(), api2, name='semesters-by-year'),
    url(r'^v2/(?P<year>[1-9]\d*)/(?P<month>[1-9]\d*)/$', views.SemesterDetailView.as_view(), api2, name='semester'),
    url(r'^v2/(?P<year>[1-9]\d*)/(?P<month>[1-9]\d*)/departments/$', views.DepartmentListView.as_view(), api2, name='departments'),
    url(r'^v2/(?P<year>[1-9]\d*)/(?P<month>[1-9]\d*)/departments/(?P<code>[A-Z]+)/$', views.CourseByDeptListView.as_view(), api2, name='courses-by-dept'),
    url(r'^v2/(?P<year>[1-9]\d*)/(?P<month>[1-9]\d*)/search/$', views.SearchCoursesListView.as_view(), api2, name='search-all-courses'),
    url(r'^v2/(?P<year>[1-9]\d*)/(?P<month>[1-9]\d*)/courses/$', views.CourseListView.as_view(), api2, name='courses'),
    url(r'^v2/(?P<year>[1-9]\d*)/(?P<month>[1-9]\d*)/courses/(?P<cid>\d+)/$', views.CourseDetailView.as_view(), api2, name='course'),
    url(r'^v2/(?P<year>[1-9]\d*)/(?P<month>[1-9]\d*)/courses/(?P<cid>\d+)/sections/$', views.SectionListView.as_view(), api2, name='sections'),
    url(r'^v2/(?P<year>[1-9]\d*)/(?P<month>[1-9]\d*)/courses/(?P<cid>\d+)/sections/(?P<secnum>\d+|study-abroad)/$', views.SectionDetailView.as_view(), api2, name='section'),
    url(r'^v2/(?P<year>[1-9]\d*)/(?P<month>[1-9]\d*)/departments/(?P<code>[A-Z]+)/(?P<number>[1-9]\d*)/$', views.CourseDetailView.as_view(), api2, name='course-by-code'),
    url(r'^v2/(?P<year>[1-9]\d*)/(?P<month>[1-9]\d*)/departments/(?P<code>[A-Z]+)/(?P<number>[1-9]\d*)/sections/$', views.SectionListView.as_view(), api2, name='sections'),
    url(r'^v2/(?P<year>[1-9]\d*)/(?P<month>[1-9]\d*)/departments/(?P<code>[A-Z]+)/(?P<number>[1-9]\d*)/sections/(?P<secnum>[\da-zA-Z]+)/$', views.SectionDetailView.as_view(), api2, name='section'),
    url(r'^v2/(?P<year>[1-9]\d*)/(?P<month>[1-9]\d*)/sections/$', views.SectionListView.as_view(), api2, name='sections'),
    url(r'^v2/(?P<year>[1-9]\d*)/(?P<month>[1-9]\d*)/sections/(?P<crn>\d+)/$', views.SectionDetailView.as_view(), api2, name='section'),
    # auto fetch latest semester
    url(r'^v2/latest/$', views.SemesterDetailView.as_view(), api2, name='semester'),
    url(r'^v2/latest/departments/$', views.DepartmentListView.as_view(), api2, name='departments'),
    url(r'^v2/latest/departments/(?P<code>[A-Z]+)/$', views.CourseByDeptListView.as_view(), api2, name='courses-by-dept'),
    url(r'^v2/latest/search/$', views.SearchCoursesListView.as_view(), api2, name='search-all-courses'),
    url(r'^v2/latest/courses/$', views.CourseListView.as_view(), api2, name='courses'),
    url(r'^v2/latest/courses/(?P<cid>\d+)/$', views.CourseDetailView.as_view(), api2, name='course'),
    url(r'^v2/latest/courses/(?P<cid>\d+)/sections/$', views.SectionListView.as_view(), api2, name='sections'),
    url(r'^v2/latest/courses/(?P<cid>\d+)/sections/(?P<secnum>\d+|study-abroad)/$', views.SectionDetailView.as_view(), api2, name='section'),
    url(r'^v2/latest/departments/(?P<code>[A-Z]+)/(?P<number>[1-9]\d*)/$', views.CourseDetailView.as_view(), api2, name='course-by-code'),
    url(r'^v2/latest/departments/(?P<code>[A-Z]+)/(?P<number>[1-9]\d*)/sections/$', views.SectionListView.as_view(), api2, name='sections'),
    url(r'^v2/latest/departments/(?P<code>[A-Z]+)/(?P<number>[1-9]\d*)/sections/(?P<secnum>[\da-zA-Z]+)/$', views.SectionDetailView.as_view(), api2, name='section'),
    url(r'^v2/latest/sections/$', views.SectionListView.as_view(), api2, name='sections'),
    url(r'^v2/latest/sections/(?P<crn>\d+)/$', views.SectionDetailView.as_view(), api2, name='section'),

    # TODO:::
    #url(r'^v2/(?P<year>[1-9]\d*)/(?P<month>[1-9]\d*)/schedules/$', views.SectionDetailView.as_view(), name='schedules'),
    #url(r'^v2/latest/schedules/$', views.SectionDetailView.as_view(), name='schedules'),
)
