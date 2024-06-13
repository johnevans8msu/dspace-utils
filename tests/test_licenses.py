# standard library imports
from collections import namedtuple
import importlib.resources as ir
import json
from unittest.mock import patch

# 3rd party library imports

# local imports
from dspace_utils import LicenseChanger
from dspace_utils.thumbnails import Bundle
from .common import TestCommon


@patch('dspace_utils.licenses.Bitstream', autospec=True)
@patch('dspace_utils.licenses.Bundle', autospec=True)
@patch('dspace_utils.common.Item', autospec=True)
@patch('dspace_utils.common.DSpaceClient', autospec=True)
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

        # make up downloaded content for the PDF bitstream
        Response = namedtuple('Response', ['content'])
        r = Response(b'stuff')
        mock_client.return_value.download_bitstream.return_value = r

        new_license_file = ir.files('tests.data').joinpath('license.txt')

        with (
            patch(
                'dspace_utils.common.pathlib.Path.read_text',
                return_value=json.dumps(self.config),
            ),
            LicenseChanger('1/12345', license_file=new_license_file) as o,
        ):
            o.run()
