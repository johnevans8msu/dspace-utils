# standard library imports
import unittest
from unittest.mock import patch

# 3rd party library imports
# from dspace_rest_client.client import DSpaceClient

# local imports
from dspace_utils import ThumbnailGenerator


@patch.dict('dspace_utils.thumbnails.os.environ', {}, clear=True)
@patch('dspace_utils.common.psycopg2', autospec=True)
@patch('dspace_utils.thumbnails.DSpaceClient', autospec=True)
class TestSuite(unittest.TestCase):

    def setUp(self):
        self.DSPACE_API_ENDPOINT = 'https://lib1.lib.montana.edu/server/api'
        self.DSPACE_API_USERNAME = 'someone'
        self.DSPACE_API_PASSWORD = 'somepass'

        self.dspace_kwargs = dict(
            api_endpoint=self.DSPACE_API_ENDPOINT,
            username=self.DSPACE_API_USERNAME,
            password=self.DSPACE_API_PASSWORD
        )

    def test_smoke(self, mock_client, mock_psycopg2):
        """
        Scenario:  test basic operation with INFO logging

        Expected result:  logging is verified
        """

        with self.assertLogs():
            ThumbnailGenerator('1/12345', verbose='INFO', **self.dspace_kwargs)
