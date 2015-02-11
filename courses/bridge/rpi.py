"""All the data-importing functions are listed here for various colleges.
"""
import re
import urllib2
import dateutil.parser
import logging
import logging.handlers
import sys
import datetime
import rpi_calendars
from contextlib import closing

from icalendar import Calendar, Event
import pytz

from django.core.mail import send_mail
from django.conf import settings
from django.db.utils import IntegrityError
from django.db import transaction

from courses.models import (
    Semester, Course, Department, Section,
    Period, SectionPeriod, OfferedFor,
    SectionCrosslisting, SemesterDepartment
)
from courses.signals import sections_modified
from courses.utils import Synchronizer, DAYS

# TODO: remove import *
from catalogparser import *

logger = logging.getLogger(__file__)
logger.setLevel(logging.DEBUG)

try:
    NullHandler = logging.NullHandler
except AttributeError:
    level = logging.INFO

    class NullHandler(object):

        def emit(self, record):
            pass
        handle = emit

# fallback, so there's no warning of no handlers
logger.addHandler(NullHandler())
logger.addHandler(logging.StreamHandler(sys.stdout))


class SemesterNotifier(object):

    def __init__(self):
        self.subject = "[YACS] New Semester for Review"
        self.message = """Hey Humans,

There's a new semester to approve. Go to the admin interface and check it out!

Love,
YACS.me
"""
        self.from_email = settings.FROM_EMAIL
        self.recipient_list = settings.ADMINS
        self.__notify = False

    def requires_notification(self):
        self.__notify = True

    def notify(self):
        if self.__notify:
            send_mail(self.subject, self.message, self.from_email, self.recipient_list, fail_silently=True)


