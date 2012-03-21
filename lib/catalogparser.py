import urllib2
import re
from BeautifulSoup import BeautifulSoup
from rpi_courses.config import DEPARTMENTS

# load a page given the url, do not include the "http://" as it is already included.
def load_page(url, data = None):
    try:
        website = urllib2.urlopen("http://"+url, data)
        return website.read()
    except urllib2.URLError, e:
        print "Could not retrieve catalog url because:", e.reason[1]

# get the list of catalogs of all the available years from the front page
def get_catalogs(frontpage):
    ids = re.findall('<option value="\d+"\s*\w*>Rensselaer Catalog', frontpage)
    out = []
    for i in ids:
        out.append(re.search("\d+", i).group(0))
    return out

# get the link id to all the courses for a catalog page
def get_courses_link_id(page):
    link = re.search('\d+" class="navbar" \w+="\d+">Courses</a>', page)
    return re.search("\d+", link.group(0)).group(0)

def get_course_ids(department_page):
    ids = re.findall('coid=\d+"', department_page)
    out = []
    for i in ids:
        out.append(re.search('\d+', i).group(0))
    return out

def get_course_detail(course_page):
    course_page = re.sub('<br */?>', '\n', course_page)
    soup = BeautifulSoup(course_page, convertEntities=BeautifulSoup.HTML_ENTITIES)
    title_text = soup.findAll('h1 h2 h3 h4 h5 h6'.split(' '))[0].text
    title = re.search('([\w+\s]+) (\d+\w+) \- (.*)', title_text)
    course = {
        'department': title.group(1),
        'num': title.group(2),
        'title': title.group(3),
        'description': get_course_description(soup.findAll('hr')[0].nextSibling)
    }
    return course

def get_course_description(tag):
    current = tag
    contents = []
    while current and getattr(current, 'name', 'text') not in ('em', 'strong'):
        contents.append(getattr(tag, 'text', tag.string))
        current = current.nextSibling
    return ''.join(contents).strip()

def special(tags):
    contents = re.findall('>??(.*?)<.*?>', tags)
    return "".join(contents)

def parse_catalog(a=False):
    courses = {}
    url = "catalog.rpi.edu"
    ids= get_catalogs(load_page(url))
    if a:
        catalogs = len(ids)
    else:
        catalogs = 1
    for i in range(catalogs):
        catalog_url = url+"/index.php?catoid="+ids[i]
        link_id = get_courses_link_id(load_page(catalog_url))
        courses_url = url+"/content.php?catoid="+ids[i]+"&navoid="+ link_id

        # parse need to parse out the coid (course id) from each department list of courses
        # then use it in the url: http://catalog.rpi.edu/preview_course.php?catoid=<id>&navoid<link_id>&coid=<course>
        # this will bring up the course descriptions and info and only the info for that course.
        for e in DEPARTMENTS.keys():
            print "parsing", e
            course_id = get_course_ids(load_page(courses_url, "filter[27]="+e))
            for c in range(0, len(course_id)):
                detail_url = url+"/preview_course.php?catoid="+ids[i]+"&coid="+course_id[c]
                temp= get_course_detail(load_page(detail_url))
                key = temp['department'] + temp['num']
                if key not in courses or temp['description'].strip() != '':
                    courses[key] = temp
    return courses
