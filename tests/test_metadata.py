# standard library imports
import importlib.resources as ir
import json
from unittest import mock

# 3rd party library imports
import requests

# local imports
import dspace_utils.common
from dspace_utils import MetadataDumper
from .common import TestCommon


class TestSuite(TestCommon):

    @mock.patch('dspace_utils.common.Item', autospec=True)
    @mock.patch('dspace_utils.common.DSpaceClient', autospec=True)
    def test_smoke(self, mock_client, mock_item):
        """
        Scenario:  test basic operation
        """

        # Mock the api_get call that returns an item
        api_get_mock = mock.create_autospec(requests.Response)
        api_get_mock.json.return_value = {'type': 'item'}
        mock_client.return_value.api_get.return_value = api_get_mock

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

        with MetadataDumper('1/12345') as o:
            actual = str(o)

        expected = ir.files('tests.data').joinpath('smoke.txt').read_text().rstrip() # noqa : E501
        self.assertEqual(actual, expected)

    @mock.patch('dspace_utils.common.Collection', autospec=True)
    @mock.patch('dspace_utils.common.Community', autospec=True)
    @mock.patch('dspace_utils.common.DSpaceClient', autospec=True)
    def test_community(self, mock_client, mock_community, mock_collection):
        """
        Scenario:  test basic operation for dumping a community
        """

        # Mock the api_get call that returns an item
        api_get_mock = mock.create_autospec(requests.Response)
        api_get_mock.json.return_value = {'type': 'community'}
        mock_client.return_value.api_get.return_value = api_get_mock

        # mock the collection object
        community = dspace_utils.common.Community()

        community.name = 'Community 1'
        community.type = 'community'
        community.handle = '1/12345'
        community.uuid = '49022849-8137-4ea0-9caf-bed74d5ea9ca'

        text = ir.files('tests.data').joinpath('community.json').read_text()
        community.metadata = json.loads(text)

        mock_community.return_value = community

        # mock the items contained in this collection
        collections = []

        coll = dspace_utils.common.Collection()
        coll.name = 'a'
        coll.uuid = '12345678-1234-5678-12345678901234567'
        coll.handle = '2/2354'
        collections.append(coll)

        coll = dspace_utils.common.Item()
        coll.name = 'b'
        coll.uuid = '22345678-1234-5678-12345678901234567'
        coll.handle = '3/4567'
        collections.append(coll)

        mock_client.return_value.get_collections.return_value = collections

        with MetadataDumper('1/12345') as o:
            actual = str(o)

        expected = ir.files('tests.data').joinpath('community.txt').read_text().rstrip() # noqa : E501
        self.assertEqual(actual, expected)

    @mock.patch('dspace_utils.common.Item', autospec=True)
    @mock.patch('dspace_utils.common.Collection', autospec=True)
    @mock.patch('dspace_utils.common.DSpaceClient', autospec=True)
    def test_collection(self, mock_client, mock_collection, mock_item):
        """
        Scenario:  test basic operation for dumping a collection
        """

        # Mock the api_get call that returns an item
        api_get_mock = mock.create_autospec(requests.Response)
        api_get_mock.json.return_value = {'type': 'collection'}
        mock_client.return_value.api_get.return_value = api_get_mock

        # mock the collection object
        collection = dspace_utils.common.Collection()

        collection.name = 'Collection 1'
        collection.type = 'collection'
        collection.handle = '1/12345'
        collection.uuid = '49022849-8137-4ea0-9caf-bed74d5ea9ca'

        text = ir.files('tests.data').joinpath('collection.json').read_text()
        collection.metadata = json.loads(text)

        mock_collection.return_value = collection

        # mock the items contained in this collection
        items = []

        item = dspace_utils.common.Item()
        item.name = 'a'
        item.type = 'item'
        item.uuid = '12345678-1234-5678-12345678901234567'
        item.handle = '2/2354'
        items.append(item)

        item = dspace_utils.common.Item()
        item.name = 'b'
        item.type = 'item'
        item.uuid = '22345678-1234-5678-12345678901234567'
        item.handle = '3/4567'
        items.append(item)

        mock_client.return_value.search_objects.return_value = items

        with MetadataDumper('1/12345') as o:
            actual = str(o)

        expected = ir.files('tests.data').joinpath('collection.txt').read_text().rstrip() # noqa : E501
        self.assertEqual(actual, expected)
