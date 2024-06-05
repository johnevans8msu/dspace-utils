# standard library imports
import json
import unittest
from unittest.mock import patch

# 3rd party library imports

# local imports
from dspace_utils import ThumbnailGenerator


@patch('dspace_utils.thumbnails.subprocess', autospec=True)
@patch('dspace_utils.common.psycopg2', autospec=True)
@patch('dspace_utils.thumbnails.Bitstream', autospec=True)
@patch('dspace_utils.thumbnails.Bundle', autospec=True)
@patch('dspace_utils.thumbnails.Item', autospec=True)
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

    def test_no_postgresql_uri(
        self, mock_client, mock_item, mock_bundle, mock_bitstream,
        mock_psycopg2, mock_subprocess
    ):
        """
        Scenario:  no postgresql URI is provided either by parameter or config
        file

        Expected result:  RuntimeError
        """
        handle = '1/18274'

        config = {
            'username': 'someuser',
            'password': 'somepass',
            'api': 'http://localhost/server/api',
        }
        s = json.dumps(config)
        with (
            patch.dict(self.dspace_kwargs, {}, clear=True),
            patch('dspace_utils.common.pathlib.Path.read_text', return_value=s)
        ):
            with self.assertRaises(RuntimeError):
                ThumbnailGenerator(handle, **self.dspace_kwargs)

    def test_no_username(
        self, mock_client, mock_item, mock_bundle, mock_bitstream,
        mock_psycopg2, mock_subprocess
    ):
        """
        Scenario:  no username is provided either by parameter or config file

        Expected result:  RuntimeError
        """
        handle = '1/18274'

        config = {
            'password': 'somepass',
            'api': 'http://localhost/server/api',
            'postgresql_uri': 'postgresql://dspace@localhost/dspace',
        }
        s = json.dumps(config)
        with (
            patch.dict(self.dspace_kwargs, {}, clear=True),
            patch('dspace_utils.common.pathlib.Path.read_text', return_value=s)
        ):
            with self.assertRaises(RuntimeError):
                ThumbnailGenerator(handle, **self.dspace_kwargs)

    def test_username_via_environment_but_no_password(
        self, mock_client, mock_item, mock_bundle, mock_bitstream,
        mock_psycopg2, mock_subprocess
    ):
        """
        Scenario:  a username is provided via command line, but no password
        either by parameter or config file

        Expected result:  RuntimeError
        """
        handle = '1/18274'

        config = {
            'username': 'somebody',
            'api': 'http://localhost/server/api',
            'postgresql_uri': 'postgresql://dspace@localhost/dspace',
        }
        s = json.dumps(config)
        with (
            patch('dspace_utils.common.pathlib.Path.read_text', return_value=s)
        ):
            with self.assertRaises(RuntimeError):
                ThumbnailGenerator(handle)

    def test_username_via_config_and_password_via_cmdline(
        self, mock_client, mock_bundle, mock_bitstream, mock_item,
        mock_psycopg2, mock_subprocess
    ):
        """
        Scenario:  the username is not provided via the command line, but is
        provided via config file

        Expected result:  no errors
        """
        handle = '1/18274'

        config = {
            'username': 'somebody',
            'api': 'http://localhost/server/api',
            'postgres_uri': 'postgresql://dspace@localhost/dspace',
        }
        s = json.dumps(config)
        with (
            patch('dspace_utils.common.pathlib.Path.read_text', return_value=s)
        ):
            ThumbnailGenerator(handle, password='somepass')

    def test_credentials_via_config_file(
        self, mock_client, mock_bundle, mock_bitstream, mock_item,
        mock_psycopg2, mock_subprocess
    ):
        """
        Scenario:  all credentials provided via config file

        Expected result:  The thumbnail generator is constructed with no
        errors
        """
        config = {
            'username': 'somebody',
            'password': 'somepass',
            'api': 'http://localhost/server/api',
            'postgres_uri': 'postgresql://dspace@localhost/dspace',
        }
        s = json.dumps(config)
        with (
            patch('dspace_utils.common.pathlib.Path.read_text', return_value=s)
        ):
            ThumbnailGenerator('1/12345')
