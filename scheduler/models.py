import itertools

from django.db import models, transaction, connection

from courses.signals import robots_signal
from courses import models as courses
from courses import managers as courses_managers
from courses.utils import dict_by_attr
from scheduler import managers


# Django bug? Using a proxy causes tests to fail (looking for database NAME).
SectionProxy = courses.Section
#class SectionProxy(courses.Section):
#    class Meta:
#        proxy = True
#
#    objects = courses_managers.QuerySetManager(courses_managers.SectionQuerySet)
#
#    def __hash__(self):
#        return hash(self.id)
#
#    def conflicts_with(self, section):
#        # self.conflicts has to be set by the view....
#        return section.id in self.conflicts


class SectionConflict(models.Model):
    """The relationship where a section conflicts with another section.

    This through model is necessary for a couple of reasons:
     - To allow an API to access the sections which conflict easily.
     - To enforce conflicts only per semester

    But we lose the symmetricallity of the relationship, so as an implicitly enforced rule,
    the lower IDed section is section1 and the higher IDed section is section2.
    """
    section1 = models.ForeignKey(courses.Section, related_name='+')
    section2 = models.ForeignKey(courses.Section, related_name='+')
    semester = models.ForeignKey(courses.Semester, related_name='section_conflicts')

    objects = managers.SectionConflictManager()

    def save(self, *args, **kwargs):
        assert self.section1.id < self.section2.id, "Section1.id should be less than section2.id."
        return super(SectionConflict, self).save(*args, **kwargs)

    class Meta:
        unique_together = ('section1', 'section2', 'semester')

    def __unicode__(self):
        return u"<SectionConflict: %r and %r for %r>" % (self.section1, self.section2, self.semester)


# TODO: move into manager
def cache_conflicts(semester_year=None, semester_month=None, semester=None, sql=True):
    assert (semester_year and semester_month) or semester, "Semester year & month must be provided or the semester object."
    import sys
    # trash existing conflict data...
    if not semester:
        semester = courses.Semester.objects.get(year=semester_year, month=semester_month)
    SectionConflict.objects.filter(semester=semester).delete()

    sections = courses.Section.objects.select_related('course').full_select(semester_year, semester_month)
    section_courses = dict_by_attr(sections, 'course')
    count = 0
    query = ["insert into scheduler_sectionconflict (section1_id, section2_id, semester_id) values "]
    for course1, course2 in itertools.combinations(section_courses.keys(), 2):
        for section1, section2 in itertools.product(section_courses[course1], section_courses[course2]):
            if section1.conflicts_with(section2):
                if section1.id > section2.id:
                    section1, section2 = section2, section1

                count += 1
                if count > 1000:
                    sys.stdout.write('.')
                    sys.stdout.flush()
                    count = 0
                if sql:
                    query += ["(", str(section1.id), ", ", str(section2.id), ", ", str(semester.id), "),"]
                else:
                    SectionConflict.objects.create(
                        section1=section1,
                        section2=section2,
                        semester=semester,
                    )

    if sql:
        query = ''.join(query)
        query = query[:-1]+";"
        print "Manually inserting...:"
        cursor = connection.cursor()
        cursor.execute(query)
        transaction.commit_unless_managed()
# attach to signals
def sitemap_for_scheduler(sender, semester, rule, **kwargs):
    url = sender.get_or_create_url('schedules', year=semester.year, month=semester.month)
    rule.disallowed.add(url)
robots_signal.connect(sitemap_for_scheduler, dispatch_uid='scheduler.sitemap_for_scheduler')

