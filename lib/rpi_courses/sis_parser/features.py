"""features.py - Implements all parsing of the XML file.

All functions related to parsing the XML file are here. To be
automatically imported by the CourseCatalog class, postfix the
function name with '_feature'
"""
import datetime
from rpi_courses.utils import FrozenDict, safeInt
from rpi_courses.config import logger, DEBUG
from rpi_courses.models import CrossListing, Course, Period, Section


def timestamp_feature(catalog, soup):
    """The datetime the xml file was last modified.
    """
    # there's really no "time created", we're using the date the courses are listed for...
    epoch = 1318790434
    catalog.timestamp = int(float(soup.title.text)) + epoch
    catalog.datetime = datetime.datetime.fromtimestamp(catalog.timestamp)
    logger.info('Catalog last updated on %s' % catalog.datetime)


def semester_feature(catalog, soup):
    """The year and semester information that this xml file hold courses for.
    """
    catalog.name = soup.find('h3').text.strip()
    raw = soup.find('h3').text.split(' Session ')
    catalog.year = int(raw[1])

    month_mapping = {'Spring': 1, 'Summer': 5, 'Fall': 9}
    catalog.semester = raw[0]
    catalog.month = month_mapping[raw[0]]

    logger.info('Catalog type: %s' % catalog.name)


#def crosslisting_feature(catalog, soup):
#    """Parses all the crosslistings. These refer to the similar CRNs,
#    such as a grad & undergrad level course.
#    """
#    listing = {}
#    for elem in soup.coursedb.findAll('crosslisting'):
#        seats = int(elem['seats'])
#        crns = [safeInt(crn.string) for crn in elem.findAll('crn')]
#
#        # we want to refer to the same object to save space
#        cl = CrossListing(crns, seats)
#        for crn in crns:
#            listing[crn] = cl
#    catalog.crosslistings = FrozenDict(listing)
#
#    logger.info('Catalog has %d course crosslistings' % len(catalog.crosslistings))


def course_feature(catalog, soup):
    """Parses all the courses (AKA, the most important part).
    """
    courses = {}
    count = 0
    for course_data in parse_tables(soup):
        c = create_course(course_data)
        count += 1
        courses[str(c)] = c
    catalog.courses = FrozenDict(courses)
    logger.info('Catalog has %d courses (manual: %d)' % (len(courses), count))


# INTERNAL FUNCTIONS


def create_period(period_data):
    return Period(**period_data)


def create_section(section_data):
    data = dict(section_data)
    data['periods'] = tuple(create_period(p) for p in section_data['periods'])
    return Section(**data)


def create_course(course_data):
    data = dict(course_data)
    data['sections'] = tuple(create_section(s) for s in course_data['sections'])
    return Course(**data)


class_days = {
    'M': 0, 'T': 1, 'W': 2, 'R': 3, 'F': 4
}


def extract_period(cells, period, G):
    # possible choices
    # [u'CRN Course-Sec', u'Course Title', u'Class Type', u'Cred Hrs', u'Gr Tp', u'Building/Room'
    # u'Class Days', u'Start Time', u'End Time', u'Instructor', u'Max Enrl', u'Enrl', u'Sts Rmng']
    #
    # use G(cells, NAME)
    #
    # class type
    period['type'] = G(cells, 'Class Type').text
    # class days
    period['int_days'] = list(class_days[x] for x in G(cells, 'Class Days').text if x.strip() != '')
    # start-time & end-time (we need end-time to figure out if it's in the morning or not)

    def is_tba(s):
        return not s or 'TBA' in s.upper()
    period['start'], period['end'] = G(cells, 'Start Time').text, G(cells, 'End Time').text

    if not is_tba(period['start']) and not is_tba(period['end']):

        is_pm = period['end'].upper().endswith('PM')

        def get_time(s):
            return int(s.replace(':', ''))

        period['start'] = get_time(period['start'])
        period['end'] = get_time(period['end'][:-2])

        if is_pm:
            period['start'] += 1200
            period['end'] += 1200
            if period['start'] >= 2400:
                period['start'] -= 1200
            if period['end'] >= 2400:
                period['end'] -= 1200

            # this covers the case of getting 11:00 - 1:50PM
            # we're assuming there's no classes from the evening that go beyond midnight.
            if period['start'] > period['end']:
                period['start'] -= 1200

        period['start'], period['end'] = str(period['start']), str(period['end'])
    # instructor
    node = G(cells, 'Instructor')
    period['instructor'] = node.text.strip() if node else ''
    # location
    node = G(cells, 'Building/Room')
    period['location'] = node.text.strip() if node else ''


def parse_tables(node):
    courses = []
    cache = {}
    last_course = last_section = last_period = None
    rows = node.findAll('tr')

    columns = [None] * len(rows[0].findAll('th'))

    for i, row in enumerate(rows[0].findAll('th')):
        columns[i] = row.text.strip()

    for i, row in enumerate(rows[1].findAll('th')):
        columns[i] += ' ' + row.text.strip() if row.text else ''

    columns = tuple(x.strip() for x in columns)

    print columns
    # possible choices
    # [u'CRN Course-Sec', u'Course Title', u'Class Type', u'Cred Hrs', u'Gr Tp', u'Building/Room'
    # u'Class Days', u'Start Time', u'End Time', u'Instructor', u'Max Enrl', u'Enrl', u'Sts Rmng']

    def G(cells, name):
        try:
            return cells[columns.index(name)]
        except (IndexError, ValueError):
            return None

    for row in rows[2:]:
        course = {'sections': []}
        section = {'notes': set(), 'periods': []}
        period = {}
        cells = row.findAll('td')
        # if we got to a new course / section
        if len(cells) < 2:
            continue
        elif cells[0].text.strip() != '':
            # <crn> <code>-<num>-<sec>
            parts = G(cells, 'CRN Course-Sec').text.split(' ', 1)
            section['crn'] = parts[0]
            course['dept'], course['num'], section['num'] = parts[1].split('-', 2)
            # course name
            course['name'] = G(cells, 'Course Title').text.strip()
            existing_obj = cache.get(course['name'] + course['dept'] + course['num'])
            if existing_obj:
                course = existing_obj

            # credit hours (eg - '1' or '1-6')
            parts = G(cells, 'Cred Hrs').text.split('-', 1)
            course['credmin'], course['credmax'] = parts[0], parts[1] if len(parts) > 1 else parts[0]
            # grade_type
            grade_type = G(cells, 'Gr Tp')
            if grade_type:
                course['grade_type'] = {
                    'SU': 'Satisfactory/Unsatisfactory',
                }.get(grade_type.text, grade_type.text)
            # seats total
            node = G(cells, 'Max Enrl')
            if node:
                section['total'] = int(node.text) if node.text.strip() else 0
            else:
                section['total'] = ''
            # seats taken
            node = G(cells, 'Enrl')
            if node:
                section['taken'] = int(node.text) if node.text.strip() else 0
            else:
                section['taken'] = ''
            # textbook link? could be usedful
            # section['textbook_link'] = cells[12].find('a')['href']
            extract_period(cells, period, G)

            # link up
            section['periods'].append(period)
            course['sections'].append(section)
            cache[course['name'] + course['dept'] + course['num']] = course

            if not existing_obj:
                courses.append(course)

            last_course, last_section, last_period = course, section, period

        elif 'NOTE:' in cells[1].text.strip():  # process note
            course, section = last_course, last_section
            section['notes'].add(cells[2].text.strip())

        else:  # process a new period type
            course, section = last_course, last_section

            period = last_period.copy()
            extract_period(cells, period, G)
            section['periods'].append(period)

    return courses
