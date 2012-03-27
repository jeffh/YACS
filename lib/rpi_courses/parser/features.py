"""features.py - Implements all parsing of the XML file.

All functions related to parsing the XML file are here. To be
automatically imported by the CourseCatalog class, postfix the
function name with '_feature'
"""
import datetime

from rpi_courses.utils import FrozenDict, safeInt
from rpi_courses.config import logger, DEBUG
from rpi_courses.models import CrossListing, Course


def timestamp_feature(catalog, soup):
    """The datetime the xml file was last modified.
    """
    catalog.timestamp = int(soup.coursedb['timestamp'])
    catalog.datetime = datetime.datetime.fromtimestamp(catalog.timestamp)
    logger.info('Catalog last updated on %s' % catalog.datetime)


def semester_feature(catalog, soup):
    """The year and semester information that this xml file hold courses for.
    """
    raw = soup.coursedb['semesternumber']
    catalog.year = int(raw[:4])

    month_mapping = {1: 'Spring', 5: 'Summer', 9: 'Fall'}
    catalog.month = int(raw[4:])
    catalog.semester = month_mapping[catalog.month]

    catalog.name = soup.coursedb['semesterdesc']

    logger.info('Catalog type: %s' % catalog.name)


def crosslisting_feature(catalog, soup):
    """Parses all the crosslistings. These refer to the similar CRNs,
    such as a grad & undergrad level course.
    """
    listing = {}
    for elem in soup.coursedb.findAll('crosslisting'):
        seats = int(elem['seats'])
        crns = [safeInt(crn.string) for crn in elem.findAll('crn')]

        # we want to refer to the same object to save space
        cl = CrossListing(crns, seats)
        for crn in crns:
            listing[crn] = cl
    catalog.crosslistings = FrozenDict(listing)

    logger.info('Catalog has %d course crosslistings' % len(catalog.crosslistings))


def course_feature(catalog, soup):
    """Parses all the courses (AKA, the most important part).
    """
    courses = {}
    course_crns = {}
    for course in soup.findAll('course'):
        c = Course.from_soup_tag(course)
        courses[str(c)] = c
    catalog.courses = courses
    catalog.courses
    logger.info('Catalog has %d courses' % len(courses))
