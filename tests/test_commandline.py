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
    @mock.patch('dspace_utils.thumbnails.psycopg2', autospec=True)
    def test_thumbnail_smoke(
        self, mock_postgres, mock_run, mock_dspace_client
    ):
        """
        Scenario:  invoke commandline utility

        Expected result:
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
