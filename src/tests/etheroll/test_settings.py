import shutil
import unittest
from tempfile import mkdtemp
from unittest import mock

from kivy.app import App
from pyetheroll.constants import ChainID

from etheroll.settings import Settings
from service.main import EtherollApp


class TestSettings(unittest.TestCase):
    """
    Unit tests Settings methods.
    """
    @classmethod
    def setUpClass(cls):
        EtherollApp()

    def setUp(self):
        """
        Creates a temporary user data dir for storing the user config.
        """
        self.temp_path = mkdtemp(prefix='etheroll')
        self.app = App.get_running_app()
        self.app._user_data_dir = self.temp_path

    def tearDown(self):
        """
        Deletes temporary user data dir.
        """
        shutil.rmtree(self.temp_path, ignore_errors=True)

    def test_get_stored_network(self):
        network = Settings.get_stored_network()
        assert network == ChainID.MAINNET

    def test_get_android_keystore_prefix(self):
        """
        The keystore prefix should be the same as user_data_dir by default.
        But it can also be persisted to the sdcard.
        """
        assert Settings.is_persistent_keystore() is False
        prefix = Settings._get_android_keystore_prefix()
        assert prefix == self.app.user_data_dir
        with mock.patch.object(
                Settings, 'is_persistent_keystore', return_value=True):
            prefix = Settings._get_android_keystore_prefix()
            assert prefix == '/sdcard/etheroll'
