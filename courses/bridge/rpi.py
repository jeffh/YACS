"""All the data-importing functions are listed here for various colleges.
"""
import re
import urllib2
import dateutil.parser
import logging
import logging.handlers
import sys
import datetime
from contextlib import closing

from courses.models import (Semester, Course, Department, Section,
    Period, SectionPeriod, OfferedFor, SectionCrosslisting, SemesterDepartment,
    SemesterSection)
from courses.signals import sections_modified


logger = logging.getLogger(__file__)
logger.setLevel(logging.DEBUG)

try:
    NullHandler = logging.NullHandler
except AttributeError:
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

    def sync(self, get_files=None, get_catalog=None, foo=234234):
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
                    continue # already up-to-date

                logger.debug('found catalog for: %r %r' % (catalog.year, catalog.month))

                semester_obj, created = Semester.objects.get_or_create(
                    year=catalog.year,
                    month=catalog.month,
                    defaults={
                        'name': catalog.name,
                        'ref': name + '.xml',
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

    def create_courses(self, catalog, semester_obj):
        "Inserts all the course data, including section information, into the database from the catalog."
        for course in catalog.get_courses():
            course_obj, created = Course.objects.get_or_create(
                number=course.num,
                department=self.get_or_create_department(semester_obj, code=course.dept, name=course.full_dept),
                defaults=dict(
                    name=course.name,
                    min_credits=course.cred[0],
                    max_credits=course.cred[1],
                    grade_type=course.grade_type
                )
            )
            if not created:
                course_obj.name = course.name
                course_obj.min_credits, course_obj.max_credits = course.cred
                course_obj.grade_type = course.grade_type
                course_obj.save()
            OfferedFor.objects.get_or_create(course=course_obj, semester=semester_obj)
            self.create_sections(course, course_obj, semester_obj)
            logger.debug((' + ' if created else '   ' ) + course.name)

    def create_sections(self, course, course_obj, semester_obj):
        "Inserts all section data, including time period information, into the database from the catalog."
        for section in course.sections:
            # TODO: encode prereqs / notes
            section_obj, created = Section.objects.get_or_create(
                crn=section.crn,
                defaults=dict(
                    notes='\n'.join(section.notes),
                    number=section.num,
                    seats_taken=section.seats_taken,
                    seats_total=section.seats_total,
                    course=course_obj,
                )
            )
            SemesterSection.objects.get_or_create(
                semester=semester_obj,
                section=section_obj,
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
            sectionperiod_obj, created = SectionPeriod.objects.get_or_create(
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

    def create_crosslistings(self, semester_obj , crosslistings):
        "Creates all crosslisting information into the database for all the sections."
        for crosslisting in crosslistings:
            refid = ','.join(map(str, sorted(tuple(crosslisting.crns))))
            crosslisting_obj, created = SectionCrosslisting.objects.get_or_create(semester=semester_obj, ref=refid)
            Section.objects.filter(crn__in=crosslisting.crns).update(crosslisted=crosslisting_obj)

class SISRPIImporter(ROCSRPIImporter):

    def get_files(self, latest_semester):
        from rpi_courses import list_sis_files
        get_files = list_sis_files

        files = list_sis_files()
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

                if not force and self.latest_semester and semester == self.latest_semester: # and catalog.datetime <= self.latest_semester.date_updated:
                    continue # already up-to-date

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


def import_data(force=False):
    "Imports RPI data into the database."
    logger.debug('Update Time: %r' % datetime.datetime.now())
    period_count = Period.objects.count()
    Period.objects.all().delete()
    logger.debug('Removed %r periods!' % period_count)
    #ROCSRPIImporter().sync() # slower.. someone manually updates this I think?
    SISRPIImporter().sync(force=force)

def import_catalog():
    from catalogparser import *
    catalog = parse_catalog()
    courses = Course.objects.all()
    for c in courses:
	key = str(c.department.code)+str(c.number)
	if key in catalog.keys():
	    if 'description' in catalog[key].keys():
	        c.description = catalog[key]['description']
	    c.name = catalog[key]['title']
	    c.save()


