from django.db import models
from timetable.courses.utils import options, capitalized

class School(models.Model):
    """A school / college -- RPI, Cornell, or whatever. Just not the term referring to a Department."""
    name = models.CharField(max_length=200) 
    slug = models.SlugField(max_length=50)
    url = models.URLField(help_text="The school's URL (eg - http://rpi.edu/)")
    scheduler_url = models.URLField(help_text="Possible URL to give to the parser module.")
    parser_module = models.CharField(max_length=300, help_text="The parser module used to read and create database data.")

class Department(models.Model):
    """Represents a department for a school."""
    school = models.ForeignKey(School, related_name='departments')
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=50)

class Semester(models.Model):
    """Represents the semester / quarter for a school. Courses may not be offered every semester.
    """
    school = models.ForeignKey(School)
    year = models.IntegerField()
    month = models.IntegerField(help_text="The starting month of the semester")
    name = models.CharField(max_length=100, help_text="(eg - 'Spring 2011')")

class Period(models.Model):
    """Represents a time period that sections are held for during the week.
    
    For particular details about a section, refer to the SectionPeriod model.
    """
    start_time = models.IntegerField()
    end_time = models.IntegerField()

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

    days_of_week_raw = models.IntegerField(choices=DAYS_OF_WEEK)

    def is_on_day(self, day):
        return self.days_of_week_raw & day

    @property
    def days_of_week(self):
        "Returns a tuple of days of the week (str)."
        days = []
        for value, name in self.DAYS_OF_WEEK.items():
            if self.on_day(value):
                days.append(name)
        return days

    @days_of_week.setter
    def days_of_week(self, days):
        "Sets the days of the week using a tuple of strings or MONDAY-SUNDAY constants."
        dow = dict((n, v) for v, n in self.DAYS_OF_WEEK.items())
        value = 0
        for name in set(days):
            if type(name) in (str, unicode):
                value += dow.get(capitalized(name), 0)
            else:
                value += int(name) or 0
        self.days_of_week_raw = value

    class Meta:
        unique_together = ('start_time', 'end_time', 'days_of_week_raw')

class Section(models.Model):
    """Represents a particular course a student can sign up for."""
    number = models.IntegerField()
    crn = models.IntegerField()
    course = models.ForeignKey('Course', related_name='sections')
    periods = models.ManyToManyField(Period, through='SectionPeriod', related_name='courses')

    seats_taken = models.IntegerField()
    seats_total = models.IntegerField()

    @property
    def seats_available(self):
        return self.seats_taken < self.seats_total

    class Meta:
        unique_together = ('number', 'course')

class Crosslisting(models.Model):
    """Interface for courses that are crosslisted. Crosslisted courses are similar to each other
    
    For example: Grad & Undergrad courses might be crosslisted if they share the same class times & location.
    """
    pass

class Course(models.Model):
    """A course offered by a particular school."""
    name = models.CharField(max_length=200)
    number = models.IntegerField()

    school = models.ForeignKey(School, related_name='courses')
    department = models.ForeignKey(Department, related_name='courses')
    semester = models.ManyToManyField(Semester, through='OfferedFor', related_name='courses')
    crosslisted = models.ForeignKey(Crosslisting, related_name='courses')

    min_credits = models.IntegerField()
    max_credits = models.IntegerField()

    grade_type = models.CharField(max_length=150)

    @property
    def credits(self):
        "Returns the number of credits the course is. If there is a range, returns the average."
        if self.min_credits == self.max_credits:
            return self.min_credits
        return (self.min_credits + self.max_credits) / 2.0

    class Meta:
        unique_together = ('name', 'number', 'school')

class OfferedFor(models.Model):
    "The M2M model of courses and semesters."
    course = models.ForeignKey(Course, related_name='offered_for')
    semester = models.ForeignKey(Semester, related_name='offers')

    class Meta:
        unique_together = ('course', 'semester')

class SectionPeriod(models.Model):
    "M2M model of sections and periods"
    period = models.ForeignKey(Period, related_name='course_times')
    section = models.ForeignKey(Section, related_name='course_times')

    instructor = models.CharField(max_length=150, blank=True)
    location = models.CharField(max_length=150, blank=True)
    kind = models.CharField(max_length=75, help_text="The kind of meeting time (eg - lab, recitation, lecture, etc.)")

    class Meta:
        unique_together = ('period', 'section')


