#!/usr/bin/env python
from dotenv import load_dotenv
from eth_utils import to_checksum_address
from kivy.app import App
from kivy.clock import Clock, mainthread
from kivy.logger import Logger
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.utils import platform
from kivymd.bottomsheet import MDListBottomSheet
from kivymd.theming import ThemeManager
from raven import Client
from requests.exceptions import ConnectionError

from etherollapp.etheroll.constants import ENV_PATH
from etherollapp.etheroll.flashqrcode import FlashQrCodeScreen
from etherollapp.etheroll.settings import Settings
from etherollapp.etheroll.settings_screen import SettingsScreen
from etherollapp.etheroll.switchaccount import SwitchAccountScreen
from etherollapp.etheroll.ui_utils import Dialog, load_kv_from_py
from etherollapp.etheroll.utils import run_in_thread
from etherollapp.osc.osc_app_server import OscAppServer
from etherollapp.sentry_utils import configure_sentry
from etherollapp.service.utils import start_roll_polling_service

load_kv_from_py(__file__)


class Controller(FloatLayout):

    current_account = ObjectProperty(allownone=True)
    current_account_string = StringProperty(allownone=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # disables the roll screen until `preload_account_utils` is done
        # disabling doesn't seem to work within the scheduled method
        # self.roll_screen.toggle_widgets(False)
        self.disabled = True
        Clock.schedule_once(self._after_init)
        self._account_passwords = {}

    def _after_init(self, dt):
        """Inits pyethapp and binds events."""
        Clock.schedule_once(self.preload_account_utils)
        self.bind_roll_button()
        self.bind_current_account_string()
        self.bind_chances_roll_under()
        self.bind_wager_property()
        self.bind_profit_property()
        self.bind_screen_manager_on_current_screen()
        self.bind_keyboard()
        self.register_screens()

    def on_keyboard(self, window, key, *args):
        """
        Handles the back button (Android) and ESC key. Goes back to the
        previous screen, dicards dialogs or exits the application if none left.
        """
        if key == 27:
            if Dialog.dialogs:
                Dialog.dismiss_all_dialogs()
                return True
            from etherollapp.etheroll.ui_utils import SubScreen
            current_screen = self.screen_manager.current_screen
            # if is sub-screen loads previous and stops the propagation
            # otherwise propagates the key to exit
            if isinstance(current_screen, SubScreen):
                current_screen.on_back()
                return True
        return False

    def on_current_account(self, instance, current_account):
        self.current_account_string = (
            current_account and f'0x{current_account.address.hex()}')

    @property
    def pyetheroll(self):
        """
        Gets or creates the Etheroll object.
        Also recreates the object if the chain_id changed.
        """
        from pyetheroll.etheroll import Etheroll
        chain_id = Settings.get_stored_network()
        return Etheroll.get_or_create(chain_id)

    @property
    def account_utils(self):
        """Gets or creates the AccountUtils object so it loads lazily."""
        from eth_accounts.account_utils import AccountUtils
        keystore_dir = Settings.get_keystore_path()
        return AccountUtils.get_or_create(keystore_dir)

    def preload_account_utils(self, dt):
        """Preloads `AccountUtils`, since it takes few seconds on Android."""
        account_utils = self.account_utils
        self.disabled = False
        # not using that returned value, but it peaces linter
        return account_utils

    def bind_wager_property(self):
        """Binds wager recap label."""
        roll_under_recap = self.roll_screen.ids.roll_under_recap_id
        bet_size = self.roll_screen.ids.bet_size_id
        bet_size_input = bet_size.ids.bet_size_input_id
        # TODO: input validation, if `bet_size.text == ''`
        bet_size_input.bind(text=roll_under_recap.setter('wager_property'))
        # synchro once now
        roll_under_recap.wager_property = bet_size_input.text

    def bind_chances_roll_under(self):
        """Binds chances of winning recap label."""
        roll_under_recap = self.roll_screen.ids.roll_under_recap_id
        # roll under recap label
        chance_of_winning = self.roll_screen.ids.chance_of_winning_id
        chances_input = chance_of_winning.ids.chances_input_id
        # TODO: input validation, if `chances_input.text == ''`
        chances_input.bind(text=roll_under_recap.setter('roll_under_property'))
        # synchronises it now
        roll_under_recap.roll_under_property = chances_input.text

    def bind_roll_button(self):
        """Binds roll screen "Roll" button to controller roll()."""
        roll_button = self.roll_screen.ids.roll_button_id
        roll_button.bind(on_release=lambda instance: self.roll())

    def bind_current_account_string(self):
        """Binds Controller.current_account -> RollScreen.current_account"""
        roll_screen = self.roll_screen
        self.bind(
            current_account_string=roll_screen.setter('current_account_string')
        )

    def bind_keyboard(self):
        """Binds keyboard keys to actions."""
        from kivy.core.window import Window
        Window.bind(on_keyboard=self.on_keyboard)

    def bind_profit_property(self):
        """Binds profit property with bet value and chances changes."""
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
        """SwitchAccountScreen.current_account -> self.current_account."""
        def on_pre_add_widget(screen_manager, screen):
            """Should only be called twice per screen instance."""
            if type(screen) is SwitchAccountScreen and \
                    not self.screen_manager.has_screen(screen.name):
                screen.bind(current_account=self.setter('current_account'))
                screen.ids.send_id.bind(
                    current_account=self.setter('current_account'))
                screen.ids.send_id.bind(on_send=self.on_send)
        self.screen_manager.bind(on_pre_add_widget=on_pre_add_widget)

    def register_screens(self):
        # lazy loading
        from etherollapp.etheroll.about import AboutScreen
        from etherollapp.etheroll.roll_results import RollResultsScreen
        screen_dicts = {
            "about_screen": AboutScreen,
            'flashqrcode': FlashQrCodeScreen,
            "roll_results_screen": RollResultsScreen,
            "settings_screen": SettingsScreen,
            "switch_account_screen": SwitchAccountScreen,
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

    def prompt_password_dialog(self, account, on_password_callback):
        """Prompt the password dialog."""
        # lazy loading
        from etherollapp.etheroll.passwordform import PasswordForm
        dialog = PasswordForm.dialog(account)

        def on_unlock_clicked(instance, dialog, account, password):
            """Caches the password and call roll method again."""
            self._account_passwords[account.address.hex()] = password
            dialog.dismiss()
            on_password_callback()

        dialog.content.bind(on_unlock=on_unlock_clicked)
        dialog.open()
        return dialog

    def get_account_password(self, account, on_password_callback):
        """Retrieve cached account password or prompt dialog."""
        address = account.address.hex()
        try:
            return self._account_passwords[address]
        except KeyError:
            self.prompt_password_dialog(account, on_password_callback)

    @staticmethod
    def on_account_none():
        """Error dialog on no account selected."""
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
    def dialog_transaction_success(tx_hash):
        title = "Transaction successful"
        body = "Transaction hash:\n" + tx_hash.hex()
        dialog = Dialog.create_dialog(title, body)
        dialog.open()

    @mainthread
    def dialog_roll_error(self, exception):
        """
        Shows different error message depending on the exception.
        On "MAC mismatch" (wrong password), void the cached password so the
        user can try again refs:
        https://github.com/AndreMiras/EtherollApp/issues/9
        """
        title = "Error rolling"
        body = str(exception)
        if body == 'MAC mismatch':
            title = "Wrong password"
            body = "Can't unlock wallet, wrong password."
            account = self.current_account
            self._account_passwords.pop(account.address.hex())
        dialog = Dialog.create_dialog(title, body)
        dialog.open()

    @run_in_thread
    def player_roll_dice(
            self, bet_size_eth, chances, wallet_path, password,
            gas_price_gwei):
        """
        Sending the bet to the smart contract requires signing a transaction
        which requires CPU computation to unlock the account, hence this
        is ran in a thread.
        """
        roll_screen = self.roll_screen
        try:
            Dialog.snackbar_message("Sending bet...")
            roll_screen.toggle_widgets(False)
            bet_size_wei = int(bet_size_eth * 1e18)
            gas_price_wei = int(gas_price_gwei * 1e9)
            tx_hash = self.pyetheroll.player_roll_dice(
                bet_size_wei, chances, wallet_path, password, gas_price_wei)
        except (ValueError, ConnectionError) as exception:
            roll_screen.toggle_widgets(True)
            self.dialog_roll_error(exception)
            return
        roll_screen.toggle_widgets(True)
        self.dialog_roll_success(tx_hash)

    @staticmethod
    def start_services():
        """
        Starts both roll polling service and OSC service.
        The roll polling service is getting the OSC server connection
        parameters so it can communicate to it.
        """
        app = App.get_running_app()
        osc_server, sockname = OscAppServer.get_or_create(app)
        server_address, server_port = sockname
        print(sockname)
        arguments = {
            'osc_server_address': server_address,
            'osc_server_port': server_port,
        }
        start_roll_polling_service(arguments)

    def roll(self):
        """
        Retrieves bet parameters from user input and sends it as a signed
        transaction to the smart contract.
        """
        roll_screen = self.roll_screen
        roll_input = roll_screen.get_roll_input()
        bet_size_eth = roll_input['bet_size']
        chances = roll_input['chances']
        gas_price_gwei = Settings.get_stored_gas_price()
        account = self.current_account
        if account is None:
            self.on_account_none()
            return
        wallet_path = account.path
        password = self.get_account_password(account, self.roll)
        if password is not None:
            self.player_roll_dice(
                bet_size_eth, chances, wallet_path, password, gas_price_gwei)
            # restarts roll polling service to reset the roll activity period
            self.start_services()

    def transaction(
            self, to, amount_eth, wallet_path, password, gas_price_gwei):
        """Converts input parameters for the underlying library."""
        value = int(amount_eth * 1e18)
        gas_price_wei = int(gas_price_gwei * 1e9)
        to = to_checksum_address(to)
        Dialog.snackbar_message("Sending transaction...")
        tx_hash = self.pyetheroll.transaction(
            to, value, wallet_path, password, gas_price_wei)
        self.dialog_transaction_success(tx_hash)

    def send(self, address, amount_eth):
        """Retrieves fields to complete the `transaction()` call."""
        gas_price_gwei = Settings.get_stored_gas_price()
        account = self.current_account
        if account is None:
            self.on_account_none()
            return
        wallet_path = account.path
        password = self.get_account_password(
            account, lambda: self.send(address, amount_eth))
        if password is not None:
            self.transaction(
                address, amount_eth, wallet_path, password, gas_price_gwei)

    def on_send(self, instance, address, amount_eth):
        self.send(address, amount_eth)

    def load_switch_account(self):
        """Loads the switch account screen."""
        screen_manager = self.screen_manager
        screen_manager.transition.direction = 'right'
        screen_manager.current = 'switch_account_screen'

    def load_flash_qr_code(self):
        """Loads the flash QR Code screen."""
        # loads ZBarCam only when needed
        from kivy_garden.zbarcam import ZBarCam  # noqa
        # loads the flash QR Code screen
        self.screen_manager.transition.direction = 'right'
        self.screen_manager.current = 'flashqrcode'

    def show_qr_code(self):
        """Shows address QR Code in a dialog."""
        # lazy loading
        from kivy_garden.qrcode import QRCodeWidget
        from kivy.metrics import dp
        account = self.current_account
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
        """Copies the current account address to the clipboard."""
        # lazy loading
        from kivy.core.clipboard import Clipboard
        account = self.current_account
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

    @staticmethod
    def on_permission_error(exception):
        title = "Permission denied"
        body = str(exception.args)
        dialog = Dialog.create_dialog(title, body)
        dialog.open()


class EtherollApp(App):

    theme_cls = ThemeManager()

    def build(self):
        self.icon = "docs/images/icon.png"
        self.theme_cls.theme_style = 'Dark'
        self.theme_cls.primary_palette = 'Indigo'
        Controller.start_services()
        return Controller()


def main():
    load_dotenv(dotenv_path=ENV_PATH)
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
