# standard library imports
import logging
import pathlib
import sys

# 3rd party library imports
import psycopg2
import yaml

# local imports


class DSpaceCommon(object):

    def __init__(self, verbose, username, password, api):

        self.setup_credentials(username, password, api)

        # Get the page number of the expected thumbnail
        self.conn = psycopg2.connect('postgres://tomcat@localhost/dspace')
        self.cursor = self.conn.cursor()

        self.setup_logging(verbose)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        pass

    def setup_credentials(self, username, password, api):

        self.username = username
        self.password = password
        self.api = api

        p = pathlib.Path.home() / '.config/dspace-utils/dspace.yml'
        try:
            config = yaml.safe_load(p.read_text())
        except FileNotFoundError:
            config = None

        try:
            if self.username is None:
                self.username = config['username']

            if self.password is None:
                self.password = config['password']

            if self.api is None:
                self.api = config['api']

        except KeyError as e:
            msg = (
                'Not all credentials provided, neither by config file nor by '
                f'parameters.  {e}'
            )
            raise RuntimeError(msg)

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
