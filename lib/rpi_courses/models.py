"""models.py - The classes that store the data retrieved by features.py

Generally, all instances should be read only.
"""
from datetime import time

from rpi_courses.utils import safeInt, FrozenDict
from rpi_courses.config import DEPARTMENTS


class ReadOnly(object):
    """All attributes that are prefixed with a single underscore will have
    a equivalent getter property without the underscore prefix.

    This restricts all those attributes to read-only.

    eg - setting self._foo, allows you to access it publicly using self.foo
    """
    def __getattr__(self, key):
        if not key.startswith('_') and not key.endswith('__'):
            value = getattr(self, '_' + key)

            the_type = type(value)
            if the_type == list:
                return tuple(value)
            if the_type == dict and type_type != FrozenDict:
                return FrozenDict(the_type)

            return value
        raise AttributeError("type object %r has no attribute %r" % (
            self.__class__.__name__, key
        ))


class CrossListing(ReadOnly):
    """Represents a crosslisted set of CRNs and Seats.
    This is immutable once created.
    """
    def __init__(self, crns, seats):
        self._crns, self._seats = frozenset(crns), seats

    def __eq__(self, other):
        return self.crns == other.crns and self.seats == other.seats

    def __add__(self, other_crosslisting):
        return self.__class__(self._crns + other_crosslisting._crns, self._seats + other_crosslisting._seats)


DAY_MAPPER = {
    0: 'Monday',
    1: 'Tuesday',
    2: 'Wednesday',
    3: 'Thursday',
    4: 'Friday',
    5: 'Saturday',
    6: 'Sunday',
}


class Period(ReadOnly):
    def __init__(self, type, instructor, start, end, location, int_days):
        self._type, self._instructor, self._location = \
            type.strip(), instructor.strip(), location.strip()

        try:
            self._start, self._end = int(start), int(end)
        except ValueError:
            # == '** TBA **'
            self._start = self._end = None
        self._int_days = tuple(map(int, int_days))
        self.__hash = None

    def __repr__(self):
        return "<Period: start=%r end=%r days=%r>" % (
            self.start, self.end, self.days
        )

    def __eq__(self, other):
        return (self.type, self.instructor, self.location, self.start, self.end, \
            self.int_days) == (other.type, other.instructor, other.location, \
            other.start, other.end, other.int_days)

    def __hash__(self):
        if self.__hash is None:
            result = hash(self.type)
            for v in (self.instructor, self.location, self.start, self.end, self.int_days):
                result = result ^ hash(v)
            self.__hash = result
        return self.__hash

    @staticmethod
    def from_soup_tag(tag):
        "Returns a new Period instance from the given beautifulsoup tag."
        days = []
        for elem in tag.findAll(recursive=False):
            if elem.name != 'day':
                raise TypeError("Unknown tag found: " + str(elem))
            days.append(elem.string)
        return Period(
            tag['type'], tag['instructor'], tag['start'], tag['end'],
            tag['location'], days
        )

    @property
    def time_range(self):
        return (self.start, self.end)

    @property
    def start_time(self):
        if self.start is None:
            return None
        s = str(self.start)
        hours, minutes = (s[:-2], s[-2:])
        return time(hour=int(hours), minute=int(minutes))

    @property
    def end_time(self):
        if self.end is None:
            return None
        s = str(self.end)
        hours, minutes = (s[:-2], s[-2:])
        return time(hour=int(hours), minute=int(minutes))

    def conflicts_with(self, period):
        "Checks this period conflicts with another period."
        if self.tba or period.tba:
            return False
        same_day = False
        for i in self.int_days:
            if i in period.int_days:
                same_day = True

        if not same_day:
            return False

        return self.start <= period.start <= self.end or \
            period.start <= self.start <= period.end or \
            self.start <= period.end <= self.end or \
            period.start <= self.end <= period.end

    @property
    def tba(self):
        "The time period hasn't been announced yet."
        return self.start is None or self.end is None

    @property
    def is_lecture(self):
        return self.type == 'LEC'

    @property
    def is_studio(self):
        return self.type == 'STU'

    @property
    def is_lab(self):
        return self.type == 'LAB'

    @property
    def is_testing_period(self):
        return self.type == 'TES'

    @property
    def is_recitation(self):
        return self.type == 'REC'

    @property
    def days(self):
        return tuple(map(DAY_MAPPER.get, self.int_days))


