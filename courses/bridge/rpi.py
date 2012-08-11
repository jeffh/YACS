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

from django.http import HttpResponse

from courses.models import (Semester, Course, Department, Section,
    Period, SectionPeriod, OfferedFor, SectionCrosslisting, SemesterDepartment)
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


class ROCSRPIImporter(object):
    """Handles the importation of RPI course data into the database."""
    FILE_RE = re.compile(r'(\d+)\.xml')

    def __init__(self):
        self.semesters = {}  # semester.ref: semester obj
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

                semester_obj, created = Semester.objects.get_or_create(
                    year=catalog.year,
                    month=catalog.month,
                    defaults={
                        'name': catalog.name,
                        'ref': filename,
                    })
                self.create_courses(catalog, semester_obj)
                self.create_crosslistings(semester_obj, set(catalog.crosslistings.values()))
                semester_obj.save()  # => update date_updated property
                if created:
                    logger.debug(' CREATE SEMESTER ' + repr(semester_obj))
                else:
                    logger.debug(' EXISTS SEMESTER ' + repr(semester_obj))
                if self.sections_changed:
                    sections_modified.send(sender=self, semester=semester_obj)

                self.clear_unused(semester_obj)

    def create_courses(self, catalog, semester_obj):
        "Inserts all the course data, including section information, into the database from the catalog."
        list = self.add_comm_intense(catalog, semester_obj)
        for course in catalog.get_courses():
            comm = False
            for course_name in list:
                if course.name == course_name:
                    comm = True
            course_obj, created = Course.objects.get_or_create(
                number=course.num,
                department=self.get_or_create_department(semester_obj, code=course.dept, name=course.full_dept),
                defaults=dict(
                    min_credits=course.cred[0],
                    max_credits=course.cred[1],
                    grade_type=course.grade_type,
                    is_comm_intense=comm,
                )
            )
            if not created:
                if self.forced:
                    course_obj.name = course.name
                course_obj.min_credits, course_obj.max_credits = course.cred
                course_obj.grade_type = course.grade_type
                course_obj.is_comm_intense = comm
                course_obj.save()
            OfferedFor.objects.get_or_create(course=course_obj, semester=semester_obj)
            self.create_sections(course, course_obj, semester_obj)
            logger.debug((' + ' if created else '   ') + course.name)

    def add_comm_intense(self, catalog, semester):
        from rpi_courses import get_comm_file
        pdf = get_comm_file(semester)
        list = []
        crns = re.findall(r"\d{5}\s[A-Z]{4}", pdf)
        print "Found " + str(len(crns)) + " communication intensive sections"
        for i in crns:
            course = catalog.find_course_by_crn(int(i.split()[0]))
            if (course != None):
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
            day = 0
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
        get_files = list_sis_files_for_date

        files = list_sis_files_for_date()
        if latest_semester:
            files.append(latest_semester.ref)

        now = datetime.datetime.now()
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
                        catalog = get_catalog(page.read())
                except urllib2.URLError:
                    logger.debug("Failed to fetch url (%r)" % (filename))
                    continue

                if not force and self.latest_semester and semester == self.latest_semester:
                    continue  # already up-to-date

                semester_obj, created = Semester.objects.get_or_create(
                    year=catalog.year,
                    month=catalog.month,
                    ref=filename,
                    defaults={
                        'name': catalog.name
                    })
                self.create_courses(catalog, semester_obj)
                # catalog doesn't support this for now.
                #self.create_crosslistings(semester_obj, set(catalog.crosslistings.values()))
                semester_obj.save()  # => update date_updated property
                if created:
                    logger.debug(' CREATE SEMESTER ' + repr(semester_obj))
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
    logger.debug('Update Time: %r' % datetime.datetime.now())
    #period_count = Period.objects.count()
    #Period.objects.all().delete()
    #logger.debug('Removed %r periods!' % period_count)
    #ROCSRPIImporter().sync() # slower.. someone manually updates this I think?
    SISRPIImporter().sync(force=force)


def import_all_semesters(force=False):
    from rpi_courses import list_sis_files, list_rocs_xml_files
    urls = []
    urls.extend(list_sis_files())
    urls.extend(list_rocs_xml_files())
    for url in urls:
        print url
        if 'rocs' in url:
            importer = ROCSRPIImporter()
        else:
            importer = SISRPIImporter()
        importer.sync(get_files=lambda *a, **k: [url])


def import_data(force=False, all=False):
    if all:
        print 'Importing all semesters'
        import_all_semesters(force=force)
    else:
        import_latest_semester(force=force)


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
    #add_cross_listing()


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
    calendar = Calendar()
    calendar.add('prodid', '-//YACS Course Schedule//EN')
    calendar.add('version', '2.0')
    sections = Section.objects.filter(crn__in=crns).prefetch_related('periods', 'section_times', 'section_times__period', 'course', 'semester')
    semester_start = datetime.datetime(sections[0].semester.year, sections[0].semester.month, 1, 0, tzinfo=pytz.timezone("America/New_York")).astimezone(pytz.utc)
    found = False
    current = datetime.datetime.utcnow()
    semester_end = semester_start + datetime.timedelta(150)
    events = list(rpi_calendars.filter_related_events(rpi_calendars.download_events(rpi_calendars.get_url_by_range(str(semester_start.date()).replace('-', ''), str(current.date()).replace('-', '')))))
    events.extend(list(rpi_calendars.filter_related_events(rpi_calendars.download_events(rpi_calendars.get_url()))))
    days_off = []
    break_start = None
    break_end = None
    for e in events:
        if re.search(str(sections[0].semester.name.split(' ')[0]) + ' ' + str(sections[0].semester.year), e.name) != None:
            semester_start = e.start
            found = True
        if re.search(".*(no classes).*", e.name.lower()) != None and found:
            days_off.append([e.start.date()])
        if re.search(".*(spring break)|(thanksgiving).*", e.name.lower()) != None and found:
            break_start = e.start
        if re.search(".*(classes resume).*", e.name.lower()) != None and break_start != None:
            break_end = e.start
        if re.search("(.*)study-review days", str(e.name).lower()) != None and found:
            semester_end = e.start
            break
    if break_start != None and break_end != None:
        length = break_end - break_start
        for i in range(length.days):
            days_off.append([(break_start + datetime.timedelta(i)).date()])
    for s in sections:
        for p in s.periods.all():
            event = Event()
            offset = weekday_offset[p.days_of_week[0]] - semester_start.weekday()
            if offset < 0:
                offset = 7 + offset
            begin = semester_start + datetime.timedelta(offset)
            event.add('summary', '%s - %s (%s)' % (s.course.code, s.course.name, s.crn))
            event.add('dtstart', datetime.datetime(begin.year, begin.month, begin.day, p.start.hour, p.start.minute, tzinfo=pytz.timezone("America/New_York")).astimezone(pytz.utc))
            event.add('dtend', datetime.datetime(begin.year, begin.month, begin.day, p.end.hour, p.end.minute, tzinfo=pytz.timezone("America/New_York")).astimezone(pytz.utc))
            days = []
            for d in p.days_of_week:
                days.append(d[:2])
            event.add('rrule', dict(
                freq='weekly',
                interval=1,
                byday=days,
                until=datetime.datetime(semester_end.year, semester_end.month, semester_end.day, p.end.hour, p.end.minute, tzinfo=pytz.timezone("America/New_York")).astimezone(pytz.utc)))
            event.add('exdate', days_off)
            calendar.add_component(event)
    output = str(calendar).replace("EXDATE", "EXDATE;VALUE=DATE")
    return output
