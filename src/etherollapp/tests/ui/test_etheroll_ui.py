import os
import shutil
import threading
import time
import unittest
from functools import partial
from tempfile import mkdtemp
from unittest import mock
from unittest.mock import patch

from hexbytes import HexBytes
from kivy.clock import Clock
from kivy.core.image import Image
from requests.exceptions import ConnectionError

from etherollapp.etheroll.constants import BASE_DIR
from etherollapp.etheroll.controller import EtherollApp
from etherollapp.etheroll.ui_utils import Dialog
from etherollapp.tests.utils import PyEtherollTestUtils


def get_camera_class():
    """
    Continuous integration providers don't have a camera available.
    """
    if os.environ.get('CI', False):
        Camera = None
    else:
        from kivy.core.camera import Camera
    return Camera


def patch_core_camera():
    Camera = get_camera_class()
    return patch('kivy.uix.camera.CoreCamera', wraps=Camera)


def patch_fetch_update_balance():
    return patch('etherollapp.etheroll.roll.RollScreen.fetch_update_balance')


def advance_frames(count):
    """
    Borrowed from Kivy 1.10.0+ /kivy/tests/common.py
    GraphicUnitTest.advance_frames()
    Makes it possible to to wait for UI to process, refs #110.
    """
    from kivy.base import EventLoop
    for i in range(count):
        EventLoop.idle()


def advance_frames_for_screen():
    """Gives screen switch animation time to render."""
    advance_frames(50)


def advance_frames_for_drawer():
    """Gives drawer switch animation time to render."""
    advance_frames_for_screen()


def load_roll_screen(screen_manager):
    """Loads back the default screen."""
    with patch_fetch_update_balance() as m_fetch_update_balance:
        # loads back the default screen
        screen_manager.current = 'roll_screen'
    assert m_fetch_update_balance.call_args_list == [mock.call()]
    advance_frames_for_screen()


