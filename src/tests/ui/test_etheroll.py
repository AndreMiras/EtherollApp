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
        accounts = controller.account_utils.get_account_list()
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

    def helper_test_toolbar(self, app):
        """
        Opens the about screen using the toolbar.
        """
        controller = app.root
        toolbar = controller.ids.toolbar_id
        left_action_items = toolbar.left_action_items
        # checking action items displayed, it should be only the menu
        self.assertEqual(len(left_action_items), 1)
        menu_action_item = left_action_items[0]
        self.assertEqual(menu_action_item[0], 'menu')
        self.assertEqual(
            menu_action_item[1].__qualname__,
            'CustomToolbar.load_default_buttons.<locals>.<lambda>')
        # this is reflected in the toolbar left_actions widget
        left_actions = toolbar.ids.left_actions
        self.assertEqual(len(left_actions.children), 1)
        # clicking the menu action item should load the navigation drawer
        left_actions.children[0].dispatch('on_release')
        # the drawer animation takes time
        self.advance_frames(50)
        # checking the drawer items
        navigation = controller.ids.navigation_id
        navigation_drawer = navigation.ids.navigation_drawer_id
        navigation_drawer_items = navigation_drawer.ids.list.children
        self.assertEqual(
            [child.text for child in navigation_drawer_items],
            ['About', 'Settings', 'Wallet', 'Home'])
        # clicking the about one
        about_item = navigation_drawer_items[0]
        about_item.dispatch('on_release')
        # the drawer animation takes time
        self.advance_frames(50)
        self.assertEqual(
            controller.ids.screen_manager_id.current, 'about_screen')
        # toolbar should now be loaded with the back button
        left_action_items = toolbar.left_action_items
        self.assertEqual(len(left_action_items), 1)
        menu_action_item = left_action_items[0]
        self.assertEqual(menu_action_item[0], 'arrow-left')
        # going back to main screen
        left_actions = toolbar.ids.left_actions
        left_actions.children[0].dispatch('on_release')
        # loading screen takes time
        self.advance_frames(50)
        self.assertEqual(
            controller.ids.screen_manager_id.current, 'roll_screen')

    def helper_test_about_screen(self, app):
        """
        Verifies the about screen loads and shows infos.
        """
        controller = app.root
        screen_manager = controller.ids.screen_manager_id
        # verify the landing screen is loaded by default
        screen = screen_manager.children[0]
        self.assertEqual(screen.name, 'roll_screen')
        # loads the about and verify
        screen_manager.current = 'about_screen'
        # loading screen takes time
        self.advance_frames(50)
        screen = screen_manager.children[0]
        self.assertEqual(screen.name, 'about_screen')
        # checks about screen content
        about_content = screen.children[0].children[0].text
        self.assertTrue('EtherollApp version: ' in about_content)
        self.assertTrue(
            'https://github.com/AndreMiras/EtherollApp' in about_content)
        # loads back the default screen
        screen_manager.current = 'roll_screen'
        # loading screen takes time
        self.advance_frames(50)

    # main test function
    def run_test(self, app, *args):
        Clock.schedule_interval(self.pause, 0.000001)
        self.helper_setup(app)
        # lets it finish to init
        self.advance_frames(1)
        self.helper_test_empty_account(app)
        self.helper_test_toolbar(app)
        self.helper_test_about_screen(app)
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
