from piston.resource import Resource
from timetable.api import handlers

dept_handler = Resource(handlers.DepartmentHandler)
semester_handler = Resource(handlers.SemesterHandler)
bulk_course_handler = Resource(handlers.BulkCourseHandler)
course_handler = Resource(handlers.CourseHandler)
section_handler = Resource(handlers.SectionHandler)
schedule_handler = Resource(handlers.ScheduleHandler)