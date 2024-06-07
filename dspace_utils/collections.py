"""
Manage DSpace collections
"""
# standard library imports

# 3rd party library imports

# local imports
from .common import DSpaceCommon


class OwningCollection(DSpaceCommon):
    """
    Sets an item's new owning collection.

    Attributes
    ----------
    item : dspace_rest_client.Item
        Item whose owning collection is at issue.
    target_collection_item : dspace_rest_client.Item
        Item representing the intended owning collection
    owning_collection_uuid : str
        UUID (str) of the owning collection, will be reset to new value.
    """

    def __init__(
        self, *, item_handle=None, target_collection_handle=None,
        verbose='info'
    ):
        super().__init__(verbose)

        self.item = self.get_item_from_handle(item_handle)
        self.target_collection_item = self.get_item_from_handle(target_collection_handle)  # noqa : E501

        self.get_owning_collection_uuid()

    def run(self):

        self.reset_collection()

        # This is verification that we got it right.
        self.get_owning_collection_uuid()

    def get_owning_collection_uuid(self):
        """
        Set member UUID (actually a str) of owning collection.
        """

        url = f'{self.api_endpoint}/core/items/{self.item.uuid}/owningCollection'  # noqa : E501
        r = self.client.api_get(url)
        r.raise_for_status()

        msg = (
            f"The current owning collection is "
            f"{r.json()['handle']} ({r.json()['uuid']})"
        )
        self.logger.info(msg)

        self.owning_collection_uuid = r.json()['uuid']
        self.owning_collection_handle = r.json()['handle']

    def reset_collection(self):

        params = {'inheritPolicies': False}

        url = f"{self.api_endpoint}/core/items/{self.item.uuid}/owningCollection"  # noqa : E501
        data = f'{self.api_endpoint}/core/collections/{self.target_collection_item.uuid}'  # noqa : E501
        headers = {
            'Content-Type':  'text/uri-list',
            'User-Agent': 'Abraxis'
        }

        r = self.client.session.put(
            url, params=params, data=data, headers=headers
        )
        r.raise_for_status()
