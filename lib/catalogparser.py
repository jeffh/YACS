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
	course = {}
	soup = BeautifulSoup(course_page, convertEntities=BeautifulSoup.HTML_ENTITIES)
	title = re.search('([\w+\s]+) (\d+\w+) \- (.*)', soup.findAll('h1')[0].contents[0])
	course['department'] = title.group(1)
	course['num'] = title.group(2)
	course['title'] = title.group(3)
	desc = soup.findAll('hr')[0].nextSibling
	if re.search('<.*>', str(desc)) == None:
		course['description'] = desc
	return course

def parse_catalog():
	url = "catalog.rpi.edu"
	ids= get_catalogs(load_page(url))
	catalog_url = url+"/index.php?catoid="+ids[0]
	link_id = get_courses_link_id(load_page(catalog_url))
	courses_url = url+"/content.php?catoid="+ids[0]+"&navoid="+ link_id

	# parse need to parse out the coid (course id) from each department list of courses
	# then use it in the url: http://catalog.rpi.edu/preview_course.php?catoid=<id>&navoid<link_id>&coid=<course>
	# this will bring up the course descriptions and info and only the info for that course.
	courses = {}
	for e in DEPARTMENTS.keys():
		print "parsing", e			
		course_id = get_course_ids(load_page(courses_url, "filter[27]="+e))
		for c in range(0, len(course_id)):
			detail_url = url+"/preview_course.php?catoid="+ids[0]+"&navoid="+link_id+"&coid="+course_id[c]
			temp= get_course_detail(load_page(detail_url))
			courses[temp['department']+temp['num']] = temp 
	return courses
