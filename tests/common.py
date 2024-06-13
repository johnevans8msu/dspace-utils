# standard library imports
import unittest

# 3rd party library imports
# from dspace_rest_client.client import DSpaceClient

# local imports


class TestCommon(unittest.TestCase):

    def setUp(self):
        self.config = {
            'username': 'someuser',
            'password': 'somepass',
            'api_endpoint': 'http://localhost/server/api',
        }
