import logging
import logging.handlers
import sys

DEBUG = True
LOG_FILENAME = 'logging'

logger = logging.getLogger('rpi_courses')
logger.setLevel(logging.DEBUG)

# fallback, so there's no warning of no handlers
logger.addHandler(logging.NullHandler())

if DEBUG:
    # stdout
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    logger.addHandler(handler)

    # stderr
    handler = logging.StreamHandler(sys.stderr)
    handler.setLevel(logging.ERROR)
    logger.addHandler(handler)


# where RPI's xml files are located.
DEFAULT_URL = "http://sis.rpi.edu/reg/rocs/"

# TODO: this may be good to parse (for textbooks)
HTML_URL = "http://sis.rpi.edu/stuclshr.htm"