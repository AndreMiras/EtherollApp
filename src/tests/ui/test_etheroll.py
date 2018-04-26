import os
import shutil
import threading
import time
import unittest
from functools import partial
from tempfile import mkdtemp
from unittest import mock

from kivy.clock import Clock
from tests import test_pyetheroll

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

    def advance_frames_for_screen(self):
        """
        Gives screen switch animation time to render.
        """
        self.advance_frames(50)

    def advance_frames_for_drawer(self):
        """
        Gives drawer switch animation time to render.
        """
        self.advance_frames_for_screen()

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
        self.advance_frames_for_drawer()
        # checking the drawer items
        navigation = controller.ids.navigation_id
        navigation_drawer = navigation.ids.navigation_drawer_id
        navigation_drawer_items = navigation_drawer.ids.list.children
        self.assertEqual(
            [child.text for child in navigation_drawer_items],
            ['About', 'Settings', 'Wallet', 'Roll results', 'Home'])
        # clicking the about one
        about_item = navigation_drawer_items[0]
        about_item.dispatch('on_release')
        self.advance_frames_for_drawer()
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
        self.advance_frames_for_screen()
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
        self.advance_frames_for_screen()
        screen = screen_manager.children[0]
        self.assertEqual(screen.name, 'about_screen')
        # checks about screen content
        about_content = screen.children[0].children[0].text
        self.assertTrue('EtherollApp version: ' in about_content)
        self.assertTrue(
            'https://github.com/AndreMiras/EtherollApp' in about_content)
        # loads back the default screen
        screen_manager.current = 'roll_screen'
        self.advance_frames_for_screen()

    def helper_no_account_checks(self, app):
        """
        Helper method for checking widget are in expected state on no account.
        """
        controller = app.root
        screen_manager = controller.ids.screen_manager_id
        account_utils = controller.account_utils
        # makes sure no account are loaded
        self.assertEqual(len(account_utils.get_account_list()), 0)
        # loads the switch account screen
        switch_account_screen = controller.switch_account_screen
        screen_manager.current = switch_account_screen.name
        self.advance_frames_for_screen()
        # it should open the warning dialog
        dialogs = Dialog.dialogs
        self.assertEqual(len(dialogs), 1)
        dialog = dialogs[0]
        self.assertEqual(dialog.title, 'No account found')
        dialog.dismiss()
        self.assertEqual(len(dialogs), 0)
        # loads the create new account tab
        create_new_account_nav_item = \
            switch_account_screen.ids.create_new_account_nav_item_id
        create_new_account_nav_item.dispatch('on_tab_press')
        # verifies no current account is setup
        self.assertEqual(switch_account_screen.current_account, None)

    def helper_test_create_first_account(self, app):
        """
        Creates the first account.
        """
        controller = app.root
        account_utils = controller.account_utils
        switch_account_screen = controller.switch_account_screen
        # retrieves the create_new_account widget
        create_new_account = switch_account_screen.ids.create_new_account_id
        # retrieves widgets (password fields, sliders and buttons)
        new_password1_id = create_new_account.ids.new_password1_id
        new_password2_id = create_new_account.ids.new_password2_id
        create_account_button_id = \
            create_new_account.ids.create_account_button_id
        # fills them up with same password
        new_password1_id.text = new_password2_id.text = "password"
        # before clicking the create account button,
        # only the main thread is running
        self.assertEqual(len(threading.enumerate()), 1)
        main_thread = threading.enumerate()[0]
        self.assertEqual(type(main_thread), threading._MainThread)
        # click the create account button
        create_account_button_id.dispatch('on_release')
        # after submitting the account creation thread should run
        self.assertEqual(len(threading.enumerate()), 2)
        self.assertEqual(type(main_thread), threading._MainThread)
        create_account_thread = threading.enumerate()[1]
        self.assertTrue(
            'function CreateNewAccount.create_account'
            in str(create_account_thread._target))
        # waits for the end of the thread
        create_account_thread.join()
        # thread has ended and the main thread is running alone again
        self.assertEqual(len(threading.enumerate()), 1)
        main_thread = threading.enumerate()[0]
        self.assertEqual(type(main_thread), threading._MainThread)
        # verifies the account was created
        self.assertEqual(len(account_utils.get_account_list()), 1)
        # TODO verify the form fields were voided
        # self.assertEqual(new_password1_id.text, '')
        # self.assertEqual(new_password2_id.text, '')
        # we should get redirected to the overview page
        self.advance_frames_for_screen()
        self.assertEqual(controller.screen_manager.current, 'roll_screen')
        # the new account should be loaded in the controller
        self.assertEqual(
            controller.switch_account_screen.current_account,
            account_utils.get_account_list()[0])
        # joins ongoing threads
        [t.join() for t in threading.enumerate()[1:]]
        # check the redirect dialog
        dialogs = Dialog.dialogs
        self.assertEqual(len(dialogs), 1)
        dialog = dialogs[0]
        self.assertEqual(dialog.title, 'Account created, redirecting...')
        dialog.dismiss()
        self.assertEqual(len(dialogs), 0)

    def helper_test_create_account_form(self, app):
        """
        Create account form validation checks.
        Testing both not matching and empty passwords.
        """
        controller = app.root
        switch_account_screen = controller.switch_account_screen
        account_utils = controller.account_utils
        # number of existing accounts before the test
        account_count_before = account_utils.get_account_list()
        # retrieves the create_new_account widget
        create_new_account = switch_account_screen.ids.create_new_account_id
        # retrieves widgets (password fields, sliders and buttons)
        new_password1_id = create_new_account.ids.new_password1_id
        new_password2_id = create_new_account.ids.new_password2_id
        create_account_button_id = \
            create_new_account.ids.create_account_button_id
        passwords_to_try = [
            # passwords not matching
            {
                'new_password1': 'not matching1',
                'new_password2': 'not matching2'
            },
            # passwords empty
            {
                'new_password1': '',
                'new_password2': ''
            },
        ]
        for password_dict in passwords_to_try:
            new_password1_id.text = password_dict['new_password1']
            new_password2_id.text = password_dict['new_password2']
            # makes the account creation fast
            # before clicking the create account button,
            # only the main thread is running
            self.assertEqual(len(threading.enumerate()), 1)
            main_thread = threading.enumerate()[0]
            self.assertEqual(type(main_thread), threading._MainThread)
            # click the create account button
            create_account_button_id.dispatch('on_release')
            # after submitting the account verification thread should run
            threads = threading.enumerate()
            # since we may run into race condition with threading.enumerate()
            # we make the test conditional
            if len(threads) == 2:
                create_account_thread = threading.enumerate()[1]
                self.assertEqual(
                    type(create_account_thread), threading.Thread)
                self.assertTrue(
                    'function CreateNewAccount.create_account'
                    in str(create_account_thread._target))
                # waits for the end of the thread
                create_account_thread.join()
            # the form should popup an error dialog
            dialogs = Dialog.dialogs
            self.assertEqual(len(dialogs), 1)
            dialog = dialogs[0]
            self.assertEqual(dialog.title, 'Invalid form')
            dialog.dismiss()
            self.assertEqual(len(dialogs), 0)
            # no account were created
            self.assertEqual(
                len(account_count_before),
                len(account_utils.get_account_list()))

    def helper_test_chances_input_binding(self, app):
        """
        Makes sure the chances input works as expected, refs:
        https://github.com/AndreMiras/EtherollApp/issues/46
        """
        controller = app.root
        # retrieves both widgets from roll screen
        roll_screen = controller.roll_screen
        chance_of_winning = roll_screen.ids.chance_of_winning_id
        chances_slider = chance_of_winning.ids.chances_slider_id
        chances_input = chance_of_winning.ids.chances_input_id
        # makes sure both values are the same
        self.assertEqual(str(chances_slider.value), chances_input.text)
        # checks the default value
        self.assertEqual(chances_slider.value, 50)
        # verifies values are binded input -> slider
        chances_input.text = '30'
        chances_input.dispatch('on_text_validate')
        self.assertEqual(chances_slider.value, 30)
        # slider -> input
        chances_slider.value = 70
        self.assertEqual(chances_input.text, '70')

    def helper_test_roll_history(self, app):
        """
        Roll history screen should display recent rolls, refs #61.
        """
        bet_results_logs = test_pyetheroll.TestEtheroll.bet_results_logs
        bet_logs = test_pyetheroll.TestEtheroll.bet_logs
        merged_logs = [
            {'bet_log': bet_logs[0], 'bet_result': bet_results_logs[0]},
            {'bet_log': bet_logs[0], 'bet_result': bet_results_logs[0]},
            # not yet resolved (no `LogResult`)
            {'bet_log': bet_logs[2], 'bet_result': None},
        ]
        controller = app.root
        switch_account_screen = controller.switch_account_screen
        # makes sure an account is selected
        self.assertIsNotNone(switch_account_screen.current_account)
        screen_manager = controller.ids.screen_manager_id
        # patches library with fake recent rolls
        with mock.patch('pyetheroll.Etheroll.get_merged_logs') \
                as m_get_merged_logs:
            m_get_merged_logs.return_value = merged_logs
            screen_manager.current = 'roll_results_screen'
            # rolls should be pulled from a thread
            self.assertEqual(len(threading.enumerate()), 2)
            get_last_results_thread = threading.enumerate()[1]
            self.assertEqual(type(get_last_results_thread), threading.Thread)
            self.assertTrue(
                'function RollResultsScreen.get_last_results'
                in str(get_last_results_thread._target))
            # waits for the end of the thread
            get_last_results_thread.join()
            self.advance_frames_for_screen()
            # thread has ended and the main thread is running alone again
            self.assertEqual(len(threading.enumerate()), 1)
            main_thread = threading.enumerate()[0]
            self.assertEqual(type(main_thread), threading._MainThread)
        # verifies recent rolls appear
        roll_results_screen = controller.roll_results_screen
        roll_list = roll_results_screen.ids.roll_list_id
        # roll results items should be displayed
        items = roll_list.children
        self.assertEqual(len(items), len(merged_logs))
        # loads back the default screen
        screen_manager.current = 'roll_screen'
        self.advance_frames_for_screen()

    def helper_test_roll_history_no_tx(self, app):
        """
        When going to the roll history screen with an account selected that has
        no transaction history, the application should fail gracefully.
        """
        # TODO: currently disabled because of a py-etherscan-api bug, refs:
        # https://github.com/AndreMiras/EtherollApp/issues/67
        return
        controller = app.root
        switch_account_screen = controller.switch_account_screen
        # makes sure an account is selected
        self.assertIsNotNone(switch_account_screen.current_account)
        screen_manager = controller.ids.screen_manager_id
        screen_manager.current = 'roll_results_screen'
        # make sure the application is not complaining
        dialogs = Dialog.dialogs
        self.assertEqual(len(dialogs), 1)
        dialog = dialogs[0]
        self.assertEqual(dialog.title, 'No transaction found')
        # loads back the default screen
        screen_manager.current = 'roll_screen'
        self.advance_frames_for_screen()

    def helper_test_roll_history_no_acccount(self, app):
        """
        When going to the roll history screen with no account selected,
        the application should complain and bring back to the main screen.
        """
        controller = app.root
        switch_account_screen = controller.switch_account_screen
        # makes sure no account is selected
        switch_account_screen.current_account = None
        screen_manager = controller.ids.screen_manager_id
        screen_manager.current = 'roll_results_screen'
        self.advance_frames_for_screen()
        dialogs = Dialog.dialogs
        self.assertEqual(len(dialogs), 1)
        dialog = dialogs[0]
        self.assertEqual(dialog.title, 'No account selected')
        dialog.dismiss()
        # we should get redirected to the overview page
        self.advance_frames_for_screen()
        self.assertEqual(controller.screen_manager.current, 'roll_screen')

    # main test function
    def run_test(self, app, *args):
        Clock.schedule_interval(self.pause, 0.000001)
        self.helper_setup(app)
        # lets it finish to init
        self.advance_frames(1)
        self.helper_test_empty_account(app)
        self.helper_test_toolbar(app)
        self.helper_test_about_screen(app)
        self.helper_test_create_first_account(app)
        self.helper_test_create_account_form(app)
        self.helper_test_chances_input_binding(app)
        self.helper_test_roll_history(app)
        self.helper_test_roll_history_no_tx(app)
        self.helper_test_roll_history_no_acccount(app)
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
