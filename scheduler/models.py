import itertools

from django.db import models, transaction, connection

from courses.signals import robots_signal
from courses import models as courses
from courses import managers as courses_managers
from courses.utils import dict_by_attr, Synchronizer
from scheduler import managers
from scheduler.utils import slugify, deserialize_numbers, serialize_numbers

from shortcuts import commit_all_or_rollback

class SavedSelection(models.Model):
    "Represents a unique set of selected sections and blocked times."
    internal_section_ids = models.CommaSeparatedIntegerField(max_length=1024)
    internal_blocked_times = models.CommaSeparatedIntegerField(max_length=1024, blank=True)

    objects = managers.SavedSelectionManager()

    @property
    def selection_dict(self):
        mapping = {}
        for section in courses.Section.objects.filter(id__in=self.section_ids):
            mapping.setdefault(section.course_id, []).append(section.id)
        return mapping

    @property
    def section_ids(self):
        return deserialize_numbers(self.internal_section_ids)

    @section_ids.setter
    def section_ids(self, section_ids):
        section_ids.sort()
        self.internal_section_ids = serialize_numbers(section_ids)

    @property
    def blocked_times(self):
        numbers = list(deserialize_numbers(self.internal_blocked_times))
        times = []
        while numbers:
            start_time, end_time = numbers.pop(0), numbers.pop(0)
            times.append((start_time, end_time))
        return times

    @blocked_times.setter
    def blocked_times(self, blocked_times):
        blocked_times.sort()
        numbers = []
        for start, end in blocked_times:
            numbers.append(int(start))
            numbers.append(int(end))
        self.internal_blocked_times = serialize_numbers(numbers)

    def __unicode__(self):
        return "%r, %r, %r" % (self.id, self.section_ids, self.blocked_times)

    def toJSON(self):
        return {
            'id': self.id,
            'selection': self.selection_dict,
            'blocked_times': self.blocked_times,
        }

class Selection(models.Model):
    """Represents a unique set of selected CRNs. It also offers a unique URL for each set.
    """
    internal_section_ids = models.CommaSeparatedIntegerField(max_length=255)
    api_cache = models.TextField(default='', blank=True)

    objects = managers.SelectionManager()

    def assign_slug_by_id(self):
        "Automatically assigns slug by id. The model must be saved before using this method."
        self.slug = self.pk

    @property
    def section_ids(self):
        return deserialize_numbers(self.internal_section_ids)

    @section_ids.setter
    def section_ids(self, section_ids):
        self.internal_section_ids = serialize_numbers(section_ids)

    def __unicode__(self):
        return "%r, %r" % (self.id, self.section_ids)


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


def cache_conflicts(semester_year=None, semester_month=None, semester=None, sql=True, stdout=False):
    assert (semester_year and semester_month) or semester, "Semester year & month must be provided or the semester object."
    import sys
    # trash existing conflict data...
    if not semester:
        semester = courses.Semester.objects.get(year=semester_year, month=semester_month)

    with commit_all_or_rollback():
        # we don't want to increment IDs too quickly (ev 25 minutes)
        #SectionConflict.objects.filter(semester=semester).delete()
        Syncer = Synchronizer(SectionConflict, SectionConflict.objects.values_list('id', flat=True))

        sections = courses.Section.objects.select_related('course', 'semester') \
                .by_semester(semester).prefetch_periods()
        section_courses = dict_by_attr(sections, 'course')

        mapping = {}
        for id, sid1, sid2 in SectionConflict.objects.filter(semester=semester).values_list('id', 'section1', 'section2'):
            mapping[(sid1, sid2)] = id

        conflicts = []

        def log(msg):
            sys.stdout.write(msg)
            sys.stdout.flush()

        def perform_insert(conflicts):
            SectionConflict.objects.bulk_create(conflicts)

        count = 0
        for course1, course2 in itertools.combinations(section_courses.keys(), 2):
            for section1, section2 in itertools.product(section_courses[course1], section_courses[course2]):
                if section1.conflicts_with(section2):
                    if section1.id > section2.id:
                        section1, section2 = section2, section1

                    count += 1
                    if sql:
                        if count % 500 == 0:
                            perform_insert(conflicts)
                            conflicts = []
                            log('.')
                        if (section1.id, section2.id) not in mapping:
                            log('C')
                            conflicts.append(
                                SectionConflict(section1=section1, section2=section2, semester=semester)
                            )
                        else:
                            Syncer.exclude_id(mapping[(section1.id, section2.id)])
                    else:
                        log('C')
                        Syncer.get_or_create(
                            section1=section1,
                            section2=section2,
                            semester=semester,
                        )

        if sql and conflicts:
            log('C')
            perform_insert(conflicts)

        log('\n')
        Syncer.trim(semester=semester)
        log('\n')


# attach to signals
def sitemap_for_scheduler(sender, semester, rule, **kwargs):
    url = sender.get_or_create_url('schedules', year=semester.year, month=semester.month)
    rule.disallowed.add(url)
robots_signal.connect(sitemap_for_scheduler, dispatch_uid='scheduler.sitemap_for_scheduler')
