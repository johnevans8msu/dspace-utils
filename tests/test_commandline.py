# standard library imports
import sys
import unittest
from unittest import mock

# local imports
from dspace_utils import commandline


class TestSuite(unittest.TestCase):

    @mock.patch('dspace_utils.thumbnails.DSpaceClient')
    @mock.patch('dspace_utils.thumbnails.ThumbnailGenerator.run')
    def test_thumbnail_smoke(self, mock_run, mock_dspace_client):
        """
        Scenario
        """

        mock_run.new = lambda x: None

        new_argv = [
            '', '1/1825', '--username', 'me', '--password', 'something'
        ]
        with mock.patch.object(sys, 'argv', new=new_argv):
            commandline.run_thumbnail_generator()