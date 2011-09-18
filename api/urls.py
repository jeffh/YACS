from django.conf.urls.defaults import patterns, include, url
from timetable.courses.models import Section
from timetable.api.resources import (dept_handler, semester_handler, bulk_course_handler,
    course_handler, section_handler, schedule_handler)

defaults = {'emitter_format': 'json', 'version': 1}
defaults_study_abroad = {'emitter_format': defaults['emitter_format'], 'crn': Section.STUDY_ABROAD, 'version': 1}

urlpatterns = patterns('',
    ## Data APIs ##
    # narrowing by semester
    url(r'^$', semester_handler, defaults, name='semesters'),
    url(r'^(?P<year>\d{4})/$', semester_handler, defaults, name='courses-by-year'),
    url(r'^(?P<year>\d{4})/(?P<month>\d{1,2})/$', bulk_course_handler, defaults, name='courses-by-semester'),
    # or courses
    url(r'^(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<cid>\d+)/$', course_handler, defaults, name='course-by-id'),
    url(r'^(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<cid>\d+)/(?P<number>\d+)/$', section_handler, defaults, name='sections-by-number'),
    url(r'^(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<cid>\d+)/study-abroad/$', section_handler, defaults_study_abroad, name='sections-by-study-abroad'),
    url(r'^(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<cid>\d+)/crn-(?P<crn>\d+)/$', section_handler, defaults, name='sections-by-crn'),
    # and departments
    url(r'^(?P<year>\d{4})/(?P<month>\d{1,2})/departments/$', dept_handler, defaults, name='departments'),
    url(r'^(?P<year>\d{4})/(?P<month>\d{1,2})/departments/(?P<code>[A-Za-z0-9]+)/$', bulk_course_handler, defaults, name='courses-by-department'),
    url(r'^(?P<year>\d{4})/(?P<month>\d{1,2})/departments/(?P<code>[A-Za-z0-9]+)/(?P<number>\d+)/$', course_handler, defaults, name='courses-by-subject'),

    # computation APIs
    url(r'^(?P<year>\d{4})/(?P<month>\d{1,2})/schedules/', schedule_handler, defaults, name='scheduler'),
)
