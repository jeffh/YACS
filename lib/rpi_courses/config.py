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
