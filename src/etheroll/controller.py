#!/usr/bin/env python
import os
from os.path import expanduser

from kivy.app import App
from kivy.clock import Clock, mainthread
from kivy.core.clipboard import Clipboard
from kivy.garden.qrcode import QRCodeWidget
from kivy.logger import LOG_LEVELS, Logger
from kivy.metrics import dp
from kivy.properties import ObjectProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.utils import platform
from kivymd.bottomsheet import MDListBottomSheet
from kivymd.theming import ThemeManager
from raven import Client
from raven.conf import setup_logging
from raven.handlers.logging import SentryHandler

import constants
from etheroll.about import AboutScreen
from etheroll.passwordform import PasswordForm
from etheroll.roll_results import RollResultsScreen
from etheroll.settings import SettingsScreen
from etheroll.switchaccount import SwitchAccountScreen
from etheroll.utils import (Dialog, load_kv_from_py,
                            patch_find_library_android, patch_typing_python351,
                            run_in_thread)
from version import __version__

patch_find_library_android()
patch_typing_python351()
# must be imported after patching
from ethereum_utils import AccountUtils  # noqa: E402, isort:skip
import pyetheroll  # noqa: E402, isort:skip


load_kv_from_py(__file__)


class Controller(FloatLayout):

    current_account = ObjectProperty(allownone=True)

    def __init__(self, **kwargs):
        super(Controller, self).__init__(**kwargs)
        Clock.schedule_once(self._after_init)
        self._init_pyethapp()
        self._account_passwords = {}
        self._pyetheroll = None

    def _after_init(self, dt):
        """
        Binds events.
        """
        self.bind_roll_button()
        self.bind_chances_roll_under()
        self.bind_wager_property()
        self.bind_profit_property()
        self.bind_screen_manager_on_current_screen()
        self.register_screens()

    def _init_pyethapp(self, keystore_dir=None):
        if keystore_dir is None:
            keystore_dir = self.get_keystore_path()
        self.account_utils = AccountUtils(keystore_dir=keystore_dir)

    @property
    def pyetheroll(self):
        """
        Gets or creates the Etheroll object.
        Also recreates the object if the chain_id changed.
        """
        chain_id = SettingsScreen.get_stored_network()
        if self._pyetheroll is None or self._pyetheroll.chain_id != chain_id:
            self._pyetheroll = pyetheroll.Etheroll(chain_id)
        return self._pyetheroll

    @classmethod
    def get_keystore_path(cls):
        """
        This is the Kivy default keystore path.
        """
        keystore_path = os.environ.get('KEYSTORE_PATH')
        if keystore_path is None:
            keystore_path = cls.get_default_keystore_path()
        return keystore_path

    @staticmethod
    def get_default_keystore_path():
        """
        Returns the keystore path, which is the same as the default pyethapp
        one.
        """
        KEYSTORE_DIR_PREFIX = expanduser("~")
        # uses kivy user_data_dir (/sdcard/<app_name>)
        if platform == "android":
            KEYSTORE_DIR_PREFIX = App.get_running_app().user_data_dir
        keystore_dir = os.path.join(
            KEYSTORE_DIR_PREFIX, constants.KEYSTORE_DIR_SUFFIX)
        return keystore_dir

    def bind_wager_property(self):
        """
        Binds wager recap label.
        """
        roll_under_recap = self.roll_screen.ids.roll_under_recap_id
        bet_size = self.roll_screen.ids.bet_size_id
        bet_size_input = bet_size.ids.bet_size_input_id
        # TODO: input validation, if `bet_size.text == ''`
        bet_size_input.bind(text=roll_under_recap.setter('wager_property'))
        # synchro once now
        roll_under_recap.wager_property = bet_size_input.text

    def bind_chances_roll_under(self):
        """
        Binds chances of winning recap label.
        """
        roll_under_recap = self.roll_screen.ids.roll_under_recap_id
        # roll under recap label
        chance_of_winning = self.roll_screen.ids.chance_of_winning_id
        chances_input = chance_of_winning.ids.chances_input_id
        # TODO: input validation, if `chances_input.text == ''`
        chances_input.bind(text=roll_under_recap.setter('roll_under_property'))
        # synchronises it now
        roll_under_recap.roll_under_property = chances_input.text

    def bind_roll_button(self):
        """
        binds roll screen "Roll" button to controller roll()
        """
        roll_button = self.roll_screen.ids.roll_button_id
        roll_button.bind(on_release=lambda instance: self.roll())

    def bind_profit_property(self):
        """
        Binds profit property with bet value and chances changes.
        """
        # chances -> profit
        chance_of_winning = self.roll_screen.ids.chance_of_winning_id
        chances_input = chance_of_winning.ids.chances_input_id
        chances_input.bind(
            text=lambda instance, value: self.update_profit_property())
        # bet value -> profit
        bet_size = self.roll_screen.ids.bet_size_id
        bet_size_input = bet_size.ids.bet_size_input_id
        bet_size_input.bind(
            text=lambda instance, value: self.update_profit_property())
        # synchro once now
        self.update_profit_property()

    def bind_screen_manager_on_current_screen(self):
        """
        Binds SwitchAccountScreen.current_account -> self.current_account.
        """
        def on_current_screen(screen_manager, screen):
            """
            Makes sure the binding is made once by unbinding itself.
            """
            if type(screen) is SwitchAccountScreen:
                screen.bind(current_account=self.setter('current_account'))
                # makes sure the above doesn't get rebinded over and over again
                self.screen_manager.unbind(current_screen=on_current_screen)
        self.screen_manager.bind(current_screen=on_current_screen)

    def register_screens(self):
        screen_dicts = {
            # "roll_screen": RollScreen,
            "roll_results_screen": RollResultsScreen,
            "switch_account_screen": SwitchAccountScreen,
            "settings_screen": SettingsScreen,
            "about_screen": AboutScreen,
        }
        for screen_name, screen_type in screen_dicts.items():
            self.screen_manager.register_screen(screen_type, screen_name)

    def update_profit_property(self):
        house_edge = 1.0 / 100
        bet_size = self.roll_screen.ids.bet_size_id.value
        chances_win = self.roll_screen.ids.chance_of_winning_id.value
        chances_loss = 100 - chances_win
        roll_under_recap = self.roll_screen.ids.roll_under_recap_id
        roll_under_recap.profit_property = 0
        if chances_win != 0 and chances_loss != 0:
            payout = ((chances_loss / chances_win) * bet_size) + bet_size
            payout *= (1 - house_edge)
            roll_under_recap.profit_property = payout - bet_size

    @property
    def navigation(self):
        return self.ids.navigation_id

    @property
    def screen_manager(self):
        return self.ids.screen_manager_id

    @property
    def roll_screen(self):
        return self.screen_manager.get_screen('roll_screen')

    @property
    def switch_account_screen(self):
        return self.screen_manager.get_screen('switch_account_screen')

    @property
    def roll_results_screen(self):
        return self.screen_manager.get_screen('roll_results_screen')

    @property
    def settings_screen(self):
        return self.screen_manager.get_screen('settings_screen')

    @property
    def about_screen(self):
        return self.screen_manager.get_screen('about_screen')

    def on_unlock_clicked(self, dialog, account, password):
        """
        Caches the password and call roll method again.
        """
        self._account_passwords[account.address.hex()] = password
        dialog.dismiss()
        # calling roll again since the password is now cached
        self.roll()

    def prompt_password_dialog(self, account):
        """
        Prompt the password dialog.
        """
        title = "Enter your password"
        content = PasswordForm()
        content.ids.account_id.text = "0x" + account.address.hex()
        dialog = Dialog.create_dialog_content_helper(
                    title=title,
                    content=content)
        # workaround for MDDialog container size (too small by default)
        dialog.ids.container.size_hint_y = 1
        dialog.add_action_button(
            "Unlock",
            action=lambda *x: self.on_unlock_clicked(
                dialog, account, content.password))
        dialog.open()
        return dialog

    def get_account_password(self, account):
        """
        Retrieve cached account password or prompt dialog.
        """
        address = account.address.hex()
        try:
            return self._account_passwords[address]
        except KeyError:
            self.prompt_password_dialog(account)

    @staticmethod
    def on_account_none():
        """
        Error dialog on no account selected.
        """
        title = "No account selected"
        body = "Please select an account before rolling"
        dialog = Dialog.create_dialog(title, body)
        dialog.open()

    @staticmethod
    @mainthread
    def dialog_roll_success(tx_hash):
        title = "Rolled successfully"
        body = "Transaction hash:\n" + tx_hash.hex()
        dialog = Dialog.create_dialog(title, body)
        dialog.open()

    @staticmethod
    @mainthread
    def dialog_roll_error(exception):
        title = "Error rolling"
        body = str(exception)
        dialog = Dialog.create_dialog(title, body)
        dialog.open()

    @run_in_thread
    def player_roll_dice(self, bet_size, chances, wallet_path, password):
        """
        Sending the bet to the smart contract requires signing a transaction
        which requires CPU computation to unlock the account, hence this
        is ran in a thread.
        """
        roll_screen = self.roll_screen
        try:
            Dialog.snackbar_message("Sending bet...")
            roll_screen.toggle_widgets(False)
            tx_hash = self.pyetheroll.player_roll_dice(
                bet_size, chances, wallet_path, password)
        except ValueError as exception:
            roll_screen.toggle_widgets(True)
            self.dialog_roll_error(exception)
            return
        roll_screen.toggle_widgets(True)
        self.dialog_roll_success(tx_hash)

    def roll(self):
        """
        Retrieves bet parameters from user input and sends it as a signed
        transaction to the smart contract.
        """
        roll_screen = self.roll_screen
        roll_input = roll_screen.get_roll_input()
        bet_size = roll_input['bet_size']
        chances = roll_input['chances']
        account = self.current_account
        if account is None:
            self.on_account_none()
            return
        wallet_path = account.path
        password = self.get_account_password(account)
        if password is not None:
            self.player_roll_dice(bet_size, chances, wallet_path, password)

    def load_switch_account(self):
        """
        Loads the switch account screen.
        """
        screen_manager = self.screen_manager
        screen_manager.transition.direction = 'right'
        screen_manager.current = 'switch_account_screen'

    def show_qr_code(self):
        """
        Shows address QR Code in a dialog.
        """
        account = self.switch_account_screen.current_account
        if not account:
            return
        address = "0x" + account.address.hex()
        title = address
        qr_code = QRCodeWidget()
        qr_code.data = address
        dialog = Dialog.create_dialog_content_helper(
                    title=title,
                    content=qr_code)
        # workaround for MDDialog container size (too small by default)
        dialog.ids.container.size_hint_y = 1
        dialog.height = dp(500)
        dialog.add_action_button(
            "OK",
            action=lambda *x: dialog.dismiss())
        dialog.open()
        return dialog

    def copy_address_clipboard(self):
        """
        Copies the current account address to the clipboard.
        """
        account = self.switch_account_screen.current_account
        if not account:
            return
        address = "0x" + account.address.hex()
        Clipboard.copy(address)

    def open_address_options(self):
        """
        Loads the address options bottom sheet.
        """
        bottom_sheet = MDListBottomSheet()
        bottom_sheet.add_item(
            'Switch account',
            lambda x: self.load_switch_account(), icon='swap-horizontal')
        bottom_sheet.add_item(
            'Show QR Code',
            lambda x: self.show_qr_code(), icon='information')
        bottom_sheet.add_item(
            'Copy address',
            lambda x: self.copy_address_clipboard(), icon='content-copy')
        bottom_sheet.open()