class Section(ReadOnly):
    """A section is a particular timeslot to take the given course.
    It is uniquely represented in SIS via CRN. The CRN is used for
    registration.
    """
    def __init__(self, crn, num, taken, total, periods, notes):
        self._crn, self._seats_taken, self._seats_total = \
            safeInt(crn), int(taken), int(total)
        self._num = num
        self._periods = tuple(periods)
        self._notes = tuple(set(notes))
        self.__hash = None

    #def __eq__(self, other):
    #    return (self.crn, self.num, self.seats_taken, self.seats_total, \
    #        self.periods, self.notes) == (other.crn, other.num, \
    #        other.seats_taken, other.periods, self.notes)

    def __hash__(self):
        if self.__hash is None:
            result = hash(self.crn)
            for v in (self.seats_taken, self.seats_total, self.num, self.periods, self.notes):
                result = result ^ hash(v)
            self.__hash = result
        return self.__hash

    def conflicts_with(self, section):
        for period in self.periods:
            for p in section.periods:
                if period.conflicts_with(p):
                    return True
        return False

    @staticmethod
    def from_soup_tag(tag):
        "Returns an instance from a given soup tag."
        periods = []
        notes = []
        for elem in tag.findAll(recursive=False):
            if elem.name not in ('period', 'note'):
                raise TypeError("Unknown tag found: " + str(elem))
            if elem.name == 'note':
                notes.append(elem.string.strip())
            elif elem.name == 'period':
                periods.append(Period.from_soup_tag(elem))
        return Section(
            tag['crn'], tag['num'], tag['students'], tag['seats'],
            periods, notes
        )

    @property
    def is_study_abroad(self):
        return self.num in ('SA', 'EXC')

    @property
    def is_off_campus(self):
        return self.num.startswith('OC')

    @property
    def is_valid(self):
        """Returns True if the given data for this section is valid."""
        return self.seats_total > 0

    @property
    def is_filled(self):
        "Returns True if the course is full and not accepting any more seats."
        return self.seats_taken >= self.seats_total

    @property
    def seats_left(self):
        """Returns the number of seats left.
        A negative number indicates more seats taken than are available.
        """
        return self.seats_total - self.seats_taken

    def __repr__(self):
        return "<Section: crn=%(crn)r num=%(num)r seats=%(used)r/%(total)r>" % {
            'crn': self.crn,
            'num': self.num,
            'used': self.seats_taken,
            'total': self.seats_total,
        }

    def __eq__(self, other):
        if isinstance(other, Section):
            return (
                self.crn == other.crn and self.num == other.num and
                self.periods == other.periods
            )
        return False


class Course(ReadOnly):
    """Represents a particular kind of course and its sections.
    Also immutable once created.
    """
    def __init__(self, name, dept, num, credmin, credmax, grade_type, sections):
        self._name, self._dept, self._num, self._cred, self._grade_type = \
            name.strip(), dept.strip(), safeInt(num, warn_only=True), \
            (int(credmin), int(credmax)), grade_type.strip(),
        self._sections = tuple(sections)
        self.__free_sections = None
        self.__hash = None

    def __contains__(self, crn):
        for section in self.sections:
            if section.crn == crn:
                return True
        return False

    def __eq__(self, other):
        return (
            self.num == other.num and self.cred == other.cred and
            self.grade_type == other.grade_type and
            self.name == other.name and self.dept == other.dept and
            self.sections == other.sections
        )

    def __hash__(self):
        if self.__hash is None:
            result = hash(self.name)
            for v in (self.dept, self.num, self.cred[0], self.cred[1], self.grade_type, self.sections):
                result = result ^ hash(v)
            self.__hash = result
        return self.__hash

    def __str__(self):
        return "%(name)s %(dept)s %(num)s" % {
            'name': self.name,
            'dept': self.dept,
            'num': self.num,
        }

    def __repr__(self):
        return "<Course: %(name)r, %(dept)r, %(num)r, %(mincred)r, %(maxcred)r, %(grade_type)r, section_count=%(section_count)s>" % {
            'name': self.name,
            'dept': self.dept,
            'num': self.num,
            'mincred': self.cred[0],
            'maxcred': self.cred[1],
            'grade_type': self.grade_type,
            'section_count': len(self.sections)
        }

    @property
    def full_dept(self):
        "Uses DEPARTMENT to convert the shorthand name into a full name of the department."
        return DEPARTMENTS.get(self.dept)

    @property
    def available_sections(self):
        if self.__free_sections is None:
            self.__free_sections = tuple(s for s in self.sections if s.seats_left > 0)
        return self.__free_sections

    @property
    def credits(self):
        """Returns either a tuple representing the credit range or a
        single integer if the range is set to one value.

        Use self.cred to always get the tuple.
        """
        if self.cred[0] == self.cred[1]:
            return self.cred[0]
        return self.cred

    @property
    def is_pass_or_fail(self):
        "Returns True if this course is graded as pass/fail."
        return self.grade_type.lower() == 'satisfactory/unsatisfactory'

    @property
    def code(self):
        "Returns the 'dept num'."
        return u"%s %s" % (self.dept, self.num)

    @staticmethod
    def from_soup_tag(tag):
        "Creates an instance from a given soup tag."
        sections = [Section.from_soup_tag(s) for s in tag.findAll('section')]
        return Course(
            tag['name'], tag['dept'], int(tag['num']), tag['credmin'],
            tag['credmax'], tag['gradetype'], [s for s in sections if s.is_valid]
        )
