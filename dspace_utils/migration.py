"""
Manage DSpace migrations
"""
# standard library imports
import datetime as dt

# 3rd party library imports
from dspace_rest_client.models import Item

# local imports
from .collections import OwningCollection
from .common import DSpaceCommon
from .thumbnails import ThumbnailGenerator


class LiveMigrator(DSpaceCommon):

    def __init__(self, source, target='1/733', verbose='info'):
        super().__init__(verbose)

        self.source = source
        self.target = target

    def run(self):

        self.source_collection = self.get_item_from_handle(self.source)

        for obj in self.client.search_objects(
            query='*:*', scope=self.source_collection.uuid, dso_type='item'
        ):
            item = Item(dso=obj)

            self.logger.info(f'Updating item {item.handle}.')
            self.update_item_metadata(item)
            self.generate_msu_thumbnail(item)
            self.move_to_new_collection(item)

    def move_to_new_collection(self, item):

        self.logger.info(f'Moving {item.handle} to {self.target}.')

        with OwningCollection(
            item_handle=item.handle,
            target_collection_handle=self.target,
            client=self.client
        ) as o:
            o.run()

    def generate_msu_thumbnail(self, item):
        """
        The best time to generate a custom thumbnail is when it is moved into
        the main collection (right now, in other words).
        """

        with ThumbnailGenerator(item.handle, client=self.client) as t:
            t.run()

    def update_item_metadata(self, item):
        """
        1. Fix the dc.identifier.uri element.
        2. Delete dc.description.provenance elements.
        3. Delete dc.date.accessioned elements.
        4. Delete dc.date.available elements.
        """

        # Fix the dc.identfier.uri if necessary, there should be no "xmlui"
        for datum in item.metadata['dc.identifier.uri']:
            datum['value'] = datum['value'].replace('/xmlui', '')

        # Delete any dc.description.provenance elements
        try:
            item.metadata.pop('dc.description.provenance')
        except KeyError:
            pass

        # Delete existing dc.date.accessioned elements, set the new one to
        # now.
        item.metadata.pop('dc.date.accessioned')
        item.metadata['dc.date.accessioned'] = [{
            'value': dt.datetime.now(tz=dt.UTC).strftime('%Y-%m-%dT%H:%M:%SZ'),
            'language': None,
            'authority': None,
            'confidence': -1,
            'place': 0,
        }]

        # Set dc.date.available to now
        item.metadata.pop('dc.date.available')
        item.metadata['dc.date.available'] = [{
            'value': dt.datetime.now(tz=dt.UTC).strftime('%Y-%m-%dT%H:%M:%SZ'),
            'language': None,
            'authority': None,
            'confidence': -1,
            'place': 0,
        }]

        self.client.update_dso(item)
