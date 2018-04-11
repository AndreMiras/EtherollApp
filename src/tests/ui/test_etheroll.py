import os
import shutil
import time
import unittest
from functools import partial
from tempfile import mkdtemp

from kivy.clock import Clock

import etheroll
from utils import Dialog


class UITestCase(unittest.TestCase):

    def setUp(self):
        """
        Sets a temporay KEYSTORE_PATH, so keystore directory and related
        application files will be stored here until tearDown().
        """
        self.temp_path = mkdtemp()
        os.environ['KEYSTORE_PATH'] = self.temp_path

    def tearDown(self):
        shutil.rmtree(self.temp_path, ignore_errors=True)

    # sleep function that catches `dt` from Clock
    def pause(*args):
        time.sleep(0.000001)

    def advance_frames(self, count):
        """
        Borrowed from Kivy 1.10.0+ /kivy/tests/common.py
        GraphicUnitTest.advance_frames()
        Makes it possible to to wait for UI to process, refs #110.
        """
        from kivy.base import EventLoop
        for i in range(count):
            EventLoop.idle()

    def helper_setup(self, app):
        etheroll.SCREEN_SWITCH_DELAY = 0.001

    def helper_test_empty_account(self, app):
        """
        Verifies the UI behaves as expected on empty account list.
        """
        controller = app.root
        accounts = controller.pyethapp.services.accounts
        # loading the app with empty account directory
        self.assertEqual(len(accounts), 0)
        # retrieving the roll button, to click it
        roll_screen = controller.roll_screen
        roll_button = roll_screen.ids.roll_button_id
        self.assertEqual(roll_button.text, 'Roll')
        roll_button.dispatch('on_release')
        # it should open the error dialog
        dialogs = Dialog.dialogs
        self.assertEqual(len(dialogs), 1)
        dialog = dialogs[0]
        self.assertEqual(dialog.title, 'No account selected')
        dialog.dismiss()
        self.assertEqual(len(dialogs), 0)

    # main test function
    def run_test(self, app, *args):
        Clock.schedule_interval(self.pause, 0.000001)
        self.helper_setup(app)
        # lets it finish to init
        self.advance_frames(1)
        self.helper_test_empty_account(app)
        # self.helper_test_empty_account(app)
        # Comment out if you are editing the test, it'll leave the
        # Window opened.
        app.stop()

    # same named function as the filename(!)
    def test_ui_base(self):
        app = etheroll.EtherollApp()
        p = partial(self.run_test, app)
        Clock.schedule_once(p, 0.000001)
        app.run()


if __name__ == '__main__':
    unittest.main()
