# standard library imports
import subprocess
import sys

# 3rd party library imports
from dspace_rest_client.client import DSpaceClient
from dspace_rest_client.models import Item, Bundle, Bitstream  # noqa : F401
import psycopg2


class ThumbnailGenerator(object):

    def __init__(
        self, handle, api_endpoint=None, username=None, password=None
    ):

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

    def run(self):

        url = f'{self.api_endpoint}/pid/find'
        params = {'id': f'hdl:{self.handle}'}
        r = self.client.api_get(url, params)
        r.raise_for_status()

        item = Item(r.json())

        bundles = self.client.get_bundles(item)
        bundle = next(filter(lambda x: x.name == 'THUMBNAIL', bundles), None)
        if not bundle:
            print('no thumbnail bundle')
            sys.exit()

        bitstreams = self.client.get_bitstreams(bundle=bundle)
        bitstream = bitstreams[0]

        # delete the existing thumbnail
        # should return 204
        url = f'{self.api_endpoint}/core/bitstreams'
        path = f'/bitstreams/{bitstream.uuid}'
        r = self.client.api_patch(url, 'remove', path, None, retry=True)
        r.raise_for_status()

        # Get the page number of the expected thumbnail
        conn = psycopg2.connect('postgres://tomcat@localhost/dspace')
        cursor = conn.cursor()

        sql = """
            select text_value::int
            from metadatavalue m
                inner join handle h on h.resource_id = m.dspace_object_id
            where h.handle = %(handle)s
            and m.metadata_field_id = 160
        """
        cursor.execute(sql, {'handle': self.handle})
        page_number = cursor.fetchone()[0]

        # get the original document
        orig_bundle = next(filter(lambda x: x.name == 'ORIGINAL', bundles), None)  # noqa : E501
        o_bitstreams = self.client.get_bitstreams(bundle=orig_bundle)
        o_bitstream = o_bitstreams[0]

        r = self.client.download_bitstream(o_bitstream.uuid)
        document = 'document.pdf'
        with open('document.pdf', mode='wb') as f:
            f.write(r.content)

        # create the new thumbnail
        thumbnail = f'{document}.jpg'
        cmd = (
            f'gm convert -thumbnail 160x160 '
            f'-flatten {document}[{page_number}] {thumbnail}'
        )
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        p.wait()

        stdout, stderr = p.communicate()
        stdout = stdout.decode('utf-8')

        if p.returncode != 0:
            stderr = stderr.decode('utf-8')
            raise RuntimeError(stderr)

        metadata = {
            'dc.title': [{"value": "THUMBNAIL", 'confidence': -1, 'place': 0}]
        }
        self.client.create_bitstream(
            bundle=bundle,
            name=thumbnail,
            path=thumbnail,
            mime='image/jpeg',
            metadata=metadata
        )
