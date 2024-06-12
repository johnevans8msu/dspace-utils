# standard library imports
import json
from unittest.mock import patch

# 3rd party library imports

# local imports
from dspace_utils import ThumbnailGenerator
from .common import TestCommon


@patch('dspace_utils.thumbnails.subprocess', autospec=True)
@patch('dspace_utils.thumbnails.Bitstream', autospec=True)
@patch('dspace_utils.thumbnails.Bundle', autospec=True)
@patch('dspace_utils.thumbnails.Item', autospec=True)
@patch('dspace_utils.common.DSpaceClient', autospec=True)
class TestSuite(TestCommon):

    def test_no_username(
        self, mock_client, mock_item, mock_bundle, mock_bitstream,
        mock_subprocess
    ):
        """
        Scenario:  no username is provided either by parameter or config file

        Expected result:  KeyError
        """
        handle = '1/18274'

        self.config.pop('password')
        s = json.dumps(self.config)
        with (
            patch('dspace_utils.common.pathlib.Path.read_text', return_value=s)
        ):
            with self.assertRaises(KeyError):
                ThumbnailGenerator(handle)

    def test_no_password(
        self, mock_client, mock_item, mock_bundle, mock_bitstream,
        mock_subprocess
    ):
        """
        Scenario:  no password either by parameter or config file

        Expected result:  KeyError
        """
        handle = '1/18274'

        self.config.pop('password')
        s = json.dumps(self.config)
        with (
            patch('dspace_utils.common.pathlib.Path.read_text', return_value=s)
        ):
            with self.assertRaises(KeyError):
                ThumbnailGenerator(handle)

    def test_api_endpoint(
        self, mock_client, mock_item, mock_bundle, mock_bitstream,
        mock_subprocess
    ):
        """
        Scenario:  no API endpoint in the config file

        Expected result:  KeyError
        """
        handle = '1/18274'

        self.config.pop('api_endpoint')
        s = json.dumps(self.config)
        with (
            patch('dspace_utils.common.pathlib.Path.read_text', return_value=s)
        ):
            with self.assertRaises(KeyError):
                ThumbnailGenerator(handle)

    def test_all_credentials_via_config_file(
        self, mock_client, mock_bundle, mock_bitstream, mock_item,
        mock_subprocess
    ):
        """
        Scenario:  all credentials provided via config file

        Expected result:  The thumbnail generator is constructed with no
        errors
        """
        config = {
            'username': 'somebody',
            'password': 'somepass',
            'api_endpoint': 'http://localhost/server/api',
        }
        s = json.dumps(config)
        with (
            patch('dspace_utils.common.pathlib.Path.read_text', return_value=s)
        ):
            ThumbnailGenerator('1/12345')
