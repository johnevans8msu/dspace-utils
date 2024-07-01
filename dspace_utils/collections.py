"""
Manage DSpace collections
"""
# standard library imports
import re
import sys
import uuid

# 3rd party library imports

# local imports
from .common import DSpaceCommon


class CollectionCreator(DSpaceCommon):
    """
    Create a new collection.

    Attributes
    ----------
    title : str
        Title/name of the new collection.
    community : str
        ID of the parent community.
    """

    def __init__(
        self, *, collection_title=None, community=None, description=None,
        verbose='info'
    ):
        super().__init__(verbose)
        self.collection_title = collection_title
        self.description = description

        # is it a handle?  if so, we need to get the UUID of the community.
        if re.match(r'\d/\d{1,5}', community) is not None:
            # Ok, we have a handle, turn it into a collection
            collection = self.get_item_from_handle(community)

            if collection.type != 'community':
                msg = (
                    f'The ID {community} was for a {collection.type}, not a '
                    'community.'
                )
                raise ValueError(msg)

            community = collection.uuid

        # Is it a UUID?
        try:
            uuid.UUID(f'{{{community}}}')
        except ValueError:
            # ok, not a UUID
            _, value, traceback = sys.exc_info()
            msg = f'The community ID was not a handle or UUID:  "{value}"'
            raise ValueError(msg).with_traceback(traceback)

        self.community = community

    def run(self):
        # put together the metadata
        metadata = {
            'type': {
                'value': 'community'
            },
            'metadata': {
                'dc.title': [
                    {
                        'language': None,
                        'value': self.collection_title,
                    },
                ],
                'dc.description': [
                    {
                        'language': None,
                        'value': self.description
                    },
                ],
                'dc.description.abstract': [
                    {
                        'language': None,
                    },
                ],
                'dc.rights': [
                    {
                        'language': None,
                    },
                ],
                'dc.rights.license': [
                    {
                        'language': None,
                    },
                ],
                'dc.description.tableofcontents': [
                    {
                        'language': None,
                    },
                ],
            }
        }

        new_collection = self.client.create_collection(
            parent=self.community, data=metadata
        )

        msg = (
            f'New collection {new_collection.uuid} create at '
            f'{new_collection.handle} with description "{self.description}".'
        )
        self.logger.info(msg)


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
        client=None, verbose='info'
    ):
        super().__init__(verbose=verbose, client=client)

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

        url = f'{self.client.API_ENDPOINT}/core/items/{self.item.uuid}/owningCollection'  # noqa : E501
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
