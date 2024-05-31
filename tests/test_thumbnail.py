# standard library imports
from collections import namedtuple
import unittest
from unittest import mock

# 3rd party library imports
# from dspace_rest_client.client import DSpaceClient

# local imports
from dspace_utils import ThumbnailGenerator
from dspace_utils.thumbnails import Bundle


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

    def test_smoke(self):
        """
        Scenario:  test basic operation
        """
        client_patcher = mock.patch(
            'dspace_utils.thumbnails.DSpaceClient', autospec=True
        )
        mock_client = client_patcher.start()
        item_patcher = mock.patch(
            'dspace_utils.thumbnails.Item', autospec=True
        )
        _ = item_patcher.start()

        bundle_patcher = mock.patch(
            'dspace_utils.thumbnails.Bundle', autospec=True
        )
        _ = bundle_patcher.start()

        bitstream_patcher = mock.patch(
            'dspace_utils.thumbnails.Bitstream', autospec=True
        )
        mock_bitstream = bitstream_patcher.start()

        # make up some fake bundles
        bundles = [Bundle(), Bundle()]
        bundles[0].uuid = '12345678-1234-1234-1234-123456789abc'
        bundles[0].name = 'ORIGINAL'
        bundles[1].uuid = '12345678-1234-1234-1234-123456789abd'
        bundles[1].name = 'THUMBNAIL'
        mock_client.return_value.get_bundles.return_value = bundles

        psycopg2_patcher = mock.patch(
            'dspace_utils.thumbnails.psycopg2', autospec=True
        )
        mock_psycopg2 = psycopg2_patcher.start()

        mock_psycopg2.connect.return_value.cursor.return_value.fetchone.return_value = (10,)  # noqa : E501

        # make up some fake bitstreams
        bitstreams = [mock_bitstream(), mock_bitstream()]
        bitstreams[0].uuid = '12345678-1234-1234-1234-123456789abc'
        bitstreams[0].name = 'ORIGINAL'
        bitstreams[1].uuid = '12345678-1234-1234-1234-123456789abd'
        bitstreams[1].name = 'THUMBNAIL'
        mock_client.return_value.get_bitstreams.return_value = bitstreams

        # make up downloaded content
        Response = namedtuple('Response', ['content'])
        r = Response(b'\xde\xad\xbe\xef')

        mock_client.return_value.download_bitstream.return_value = r

        subprocess_patcher = mock.patch(
            'dspace_utils.thumbnails.subprocess', autospec=True
        )
        mock_subprocess = subprocess_patcher.start()
        mock_subprocess.Popen.return_value.returncode = 0

        mock_subprocess.Popen.return_value.communicate.return_value = (b'', b'')  # noqa : E501

        handle = '1/18274'

        with ThumbnailGenerator(handle, **self.dspace_kwargs) as o:
            o.run()
