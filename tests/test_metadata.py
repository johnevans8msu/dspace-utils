# standard library imports
import importlib.resources as ir
import json
from unittest.mock import patch

# 3rd party library imports

# local imports
import dspace_utils.common
from dspace_utils import MetadataDumper
from .common import TestCommon


@patch('dspace_utils.common.Item', autospec=True)
@patch('dspace_utils.common.DSpaceClient', autospec=True)
class TestSuite(TestCommon):

    def test_smoke(self, mock_client, mock_item):
        """
        Scenario:  test basic operation
        """

        item = dspace_utils.common.Item()
        item.name = 'AVATAR: A CULTURAL AND ETHICAL JOURNEY ACROSS SETTLER-COLONIALISM'  # noqa : E501
        item.type = 'item'
        item.inArchive = 'true'
        item.handle = '1/18292'
        item.uuid = '49022849-8137-4ea0-9caf-bed74d5ea9ca'
        item.withdrawn = 'false'

        text = ir.files('tests.data').joinpath('smoke.json').read_text()
        item.metadata = json.loads(text)['metadata']

        mock_item.return_value = item

        with (
            patch(
                'dspace_utils.common.pathlib.Path.read_text',
                return_value=json.dumps(self.config),
            ),
            MetadataDumper('1/12345') as o,
        ):
            actual = str(o)

        expected = ir.files('tests.data').joinpath('smoke.txt').read_text().rstrip() # noqa : E501
        self.assertEqual(actual, expected)
