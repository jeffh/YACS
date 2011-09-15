from django.db import models
#from timetable.courses.models import Course, Semester, Section, SectionPeriod, Period
#from timetable.scheduler import managers 

#class Schedule(models.Model):
#    "A cache of computed schedules."
#    slug = models.SlugField(max_length=100, help_text="A unique slug so users can link schedules.")
#    semester = models.ForeignKey(Semester, related_name='schedules')
#    sections = models.ManyToManyField(Section, through='SectionInSchedule', related_name='schedules')
#    courses = models.ManyToManyField(Course, through='CourseInSchedule', related_name='schedules')
#
#    objects = managers.ScheduleManager()
#
#class SectionInSchedule(models.Model):
#    schedule = models.ForeignKey(Schedule, related_name='sections_in_schedule')
#    section = models.ForeignKey(Section, related_name='section_in_schedules')
#
#    class Meta:
#        unique_together = ('schedule', 'section')
#
#class CourseInSchedule(models.Model):
#    schedule = models.ForeignKey(Schedule, related_name='courses_in_schedule')
#    course = models.ForeignKey(Course, related_name='course_in_schedules')
#
#    class Meta:
#        unique_together = ('schedule', 'course')

