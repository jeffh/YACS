"""web.py - Handles all the http interaction of getting the course
catalog data. This isn't your web.py web dev framework!
"""
import urllib2
import datetime
from contextlib import closing

from BeautifulSoup import BeautifulSoup

from config import ROCS_URL, SIS_URL


def get(url, last_modified=None):
    """Performs a get request to a given url. Returns an empty str on error.
    """
    try:
        with closing(urllib2.urlopen(url)) as page:
            if last_modified is not None:
                last_mod = dateutil.parser.parse(dict(page.info())['last-modified'])
                if last_mod <= last_modified:
                    return ""
            return page.read()
    except urllib2.URLError:
        return ""


def list_sis_files(datetimes, url_base=SIS_URL):
    today = datetime.datetime.now()
    format = '%szs%.4d%.2d.htm'
    base = []
    months = (1, 5, 9)
    for m in months:
        if m >= today.month:
            base.append(format % (url_base, today.year, m))
            break
    if not base:
            base.append(format % (url_base, today.year + 1, 1))
    for dt in datetimes:
        base.append(format % (url_base, dt.year, dt.month))
    return base


def list_rocs_files(url=ROCS_URL):
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


def list_rocs_xml_files(url=ROCS_URL):
    "Gets all the xml files."
    return list(filter(is_xml, list_rocs_files(url)))