class DebugRavenClient(object):
    """
    The DebugRavenClient should be used in debug mode, it just raises
    the exception rather than capturing it.
    """

    def captureException(self):
        raise


def configure_sentry(in_debug=False):
    """
    Configure the Raven client, or create a dummy one if `in_debug` is `True`.
    """
    key = 'b290ecc8934f4cb599e6fa6af6cc5cc2'
    # the public DSN URL is not available on the Python client
    # so we're exposing the secret and will be revoking it on abuse
    # https://github.com/getsentry/raven-python/issues/569
    secret = '0ae02bcb5a75467d9b4431042bb98cb9'
    project_id = '1111738'
    dsn = 'https://{key}:{secret}@sentry.io/{project_id}'.format(
        key=key, secret=secret, project_id=project_id)
    if in_debug:
        client = DebugRavenClient()
    else:
        client = Client(dsn=dsn, release=__version__)
        # adds context for Android devices
        if platform == 'android':
            from jnius import autoclass
            Build = autoclass("android.os.Build")
            VERSION = autoclass('android.os.Build$VERSION')
            android_os_build = {
                'model': Build.MODEL,
                'brand': Build.BRAND,
                'device': Build.DEVICE,
                'manufacturer': Build.MANUFACTURER,
                'version_release': VERSION.RELEASE,
            }
            client.user_context({'android_os_build': android_os_build})
        # Logger.error() to Sentry
        # https://docs.sentry.io/clients/python/integrations/logging/
        handler = SentryHandler(client)
        handler.setLevel(LOG_LEVELS.get('error'))
        setup_logging(handler)
    return client


class EtherollApp(App):

    theme_cls = ThemeManager()

    def build(self):
        self.icon = "docs/images/icon.png"
        return Controller()


def main():
    # only send Android errors to Sentry
    in_debug = platform != "android"
    client = configure_sentry(in_debug)
    try:
        EtherollApp().run()
    except Exception:
        if type(client) == Client:
            Logger.info(
                'Errors will be sent to Sentry, run with "--debug" if you '
                'are a developper and want to the error in the shell.')
        client.captureException()


if __name__ == '__main__':
    main()
