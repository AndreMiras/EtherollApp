#!/usr/bin/env python
from kivy.app import App
from kivy.clock import Clock, mainthread
from kivy.logger import Logger
from kivy.properties import ObjectProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.utils import platform
from kivymd.bottomsheet import MDListBottomSheet
from kivymd.theming import ThemeManager
from raven import Client
from requests.exceptions import ConnectionError

from etheroll.patches import patch_find_library_android, patch_typing_python351
from etheroll.settings import SettingsScreen
from etheroll.switchaccount import SwitchAccountScreen
from etheroll.ui_utils import Dialog, load_kv_from_py
from etheroll.utils import run_in_thread
from osc.osc_app_server import OscAppServer
from sentry_utils import configure_sentry
from service.utils import start_roll_pulling_service

patch_find_library_android()
patch_typing_python351()
load_kv_from_py(__file__)


class Controller(FloatLayout):

    current_account = ObjectProperty(allownone=True)

    def __init__(self, **kwargs):
        super(Controller, self).__init__(**kwargs)
        # disables the roll screen until `preload_account_utils` is done
        # disabling doesn't seem to work within the scheduled method
        # self.roll_screen.toggle_widgets(False)
        self.disabled = True
        Clock.schedule_once(self._after_init)
        self._account_passwords = {}
        self._pyetheroll = None
        self._account_utils = None

    def _after_init(self, dt):
        """
        Inits pyethapp and binds events.
        """
        Clock.schedule_once(self.preload_account_utils)
        self.bind_roll_button()
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
            from etheroll.ui_utils import SubScreen
            current_screen = self.screen_manager.current_screen
            # if is sub-screen loads previous and stops the propagation
            # otherwise propagates the key to exit
            if isinstance(current_screen, SubScreen):
                current_screen.on_back()
                return True
        return False

    @property
    def pyetheroll(self):
        """
        Gets or creates the Etheroll object.
        Also recreates the object if the chain_id changed.
        """
        from pyetheroll.etheroll import Etheroll
        chain_id = SettingsScreen.get_stored_network()
        if self._pyetheroll is None or self._pyetheroll.chain_id != chain_id:
            self._pyetheroll = Etheroll(chain_id)
        return self._pyetheroll

    @property
    def account_utils(self):
        """
        Gets or creates the AccountUtils object so it loads lazily.
        """
        from ethereum_utils import AccountUtils
        from etheroll.store import Store
        if self._account_utils is None:
            keystore_dir = Store.get_keystore_path()
            self._account_utils = AccountUtils(keystore_dir=keystore_dir)
        return self._account_utils

    def preload_account_utils(self, dt):
        """
        Preloads `AccountUtils`, since it takes few seconds on Android.
        """
        account_utils = self.account_utils
        self.disabled = False
        # not using that returned value, but it peaces linter
        return account_utils

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
        Binds roll screen "Roll" button to controller roll().
        """
        roll_button = self.roll_screen.ids.roll_button_id
        roll_button.bind(on_release=lambda instance: self.roll())

    def bind_keyboard(self):
        """
        Binds keyboard keys to actions.
        """
        from kivy.core.window import Window
        Window.bind(on_keyboard=self.on_keyboard)

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
        # lazy loading
        from etheroll.about import AboutScreen
        from etheroll.roll_results import RollResultsScreen
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

    def on_unlock_clicked(self, instance, dialog, account, password):
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
        # lazy loading
        from etheroll.passwordform import PasswordForm
        dialog = PasswordForm.dialog(account)
        dialog.content.bind(on_unlock=self.on_unlock_clicked)
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
            self, bet_size, chances, wallet_path, password, gas_price):
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
                bet_size, chances, wallet_path, password, gas_price)
        except (ValueError, ConnectionError) as exception:
            roll_screen.toggle_widgets(True)
            self.dialog_roll_error(exception)
            return
        roll_screen.toggle_widgets(True)
        self.dialog_roll_success(tx_hash)

    @staticmethod
    def start_services():
        """
        Starts both roll pulling service and OSC service.
        The roll pulling service is getting the OSC server connection
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
        start_roll_pulling_service(arguments)

    def roll(self):
        """
        Retrieves bet parameters from user input and sends it as a signed
        transaction to the smart contract.
        """
        roll_screen = self.roll_screen
        roll_input = roll_screen.get_roll_input()
        bet_size = roll_input['bet_size']
        chances = roll_input['chances']
        gas_price = SettingsScreen.get_stored_gas_price()
        account = self.current_account
        if account is None:
            self.on_account_none()
            return
        wallet_path = account.path
        password = self.get_account_password(account)
        if password is not None:
            self.player_roll_dice(
                bet_size, chances, wallet_path, password, gas_price)
            # restarts roll pulling service to reset the roll activity period
            self.start_services()

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
        # lazy loading
        from kivy.garden.qrcode import QRCodeWidget
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
        """
        Copies the current account address to the clipboard.
        """
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


class DebugRavenClient(object):
    """
    The DebugRavenClient should be used in debug mode, it just raises
    the exception rather than capturing it.
    """

    def captureException(self):
        raise


class EtherollApp(App):

    theme_cls = ThemeManager()

    def build(self):
        self.icon = "docs/images/icon.png"
        self.theme_cls.theme_style = 'Dark'
        self.theme_cls.primary_palette = 'Indigo'
        Controller.start_services()
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
