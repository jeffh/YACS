import logging
import logging.handlers
import sys


DEBUG = True
LOG_FILENAME = 'logging'

logger = logging.getLogger('rpi_courses')
logger.setLevel(logging.DEBUG)


if hasattr(logging, 'NullHandler'):
    NullHandler = logging.NullHandler
else:
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass

# fallback, so there's no warning of no handlers
logger.addHandler(NullHandler())

if DEBUG:
    # stdout
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    logger.addHandler(handler)

    # stderr
    handler = logging.StreamHandler(sys.stderr)
    handler.setLevel(logging.ERROR)
    logger.addHandler(handler)

SIS_URL = "http://sis.rpi.edu/reg/"
# where ROCS's xml files are located.
ROCS_URL = "http://sis.rpi.edu/reg/rocs/"

# TODO: this may be good to parse (for textbooks)
HTML_URL = "http://sis.rpi.edu/stuclshr.htm"

# it would be best to get this data from a reliable data source:
# like the course catalog: http://catalog.rpi.edu/content.php?catoid=10&navoid=232
# instead of manually entering this data.

# code: name
DEPARTMENTS = dict(
    ADMN="Administration",
    ARCH="Architecture",
    ARTS="Arts",
    ASTR="Astronomy",
    BCBP="Biochemistry and Biophysics",
    BIOL="Biology",
    BMED="Biomedical Engineering",
    CHEM="Chemistry",
    CHME="Chemical Engineering",
    CISH="Computer Science at Hartford",
    CIVL="Civil Engineering",
    COGS="Cognitive Science",
    COOP="Cooperative Education",
    COMM="Communication",
    CSCI="Computer Science",
    ECON="Economics",
    ECSE="Electrical, Computer, and Systems Engineering",
    ENGR="General Engineering",
    ENVE="Environmental Engineering",
    EPOW="Electrical, Computer, and Systems Engineering",
    ERTH="Earth and Environmental Sciences",
    ESCI="Engineering Science",
    EXCH="Exchange (Study Abroad)",
    IENV="Interdisciplinary Environmental",
    IHSS="Interdisciplinary Studies",
    ISCI="Interdisciplinary Science",
    ISYE="Industrial and Systems Engineering",
    ITWS="Information Technology and Web Science",
    LANG="Foreign Languages",
    LGHT="Lighting",
    LITR="Literature",
    MANE="Mechanical, Aerospace, and Nuclear Engineering",
    MATH="Mathematics",
    MATP="Mathematical Programming, Probability, and Statistics",
    MGMT="Management",
    MTLE="Materials Science and Engineering",
    NSST="Natural Science for School Teachers",
    PHIL="Philosophy",
    PHYS="Physics",
    PSYC="Psychology",
    STSH="Science and Technology Studies (Humanities Courses)",
    STSS="Science and Technology Studies (Social Sciences Courses)",
    USAF="Aerospace Studies (Air Force ROTC)",
    USAR="Military Science (Army ROTC)",
    USNA="Naval Science (Navy ROTC)",
    WRIT="Writing",
)
