# standard library imports
import unittest

# 3rd party library imports

# local imports


class TestCommon(unittest.TestCase):

    def setUp(self):
        self.config = {
            'username': 'someuser',
            'password': 'somepass',
            'api_endpoint': 'http://localhost/server/api',
        }

        self.config_mocker = unittest.mock.patch(
            'dspace_utils.common.yaml.safe_load', return_value=self.config,
        )
        self.config_mocker.start()

    def tearDown(self):
        self.config_mocker.stop()
