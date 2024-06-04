# standard library imports
import logging
import sys

# 3rd party library imports
import psycopg2

# local imports


class DSpaceCommon(object):

    def __init__(self, verbose):

        # Get the page number of the expected thumbnail
        self.conn = psycopg2.connect('postgres://tomcat@localhost/dspace')
        self.cursor = self.conn.cursor()

        self.setup_logging(verbose)

    def setup_logging(self, log_level):

        level = getattr(logging, log_level.upper())

        self.logger = logging.getLogger('dspace-utils')
        self.logger.setLevel(level)

        format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        formatter = logging.Formatter(format)

        # send logs to the terminal
        h = logging.StreamHandler(sys.stdout)
        h.setLevel(level)
        h.setFormatter(formatter)
        self.logger.addHandler(h)
