import datetime
import urllib2

from BeautifulSoup import BeautifulStoneSoup

from rpi_courses.web import get
from rpi_courses.parser.features import *  # all object postfixed with '_feature' will get used.


class CourseCatalog(object):
    """Represents the RPI course catalog.

    This takes a BeautifulSoup instance (usually a BeautifulStoneSoup instance)
    allows an object-oriented method of accessing the data.
    """

    # this keeps the parsing separate from the actual data fetching.
    # We'll call each feature we imported that ends with '_feature'.
    FEATURES = [obj for name, obj in globals().iteritems() if name.endswith('_feature')]

    def __init__(self, soup=None):
        """Instanciates a CourseCatalog given a BeautifulSoup instance.
        Pass nothing to initiate an empty course catalog.
        """
        if soup is not None:
            self.parse(soup)

    @staticmethod
    def from_string(xml_str):
        "Creates a new CourseCatalog instance from an string containing xml."
        return CourseCatalog(BeautifulStoneSoup(xml_str,
            convertEntities=BeautifulStoneSoup.XML_ENTITIES
        ))

    @staticmethod
    def from_stream(stream):
        "Creates a new CourseCatalog instance from a filehandle-like stream."
        return CourseCatalog.from_string(stream.read())

    @staticmethod
    def from_file(filepath):
        "Creates a new CourseCatalog instance from a local filepath."
        with open(filepath) as f:
            return CourseCatalog.from_stream(f)

    @staticmethod
    def from_url(url):
        "Creates a new CourseCatalog instance from a given url."
        return CourseCatalog.from_string(get(url))

    def parse(self, soup):
        "Parses the soup instance as RPI's XML course catalog file."
        for feature in self.FEATURES:
            feature(self, soup)

    def crosslisted_with(self, crn):
        """Returns all the CRN courses crosslisted with the given crn.
        The returned crosslisting does not include the original CRN.
        """
        return tuple([c for c in self.crosslistings[crn].crns if c != crn])

    def find_courses(self, partial):
        """Finds all courses by a given substring. This is case-insensitive.
        """
        partial = partial.lower()
        keys = self.courses.keys()
        keys = [k for k in keys if k.lower().find(partial) != -1]
        courses = [self.courses[k] for k in keys]
        return list(set(courses))

    def get_courses(self):
        """Returns all course objects from this catalog.
        """
        return self.courses.values()

    def find_course_by_crn(self, crn):
        """Searches all courses by CRNs. Not particularly efficient.
        Returns None if not found.
        """
        for name, course in self.courses.iteritems():
            if crn in course:
                return course
        return None

    def find_course_and_crosslistings(self, partial):
        """Returns the given course and all other courses it is
        crosslisted with.
        """
        course = self.find_course(partial)
        crosslisted = self.crosslisted_with(course.crn)
        return (course,) + tuple(map(self.find_course_by_crn, crosslisted))
