# standard library imports
from collections import namedtuple
import unittest
from unittest.mock import patch

# 3rd party library imports
# from dspace_rest_client.client import DSpaceClient

# local imports
from dspace_utils import ThumbnailGenerator
from dspace_utils.thumbnails import Bundle


@patch.dict('dspace_utils.thumbnails.os.environ', {}, clear=True)
@patch('dspace_utils.thumbnails.subprocess', autospec=True)
@patch('dspace_utils.thumbnails.psycopg2', autospec=True)
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

    def test_smoke(
        self, mock_client, mock_item, mock_bundle, mock_bitstream,
        mock_psycopg2, mock_subprocess
    ):
        """
        Scenario:  test basic operation
        """

        # make up some fake bundles
        bundles = [Bundle(), Bundle()]
        bundles[0].uuid = '12345678-1234-1234-1234-123456789abc'
        bundles[0].name = 'ORIGINAL'
        bundles[1].uuid = '12345678-1234-1234-1234-123456789abd'
        bundles[1].name = 'THUMBNAIL'
        mock_client.return_value.get_bundles.return_value = bundles

        mock_psycopg2.connect.return_value.cursor.return_value.fetchone.return_value = (10,)  # noqa : E501
        # make up some fake bitstreams
        bitstreams = [mock_bitstream(), mock_bitstream()]
        bitstreams[0].uuid = '12345678-1234-1234-1234-123456789abc'
        bitstreams[0].name = 'ORIGINAL'
        bitstreams[1].uuid = '12345678-1234-1234-1234-123456789abd'
        bitstreams[1].name = 'THUMBNAIL'
        mock_client.return_value.get_bitstreams.return_value = bitstreams

        # make up downloaded content for the PDF bitstream
        Response = namedtuple('Response', ['content'])
        r = Response(b'\xde\xad\xbe\xef')
        mock_client.return_value.download_bitstream.return_value = r

        mock_subprocess.Popen.return_value.returncode = 0
        mock_subprocess.Popen.return_value.communicate.return_value = b'', b''

        with ThumbnailGenerator('1/12345', **self.dspace_kwargs) as o:
            o.run()

    def test_no_username(
        self, mock_client, mock_item, mock_bundle, mock_bitstream,
        mock_psycopg2, mock_subprocess
    ):
        """
        Scenario:  no username is provided

        Expected result:  RuntimeError
        """
        handle = '1/18274'

        with (
            patch.dict(self.dspace_kwargs, {}, clear=True),
        ):
            with self.assertRaises(RuntimeError):
                ThumbnailGenerator(handle, **self.dspace_kwargs)

    def test_username_via_environment_but_no_password(
        self, mock_client, mock_item, mock_bundle, mock_bitstream,
        mock_psycopg2, mock_subprocess
    ):
        """
        Scenario:  a username is provided, but not a password

        Expected result:  RuntimeError
        """
        handle = '1/18274'

        with (
            patch.dict(
                'dspace_utils.thumbnails.os.environ',
                {'DSPACE_API_USERNAME': 'somebody'},
                clear=True
            ),
        ):
            with self.assertRaises(RuntimeError):
                ThumbnailGenerator(handle)

    def test_username_via_environment_variable_password_via_cmdline(
        self, mock_client, mock_bundle, mock_bitstream, mock_item,
        mock_psycopg2, mock_subprocess
    ):
        """
        Scenario:  the username is not provided via the command line, but is
        provided via environment variable

        Expected result:  no errors
        """
        handle = '1/18274'

        with (
            patch.dict(
                'dspace_utils.thumbnails.os.environ',
                {'DSPACE_API_USERNAME': 'somebody'},
                clear=True
            ),
        ):
            ThumbnailGenerator(handle, password='somepass')

    def test_credentials_via_environment_variable(
        self, mock_client, mock_bundle, mock_bitstream, mock_item,
        mock_psycopg2, mock_subprocess
    ):
        """
        Scenario:  both username and password are provided via environment
        variables

        Expected result:  The thumbnail generator is constructed with no
        errors
        """
        env = {
            'DSPACE_API_USERNAME': 'somebody',
            'DSPACE_API_PASSWORD': 'somepass'
        }
        with (
            patch.dict('dspace_utils.thumbnails.os.environ', env, clear=True)
        ):
            ThumbnailGenerator('1/12345')
