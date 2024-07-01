# standard library imports
import logging
import pathlib
import sys

# 3rd party library imports
from dspace_rest_client.client import DSpaceClient
from dspace_rest_client.models import Collection, Community, Item, Bundle, Bitstream  # noqa : F401
import yaml

# local imports


class DSpaceCommon(object):
    """
    Attributes
    ----------
    client : DSpaceClient
        3rd party wrapper for REST methods
    """

    def __init__(self, verbose=None, client=None):

        self.setup_credentials(client)

        self.setup_logging(verbose)

        self.logger.info('Setup nearly complete.')

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        pass

    def setup_credentials(self, client):
        """
        Authorize ourselves to take administrative action with dspace.

        Parameters
        ----------
        client : dspace_rest_client.DSpaceClient
            If this parameter is passed, then we are already authorized.
        """

        if client is not None:
            self.client = client
            return

        p = pathlib.Path.home() / '.config/dspace-utils/dspace.yml'
        config = yaml.safe_load(p.read_text())

        self.username = config['username']
        self.password = config['password']
        self.api_endpoint = config['api_endpoint']

        self.client = DSpaceClient(
            api_endpoint=self.api_endpoint,
            username=self.username,
            password=self.password,
            fake_user_agent=True
        )
        self.client.authenticate()

    def setup_logging(self, log_level):

        level = getattr(logging, log_level.upper())

        self.logger = logging.getLogger('dspace-utils')
        self.logger.setLevel(level)

        format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        formatter = logging.Formatter(format)

        # send logs to the terminal
        h = logging.StreamHandler(sys.stdout)
        h.setLevel(level)
        h.setFormatter(formatter)
        self.logger.addHandler(h)

    def get_item_from_handle(self, handle):
        """
        Locate the entity tied to the given handle.  This can be a collection,
        community, or item.
        """

        url = f'{self.client.API_ENDPOINT}/pid/find'
        params = {'id': f'hdl:{handle}'}
        r = self.client.api_get(url, params)
        r.raise_for_status()

        js = r.json()

        match js['type']:

            case 'collection':
                obj = Collection(js)

            case 'community':
                obj = Community(js)

            case 'item':
                obj = Item(js)

        msg = (
            f"Constructed {js['type']} with UUID {obj.uuid} "
            f"from handle {handle}"
        )
        self.logger.debug(msg)

        return obj
