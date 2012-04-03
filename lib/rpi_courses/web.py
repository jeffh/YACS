"""web.py - Handles all the http interaction of getting the course
catalog data. This isn't your web.py web dev framework!
"""
import urllib2
import datetime
import tempfile
import pyPdf
from contextlib import closing

from BeautifulSoup import BeautifulSoup

from config import ROCS_URL, SIS_URL, COMM_URL


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


def list_sis_files_for_date(date=None, url_base=SIS_URL):
    date = date or datetime.datetime.now()
    format = '%szs%.4d%.2d.htm'
    base = []
    months = (1, 5, 9)
    prev_m = None
    for m in months:
        if m >= date.month:
            base.append(format % (url_base, date.year, m))
            if prev_m and prev_m < date.month:
                base.append(format % (url_base, date.year, prev_m))
        prev_m = m
    if not base:
        base.append(format % (url_base, date.year + 1, 1))
    return base


def list_sis_files(url_base=SIS_URL):
    date = datetime.date(year=2011, month=1, day=1)
    today = datetime.date.today()
    urls = []
    while date.year <= today.year:
        urls.extend(list_sis_files_for_date(date, url_base=url_base))
        date = datetime.date(year=date.year + 1, month=1, day=1)
    return urls


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
        files.append(url + elem['href'])
    return files


def is_xml(filename):
    "Returns True if the filename ends in an xml file extension."
    return filename.strip().endswith('.xml')


def list_rocs_xml_files(url=ROCS_URL):
    "Gets all the xml files."
    return list(filter(is_xml, list_rocs_files(url)))


def get_comm_file(date, base_url=COMM_URL):
    format = '%.4d.pdf'
    if date.month == 9:
        url = base_url + "Fall" + str(format % (date.year))
    else:
        url = base_url + "Spring" + str(format % (date.year))

    req = urllib2.Request(url)
    print "Getting communication intensive list from: " + url

    try:
        f = urllib2.urlopen(req)
        temp = tempfile.NamedTemporaryFile()
        temp.write(f.read())
        temp.seek(0)
    except urllib2.HTTPError, e:
        print "HTTP Error:", e.code, url
    except urllib2.URLError, e:
        print "URL Error:", e.reason, url

    full_text = ""
    pdf = pyPdf.PdfFileReader(open(temp.name, 'rb'))
    for page in pdf.pages:
        full_text += page.extractText()

    temp.close()
    return full_text.strip()
