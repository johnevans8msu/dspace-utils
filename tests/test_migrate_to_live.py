# standard library imports
import importlib.resources as ir
import json
from unittest import mock

# 3rd party library imports
import requests

# local imports
import dspace_utils.common
from dspace_utils import LiveMigrator
from .common import TestCommon


@mock.patch('dspace_utils.migration.Item', autospec=True)
@mock.patch('dspace_utils.common.Collection', autospec=True)
@mock.patch('dspace_utils.common.DSpaceClient', autospec=True)
class TestSuite(TestCommon):

    def test_smoke(self, mock_client, mock_collection, mock_item):
        """
        Scenario:  move item from one collection to the live collection

        Expected result:  no errors
        """

        # mock the collection that originally holds the item
        #
        # first we interrogate dspace for the collection handle
        m1 = mock.create_autospec(requests.Response)
        m1.json.return_value = {'type': 'collection'}
        mock_client.return_value.api_get.side_effect = [m1]

        # from the JSON returned from that we hydrate the collection
        collection = dspace_utils.common.Collection()

        collection.name = 'Collection 1'
        collection.type = 'collection'
        collection.handle = '1/19237'
        collection.uuid = '49022849-8137-4ea0-9caf-bed74d5ea9ca'

        text = ir.files('tests.data').joinpath('collection.json').read_text()
        collection.metadata = json.loads(text)

        mock_collection.return_value = collection

        # Mock the items belonging to that collection.  Two step process, first
        # we search for the objects, then turn them into items.  We don't need
        # to hydrate the objects returned by the search because we turn them
        # into Items and then discard them.
        mock_client.return_value.search_objects.return_value = [None]

        item1 = dspace_utils.migration.Item()
        item1.handle = '1/12345'
        item1.uuid = '12345678-1234-1234-1234-123456789abc'
        item1.to_json.return_value = {
            'handle': item1.handle,
            'uuid': item1.uuid,
        }
        text = ir.files('tests.data').joinpath('item.json').read_text()
        item1.metadata = json.loads(text)

        mock_item.side_effect = [item1]

        # we don't want to actually run thumbnail generation or moving between
        # collections, we test that elsewhere
        with (
            mock.patch('dspace_utils.migration.ThumbnailGenerator'),
            mock.patch('dspace_utils.migration.OwningCollection')
        ):
            with LiveMigrator(collection.handle) as o:
                o.run()
