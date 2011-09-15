"""web.py - Handles all the http interaction of getting the course
catalog data. This isn't your web.py web dev framework!
"""
import urllib2
from contextlib import closing
from BeautifulSoup import BeautifulSoup
from config import DEFAULT_URL

def get(url):
    """Performs a get request to a given url. Returns an empty str on error.
    """
    try:
        with closing(urllib2.urlopen(url)) as page:
            return page.read()
    except urllib2.URLError:
        return ""

def list_files(url=DEFAULT_URL):
    """Gets the contents of the given url.
    """
    soup = BeautifulSoup(get(url))
    if not url.endswith('/'):
        url += '/'
    files = []
    for elem in soup.findAll('a'):
        if elem['href'].startswith('?'):
            continue
        if elem.string.lower() == 'parent directory':
            continue
        files.append(url+elem['href'])
    return files

def is_xml(filename):
    "Returns True if the filename ends in an xml file extension."
    return filename.strip().endswith('.xml')

def list_xml_files(url=DEFAULT_URL):
    "Gets all the xml files."
    return list(filter(is_xml, list_files(url)))