class UITestCase(unittest.TestCase):

    def setUp(self):
        """
        Sets a temporay KEYSTORE_PATH, so keystore directory and related
        application files will be stored here until tearDown().
        """
        self.temp_path = mkdtemp()
        os.environ['KEYSTORE_PATH'] = self.temp_path
        # see `kivy.App._get_user_data_dir()`
        os.environ['XDG_CONFIG_HOME'] = self.temp_path

    def tearDown(self):
        shutil.rmtree(self.temp_path, ignore_errors=True)

    def helper_setup(self, app):
        pass
        # etheroll.SCREEN_SWITCH_DELAY = 0.001

    # sleep function that catches `dt` from Clock
    def pause(*args):
        time.sleep(0.000001)

    @staticmethod
    def join_threads():
        """Joins pending threads except for main and OSC threads."""
        threads = threading.enumerate()
        # lists all threads but the main one
        for thread in threads[2:]:
            thread.join()

    @staticmethod
    def wait_mock_called(m, timeout=1):
        """Returns True if `m` was called before the `timeout` in seconds."""
        step = 0.1
        while timeout > 0 and not m.called:
            time.sleep(step)
            timeout -= step
        return m.called

    def helper_test_empty_account(self, app):
        """Verifies the UI behaves as expected on empty account list."""
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
        """Opens the about screen using the toolbar."""
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
        advance_frames_for_drawer()
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
        advance_frames_for_drawer()
        self.assertEqual(
            controller.screen_manager.current, 'about_screen')
        # toolbar should now be loaded with the back button
        left_action_items = toolbar.left_action_items
        self.assertEqual(len(left_action_items), 1)
        menu_action_item = left_action_items[0]
        self.assertEqual(menu_action_item[0], 'arrow-left')
        # going back to main screen
        left_actions = toolbar.ids.left_actions
        with patch_fetch_update_balance() as m_fetch_update_balance:
            left_actions.children[0].dispatch('on_release')
        assert m_fetch_update_balance.call_args_list == [mock.call()]
        advance_frames_for_screen()
        self.assertEqual(
            controller.screen_manager.current, 'roll_screen')

    def helper_test_about_screen(self, app):
        """Verifies the about screen loads and shows infos."""
        controller = app.root
        screen_manager = controller.screen_manager
        # verify the landing screen is loaded by default
        screen = screen_manager.children[0]
        self.assertEqual(screen.name, 'roll_screen')
        # loads the about and verify
        screen_manager.current = 'about_screen'
        advance_frames_for_screen()
        screen = screen_manager.children[0]
        self.assertEqual(screen.name, 'about_screen')
        # checks about screen content
        about_screen_manager = screen.children[0].children[1]
        about_overview = about_screen_manager.get_screen('about_overview')
        about_content = about_overview.children[0].children[0].text
        self.assertTrue('EtherollApp version: ' in about_content)
        self.assertTrue(
            'https://github.com/AndreMiras/EtherollApp' in about_content)
        load_roll_screen(screen_manager)

    def helper_no_account_checks(self, app):
        """
        Helper method for checking widget are in expected state on no account.
        """
        controller = app.root
        screen_manager = controller.screen_manager
        account_utils = controller.account_utils
        # makes sure no account are loaded
        self.assertEqual(len(account_utils.get_account_list()), 0)
        # loads the switch account screen
        screen_manager.current = 'switch_account_screen'
        advance_frames_for_screen()
        switch_account_screen = controller.switch_account_screen
        advance_frames_for_screen()
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
        """Creates the first account."""
        controller = app.root
        account_utils = controller.account_utils
        screen_manager = controller.screen_manager
        screen_manager.current = 'switch_account_screen'
        advance_frames_for_screen()
        # makes sure it still complains for no account
        dialogs = Dialog.dialogs
        self.assertEqual(len(dialogs), 1)
        dialog = dialogs[0]
        self.assertEqual(dialog.title, 'No account found')
        dialog.dismiss()
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
        # only the main and OSC threads are running
        threads = threading.enumerate()
        self.assertEqual(len(threads), 2, threads[-1]._target)
        main_thread = threads[0]
        self.assertEqual(type(main_thread), threading._MainThread)
        with patch_fetch_update_balance() as m_fetch_update_balance:
            # click the create account button
            create_account_button_id.dispatch('on_release')
            # after submitting the account creation thread should also run
            threads = threading.enumerate()
            self.assertEqual(len(threads), 3)
            self.assertEqual(type(main_thread), threading._MainThread)
            create_account_thread = threads[2]
            self.assertTrue(
                'function CreateNewAccount.create_account'
                in str(create_account_thread._target))
            # waits for the end of the thread
            create_account_thread.join()
        assert m_fetch_update_balance.call_args_list == [mock.call()]
        # thread has ended, main & OSC threads only are running again
        threads = threading.enumerate()
        self.assertEqual(len(threads), 2)
        main_thread = threads[0]
        self.assertEqual(type(main_thread), threading._MainThread)
        # verifies the account was created
        self.assertEqual(len(account_utils.get_account_list()), 1)
        # TODO verify the form fields were voided
        # self.assertEqual(new_password1_id.text, '')
        # self.assertEqual(new_password2_id.text, '')
        # we should get redirected to the overview page
        advance_frames_for_screen()
        self.assertEqual(controller.screen_manager.current, 'roll_screen')
        # the new account should be loaded in the controller
        self.assertEqual(
            controller.current_account,
            account_utils.get_account_list()[0])
        self.join_threads()
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
        screen_manager = controller.screen_manager
        screen_manager.current = 'switch_account_screen'
        advance_frames_for_screen()
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
            # only the main and OSC threads are running
            self.assertEqual(len(threading.enumerate()), 2)
            main_thread = threading.enumerate()[0]
            self.assertEqual(type(main_thread), threading._MainThread)
            # click the create account button
            create_account_button_id.dispatch('on_release')
            # after submitting the account verification thread should run
            threads = threading.enumerate()
            # since we may run into race condition with threading.enumerate()
            # we make the test conditional
            if len(threads) == 3:
                create_account_thread = threading.enumerate()[2]
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
        """Makes sure the chances input works as expected, refs #46."""
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
        """Roll history screen should display recent rolls, refs #61."""
        bet_results_logs = PyEtherollTestUtils.bet_results_logs
        bet_logs = PyEtherollTestUtils.bet_logs
        merged_logs = [
            {'bet_log': bet_logs[0], 'bet_result': bet_results_logs[0]},
            {'bet_log': bet_logs[0], 'bet_result': bet_results_logs[0]},
            # not yet resolved (no `LogResult`)
            {'bet_log': bet_logs[2], 'bet_result': None},
        ]
        controller = app.root
        # makes sure an account is selected
        self.assertIsNotNone(controller.current_account)
        screen_manager = controller.screen_manager
        # patches library with fake recent rolls
        with patch('pyetheroll.etheroll.Etheroll.get_merged_logs') \
                as m_get_merged_logs:
            m_get_merged_logs.return_value = merged_logs
            screen_manager.current = 'roll_results_screen'
            # waits and makes sure the mock to be called, refs #138
            self.assertTrue(self.wait_mock_called(m_get_merged_logs))
            # since get_merged_logs got called, the get_last_results thread
            # should be over, only main & OSC threads only are running
            thread_info = [(t, t._target) for t in threading.enumerate()]
            self.assertEqual(
                len(threading.enumerate()), 2, thread_info)
            advance_frames_for_screen()
            # thread has ended, main & OSC threads only are running again
            self.assertEqual(len(threading.enumerate()), 2)
            main_thread = threading.enumerate()[0]
            self.assertEqual(type(main_thread), threading._MainThread)
        # verifies recent rolls appear
        roll_results_screen = controller.roll_results_screen
        roll_list = roll_results_screen.ids.roll_list_id
        # roll results items should be displayed
        items = roll_list.children
        self.assertEqual(len(items), len(merged_logs))
        load_roll_screen(screen_manager)

    def helper_test_roll_history_no_tx(self, app):
        """
        When going to the roll history screen with an account selected that has
        no transaction history, the application should fail gracefully.
        """
        # TODO: currently disabled because of a py-etherscan-api bug, refs:
        # https://github.com/AndreMiras/EtherollApp/issues/67
        return
        controller = app.root
        # makes sure an account is selected
        self.assertIsNotNone(controller.current_account)
        screen_manager = controller.screen_manager
        screen_manager.current = 'roll_results_screen'
        # make sure the application is not complaining
        dialogs = Dialog.dialogs
        self.assertEqual(len(dialogs), 1)
        dialog = dialogs[0]
        self.assertEqual(dialog.title, 'No transaction found')
        load_roll_screen(screen_manager)

    def helper_test_roll_history_no_account(self, app):
        """
        When going to the roll history screen with no account selected,
        the application should complain and bring back to the main screen.
        """
        controller = app.root
        screen_manager = controller.screen_manager
        controller.current_account = None
        screen_manager = controller.screen_manager
        with patch_fetch_update_balance() as m_fetch_update_balance:
            screen_manager.current = 'roll_results_screen'
            advance_frames_for_screen()
        assert m_fetch_update_balance.call_args_list == [mock.call()]
        dialogs = Dialog.dialogs
        self.assertEqual(len(dialogs), 1)
        dialog = dialogs[0]
        self.assertEqual(dialog.title, 'No account selected')
        dialog.dismiss()
        # we should get redirected to the overview page
        advance_frames_for_screen()
        self.assertEqual(controller.screen_manager.current, 'roll_screen')
        # e.g. fetch_update_balance thread
        self.join_threads()

    def helper_test_roll(self, app):
        """Trying to place a valid roll."""
        controller = app.root
        # makes sure an account is selected
        # TODO: do it the proper way by clicking the UI
        controller.current_account = \
            controller.account_utils.get_account_list()[0]
        # retrieving the roll button, to click it
        roll_screen = controller.roll_screen
        roll_button = roll_screen.ids.roll_button_id
        self.assertEqual(roll_button.text, 'Roll')
        roll_button.dispatch('on_release')
        # it should open the error dialog
        dialogs = Dialog.dialogs
        self.assertEqual(len(dialogs), 1)
        dialog = dialogs[0]
        self.assertEqual(dialog.title, 'Enter your password')
        dialog.content.password = 'password'
        unlock_button = dialog._action_buttons[0]
        with patch('pyetheroll.etheroll.Etheroll.player_roll_dice') \
                as m_player_roll_dice:
            m_player_roll_dice.return_value = HexBytes(
                '0x7be6e37621eb12db7dc535954345f69'
                'd8cc5644b2de0ec32a344ca33c3054237')
            unlock_button.dispatch('on_release')
            threads = threading.enumerate()
            # since we may run into race condition with threading.enumerate()
            # we make the test conditional
            if len(threads) == 3:
                # rolls should be fetched from a thread
                self.assertEqual(len(threads), 3)
                player_roll_dice_thread = threads[2]
                self.assertEqual(
                    type(player_roll_dice_thread), threading.Thread)
                self.assertTrue(
                    'function Controller.player_roll_dice'
                    in str(player_roll_dice_thread._target))
                # waits for the end of the thread
                player_roll_dice_thread.join()
        advance_frames_for_screen()
        # thread has ended, main & OSC threads only are running again
        self.assertEqual(len(threading.enumerate()), 2)
        main_thread = threading.enumerate()[0]
        self.assertEqual(type(main_thread), threading._MainThread)
        # a confirmation dialog with transaction hash should pop
        dialogs = Dialog.dialogs
        self.assertEqual(len(dialogs), 1)
        dialog = dialogs[0]
        self.assertEqual(dialog.title, 'Rolled successfully')
        dialog.dismiss()
        self.assertEqual(len(dialogs), 0)

    def helper_test_roll_connection_error(self, app):
        """
        Makes sure ConnectionError on roll is handled gracefully, refs #111.
        """
        controller = app.root
        # retrieving the roll button, to click it
        roll_screen = controller.roll_screen
        roll_button = roll_screen.ids.roll_button_id
        self.assertEqual(roll_button.text, 'Roll')
        with patch('web3.eth.Eth.getTransactionCount') \
                as m_getTransactionCount:
            m_getTransactionCount.side_effect = \
                ConnectionError('Whatever ConnectionError')
            roll_button.dispatch('on_release')
            threads = threading.enumerate()
            # since we may run into race condition with threading.enumerate()
            # we make the test conditional
            if len(threads) == 3:
                # rolls should be fetched from a thread
                self.assertEqual(len(threads), 3)
                player_roll_dice_thread = threads[2]
                self.assertEqual(
                    type(player_roll_dice_thread), threading.Thread)
                self.assertTrue(
                    'function Controller.player_roll_dice'
                    in str(player_roll_dice_thread._target))
                # waits for the end of the thread
                player_roll_dice_thread.join()
        advance_frames_for_screen()
        # thread has ended, main & OSC threads only are running again
        self.assertEqual(len(threading.enumerate()), 2)
        main_thread = threading.enumerate()[0]
        self.assertEqual(type(main_thread), threading._MainThread)
        # an error dialog should pop
        dialogs = Dialog.dialogs
        self.assertEqual(len(dialogs), 1)
        dialog = dialogs[0]
        self.assertEqual(dialog.title, 'Error rolling')
        self.assertEqual(dialog.content.text, 'Whatever ConnectionError')
        dialog.dismiss()
        self.assertEqual(len(dialogs), 0)

    def helper_test_roll_password(self, app):
        """
        Makes sure wrong passwords are handled properly.
        Relevant error messages should prompt and it should be possible to
        try again, refs #9.
        """
        controller = app.root
        # makes sure an account is selected
        self.assertIsNotNone(controller.current_account)
        # voids cached passwords
        controller._account_passwords = {}
        # retrieving the roll button, to click it
        roll_screen = controller.roll_screen
        roll_button = roll_screen.ids.roll_button_id
        self.assertEqual(roll_button.text, 'Roll')
        roll_button.dispatch('on_release')
        # it should open the error dialog
        dialogs = Dialog.dialogs
        self.assertEqual(len(dialogs), 1)
        dialog = dialogs[0]
        self.assertEqual(dialog.title, 'Enter your password')
        dialog.content.password = 'wrong password'
        unlock_button = dialog._action_buttons[0]
        unlock_button.dispatch('on_release')
        # runs in a thread since password unlocking and tx signing takes time
        threads = threading.enumerate()
        # since we may run into race condition with threading.enumerate()
        # we make the test conditional
        if len(threads) == 3:
            # rolls should be fetched from a thread
            self.assertEqual(len(threads), 3)
            player_roll_dice_thread = threads[2]
            self.assertEqual(
                type(player_roll_dice_thread), threading.Thread)
            self.assertTrue(
                'function Controller.player_roll_dice'
                in str(player_roll_dice_thread._target))
            # waits for the end of the thread
            player_roll_dice_thread.join()
        advance_frames_for_screen()
        # thread has ended, main & OSC threads only are running again
        self.assertEqual(len(threading.enumerate()), 2)
        main_thread = threading.enumerate()[0]
        self.assertEqual(type(main_thread), threading._MainThread)
        # an error dialog should pop
        dialogs = Dialog.dialogs
        self.assertEqual(len(dialogs), 1)
        dialog = dialogs[0]
        self.assertEqual(dialog.title, 'Wrong password')
        dialog.dismiss()
        # the wrong password should not get cached and a password form should
        # be prompted again next time we try to roll
        roll_button.dispatch('on_release')
        # it should open the error dialog
        dialogs = Dialog.dialogs
        self.assertEqual(len(dialogs), 1)
        dialog = dialogs[0]
        self.assertEqual(dialog.title, 'Enter your password')
        dialog.dismiss()

    def helper_test_settings_screen(self, app):
        """Verifies the settings screen loads and shows infos."""
        controller = app.root
        screen_manager = controller.screen_manager
        # verify the landing screen is loaded by default
        screen = screen_manager.children[0]
        self.assertEqual(screen.name, 'roll_screen')
        # loads the about and verify
        screen_manager.current = 'settings_screen'
        advance_frames_for_screen()
        screen = screen_manager.children[0]
        self.assertEqual(screen.name, 'settings_screen')
        # checks settings screen attributes
        self.assertEqual(screen.is_ui_mainnet(), True)
        self.assertEqual(screen.is_ui_testnet(), False)
        load_roll_screen(screen_manager)

    def helper_test_transaction(self, app):
        """Trying to send ETH."""
        controller = app.root
        switch_account_screen = controller.switch_account_screen
        send_subscreen = switch_account_screen.ids.send_id
        send_subscreen.parent.dispatch('on_tab_press')
        advance_frames_for_screen()
        # makes sure an account is selected
        controller.current_account = \
            controller.account_utils.get_account_list()[0]
        # retrieving the send button, to click it
        send_to_address = '0x46044beAa1E985C67767E04dE58181de5DAAA00F'
        send_subscreen.ids.send_to_id.text = send_to_address
        amount_eth = 1.2
        send_subscreen.ids.amount_eth_id.text = f'{amount_eth}'
        send_button = send_subscreen.ids.send_button_id
        self.assertEqual(send_button.text, 'Send')
        send_button.dispatch('on_release')
        # it should open the password dialog
        dialogs = Dialog.dialogs
        self.assertEqual(len(dialogs), 1)
        dialog = dialogs[0]
        self.assertEqual(dialog.title, 'Enter your password')
        password = 'password'
        dialog.content.password = password
        unlock_button = dialog._action_buttons[0]
        with patch('pyetheroll.etheroll.Etheroll.transaction', autospec=True) \
                as m_transaction:
            m_transaction.return_value = HexBytes(
                '0x7be6e37621eb12db7dc535954345f69'
                'd8cc5644b2de0ec32a344ca33c3054237')
            unlock_button.dispatch('on_release')
        pyetheroll = controller.pyetheroll
        to = send_to_address
        value = int(amount_eth * 1e18)
        wallet_path = controller.current_account.path
        gas_price_wei = mock.ANY
        self.assertEqual(m_transaction.mock_calls, [
            mock.call(
                pyetheroll, to, value, wallet_path, password, gas_price_wei)
        ])
        advance_frames_for_screen()
        threads = threading.enumerate()
        # thread has ended, main & OSC threads only are running again
        self.assertEqual(len(threads), 2, threads[-1]._target)
        main_thread = threads[0]
        self.assertEqual(type(main_thread), threading._MainThread)
        # a confirmation dialog with transaction hash should pop
        dialogs = Dialog.dialogs
        self.assertEqual(len(dialogs), 1)
        dialog = dialogs[0]
        self.assertEqual(dialog.title, 'Transaction successful')
        dialog.dismiss()
        self.assertEqual(len(dialogs), 0)
        # screen_manager = controller.screen_manager
        # load_roll_screen(screen_manager)

    def helper_test_flashqrcode(self, app):
        """Verifies the flash QRCode screen loads and can flash codes."""
        controller = app.root
        with patch_core_camera():
            controller.load_flash_qr_code()
        advance_frames_for_screen()
        screen_manager = controller.screen_manager
        self.assertEqual(screen_manager.current, 'flashqrcode')
        flashqrcode_screen = screen_manager.get_screen('flashqrcode')
        zbarcam = flashqrcode_screen.ids.zbarcam_id
        fixture_path = os.path.join(BASE_DIR, 'tests', 'address_qrcode.png')
        texture = Image(fixture_path).texture
        camera = mock.Mock(texture=texture)
        zbarcam._on_texture(camera)
        switch_account_screen = controller.switch_account_screen
        send_screen = switch_account_screen.ids.send_id
        self.assertEqual(
            send_screen.ids.send_to_id.text,
            '0x46044beaa1e985c67767e04de58181de5daaa00f')
        advance_frames_for_screen()

    # main test function
    def run_test(self, app, *args):
        Clock.schedule_interval(self.pause, 0.000001)
        self.helper_setup(app)
        # lets it finish to init
        advance_frames(1)
        self.helper_test_empty_account(app)
        self.helper_test_toolbar(app)
        self.helper_test_about_screen(app)
        self.helper_test_create_first_account(app)
        self.helper_test_create_account_form(app)
        self.helper_test_chances_input_binding(app)
        self.helper_test_roll_history(app)
        self.helper_test_roll_history_no_tx(app)
        self.helper_test_roll_history_no_account(app)
        self.helper_test_roll(app)
        self.helper_test_roll_connection_error(app)
        self.helper_test_roll_password(app)
        self.helper_test_settings_screen(app)
        self.helper_test_transaction(app)
        self.helper_test_flashqrcode(app)
        # Comment out if you are editing the test, it'll leave the
        # Window opened.
        app.stop()

    # same named function as the filename(!)
    def test_ui_base(self):
        app = EtherollApp()
        p = partial(self.run_test, app)
        Clock.schedule_once(p, 0.000001)
        app.run()


if __name__ == '__main__':
    unittest.main()
