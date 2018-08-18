'''
Script to handle logging
'''

import logging
from _colors import COLOR

# Configure the logger object and set logging level
logger = logging.getLogger()
# Add log handler
ch = logging.StreamHandler()
# Add message format
formatter = logging.Formatter(
    '%(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)
logger.setLevel(logging.DEBUG)


def warning(msg, sign="app"):
    '''Logs a warning message'''

    logger.warning(COLOR["YELLOW"] + sign + ": " + msg + COLOR["END"])


def error(msg, sign="app"):
    '''Logs an error message'''

    logger.error(COLOR["RED"] + sign + ": " + msg + COLOR["END"])


def debug(msg, sign="app"):
    '''Logs a debug message'''

    logger.debug(COLOR["CYAN"] + sign + ": " + msg + COLOR["END"])
