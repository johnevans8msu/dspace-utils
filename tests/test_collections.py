# standard library imports
from unittest import mock

# 3rd party library imports
import requests

# local imports
import dspace_utils
from dspace_utils import OwningCollection
from .common import TestCommon


@mock.patch('dspace_utils.common.Item', autospec=True)
@mock.patch('dspace_utils.common.DSpaceClient', autospec=True)
class TestSuite(TestCommon):

    def test_owning_collection_smoke(self, mock_client, mock_item):
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

        # There are 4 calls to the client api_get
        #
        # The first two return Responses whos values we care not, as we
        # manufacture Items out of them (see above).  We do care about the
        # 3rd and 4th calls.
        #
        # 1 - don't care, produce an Item from result
        # 2 - don't care, produce an Item from result
        # 3 - produces JSON for current owning collection (don't care)
        # 4 - produces JSON for final owning collection
        m1 = mock.create_autospec(requests.Response)
        m2 = mock.create_autospec(requests.Response)
        m3 = mock.create_autospec(requests.Response)
        m3.json.return_value = {
            'handle': 'not-important', 'uuid': 'not-important'
        }
        m4 = mock.create_autospec(requests.Response)
        m4.json.return_value = {'handle': item2.handle, 'uuid': item2.uuid}

        mock_client.return_value.api_get.side_effect = [m1, m2, m3, m4]

        with OwningCollection(
            item_handle=items[0].handle,
            target_collection_handle=items[1].handle
        ) as o:
            o.run()

            self.assertEqual(o.owning_collection_uuid, items[1].uuid)

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
        # The first two return Responses whos values we care not, as we
        # manufacture Items out of them (see above).  The 3rd call produces
        # JSON, but we don't care about it.  We never get to the final 4th call
        # referenced in the above test.
        #
        # 1 - don't care, produce an Item from result
        # 2 - don't care, produce an Item from result
        # 3 - produces JSON for current owning collection (don't care)
        m1 = mock.create_autospec(requests.Response)
        m2 = mock.create_autospec(requests.Response)
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