class ROCSRPIImporter(object):
    "Handles the importation of RPI course data into the database."
    FILE_RE = re.compile(r'(\d+)\.xml')

    def __init__(self, notifier):
        self.semesters = {}  # semester.ref: semester obj
        self.notifier = notifier
        for semester in Semester.objects.filter(ref__startswith='http://sis.rpi.edu/reg/rocs/'):
            self.semesters[semester.ref] = semester

        self.latest_semester = None
        if len(self.semesters) > 0:
            self.latest_semester = max(self.semesters.values())

        self.sections_changed = False
        self.SectionPeriod = Synchronizer(SectionPeriod, SectionPeriod.objects.values_list('id', flat=True))

    def clear_unused(self, semester):
        self.SectionPeriod.trim(semester=semester)

    def sync(self, get_files=None, get_catalog=None):
        "Performs the updating of the database data from RPI's SIS"
        if get_files is None:
            from rpi_courses import list_rocs_xml_files
            get_files = list_rocs_xml_files

        if get_catalog is None:
            from rpi_courses import ROCSCourseCatalog
            get_catalog = ROCSCourseCatalog.from_url

        for filename in get_files():
            name = self.FILE_RE.finditer(filename).next().groups()[0]
            semester = self.semesters.get(name + '.xml')
            # if latest semester or newer semester
            if (not semester) or semester == self.latest_semester:
                catalog = get_catalog(filename)

                if self.latest_semester and semester == self.latest_semester and catalog.datetime <= self.latest_semester.date_updated:
                    continue  # already up-to-date

                logger.debug('found catalog for: %r %r' % (catalog.year, catalog.month))

                semester_obj = None
                try:
                    semester_obj, created = Semester.objects.get_or_create(
                        year=catalog.year,
                        month=catalog.month,
                        defaults={
                            'visible': True,
                            'name': catalog.name,
                            'ref': filename,
                        })
                except IntegrityError as error:
                    logger.debug(' DUPLICATE SEMESTER ' + repr(semester_obj) + ': ' + repr(error))
                    continue
                self.create_courses(catalog, semester_obj)
                self.create_crosslistings(semester_obj, set(catalog.crosslistings.values()))
                semester_obj.save()  # => update date_updated property
                if created:
                    logger.debug(' CREATE SEMESTER ' + repr(semester_obj))
                    self.notifier.requires_notification()
                else:
                    logger.debug(' EXISTS SEMESTER ' + repr(semester_obj))
                if self.sections_changed:
                    sections_modified.send(sender=self, semester=semester_obj)

                self.clear_unused(semester_obj)

    def create_courses(self, catalog, semester_obj):
        "Inserts all the course data, including section information, into the database from the catalog."
        list = self.add_comm_intense(catalog, semester_obj)
        for course in catalog.get_courses():
            comm = (course.name in list)
            department = self.get_or_create_department(semester_obj, code=course.dept, name=course.full_dept)
            # we use our OfferedFor.ref to determine if we need to create a new
            # course or not.
            ref_name = '%r:%r:%r' % (course.name, course.dept, course.num)
            qs = OfferedFor.objects.filter(semester=semester_obj, course__department__code=course.dept, course__number=course.num)
            qs = qs.select_related('course')
            try:
                offered_for = qs.get(ref=ref_name)
                course_obj = offered_for.course
                created = False
            except OfferedFor.DoesNotExist:
                course_obj = None

            if not course_obj:
                # for migration support... set empty refs.
                try:
                    offered_for = qs.get(ref='')
                    offered_for.ref = ref_name
                    offered_for.save()
                    course_obj = offered_for.course
                    created = False
                except OfferedFor.DoesNotExist:
                    course_obj = None

            if not course_obj:
                course_obj = Course.objects.create(
                    name=course.name,
                    number=course.num,
                    department=department,
                    min_credits=course.cred[0],
                    max_credits=course.cred[1],
                    grade_type=course.grade_type,
                    is_comm_intense=comm,
                )
                created = True

            if not created:
                if self.forced:
                    course_obj.name = course.name
                course_obj.min_credits, course_obj.max_credits = course.cred
                course_obj.grade_type = course.grade_type
                course_obj.is_comm_intense = comm
                course_obj.save()
            else:
                OfferedFor.objects.get_or_create(
                    course=course_obj, semester=semester_obj, ref=ref_name
                )
            self.create_sections(course, course_obj, semester_obj)
            crns = [str(s.crn) for s in course_obj.sections.all()]
            logger.debug(' %s %s (crns: %s)' % (('+' if created else ' '), course.name, ', '.join(crns)))

    def add_comm_intense(self, catalog, semester):
        from rpi_courses import get_comm_file
        pdf = get_comm_file(semester)
        list = []
        crns = re.findall(r"\d{5}\s[A-Z]{4}", pdf)
        print "Found " + str(len(crns)) + " communication intensive sections"
        for i in crns:
            course = catalog.find_course_by_crn(int(i.split()[0]))
            if course is not None:
                print course.name
                list.append(course.name)
        return list

    def create_sections(self, course, course_obj, semester_obj):
        "Inserts all section data, including time period information, into the database from the catalog."
        for section in course.sections:
            # TODO: encode prereqs / notes
            remove_prereq_notes(section)
            section_obj, created = Section.objects.get_or_create(
                crn=section.crn,
                semester=semester_obj,
                defaults=dict(
                    notes='\n'.join(section.notes),
                    number=section.num,
                    seats_taken=section.seats_taken,
                    seats_total=section.seats_total,
                    course=course_obj,
                )
            )

            if not created:
                section_obj.number = section.num
                section_obj.seats_taken = section.seats_taken
                section_obj.seats_total = section.seats_total
                section_obj.course = course_obj
                section_obj.notes = '\n'.join(section.notes)
                section_obj.save()
            else:
                self.sections_changed = False

            self.create_timeperiods(semester_obj, section, section_obj)

    # maps from catalog data to database representation
    DOW_MAPPER = {
        'Monday': Period.MONDAY,
        'Tuesday': Period.TUESDAY,
        'Wednesday': Period.WEDNESDAY,
        'Thursday': Period.THURSDAY,
        'Friday': Period.FRIDAY,
        'Saturday': Period.SATURDAY,
        'Sunday': Period.SUNDAY,
    }

    def compute_dow(self, days_of_week):
        """Assists in converting rpi_course's representation of days of the week to the database kind."""
        value = 0
        for dow in days_of_week:
            value = value | self.DOW_MAPPER.get(dow, 0)
        return value

    def create_timeperiods(self, semester_obj, section, section_obj):
        """Creates all the SectionPeriod and Period instances for the given section object from
        the catalog and the section_obj database equivalent to refer to.
        """
        for period in section.periods:
            if None in (period.start, period.end):
                continue  # invalid period for all we care about... ignore.
            period_obj, pcreated = Period.objects.get_or_create(
                start=period.start_time,
                end=period.end_time,
                days_of_week_flag=self.compute_dow(period.days),
            )
            sectionperiod_obj, created = self.SectionPeriod.get_or_create(
                period=period_obj,
                section=section_obj,
                semester=semester_obj,
                defaults=dict(
                    instructor=period.instructor,
                    location=period.location,
                    kind=period.type,
                )
            )
            if not created:
                sectionperiod_obj.instructor = period.instructor
                sectionperiod_obj.location = period.location
                sectionperiod_obj.kind = period.type
                sectionperiod_obj.save()

    def get_or_create_department(self, semester_obj, code, name=None):
        dept, created = Department.objects.get_or_create(
            code=code,
            defaults={
                'name': name or ''
            }
        )
        SemesterDepartment.objects.get_or_create(
            semester=semester_obj,
            department=dept
        )
        return dept

    def create_crosslistings(self, semester_obj, crosslistings):
        "Creates all crosslisting information into the database for all the sections."
        for crosslisting in crosslistings:
            refid = ','.join(map(str, sorted(tuple(crosslisting.crns))))
            crosslisting_obj, created = SectionCrosslisting.objects.get_or_create(semester=semester_obj, ref=refid)
            Section.objects.filter(crn__in=crosslisting.crns).update(crosslisted=crosslisting_obj)


