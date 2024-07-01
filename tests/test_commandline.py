# standard library imports
import sys
from unittest import mock

# 3rd party library imports
import requests

# local imports
from dspace_utils import commandline
from .common import TestCommon


@mock.patch('dspace_utils.common.DSpaceClient')
class TestSuite(TestCommon):

    @mock.patch('dspace_utils.migration.LiveMigrator.run')
    def test_migrate_to_live_smoke(self, mock_run, mock_dspace_client):
        """
        Scenario:  invoke commandline utility

        Expected result:  no errors
        """

        mock_run.new = lambda x: None

        new_argv = ['', '1/1825', '--verbose', 'info']
        with mock.patch.object(sys, 'argv', new=new_argv):
            commandline.run_live_migration()

    @mock.patch('dspace_utils.thumbnails.ThumbnailGenerator.run')
    def test_thumbnail_smoke(self, mock_run, mock_dspace_client):
        """
        Scenario:  invoke commandline utility

        Expected result:  no errors
        """

        mock_run.new = lambda x: None

        new_argv = ['', '1/1825', '--verbose', 'info']
        with mock.patch.object(sys, 'argv', new=new_argv):
            commandline.run_thumbnail_generator()

    @mock.patch('dspace_utils.collections.CollectionCreator.run')
    def test_create_collection_smoke(self, mock_run, mock_dspace_client):
        """
        Scenario:  invoke commandline utility for creating a collection.

        Expected result: no errors
        """

        mock_run.new = lambda x: None

        new_argv = ['', 'thang', '12345678-1234-1234-1234-123456789abc']
        with mock.patch.object(sys, 'argv', new=new_argv):
            commandline.run_create_collection()

    @mock.patch('dspace_utils.collections.OwningCollection.run')
    def test_owning_collection_smoke(self, mock_run, mock_dspace_client):
        """
        Scenario:  invoke commandline utility for changing the owning
        collection

        Expected result: no errors
        """

        mock_run.new = lambda x: None

        # Mock the api_get call that returns an item
        api_get_mock = mock.create_autospec(requests.Response)
        api_get_mock.json.return_value = {
            'type': 'item',
            'uuid': '98765432-1234-1234-1234-123456789abc',
            'handle': '1/2345'
        }
        mock_dspace_client.return_value.api_get.return_value = api_get_mock

        new_argv = ['', '1/1234', '1/2345']
        with mock.patch.object(sys, 'argv', new=new_argv):
            commandline.run_change_owning_collection()

    @mock.patch('dspace_utils.metadata.MetadataDumper.run')
    def test_dump_metadata_smoke(self, mock_run, mock_dspace_client):
        """
        Scenario:  invoke commandline utility for dumping metadata

        Expected result: no errors
        """

        mock_run.new = lambda x: None

        # Mock the api_get call that returns an item
        api_get_mock = mock.create_autospec(requests.Response)
        api_get_mock.json.return_value = {'type': 'item'}
        mock_dspace_client.return_value.api_get.return_value = api_get_mock

        new_argv = ['', '1/1234']
        with mock.patch.object(sys, 'argv', new=new_argv):
            commandline.run_dump_item_metadata()

    @mock.patch('dspace_utils.licenses.LicenseChanger.run')
    def test_change_license_smoke(self, mock_run, mock_dspace_client):
        """
        Scenario:  invoke commandline utility for changing the license

        Expected result: no errors
        """

        mock_run.new = lambda x: None

        new_argv = ['', '1/1234', 'tests/data/new-license.txt']
        with mock.patch.object(sys, 'argv', new=new_argv):
            commandline.run_change_license()
