# standard library imports
import logging
import pathlib
import sys

# 3rd party library imports
import psycopg2
import yaml

# local imports


class DSpaceCommon(object):

    def __init__(self, verbose):

        self.setup_credentials()

        # Get the page number of the expected thumbnail
        self.conn = psycopg2.connect(self.postgres_uri)
        self.cursor = self.conn.cursor()

        self.setup_logging(verbose)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        pass

    def setup_credentials(self):

        p = pathlib.Path.home() / '.config/dspace-utils/dspace.yml'
        config = yaml.safe_load(p.read_text())

        self.username = config['username']
        self.password = config['password']
        self.api_endpoint = config['api_endpoint']
        self.postgres_uri = config['postgres_uri']

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