class SISRPIImporter(ROCSRPIImporter):

    def get_files(self, latest_semester):
        from rpi_courses import list_sis_files_for_date

        files = list_sis_files_for_date()
        if latest_semester:
            files.append(latest_semester.ref)

        return list(set(files))

    def sync(self, get_files=None, get_catalog=None, force=False):
        if get_files is None:
            get_files = self.get_files

        if get_catalog is None:
            from rpi_courses import CourseCatalog
            get_catalog = CourseCatalog.from_string

        self.forced = force

        for filename in get_files(self.latest_semester):
            semester = self.semesters.get(filename)
            # if latest semester or newer semester
            if (not semester) or semester == self.latest_semester:
                try:
                    with closing(urllib2.urlopen(filename)) as page:
                        logger.debug("OPEN " + filename)
                        if force or (semester and semester.date_updated is not None):
                            last_mod = dateutil.parser.parse(dict(page.info())['last-modified']).replace(tzinfo=None)
                            if not force and last_mod <= semester.date_updated:
                                logger.debug("Skipping b/c of mod date: %r <= %r" % (last_mod, semester.date_updated))
                                continue
                        catalog = get_catalog(page.read(), filename)
                except urllib2.URLError:
                    logger.debug("Failed to fetch url (%r)" % (filename))
                    continue

                if not force and self.latest_semester and semester == self.latest_semester:
                    continue  # already up-to-date

                logger.debug("Semester: %r => %s-%s" % (
                    filename,
                    catalog.year,
                    catalog.month,
                ))
                semester_obj = None
                try:
                    semester_obj, created = Semester.objects.get_or_create(
                        year=catalog.year,
                        month=catalog.month,
                        defaults={
                            'visible': False,
                            'name': catalog.name,
                            'ref': filename,
                        })
                except IntegrityError as error:
                    logger.debug(' DUPLICATE SEMESTER ' + repr(semester_obj) + ': ' + repr(error))
                    continue
                self.create_courses(catalog, semester_obj)
                # catalog doesn't support this for now.
                # self.create_crosslistings(semester_obj, set(catalog.crosslistings.values()))
                semester_obj.save()  # => update date_updated property
                if created:
                    logger.debug(' CREATE SEMESTER ' + repr(semester_obj))
                    self.notifier.requires_notification()
                else:
                    logger.debug(' EXISTS SEMESTER ' + repr(semester_obj))
                if self.sections_changed:
                    sections_modified.send(sender=self, semester=semester_obj)

                self.clear_unused(semester_obj)


def remove_prereq_notes(section):
    all_notes = []
    for i in range(0, len(section.notes)):
        notes = section.notes[i]
        m = re.match("PRE-REQ: ", notes)
        if m:
            notes = ""
        all_notes.append(notes)
    section.notes = all_notes


def import_latest_semester(force=False):
    "Imports RPI data into the database."
    logger.debug('Importing latest semester: %s' % datetime.datetime.now().strftime('%A %x %X %f%Z'))
    notifier = SemesterNotifier()
    # ROCSRPIImporter().sync() # slower.. someone manually updates this I think?
    with transaction.atomic():
        SISRPIImporter(notifier).sync(force=force)
    notifier.notify()


def import_all_semesters(force=False):
    from rpi_courses import list_sis_files, list_rocs_xml_files
    logger.debug('Importing ALL semesters: %s' % datetime.datetime.now().strftime('%A %x %X %f%Z'))
    notifier = SemesterNotifier()
    urls = []
    urls.extend(list_sis_files())
    urls.extend(list_rocs_xml_files())
    for url in urls:
        print url
        if 'rocs' in url:
            importer = ROCSRPIImporter(notifier)
        else:
            importer = SISRPIImporter(notifier)
        with transaction.atomic():
            importer.sync(get_files=lambda *a, **k: [url])
    notifier.notify()


def import_catalog(a=False):
    catalog = parse_catalog(a)
    courses = Course.objects.all()
    for c in courses:
        key = str(c.department.code) + str(c.number)
        if key in catalog.keys():
            if 'description' in catalog[key].keys() and catalog[key]['description'] != "":
                c.description = catalog[key]['description']
            c.name = catalog[key]['title']
            c.prereqs = catalog[key]['prereqs']
            c.save()
    # uses >1GB of ram - currently unacceptable
    # add_cross_listing()


