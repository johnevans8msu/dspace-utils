# standard library imports
import argparse

# local imports
from dspace_utils import ThumbnailGenerator


def run_thumbnail_generator():

    parser = argparse.ArgumentParser()

    parser.add_argument('handle')

    help = "Connect to this API endpoint."
    default = 'https://lib1.lib.montana.edu/server/api'
    parser.add_argument('-e', '--api_endpoint', default=default, help=help)

    help = "Authenticate to dspace instance as this user."
    parser.add_argument('-u', '--username', help=help)

    help = "Authenticate to dspace instance with this password."
    parser.add_argument('-p', '--password', help=help)

    args = parser.parse_args()

    with ThumbnailGenerator(
        args.handle,
        api_endpoint=args.api_endpoint,
        username=args.username,
        password=args.password,
    ) as p:
        p.run()