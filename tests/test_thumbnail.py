# standard library imports
from collections import namedtuple
import unittest
from unittest.mock import patch

# 3rd party library imports

# local imports
from dspace_utils import ThumbnailGenerator
from dspace_utils.thumbnails import Bundle


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

    def test_no_bitstreams_for_thumbnails_bundle(
        self, mock_client, mock_item, mock_bundle, mock_bitstream,
        mock_psycopg2, mock_subprocess
    ):
        """
        Scenario:  there are no bitstreams associated with the thumbnail bundle

        Expected result:  no errors
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
        # We call get_bitstreams twice, once for the thumbnail bitstreams
        # (which will be empty) and once for the original bitstream, which
        # has stuff in it.
        thumbnail_bitstreams = []
        orig_bitstreams = [mock_bitstream(), mock_bitstream()]
        orig_bitstreams[0].uuid = '12345678-1234-1234-1234-123456789abc'
        orig_bitstreams[0].name = 'ORIGINAL'
        orig_bitstreams[1].uuid = '12345678-1234-1234-1234-123456789abd'
        orig_bitstreams[1].name = 'THUMBNAIL'
        mock_client.return_value.get_bitstreams.side_effect = [
            thumbnail_bitstreams, orig_bitstreams
        ]

        # make up downloaded content for the PDF bitstream (ORIG document)
        Response = namedtuple('Response', ['content'])
        r = Response(b'\xde\xad\xbe\xef')
        mock_client.return_value.download_bitstream.return_value = r

        mock_subprocess.Popen.return_value.returncode = 0
        mock_subprocess.Popen.return_value.communicate.return_value = b'', b''

        with ThumbnailGenerator('1/12345', **self.dspace_kwargs) as o:
            o.run()
