# standard library imports
import argparse

# local imports
from dspace_utils import (
    LicenseChanger, OwningCollection, ThumbnailGenerator, MetadataDumper,
    CollectionCreator
)

_LOGGING_VERBOSITY_CHOICES = ["critical", "error", "warning", "info", "debug"]

_EPILOG = (
    "Rather than use command line arguments for passing credentials, it is \n"
    "required to make use of a configuration file.  This YAML file should \n"
    "be located at $HOME/.config/dspace-utils/dspace.yml.  The format of \n"
    "the file should be as follows:\n\n"
    "    +----------------------------------------------------------\n"
    "    | config:\n"
    "    |     username: the-username\n"
    "    |     password: the-user-password\n"
    "    |     api: DSpace API endpoint,\n"
    "    |          e.g. https://localhost/server/api\n\n"
)


def run_thumbnail_generator():

    description = "Try to force an item's thumbnail to be regenerated."
    parser = argparse.ArgumentParser(
        description=description,
        epilog=_EPILOG,
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


def run_create_collection():

    description = "Create a collection."
    parser = argparse.ArgumentParser(
        description=description,
        epilog=_EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    help = "Title of new collection."
    parser.add_argument('collection_title', help=help)

    help = (
        "ID of the parent community.  This can be either a UUID or a handle."
    )
    parser.add_argument('community', help=help)

    help = "Description of new collection, can be HTML."
    parser.add_argument('--description', help=help)

    parser.add_argument(
        '--verbose', help='Logging level',
        choices=_LOGGING_VERBOSITY_CHOICES,
        default='info'
    )

    args = parser.parse_args()

    with CollectionCreator(
        collection_title=args.collection_title,
        community=args.community,
        description=args.description,
        verbose=args.verbose
    ) as p:
        p.run()


def run_change_owning_collection():

    description = "Change the owning collection of an article/item."
    parser = argparse.ArgumentParser(
        description=description,
        epilog=_EPILOG,
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


def run_change_license():

    description = "Change the license for an article/item."
    parser = argparse.ArgumentParser(
        description=description,
        epilog=_EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument('item_handle', help="Handle for existing item.")
    parser.add_argument('license', help="File containing new license text.")

    parser.add_argument(
        '--verbose', help='Logging level',
        choices=_LOGGING_VERBOSITY_CHOICES,
        default='info'
    )

    args = parser.parse_args()

    with LicenseChanger(
        item_handle=args.item_handle, license_file=args.license,
        verbose=args.verbose
    ) as p:
        p.run()


def run_dump_item_metadata():

    description = "Change the owning collection of an article/item."
    parser = argparse.ArgumentParser(
        description=description,
        epilog=_EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument('item_handle', help="Handle for existing item.")

    parser.add_argument(
        '--verbose', help='Logging level',
        choices=_LOGGING_VERBOSITY_CHOICES,
        default='info'
    )

    args = parser.parse_args()

    with MetadataDumper(
        item_handle=args.item_handle, verbose=args.verbose
    ) as p:
        print(p)
