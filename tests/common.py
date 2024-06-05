# standard library imports
import unittest
from unittest.mock import patch

# 3rd party library imports
# from dspace_rest_client.client import DSpaceClient

# local imports


@patch('dspace_utils.common.psycopg2', autospec=True)
@patch('dspace_utils.thumbnails.DSpaceClient', autospec=True)
class TestCommon(unittest.TestCase):

    def setUp(self):
        self.DSPACE_API_ENDPOINT = 'https://lib1.lib.montana.edu/server/api'
        self.DSPACE_API_USERNAME = 'someone'
        self.DSPACE_API_PASSWORD = 'somepass'
        self.DSPACE_POSTGRES_URI = 'postgres://dspace@localhost/dspace'

        self.dspace_kwargs = dict(
            api_endpoint=self.DSPACE_API_ENDPOINT,
            username=self.DSPACE_API_USERNAME,
            password=self.DSPACE_API_PASSWORD,
            postgres_uri=self.DSPACE_POSTGRES_URI
        )
