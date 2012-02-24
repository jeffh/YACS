import datetime

import factory

from courses import models


class SemesterFactory(factory.Factory):
    FACTORY_FOR = models.Semester

    year = factory.Sequence(lambda n: 2009 + int(n))
    month = 1
    name = factory.Sequence(lambda n: 'Semester %s' % n)
    ref = factory.LazyAttribute(lambda s: 'Semester%s-%s.xml' % (s.year, s.month))
    date_updated = factory.LazyAttribute(lambda s: datetime.datetime.now())


class DepartmentFactory(factory.Factory):
    FACTORY_FOR = models.Department

    name = factory.Sequence(lambda n: 'Department %s' % n)
    code = factory.Sequence(lambda n: 'DEPT%s' % n)


class PeriodFactory(factory.Factory):
    FACTORY_FOR = models.Period

    start = factory.Sequence(lambda n: datetime.time(hour=int(n) % 24))
    end = factory.Sequence(lambda n: datetime.time(hour=int(n) % 24, minute=50))
    days_of_week_flag = models.Period.MONDAY & models.Period.THURSDAY


class SectionCrosslistingFactory(factory.Factory):
    FACTORY_FOR = models.SectionCrosslisting

    semester = factory.LazyAttribute(lambda s: SemesterFactory())
    ref = factory.Sequence(lambda n: 'ref-%s' % n)


class SectionFactory(factory.Factory):
    FACTORY_FOR = models.Section

    number = factory.Sequence(lambda n: n)
    crn = factory.Sequence(lambda n: n)
    course = factory.LazyAttribute(lambda s: CourseFactory())

    seats_taken = 10
    seats_total = 100
    notes = ''


class CourseFactory(factory.Factory):
    FACTORY_FOR = models.Course

    name = 'Course'
    number = factory.Sequence(lambda n: n)
    department = factory.LazyAttribute(lambda s: DepartmentFactory())
    #semesters =

    min_credits = 4
    max_credits = 4
    grade_type = ''

class OfferedForFactory(factory.Factory):
    FACTORY_FOR = models.OfferedFor

    course = factory.LazyAttribute(lambda s: CourseFactory())
    semester = factory.LazyAttribute(lambda s: SemesterFactory())


class SectionPeriodFactory(factory.Factory):
    FACTORY_FOR = models.SectionPeriod

    period = factory.LazyAttribute(lambda s: PeriodFactory())
    section = factory.LazyAttribute(lambda s: SectionFactory())
    semester = factory.LazyAttribute(lambda s: SemesterFactory())
    instructor = 'Goldschmit'
    location = 'DCC 1337'
    kind = 'LEC'


class SemesterDepartmentFactory(factory.Factory):
    FACTORY_FOR = models.SemesterDepartment

    department = factory.LazyAttribute(lambda s: DepartmentFactory())
    semester = factory.LazyAttribute(lambda s: SemesterFactory())


class SemesterSectionFactory(factory.Factory):
    FACTORY_FOR = models.SemesterSection

    semester = factory.LazyAttribute(lambda s: SemesterFactory())
    section = factory.LazyAttribute(lambda s: SemesterSectionFactory())

