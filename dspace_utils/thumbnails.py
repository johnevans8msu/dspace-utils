# standard library imports
import subprocess
import tempfile

# 3rd party library imports
from dspace_rest_client.models import Item, Bundle, Bitstream  # noqa : F401

# local imports
from .common import DSpaceCommon


class ThumbnailGenerator(DSpaceCommon):
    """
    Generate thumbnail images for dspace instance

    Attributes
    ----------
    api_endpoint : str
        base path to DSpace REST API, eg. http://localhost:8080/server/api
    username : str
        username with appropriate privileges to perform operations on REST API
    username : str
        password for the above username
    handle : str
        persistent identifier for the item in question
    client : object
        REST interface wrapper
    """

    def __init__(self, handle, verbose='info', client=None):
        super().__init__(verbose=verbose, client=client)

        self.handle = handle

    def delete_thumbnail_bitstream(self, item):
        """
        Delete the thumbnail bitstream associated with the current item.
        """

        bundles = self.client.get_bundles(item)
        bundle = next(filter(lambda x: x.name == 'THUMBNAIL', bundles), None)

        bitstreams = self.client.get_bitstreams(bundle=bundle)

        # there may be zero, one, or more than one bitstream.  But if they
        # are associated with the THUMBNAIL bundle, we will delete it.

        for bitstream in bitstreams:

            # delete the existing thumbnail
            # should return 204
            url = f'{self.api_endpoint}/core/bitstreams'
            path = f'/bitstreams/{bitstream.uuid}'
            r = self.client.api_patch(url, 'remove', path, None, retry=True)
            r.raise_for_status()

            msg = f"Deleted bitstream {bitstream.uuid}."
            self.logger.debug(msg)

    def get_pagenumber(self, item):
        """
        Retrieve the thumbnail pagenumber associated with the current item.
        """
        page_number = int(item.metadata['mus.data.thumbpage'][0]['value'])

        self.logger.info(f'Retrieved page number {page_number}.')

        return page_number

    def create_thumbnail_image(
        self, orig_doc_path, new_thumbnail_path, page_number, r
    ):
        """
        Create a thumbnail JPEG image from the PDF document.
        """

        with open(orig_doc_path, mode='wb') as f:
            f.write(r.content)

            msg = f"Wrote original document content to {orig_doc_path}"
            self.logger.debug(msg)

        # create the new thumbnail
        cmd = (
            f'gm convert -thumbnail 160x160 '
            f'-flatten {orig_doc_path}[{page_number}] {new_thumbnail_path}'
        )
        self.logger.info(f'Running command "{cmd}"...')
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        p.wait()

        stdout, stderr = p.communicate()
        stdout = stdout.decode('utf-8')

        if p.returncode != 0:
            stderr = stderr.decode('utf-8')
            raise RuntimeError(stderr)

        msg = f"Created new thumbnail image at {new_thumbnail_path}"
        self.logger.debug(msg)

    def create_new_thumbnail(self, item, page_number):
        """
        Create a new thumbnail for the current image, overwriting the old.
        """

        bundles = self.client.get_bundles(item)
        thumbnail_bundle = next(
            filter(lambda x: x.name == 'THUMBNAIL', bundles),
            None
        )
        if thumbnail_bundle is None:
            thumbnail_bundle = self.client.create_bundle(parent=item, name='THUMBNAIL')

        # get the original document
        orig_bundle = next(
            filter(lambda x: x.name == 'ORIGINAL', bundles),
            None
        )
        o_bitstreams = self.client.get_bitstreams(bundle=orig_bundle)
        o_bitstream = o_bitstreams[0]

        docname = o_bitstream.metadata['dc.title'][0]['value']
        thumbnail_name = f"{docname}.jpg"

        r = self.client.download_bitstream(o_bitstream.uuid)

        with tempfile.TemporaryDirectory() as tdir:

            orig_doc_path = f'{tdir}/{docname}'
            new_thumbnail_path = f'{tdir}/{thumbnail_name}'
            self.create_thumbnail_image(
                orig_doc_path, new_thumbnail_path, page_number, r
            )

            metadata = {
                'dc.description': [{
                    "value": "Custom Thumbnail",
                    'language': None,
                    'authority': None,
                    'confidence': -1,
                    'place': 0
                }],
                'dc.source': [{
                    "value": 'Written by ThumbnailGenerator',
                    'language': None,
                    'authority': None,
                    'confidence': -1,
                    'place': 0
                }],
                'dc.title': [{
                    "value": thumbnail_name,
                    'language': None,
                    'authority': None,
                    'confidence': -1,
                    'place': 0
                }]
            }

            self.client.create_bitstream(
                bundle=thumbnail_bundle,
                name=thumbnail_name,
                path=new_thumbnail_path,
                mime='image/jpeg',
                metadata=metadata
            )

            self.logger.debug("Created new thumbnail bitstream.")

    def run(self):

        item = self.get_obj_from_handle(self.handle)
        page_number = self.get_pagenumber(item)
        self.delete_thumbnail_bitstream(item)
        self.create_new_thumbnail(item, page_number)
