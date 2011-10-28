from django.utils.importlib import import_module
from django.db import models
from yacs.courses import managers
from yacs.courses.utils import options, capitalized
from django.core.exceptions import ValidationError
from django.db.models import F

__all__ = ['Department', 'Semester', 'Period', 'Section', 'SectionCrosslisting',
    'Course', 'OfferedFor', 'SectionPeriod']

def has_model(select_related, model):
    return any(s == model._meta.db_table for s, _ in select_related)

class Semester(models.Model):
    """Represents the semester / quarter for a college. Courses may not be offered every semester.
    """
    year = models.IntegerField()
    month = models.IntegerField(help_text="The starting month of the semester")
    name = models.CharField(max_length=100, help_text="(eg - 'Spring 2011')")
    ref = models.CharField(max_length=150, help_text="Internally used by bridge module to refer to a semester.", unique=True)
    date_updated = models.DateTimeField(auto_now=True)

    objects = managers.QuerySetManager(managers.SerializableQuerySet)

    class Meta:
        unique_together = (
            ('year', 'month'),
        )
        ordering = ['-year', '-month']

    def __unicode__(self):
        return self.name

    def __repr__(self):
        return "<Semester: %d-%d @ %r>" % (self.year, self.month, self.ref)

    def toJSON(self, select_related=()):
        json = {
            'year': self.year,
            'month': self.month,
            'name': self.name,
            'date_updated': self.date_updated,
        }
        if has_model(select_related, Department):
            json['departments'] = self.departments.all().toJSON(select_related)
        return json

    def __cmp__(self, other):
        return cmp(self.year, other.year) or cmp(self.month, other.month)

class Department(models.Model):
    """Represents a department. Provides UI organization capabilities to drill-down courses by department."""
    name = models.CharField(max_length=200, blank=True, default='')
    code = models.CharField(max_length=50, unique=True)
    semesters = models.ManyToManyField(Semester, through='SemesterDepartment', related_name='departments')

    objects = managers.QuerySetManager(managers.SemesterBasedQuerySet)

    class Meta:
        ordering = ['code']

    def __unicode__(self):
        if self.name:
            return u"%s (%s)" % (self.name, self.code)
        return self.code

    def toJSON(self, select_related=()):
        json = {
            'name': self.name,
            'code': self.code,
        }
        if has_model(select_related, Semester):
            json['semesters'] = self.semesters.all().toJSON(select_related)
        return json

class Period(models.Model):
    """Represents a time period that sections are held for during the week.

    For particular details about a section, refer to the SectionPeriod model.
    """
    start = models.TimeField(default=None, null=True)
    end = models.TimeField(default=None, null=True)

    MONDAY, TUESDAY, WEDNESDAY, THURSDAY, FRIDAY, SATURDAY, SUNDAY = options(7)
    DAYS_OF_WEEK = (
        (MONDAY, 'Monday'),
        (TUESDAY, 'Tuesday'),
        (WEDNESDAY, 'Wednesday'),
        (THURSDAY, 'Thursday'),
        (FRIDAY, 'Friday'),
        (SATURDAY, 'Saturday'),
        (SUNDAY, 'Sunday'),
    )

    #objects = managers.QuerySetManager()

    days_of_week_flag = models.IntegerField()

    class Meta:
        unique_together = ('start', 'end', 'days_of_week_flag')

    def __unicode__(self):
        return u"%s to %s on %s" % (self.start_time, self.end_time, ', '.join(self.days_of_week))

    def toJSON(self, select_related=()):
        return {
            'start_time': self.start,
            'end_time': self.end,
            'days_of_the_week': self.days_of_week,
            #'is_to_be_announced': self.is_to_be_announced,
        }

    def _validate_time(self, value, name):
        s = str(value)
        hour, minute = (int(s[:-2]), int(s[-2:]))
        if not (0 <= hour < 24):
            raise ValidationError("%s's hour should be greater than or equal to 0 and less than 24" % name)
        if not (0 <= minute < 60):
            raise ValidationError("%s's minute should be greater than or equal to 0 and less than 60" % name)

    def clean(self):
        "Ensures time ranges follow integer format of HHMM."
        self._validate_time(self.start, 'start')
        self._validate_time(self.end, 'end')

    @property
    def start_time(self):
        return self.start.strftime("%H:%M")

    @property
    def end_time(self):
        return self.end.strftime("%H:%M")

    @property
    def is_to_be_announced(self):
        return None in (self.start, self.end)

    def conflicts_with(self, period):
        "Returns True if the given period conflicts the current one."
        if self == period:
            return True
        days = self.days_of_week_flag & period.days_of_week_flag
        return days and (
            (self.start <= period.start <= self.end) or \
            (self.start <= period.end <= self.end) or \
            (period.start <= self.start <= period.end) or \
            (period.start <= self.end <= period.end)
        )

    def is_on_day(self, day):
        return self.days_of_week_flag & day

    @property
    def days_of_week(self):
        "Returns a tuple of days of the week (str)."
        days = []
        for value, name in self.DAYS_OF_WEEK:
            if self.is_on_day(value):
                days.append(name)
        return days

    @days_of_week.setter
    def days_of_week(self, days):
        "Sets the days of the week using a tuple of strings or MONDAY-SUNDAY constants."
        dow = dict((n, v) for v, n in self.DAYS_OF_WEEK)
        value = 0
        for name in set(days):
            if type(name) in (str, unicode):
                value += dow.get(capitalized(name), 0)
            else:
                value += int(name) or 0
        self.days_of_week_flag = value

    def to_tuple(self):
        return (self.start, self.end, self.days_of_week_flag)

