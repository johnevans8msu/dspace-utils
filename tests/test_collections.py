# standard library imports
from unittest import mock

# 3rd party library imports
import requests

# local imports
import dspace_utils
from dspace_utils import OwningCollection, CollectionCreator
from .common import TestCommon


@mock.patch('dspace_utils.common.Item', autospec=True)
@mock.patch('dspace_utils.common.DSpaceClient', autospec=True)
class TestSuite(TestCommon):

    def test_smoke(self, mock_client, mock_item):
        """
        Scenario:  test basic operation for changing the owning collection

        Expected result:  no errors
        """

        # make up some fake items.  The first is the item in question,
        # the second is the item describing the target owning collection.
        item1 = dspace_utils.common.Item()
        item1.handle = '1/12345'
        item1.uuid = '12345678-1234-1234-1234-123456789abc'
        item1.to_json.return_value = {
            'handle': item1.handle,
            'uuid': item1.uuid,
        }

        # the current collection item
        item2 = dspace_utils.common.Item()
        item2.handle = '1/23456'
        item2.uuid = '23456789-1234-1234-1234-123456789abc'
        item2.to_json.return_value = {
            'handle': item2.handle,
            'uuid': item2.uuid,
        }

        # ask for the item in question and then the current collection
        items = [item1, item2]
        mock_item.side_effect = items

        # There are 3 calls to the client api_get
        #
        # 1 - produces JSON for an Item
        # 2 - produces JSON for an Item
        # 3 - produces JSON for current owning collection (don't care)
        m1 = mock.create_autospec(requests.Response)
        m1.json.return_value = {'type': 'item'}
        m2 = mock.create_autospec(requests.Response)
        m2.json.return_value = {'type': 'item'}
        m3 = mock.create_autospec(requests.Response)
        m3.json.return_value = {
            'handle': 'not-important', 'uuid': 'not-important'
        }

        mock_client.return_value.api_get.side_effect = [m1, m2, m3]

        with OwningCollection(
            item_handle=items[0].handle,
            target_collection_handle=items[1].handle
        ) as o:
            o.run()

    def test_api_put_produces_400(self, mock_client, mock_item):
        """
        Scenario:  The actual PUT produces a 400 status code, most likely
        because the target collection is already the same as the owning
        collection

        Expected result:  HTTPError
        """

        # make up some fake items.  The first is the item in question,
        # the second is the item describing the target owning collection.
        item1 = dspace_utils.common.Item()
        item1.handle = '1/12345'
        item1.uuid = '12345678-1234-1234-1234-123456789abc'
        item1.to_json.return_value = {
            'handle': item1.handle,
            'uuid': item1.uuid,
        }

        # the current collection item
        item2 = dspace_utils.common.Item()
        item2.handle = '1/23456'
        item2.uuid = '23456789-1234-1234-1234-123456789abc'
        item2.to_json.return_value = {
            'handle': item2.handle,
            'uuid': item2.uuid,
        }

        # ask for the item in question and then the current collection
        items = [item1, item2]
        mock_item.side_effect = items

        # There are 3 calls to the client api_get
        #
        # The first two return Responses that need to be turned into Items.
        #
        # The 3rd call produces JSON, but we don't care about it.
        # We never get to the final 4th call referenced in the above test.
        m1 = mock.create_autospec(requests.Response)
        m1.json.return_value = {'type': 'item'}
        m2 = mock.create_autospec(requests.Response)
        m2.json.return_value = {'type': 'item'}

        m3 = mock.create_autospec(requests.Response)
        m3.json.return_value = {
            'handle': 'not-important', 'uuid': 'not-important'
        }
        mock_client.return_value.api_get.side_effect = [m1, m2, m3]

        # The actual PUT operation returns a 400 code, but we never see that.
        # Instead we rely on the response raising an exception.
        m = mock.create_autospec(requests.Response)
        m.raise_for_status.side_effect = requests.HTTPError
        mock_client.return_value.session.put.return_value = m

        with OwningCollection(
            item_handle=items[0].handle,
            target_collection_handle=items[1].handle
        ) as o:
            with self.assertRaises(requests.HTTPError):
                o.run()


@mock.patch('dspace_utils.common.DSpaceClient', autospec=True)
class TestSuiteCollections(TestCommon):

    def test_smoke(self, mock_client):
        """
        Scenario:  create a collection in some random community

        Expected result:  no errors
        """

        with CollectionCreator(
            collection_title='Test Collection',
            community='98765432-1234-1234-1234-123456789abc'
        ) as o:
            with self.assertLogs():
                o.run()

    def test_smoke_handle(self, mock_client):
        """
        Scenario:  create a collection in some random community that is
        identified by a handle

        Expected result:  no errors
        """

        # Mock the api_get call that returns an item
        api_get_mock = mock.create_autospec(requests.Response)
        api_get_mock.json.return_value = {
            'type': 'community',
            'uuid': '98765432-1234-1234-1234-123456789abc',
        }
        mock_client.return_value.api_get.return_value = api_get_mock

        with CollectionCreator(
            collection_title='Test Collection',
            community='1/2345'
        ) as o:
            with self.assertLogs():
                o.run()

    def test_handle_is_for_an_item(self, mock_client):
        """
        Scenario:  pass a handle for the community ID, but it's a handle for
        an item.

        Expected result:  ValueError
        """

        # Mock the api_get call that returns an item
        api_get_mock = mock.create_autospec(requests.Response)
        api_get_mock.json.return_value = {
            'type': 'item',
            'uuid': '98765432-1234-1234-1234-123456789abc',
        }
        mock_client.return_value.api_get.return_value = api_get_mock

        with self.assertRaises(ValueError):
            CollectionCreator(
                collection_title='Test Collection',
                community='1/2345'
            )

    def test_community_id_is_mangled_uuid(self, mock_client):
        """
        Scenario:  pass a mangled uuid as the community identifier

        Expected result:  ValueError
        """

        with self.assertRaises(ValueError):
            CollectionCreator(
                collection_title='Test Collection',
                community='98765432-1234-1234-123456789abc-1234-1243'
            )

    def test_add_description(self, mock_client):
        """
        Scenario: an an optional description

        Expected result:  the description shows up in the logs
        """

        # Mock the api_get call that returns an item
        api_get_mock = mock.create_autospec(requests.Response)
        api_get_mock.json.return_value = {
            'type': 'community',
            'uuid': '98765432-1234-1234-1234-123456789abc',
        }
        mock_client.return_value.api_get.return_value = api_get_mock

        description = 'something obvious'
        with CollectionCreator(
            collection_title='Test Collection',
            community='1/2345',
            description=description
        ) as o:
            with self.assertLogs() as cl:
                o.run()

                self.assertIn(description, cl.output[-1])
