# standard library imports
from collections import namedtuple
import importlib.resources as ir
from unittest import mock

# 3rd party library imports
import requests

# local imports
from dspace_utils import LicenseChanger
from dspace_utils.thumbnails import Bundle
from .common import TestCommon


@mock.patch('dspace_utils.licenses.Bitstream', autospec=True)
@mock.patch('dspace_utils.licenses.Bundle', autospec=True)
@mock.patch('dspace_utils.common.Item', autospec=True)
@mock.patch('dspace_utils.common.DSpaceClient', autospec=True)
class TestSuite(TestCommon):

    def test_smoke(
        self, mock_client, mock_item, mock_bundle, mock_bitstream,
    ):
        """
        Scenario:  test basic operation
        """

        # make up some fake bundles
        bundles = [Bundle(), Bundle()]
        bundles[0].uuid = '12345678-1234-1234-1234-123456789abc'
        bundles[0].name = 'ORIGINAL'
        bundles[1].uuid = '12345678-1234-1234-1234-123456789abd'
        bundles[1].name = 'LICENSE'
        mock_client.return_value.get_bundles.return_value = bundles

        # make up some fake bitstreams
        bitstreams = [mock_bitstream(), mock_bitstream()]
        bitstreams[0].uuid = '12345678-1234-1234-1234-123456789abc'
        bitstreams[0].name = 'ORIGINAL'
        bitstreams[1].uuid = '12345678-1234-1234-1234-123456789abd'
        bitstreams[1].name = 'LICENSE'
        mock_client.return_value.get_bitstreams.return_value = bitstreams

        # Mock the api_get call that returns an item
        api_get_mock = mock.create_autospec(requests.Response)
        api_get_mock.json.return_value = {'type': 'item'}
        mock_client.return_value.api_get.return_value = api_get_mock

        # make up downloaded content for the license bitstream
        Response = namedtuple('Response', ['content'])
        r = Response(b'stuff')
        mock_client.return_value.download_bitstream.return_value = r

        new_license_file = ir.files('tests.data').joinpath('license.txt')

        # mock newly-created bitstream
        new_bitstream = mock_bitstream()
        mock_client.return_value.create_bitstream.return_value = new_bitstream

        with LicenseChanger('1/12345', license_file=new_license_file) as o:
            o.run()