class SectionCrosslisting(models.Model):
    """Interface for courses that are crosslisted. Crosslisted sections are similar to each other.

    For example: Grad & Undergrad courses might be crosslisted if they share the same class times & location.
    """
    semester = models.ForeignKey(Semester, related_name='section_crosslistings')
    ref = models.CharField(max_length=200, unique=True, help_text='Internal unique identification used by bridge module.')

    #objects = managers.QuerySetManager()

    class Meta:
        verbose_name = 'Section Crosslisting'
        verbose_name_plural = 'Section Crosslistings'

    def __unicode__(self):
        return "%s for %s" % (self.semester, self.ref)

class Section(models.Model):
    """Represents a particular course a student can sign up for."""
    STUDY_ABROAD = -1
    OFF_CAMPUS = -2
    number = models.CharField(max_length=5)

    crn = models.IntegerField(unique=True)
    course = models.ForeignKey('Course', related_name='sections')
    semesters = models.ManyToManyField(Semester, through='SemesterSection', related_name='sections')
    periods = models.ManyToManyField(Period, through='SectionPeriod', related_name='sections')
    crosslisted = models.ForeignKey(SectionCrosslisting, related_name='sections', null=True, blank=True)

    seats_taken = models.IntegerField()
    seats_total = models.IntegerField()

    objects = managers.QuerySetManager(managers.SectionQuerySet)

    class Meta:
        ordering = ['number']

    #class Meta:
    #    unique_together = ('number', 'course')

    def __unicode__(self):
        return "%s (%s) Seats: %d / %d" % (self.number, self.crn, self.seats_taken, self.seats_total)

    def __hash__(self):
        return hash(self.id)

    def toJSON(self, select_related=()):
        values = {
            'number': self.number,
            'crn': self.crn,
            'seats_taken': self.seats_taken,
            'seats_total': self.seats_total,
            'seats_left': self.seats_left,
        }
        if has_model(select_related, Course):
            values['course'] = self.course.toJSON(select_related)
        if hasattr(self, 'all_section_periods'):
            values['periods'] = [sp.toJSON() for sp in self.all_section_periods]
        return values

    @property
    def is_study_abroad(self):
        return self.number == self.STUDY_ABROAD

    @property
    def is_full(self):
        return self.seats_left <= 0

    @property
    def seats_left(self):
        return max(self.seats_total - self.seats_taken, 0)

    def periods_for_semester(self, **semester_filter_options):
        options = {}
        for name, value in semester_filter_options.items():
            options['semester__'+name] = value
        return self.course_times.filter().select_related('period')

    def get_periods(self):
        if getattr(self, 'all_periods', None) is None:
            self.all_periods = self.periods.all()
        return self.all_periods

    def conflicts_with(self, section):
        "Returns True if the given section conflicts with another provided section."
        if self == section:
            return True
        # START --- this should really be a proxy in scheduler.models.SectionProxy
        # but there seems to be a django bug with Proxy models causing tests to fail.
        # self.conflicts has to be set by the view....
        if hasattr(self, 'conflicts'):
            return section.id in self.conflicts
        # END ---
        periods = section.get_periods()
        for period1 in self.get_periods():
            for period2 in periods:
                if period1.conflicts_with(period2):
                    return True
        return False