def import_data(force=False, all=False, catalog=False):
    if all:
        print 'Importing all semesters'
        import_all_semesters(force=force)
    else:
        import_latest_semester(force=force)
    if catalog:
        import_catalog(all=all)


def add_cross_listing():
    from itertools import product
    courses = Course.objects.all().prefetch_related('sections')
    for c in courses:
        sections = c.sections.all()
        cross_list = set()
        for s1, s2 in product(sections, sections):
            if s1 != s2 and s1.conflicts_with(s2) and s1.instructors == s2.instructors:
                cross_list.add(str(s1.id))
                cross_list.add(str(s2.id))
        sc = SectionCrosslisting(semester=Semester.objects.get(id=s1.semester), ref=",".join(cross_list[i]))
        for s in cross_list:
            courses.sections.get(id=s).crosslisted = sc.id


def export_schedule(crns):
    weekday_offset = {}
    for i, day in enumerate(DAYS):
        weekday_offset[day] = i

    tzinfo = pytz.timezone("America/New_York")
    calendar = Calendar()
    calendar.add('prodid', '-//YACS Course Schedule//EN')
    calendar.add('version', '2.0')
    sections = Section.objects.filter(crn__in=crns).prefetch_related('periods', 'section_times', 'section_times__period', 'course', 'semester')
    semester_start = datetime.datetime(sections[0].semester.year, sections[0].semester.month, 1, 0, tzinfo=pytz.timezone("America/New_York")).astimezone(pytz.utc)
    current = datetime.datetime.utcnow()
    semester_end = semester_start + datetime.timedelta(150)
    start_date = str(semester_start.date()).replace('-', '')
    end_date = str(current.date()).replace('-', '')
    # events = list(rpi_calendars.filter_related_events(rpi_calendars.download_events(rpi_calendars.get_url_by_range(start_date, end_date))))
    # events.extend(list(rpi_calendars.filter_related_events(rpi_calendars.download_events(rpi_calendars.get_url()))))
    events = list(rpi_calendars.filter_related_events(rpi_calendars.download_events(rpi_calendars.get_url())))
    days_off = []
    break_start = None
    break_end = None
    logger.debug('== Events ==')
    for e in events:
        is_after_start = e.start.date() > semester_start.date()
        logger.debug(' %s %s' % (e.start.date(), e.name))
        if re.search(str(sections[0].semester.name.split(' ')[0]) + ' ' + str(sections[0].semester.year), e.name) is not None:
            semester_start = e.start
            logger.debug(' -> Semester Start')
        if re.search(".*(no classes).*", e.name.lower()) is not None and is_after_start:
            days_off.append(e.start.date())
            logger.debug(' -> Day Off')
        if re.search(".*(spring break)|(thanksgiving).*", e.name.lower()) is not None and is_after_start:
            break_start = e.start
            logger.debug(' -> Range of days off')
        if re.search(".*(classes resume).*", e.name.lower()) is not None and break_start is not None:
            break_end = e.start
            logger.debug(' -> Range of days end')
        if re.search("(.*)study-review days", str(e.name).lower()) is not None and is_after_start:
            semester_end = e.start
            logger.debug(' -> Semester End')
            break
    if break_start is not None and break_end is not None:
        length = break_end - break_start
        for i in range(length.days):
            days_off.append((break_start + datetime.timedelta(i)).date())
    logger.debug('Semester start: %s' % semester_start)
    logger.debug('Semester end: %s' % semester_end)
    logger.debug('days off: %s' % days_off)
    for s in sections:
        for p in s.periods.all():
            event = Event()
            offset = weekday_offset[p.days_of_week[0]] - semester_start.weekday()
            if offset < 0:
                offset = 7 + offset
            begin = semester_start + datetime.timedelta(offset)
            event.add('summary', '%s - %s (%s)' % (s.course.code, s.course.name, s.crn))
            event.add('dtstart', datetime.datetime(begin.year, begin.month, begin.day, p.start.hour, p.start.minute, tzinfo=tzinfo))
            event.add('dtend', datetime.datetime(begin.year, begin.month, begin.day, p.end.hour, p.end.minute, tzinfo=tzinfo))
            days = []
            for d in p.days_of_week:
                days.append(d[:2])
            event.add('rrule', dict(
                freq='weekly',
                interval=1,
                byday=days,
                until=datetime.datetime(semester_end.year, semester_end.month, semester_end.day, p.end.hour, p.end.minute, tzinfo=tzinfo)))
            event.add('exdate', days_off)
            calendar.add_component(event)
    return calendar.to_ical().replace("EXDATE", "EXDATE;VALUE=DATE")
