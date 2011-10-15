#from django.db import models
#from yacs.courses.models import Course, Semester, Section, SectionPeriod, Period
#from yacs.scheduler import managers
#from yacs.scheduler.fields import SetOfIntegersField
#import traceback as tb
#
#class Schedule(models.Model):
#    "A cache of computed schedules."
#    crns = SetOfIntegersField(db_index=True, help_text='CRNs this schedule uses.')
#    course_ids = SetOfIntegersField(db_index=True, help_text='The course ids this schedule uses.')
#    semester = models.ForeignKey(Semester, related_name='schedules')
#
#    objects = managers.ScheduleManager()
#
#    class Meta:
#        unique_together = ('crns', 'semester')
#
#    def __unicode__(self):
#        return "Schedule of %s for %r" % (', '.join(map(str, self.crns)), self.semester)
#
#    def to_dict(self):
#        return dict(zip(self.course_ids, self.crns))
#
#    @property
#    def courses(self):
#        return Course.objects.filter(semesters=self.semester, id__in=self.course_ids)
#
#    @property
#    def sections(self):
#        return Section.objects.filter(semesters=self.semester, crn__in=self.crns)
#
#class Combination(models.Model):
#    """The "input" to try and generate schedules.
#    Use this to fetch all the appropriate schedules for a given set of CRNs as input.
#    """
#    crns = SetOfIntegersField(unique=True)
#    semester = models.ForeignKey(Semester, related_name='+')
#    schedules = models.ManyToManyField(Schedule, related_name='input_combinations')
#