class Course(models.Model):
    """A course offered."""
    name = models.CharField(max_length=200)
    number = models.IntegerField()

    department = models.ForeignKey(Department, related_name='courses')
    semesters = models.ManyToManyField(Semester, through='OfferedFor', related_name='courses')

    min_credits = models.IntegerField()
    max_credits = models.IntegerField()

    grade_type = models.CharField(max_length=150, blank=True, default='')

    objects = managers.QuerySetManager(managers.CourseQuerySet)

    class Meta:
        unique_together = ('name', 'department', 'number')
        ordering = ['department__code', 'number']

    def __unicode__(self):
        return "%s (%s %s)" % (self.name, self.department.code, self.number)

    def __hash__(self):
        return hash(self.id)

    def conflicts_with(self, course):
        "Returns True if the provided course conflicts with this one on time periods."
        sections = course.sections.all()
        for section1 in self.sections.all():
            for section2 in sections:
                if section1.conflicts_with(section2):
                    return True
        return False

    def toJSON(self, select_related=()):
        values = {
            'id': self.pk,
            'name': self.name,
            'number': self.number,
            'min_credits': self.min_credits,
            'max_credits': self.max_credits,
            }
        if has_model(select_related, Department):
            values['department'] = self.department.toJSON(select_related)
        if hasattr(self, 'all_sections'):
            values['sections'] = [s.toJSON() for s in self.all_sections]
        return values

    @property
    def code(self):
        "Returns the department code and course number as a string."
        return '%s %s' % (self.department.code, self.number)

    @property
    def credits(self):
        "Returns the number of credits the course is. If there is a range, returns the average."
        if self.min_credits == self.max_credits:
            return self.min_credits
        return (self.min_credits + self.max_credits) / 2.0

    @property
    def credits_display(self):
        "Returns the number of credits the course for those needy humans."
        if self.min_credits == self.max_credits:
            return "%d credit%s" % (self.min_credits, '' if self.min_credits == 1 else 's')
        return "%d - %d credits" % (self.min_credits, self.max_credits)

    @credits.setter
    def credits(self, value):
        self.min_credits = self.max_credits = int(value)

    @property
    def available_sections(self):
        return self.sections.by_availability()

    def sections_by_semester(self, semester):
        return self.sections.filter(semesters__contains=semester)

    def available_sections_by_semester(self, semester):
        return self.available_sections.filter(semesters__contains=semester)

    # TODO: These few properties should be moved into a manager for query optimization
    @property
    def section_periods(self):
        if not hasattr(self, 'all_section_periods'):
            return SectionPeriod.objects.by_course(course=self)
        return self.all_section_periods

    @property
    def crns(self):
        if not hasattr(self, 'all_section_periods'):
            return SectionPeriod.objects.by_course(course=self).values_list('section__crn', flat=True)
        return set(sp.section.crn for sp in self.section_periods)

    @property
    def full_crns(self):
        if not hasattr(self, 'all_section_periods'):
            return SectionPeriod.objects.by_course(course=self).filter(section__seats_taken__lt=F('section__seats_total')).values_list('section__crn', flat=True)
        return set(sp.section.crn for sp in self.section_periods if sp.section.seats_taken >= sp.section.seats_total)

    @property
    def instructors(self):
        if not hasattr(self, 'all_section_periods'):
            return SectionPeriod.objects.select_instructors(course=self)
        return set(sp.instructor for sp in self.section_periods)

    @property
    def kinds(self):
        if not hasattr(self, 'all_section_periods'):
            return SectionPeriod.objects.select_kinds(course=self)
        return set(sp.kind for sp in self.section_periods)


class OfferedFor(models.Model):
    "The M2M model of courses and semesters."
    course = models.ForeignKey('Course', related_name='offered_for')
    semester = models.ForeignKey('Semester', related_name='offers')

    class Meta:
        unique_together = ('course', 'semester')
        verbose_name = 'Offers'
        verbose_name_plural = 'Offerings'

    def __unicode__(self):
        return u"%s is offered for %s" % (self.course, self.semester)

class SectionPeriod(models.Model):
    "M2M model of sections and periods"
    period = models.ForeignKey('Period', related_name='section_times')
    section = models.ForeignKey('Section', related_name='section_times')

    # we could do M2M here, but the other data here is related, and it's just easier have one link
    # per semeter...
    semester = models.ForeignKey('Semester', related_name='section_times')
    instructor = models.CharField(max_length=150, blank=True)
    location = models.CharField(max_length=150, blank=True)
    kind = models.CharField(max_length=75, help_text="The kind of meeting time (eg - lab, recitation, lecture, etc.)")

    objects = managers.QuerySetManager(managers.SectionPeriodQuerySet)

    class Meta:
        unique_together = (
            ('period', 'section', 'semester'),
        )
        verbose_name = 'Section Period'
        verbose_name_plural = 'Section Periods'

    def __unicode__(self):
        return "%s holds %s during %r at %s for section %s" % (self.instructor, self.kind, self.period, self.location, self.section)

    def toJSON(self, select_related=()):
        json = {
            'instructor': self.instructor,
            'location': self.location,
            'kind': self.kind,
        }
        json.update(self.period.toJSON())
        return json

    def conflicts_with(self, section_period):
        "Returns True if times conflict with the given section period."
        return self.period.conflicts_with(section_period.period)

class SemesterDepartment(models.Model):
    "M2M model of departments and semesters."
    department = models.ForeignKey('Department', related_name='+')
    semester = models.ForeignKey('Semester', related_name='+')

    class Meta:
        unique_together = ('department', 'semester')

class SemesterSection(models.Model):
    "M2M model of semesters and sections."
    semester = models.ForeignKey('Semester', related_name='+')
    section = models.ForeignKey('Section', related_name='+')

    class Meta:
        unique_together = ('semester', 'section')

### END RELATED MODELS ###
