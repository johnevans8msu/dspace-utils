"""
Test suite that only tests common functionality.
"""

# standard library imports
import json
from unittest.mock import patch

# 3rd party library imports
# from dspace_rest_client.client import DSpaceClient

# local imports
from dspace_utils import ThumbnailGenerator
from .common import TestCommon


@patch('dspace_utils.common.DSpaceClient', autospec=True)
class TestSuite(TestCommon):

    def test_smoke(self, mock_client):
        """
        Scenario:  test basic operation with INFO logging

        Expected result:  logging is verified
        """

        with (
            patch(
                'dspace_utils.common.pathlib.Path.read_text',
                return_value=json.dumps(self.config),
            ),
        ):
            with self.assertLogs():
                ThumbnailGenerator('1/12345', verbose='INFO')
