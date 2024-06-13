# standard library imports
import json
import sys
from unittest import mock

# local imports
from dspace_utils import commandline
from .common import TestCommon


class TestSuite(TestCommon):

    @mock.patch('dspace_utils.common.DSpaceClient')
    @mock.patch('dspace_utils.thumbnails.ThumbnailGenerator.run')
    def test_thumbnail_smoke(self, mock_run, mock_dspace_client):
        """
        Scenario:  invoke commandline utility

        Expected result:  no errors
        """

        mock_run.new = lambda x: None

        new_argv = ['', '1/1825', '--verbose', 'info']
        with (
            mock.patch(
                'dspace_utils.common.pathlib.Path.read_text',
                return_value=json.dumps(self.config),
            ),
            mock.patch.object(sys, 'argv', new=new_argv),
        ):
            commandline.run_thumbnail_generator()

    @mock.patch('dspace_utils.common.DSpaceClient')
    @mock.patch('dspace_utils.collections.OwningCollection.run')
    def test_owning_collection_smoke(self, mock_run, mock_dspace_client):
        """
        Scenario:  invoke commandline utility for changing the owning
        collection

        Expected result: no errors
        """

        mock_run.new = lambda x: None

        new_argv = ['', '1/1234', '1/2345']
        with (
            mock.patch(
                'dspace_utils.common.pathlib.Path.read_text',
                return_value=json.dumps(self.config),
            ),
            mock.patch.object(sys, 'argv', new=new_argv),
        ):
            commandline.run_change_owning_collection()

    @mock.patch('dspace_utils.common.DSpaceClient')
    @mock.patch('dspace_utils.metadata.MetadataDumper.run')
    def test_dump_metadata_smoke(self, mock_run, mock_dspace_client):
        """
        Scenario:  invoke commandline utility for dumping metadata

        Expected result: no errors
        """

        mock_run.new = lambda x: None

        new_argv = ['', '1/1234']
        with (
            mock.patch(
                'dspace_utils.common.pathlib.Path.read_text',
                return_value=json.dumps(self.config),
            ),
            mock.patch.object(sys, 'argv', new=new_argv),
        ):
            commandline.run_dump_item_metadata()

    @mock.patch('dspace_utils.common.DSpaceClient')
    @mock.patch('dspace_utils.licenses.LicenseChanger.run')
    def test_change_license_smoke(self, mock_run, mock_dspace_client):
        """
        Scenario:  invoke commandline utility for changing the license

        Expected result: no errors
        """

        mock_run.new = lambda x: None

        new_argv = ['', '1/1234', 'tests/data/new-license.txt']
        with (
            mock.patch(
                'dspace_utils.common.pathlib.Path.read_text',
                return_value=json.dumps(self.config),
            ),
            mock.patch.object(sys, 'argv', new=new_argv),
        ):
            commandline.run_change_license()
