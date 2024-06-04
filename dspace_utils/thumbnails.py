# standard library imports
import os
import subprocess
import sys
import tempfile

# 3rd party library imports
from dspace_rest_client.client import DSpaceClient
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

    def __init__(
        self, handle, api_endpoint=None, username=None, password=None
    ):
        super().__init__()

        if username is None:
            username = os.environ.get('DSPACE_API_USERNAME', None)

        if password is None:
            password = os.environ.get('DSPACE_API_PASSWORD', None)

        if username is None or password is None:
            raise RuntimeError("Username or password not provided.")

        self.handle = handle

        self.api_endpoint = api_endpoint
        self.username = username
        self.password = password

        self.client = DSpaceClient(
            api_endpoint=api_endpoint,
            username=username,
            password=password,
            fake_user_agent=True
        )
        self.client.authenticate()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        pass

    def get_item_from_handle(self):
        """
        Locate the item tied to the current handle.
        """

        url = f'{self.api_endpoint}/pid/find'
        params = {'id': f'hdl:{self.handle}'}
        r = self.client.api_get(url, params)
        r.raise_for_status()

        return Item(r.json())

    def delete_thumbnail_bitstream(self, item):
        """
        Delete the thumbnail bitstream associated with the current item.
        """

        bundles = self.client.get_bundles(item)
        bundle = next(filter(lambda x: x.name == 'THUMBNAIL', bundles), None)
        if not bundle:
            print('no thumbnail bundle')
            sys.exit()

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

    def get_database_pagenumber(self):
        """
        Retrieve the thumbnail pagenumber associated with the current item.
        """

        sql = """
            select text_value::int
            from metadatavalue m
                inner join handle h on h.resource_id = m.dspace_object_id
            where h.handle = %(handle)s
            and m.metadata_field_id = 160
        """
        self.cursor.execute(sql, {'handle': self.handle})
        page_number = self.cursor.fetchone()[0]

        return page_number

    def create_thumbnail_image(
        self, orig_doc_path, new_thumbnail_path, page_number, r
    ):
        """
        Create a thumbnail JPEG image from the PDF document.
        """

        with open(orig_doc_path, mode='wb') as f:
            f.write(r.content)

        # create the new thumbnail
        cmd = (
            f'gm convert -thumbnail 160x160 '
            f'-flatten {orig_doc_path}[{page_number}] {new_thumbnail_path}'
        )
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        p.wait()

        stdout, stderr = p.communicate()
        stdout = stdout.decode('utf-8')

        if p.returncode != 0:
            stderr = stderr.decode('utf-8')
            raise RuntimeError(stderr)

    def create_new_thumbnail(self, item):
        """
        Create a new thumbnail for the current image, overwriting the old.
        """

        page_number = self.get_database_pagenumber()

        bundles = self.client.get_bundles(item)
        thumbnail_bundle = next(
            filter(lambda x: x.name == 'THUMBNAIL', bundles),
            None
        )

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

    def run(self):

        item = self.get_item_from_handle()
        self.delete_thumbnail_bitstream(item)
        self.create_new_thumbnail(item)
