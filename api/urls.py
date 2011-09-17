from django.conf.urls.defaults import patterns, include, url
from piston.resource import Resource
from timetable.api import handlers
from timetable.courses.models import Section

defaults = {'emitter_format': 'json'}
defaults_study_abroad = {'emitter_format': defaults['emitter_format'], 'crn': Section.STUDY_ABROAD}

dept_handler = Resource(handlers.DepartmentHandler)
semester_handler = Resource(handlers.SemesterHandler)
bulk_course_handler = Resource(handlers.BulkCourseHandler)
course_handler = Resource(handlers.CourseHandler)
section_handler = Resource(handlers.SectionHandler)

urlpatterns = patterns('',
    ## Meta API calls - APIs about the API ##
    url(r'^$', 'django.views.generic.simple.direct_to_template', {'template': 'api/api.json'}),
    url(r'^(?P<version>[1-9]\d*)/$', 'timetable.api.views.api_support', name='status'),

    ## Data APIs ##
    # narrowing by departments
    url(r'^(?P<version>[1-9]\d*)/departments/$', dept_handler, defaults, name='departments'),
    url(r'^(?P<version>[1-9]\d*)/departments/(?P<code>[A-Za-z0-9]+)/$', bulk_course_handler, defaults, name='courses-by-department'),
    url(r'^(?P<version>[1-9]\d*)/departments/(?P<code>[A-Za-z0-9]+)/(?P<number>\d+)/$', bulk_course_handler, defaults, name='courses-by-subject'),

    # courses
    url(r'^(?P<version>[1-9]\d*)/courses/$', bulk_course_handler, defaults, name='courses'),
    url(r'^(?P<version>[1-9]\d*)/courses/(?P<cid>\d+)/$', course_handler, defaults, name='course-by-id'),
    url(r'^(?P<version>[1-9]\d*)/courses/(?P<cid>\d+)/(?P<number>\d+)/$', section_handler, defaults, name='sections-by-number'),
    url(r'^(?P<version>[1-9]\d*)/courses/(?P<cid>\d+)/study-abroad/$', section_handler, defaults_study_abroad, name='sections-by-study-abroad'),
    url(r'^(?P<version>[1-9]\d*)/courses/(?P<cid>\d+)/crn-(?P<crn>\d+)/$', section_handler, defaults, name='sections-by-crn'),

    # narrowing by semester
    url(r'^(?P<version>[1-9]\d*)/semesters/$', semester_handler, defaults, name='semesters'),
    url(r'^(?P<version>[1-9]\d*)/semesters/(?P<year>\d{4})/$', semester_handler, defaults, name='courses-by-year'),
    url(r'^(?P<version>[1-9]\d*)/semesters/(?P<year>\d{4})/(?P<month>\d{1,2})/$', bulk_course_handler, defaults, name='courses-by-semester'),
    # or courses
    url(r'^(?P<version>[1-9]\d*)/semesters/(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<cid>\d+)/$', course_handler, defaults, name='course-by-id'),
    url(r'^(?P<version>[1-9]\d*)/semesters/(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<cid>\d+)/(?P<number>\d+)/$', section_handler, defaults, name='sections-by-number'),
    url(r'^(?P<version>[1-9]\d*)/semesters/(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<cid>\d+)/study-abroad/$', section_handler, defaults_study_abroad, name='sections-by-study-abroad'),
    url(r'^(?P<version>[1-9]\d*)/semesters/(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<cid>\d+)/crn-(?P<crn>\d+)/$', section_handler, defaults, name='sections-by-crn'),
    # and departments
    url(r'^(?P<version>[1-9]\d*)/semesters/(?P<year>\d{4})/(?P<month>\d{1,2})/departments/$', dept_handler, defaults, name='departments'),
    url(r'^(?P<version>[1-9]\d*)/semesters/(?P<year>\d{4})/(?P<month>\d{1,2})/departments/(?P<code>[A-Za-z0-9]+)/$', bulk_course_handler, defaults, name='courses-by-department'),
    url(r'^(?P<version>[1-9]\d*)/semesters/(?P<year>\d{4})/(?P<month>\d{1,2})/departments/(?P<code>[A-Za-z0-9]+)/(?P<number>\d+)/$', bulk_course_handler, defaults, name='courses-by-subject'),


    # computation APIs
)
