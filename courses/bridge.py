"""All the data-importing functions are listed here for various colleges.
"""
from django.utils.importlib import import_module
import re
from timetable.courses.models import (Semester, Course, Department, Section,
    Period, SectionPeriod, OfferedFor, SectionCrosslisting, SemesterDepartment,
    SemesterSection)


class RPIImporter(object):
    """Handles the importation of RPI course data into the database."""

    FILE_RE = re.compile(r'(\d+)\.xml')
    def __init__(self):
        self.semesters = {}  # semester.ref: semester obj
        for semester in Semester.objects.all():
            self.semesters[semester.ref] = semester
        
        self.latest_semester = None
        if len(self.semesters) > 0:
            self.latest_semester = max(self.semesters.values())

    def sync(self, get_files=None, get_catalog=None):
        "Performs the updating of the database data from RPI's SIS"
        if get_files is None:
            from rpi_courses import list_xml_files
            get_files = list_xml_files
        
        if get_catalog is None:
            from rpi_courses import CourseCatalog
            get_catalog = CourseCatalog.from_url

        for filename in get_files():
            name = self.FILE_RE.finditer(filename).next().groups()[0]
            semester = self.semesters.get(name + '.xml')
            # if latest semester or newer semseter than what's in the database
            if (not semester) or (semester == self.latest_semester):
                catalog = get_catalog(filename)
                semester_obj, created = Semester.objects.get_or_create(
                    year=catalog.year,
                    month=catalog.month,
                    ref=name + '.xml',
                    defaults={
                        'name': catalog.name
                    })
                self.create_courses(catalog, semester_obj)
                self.create_crosslistings(semester_obj, set(catalog.crosslistings.values()))
                semester_obj.save()  # => update date_updated property

    def create_courses(self, catalog, semester_obj):
        "Inserts all the course data, including section information, into the database from the catalog."
        for course in catalog.get_courses():
            course_obj, created = Course.objects.get_or_create(
                number=course.num,
                department=self.get_or_create_department(semester_obj, code=course.dept),
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

    def create_sections(self, course, course_obj, semester_obj):
        "Inserts all section data, including time period information, into the database from the catalog."
        for section in course.sections:
            # TODO: encode prereqs / notes
            number = section.num
            if section.is_study_abroad:
                number = Section.STUDY_ABROAD
            section_obj, created = Section.objects.get_or_create(
                crn=section.crn,
                course=course_obj,
                defaults=dict(
                    number=number,
                    seats_taken=section.seats_taken,
                    seats_total=section.seats_total,
                )
            )
            SemesterSection.objects.get_or_create(
                semester=semester_obj,
                section=section_obj,
            )

            if not created:
                section_obj.number = number
                section_obj.seats_taken = section.seats_taken
                section_obj.seats_total = section.seats_total
                section_obj.save()

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
            period_obj, created = Period.objects.get_or_create(
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

    def get_or_create_department(self, semester_obj, code, name=''):
        dept, created = Department.objects.get_or_create(
            code=code,
            defaults={
                'name': name
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


def import_rpi():
    "Imports RPI data into the database."
    importer = RPIImporter()
    importer.sync()

def import_courses():
    "Runs the course importer specified in settings.py"
    from django.db import transaction

    with transaction.commit_on_success():
        from django.conf import settings

        module, funcname = settings.COURSES_COLLEGE_PARSER.rsplit('.', 1)
        mod = import_module(module)
        getattr(mod, funcname)()
