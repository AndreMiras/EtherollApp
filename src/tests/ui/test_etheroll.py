import os
import time
from http.client import RemoteDisconnected
from json.decoder import JSONDecodeError

from requests.exceptions import ConnectionError
from telenium.tests import TeleniumTestCase
from urllib3.exceptions import ProtocolError


def src_dir():
    return os.path.join(
        os.path.dirname(os.path.abspath(__file__)), '../..')


def main_path():
    return os.path.join(src_dir(), 'main.py')


class UITestCase(TeleniumTestCase):

    cmd_entrypoint = [main_path()]

    def init(self):
        """
        Gives time for `App.get_running_app().root` to be ready.
        """
        time.sleep(1)

    @classmethod
    def tearDownClass(cls):
        try:
            super(UITestCase, cls).tearDownClass()
        except (RemoteDisconnected, JSONDecodeError,
                ProtocolError, ConnectionError):
            # TODO: this is probably happening because `Thread.daemon = True`
            pass

    def test_roll_exists(self):
        """
        Basic test that simply verifies the lending screen has the roll button.
        """
        self.assertExists(
            "/Controller//MDRaisedButton[0]/MDLabel[0][@text=\"ROLL\"]")
