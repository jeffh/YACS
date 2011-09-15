from django.conf.urls.defaults import patterns, include, url


urlpatterns = patterns('',
    url(r'^schools/$', 'timetable.scheduler.views.school_list', name='schools'),

    # TODO: index page should redirect to dept listing?
    url(r'^schools/(?P<school>[A-Za-z0-9]+)/$', 'timetable.scheduler.views.semesters', name='school'),

    # selecting courses
    url(r'^schools/(?P<school>[A-Za-z0-9]+)/selected/$', 'timetable.scheduler.views.selected_courses', name='selected-courses'),

    # finding courses
    url(r'^schools/(?P<school>[A-Za-z0-9]+)/(?P<semester>[A-Za-z0-9_]+)/$', 'timetable.scheduler.views.dept_list', name='departments'),
    url(r'^schools/(?P<school>[A-Za-z0-9]+)/(?P<semester>[A-Za-z0-9_]+)/(?P<dept>[A-Za-z0-9]+)/$', 'timetable.scheduler.views.courses_from_dept', name='courses-from-dept'),
    url(r'^schools/(?P<school>[A-Za-z0-9]+)/(?P<semester>[A-Za-z0-9_]+)/(?P<dept>[A-Za-z0-9]+)/(?P<num>\d+)/$', 'timetable.scheduler.views.course_detail', name='course'),

    # 
    #url(r'^schools/(?P<school>[a-z0-9]+)/schedules/$', 'timetable.scheduler.views.schedules', name='courses'),
    # Examples:
    # url(r'^$', 'timetable.views.home', name='home'),
    # url(r'^timetable/', include('timetable.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
