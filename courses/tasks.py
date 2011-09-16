from celery.task import task
from timetable.courses.bridge import import_courses

import_courses = task(import_courses)