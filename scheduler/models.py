from django.db import models
from timetable.courses.models import Course, Semester, Section, SectionPeriod, Period
from timetable.scheduler import managers 
import traceback as tb

class Schedule(models.Model):
    "A cache of computed schedules."
    crns_used = models.SlugField(max_length=200, help_text="A unique slug of CRNs to identify this schedule")
    course_ids_used = models.CharField(max_length=200, db_index=True,
        help_text="The ordered list of course ids used to identify this as a possible schedule.")
    semester = models.ForeignKey(Semester, related_name='schedules')
    sections = models.ManyToManyField(Section, through='SectionInSchedule', related_name='schedules')
    courses = models.ManyToManyField(Course, through='CourseInSchedule', related_name='schedules')

    objects = managers.ScheduleManager()

    class Meta:
        unique_together = ('crns_used', 'semester')

    def __unicode__(self):
        return "Schedule of %s for %r" % (', '.join(map(str, self.crns)), self.semester)

    SEPARATOR = ','

    # use classmethods so that our manager can use them too.
    @classmethod
    def str_to_ints(cls, string):
        if string == '':
            return []
        return tuple(int(x) for x in string.split(cls.SEPARATOR))

    @classmethod
    def ints_to_str(cls, ints):
        return cls.SEPARATOR.join(str(int(x)) for x in sorted(ints))

    @property
    def crns(self):
        return Schedule.str_to_ints(self.crns_used)

    @crns.setter
    def crns(self, crns):
        self.crns_used = Schedule.ints_to_str(crns)
    
    @property
    def course_ids(self):
        return Schedule.str_to_ints(self.course_ids_used)
    
    @course_ids.setter
    def course_ids(self, cids):
        self.course_ids_used = Schedule.ints_to_str(cids)

    def to_dict(self):
        return dict(zip(self.course_ids, self.crns))


class SectionInSchedule(models.Model):
    schedule = models.ForeignKey(Schedule, related_name='sections_in_schedule')
    section = models.ForeignKey(Section, related_name='section_in_schedules')
    semester = models.ForeignKey(Semester, related_name='+')

    class Meta:
        unique_together = ('schedule', 'section')

class CourseInSchedule(models.Model):
    schedule = models.ForeignKey(Schedule, related_name='courses_in_schedule')
    course = models.ForeignKey(Course, related_name='course_in_schedules')
    semester = models.ForeignKey(Semester, related_name='+')

    class Meta:
        unique_together = ('schedule', 'course')

