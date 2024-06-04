# standard library imports

# 3rd party library imports
import psycopg2

# local imports


class DSpaceCommon(object):

    def __init__(self):

        # Get the page number of the expected thumbnail
        self.conn = psycopg2.connect('postgres://tomcat@localhost/dspace')
        self.cursor = self.conn.cursor()
