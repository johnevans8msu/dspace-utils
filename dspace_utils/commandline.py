# standard library imports
import argparse

# local imports
from dspace_utils import OwningCollection
from dspace_utils import ThumbnailGenerator

_LOGGING_VERBOSITY_CHOICES = ["critical", "error", "warning", "info", "debug"]


def run_thumbnail_generator():

    epilog = (
        "Rather than use command line arguments for passing credentials, it \n"
        "is required to make use of a configuration file.  This YAML file\n"
        "should be located at $HOME/.config/dspace-utils/dspace.yml.  The \n"
        "format of the file should be as follows:\n\n"
        "    +----------------------------------------------------------\n"
        "    | config:\n"
        "    |     username: the-username\n"
        "    |     password: the-user-password\n"
        "    |     api: DSpace API endpoint,\n"
        "    |          e.g. https://localhost/server/api\n"
        "    |     postgres_uri: postgres URI,\n"
        "    |          e.g. postgres://dspace:password@localhost/dspace\n"
    )
    parser = argparse.ArgumentParser(
        epilog=epilog,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument('handle')

    parser.add_argument(
        '--verbose', help='Logging level',
        choices=_LOGGING_VERBOSITY_CHOICES,
        default='info'
    )

    args = parser.parse_args()

    with ThumbnailGenerator(args.handle, verbose=args.verbose) as p:
        p.run()


def run_change_owning_collection():

    epilog = (
        "Rather than use command line arguments for passing credentials, it \n"
        "is required to make use of a configuration file.  This YAML file\n"
        "should be located at $HOME/.config/dspace-utils/dspace.yml.  The \n"
        "format of the file should be as follows:\n\n"
        "    +----------------------------------------------------------\n"
        "    | config:\n"
        "    |     username: the-username\n"
        "    |     password: the-user-password\n"
        "    |     api: DSpace API endpoint,\n"
        "    |          e.g. https://localhost/server/api\n"
        "    |     postgres_uri: postgres URI,\n"
        "    |          e.g. postgres://dspace:password@localhost/dspace\n"
    )
    parser = argparse.ArgumentParser(
        epilog=epilog,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument('item_handle', help="Handle for existing item.")
    parser.add_argument('new', help="Handle for new owning collection.")

    parser.add_argument(
        '--verbose', help='Logging level',
        choices=_LOGGING_VERBOSITY_CHOICES,
        default='info'
    )

    args = parser.parse_args()

    with OwningCollection(
        item_handle=args.item_handle,
        target_collection_handle=args.new,
        verbose=args.verbose
    ) as p:
        p.run()
