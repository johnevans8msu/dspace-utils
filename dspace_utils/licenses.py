# standard library imports
import datetime as dt

# 3rd party library imports
from dspace_rest_client.models import Item, Bundle, Bitstream  # noqa : F401

# local imports
from .common import DSpaceCommon


class LicenseChanger(DSpaceCommon):
    """
    Change the license for a specific item.

    Attributes
    ----------
    handle : str
        persistent identifier for the item in question
    client : object
        REST interface wrapper
    """

    def __init__(self, item_handle, license_file, verbose='info'):
        super().__init__(verbose)

        self.handle = item_handle
        self.license_file = license_file

    def delete_license_bitstream(self, item):
        """
        Delete the license bitstream(s) associated with the current item.
        """

        bundles = self.client.get_bundles(item)
        bundle = next(filter(lambda x: x.name == 'LICENSE', bundles), None)

        bitstreams = self.client.get_bitstreams(bundle=bundle)

        # there may be zero, one, or more than one bitstream.  But if they
        # are associated with the LICENSE bundle, we will delete it.

        for bitstream in bitstreams:

            url = f'{self.api_endpoint}/core/bitstreams'
            path = f'/bitstreams/{bitstream.uuid}'
            r = self.client.api_patch(url, 'remove', path, None, retry=True)
            r.raise_for_status()

            msg = f"Deleted bitstream {bitstream.uuid}."
            self.logger.debug(msg)

    def run(self):

        item = self.get_item_from_handle(self.handle)
        self.delete_license_bitstream(item)
        self.create_new_license_bitstream(item)

    def create_new_license_bitstream(self, item):
        """
        Create a new license, overwriting the old.
        """

        bundles = self.client.get_bundles(item)
        bundle = next(filter(lambda x: x.name == 'LICENSE', bundles), None)

        metadata = {
            'dcterms.accessRights': [{
                "value": dt.datetime.now(tz=dt.UTC).strftime('%Y-%m-%dT%H:%M:%SZ'),  # noqa : E501
                'language': None,
                'authority': None,
                'confidence': -1,
                'place': 0
            }],
            'dc.source': [{
                "value": 'Written by LicenseChanger',
                'language': None,
                'authority': None,
                'confidence': -1,
                'place': 0
            }],
            'dc.title': [{
                "value": 'license.txt',
                'language': None,
                'authority': None,
                'confidence': -1,
                'place': 0
            }]
        }

        new_bitstream = self.client.create_bitstream(
            bundle=bundle,
            name='license.txt',
            path=self.license_file,
            mime='text/plain',
            metadata=metadata
        )

        self.logger.info("Created new license bitstream.")
        self.logger.debug(f"{new_bitstream.as_dict()}")
