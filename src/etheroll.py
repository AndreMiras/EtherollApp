#!/usr/bin/env python
import os
from os.path import expanduser

from kivy.app import App
from kivy.clock import Clock
from kivy.logger import LOG_LEVELS, Logger
from kivy.properties import NumericProperty, ObjectProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import Screen
from kivy.utils import platform
from kivymd.list import OneLineListItem
from kivymd.theming import ThemeManager
from kivymd.toolbar import Toolbar
from raven import Client
from raven.conf import setup_logging
from raven.handlers.logging import SentryHandler

from utils import Dialog, patch_find_library_android, patch_typing_python351
from version import __version__

patch_find_library_android()
patch_typing_python351()
import pyetheroll  # noqa: E402, isort:skip, must be imported after patching

# default pyethapp keystore path
KEYSTORE_DIR_SUFFIX = ".config/pyethapp/keystore/"
ROUND_DIGITS = 1


class PasswordForm(BoxLayout):
    password = StringProperty()


class SwitchAccount(BoxLayout):

    def __init__(self, **kwargs):
        super(SwitchAccount, self).__init__(**kwargs)
        self.register_event_type('on_account_selected')

    def on_release(self, list_item):
        """
        Fires on_account_selected() event.
        """
        self.dispatch('on_account_selected', list_item.account)

    def on_account_selected(self, *args):
        """
        Default handler.
        """
        pass

    def create_item(self, account):
        """
        Creates an account list item from given account.
        """
        address = "0x" + account.address.hex()
        list_item = OneLineListItem(text=address)
        # makes sure the address doesn't overlap on small screen
        list_item.ids._lbl_primary.shorten = True
        list_item.account = account
        list_item.bind(on_release=lambda x: self.on_release(x))
        return list_item

    def load_account_list(self):
        """
        Fills account list widget from library account list.
        """
        self.controller = App.get_running_app().root
        account_list_id = self.ids.account_list_id
        account_list_id.clear_widgets()
        accounts = self.controller.pyethapp.services.accounts
        if len(accounts) == 0:
            self.on_empty_account_list()
        for account in accounts:
            list_item = self.create_item(account)
            account_list_id.add_widget(list_item)

    @staticmethod
    def on_empty_account_list():
        controller = App.get_running_app().root
        keystore_dir = controller.pyethapp.services.accounts.keystore_dir
        title = "No account found"
        body = "No account found in:\n%s" % keystore_dir
        dialog = Dialog.create_dialog(title, body)
        dialog.open()


class CustomToolbar(Toolbar):
    """
    Toolbar with helper method for loading default/back buttons.
    """

    def __init__(self, **kwargs):
        super(CustomToolbar, self).__init__(**kwargs)
        Clock.schedule_once(self.load_default_buttons)

    def load_default_buttons(self, dt=None):
        app = App.get_running_app()
        self.left_action_items = [
            ['menu', lambda x: app.root.navigation.toggle_nav_drawer()]]
        self.right_action_items = [[
                'dots-vertical',
                lambda x: app.root.navigation.toggle_nav_drawer()]]

    def load_back_button(self, function):
        self.left_action_items = [['arrow-left', lambda x: function()]]


class SubScreen(Screen):
    """
    Helper parent class for updating toolbar on enter/leave.
    """

    def on_back(self):
        self.manager.transition.direction = 'right'
        self.manager.current = 'roll_screen'

    def on_enter(self):
        """
        Loads the toolbar back button.
        """
        app = App.get_running_app()
        app.root.ids.toolbar_id.load_back_button(self.on_back)

    def on_leave(self):
        """
        Loads the toolbar default button.
        """
        app = App.get_running_app()
        app.root.ids.toolbar_id.load_default_buttons()


class ImportKeystore(BoxLayout):
    keystore_path = StringProperty()

    def __init__(self, **kwargs):
        super(ImportKeystore, self).__init__(**kwargs)
        Clock.schedule_once(self._after_init)

    def _after_init(self, dt):
        """
        Sets keystore_path.
        """
        controller = App.get_running_app().root
        self.keystore_path = controller.get_keystore_path()


class SwitchAccountScreen(SubScreen):
    current_account = ObjectProperty()

    def __init__(self, **kwargs):
        super(SwitchAccountScreen, self).__init__(**kwargs)
        Clock.schedule_once(self._after_init)

    def _after_init(self, dt):
        """
        Binds SwitchAccount.on_account_selected() event.
        """
        switch_account = self.ids.switch_account_id
        switch_account.bind(
            on_account_selected=lambda
            instance, account: self.on_account_selected(account))

    def on_account_selected(self, account):
        """
        Sets current account and loads previous screen.
        """
        self.current_account = account
        self.on_back()


class SettingsScreen(SubScreen):
    """
    Screen for configuring network, gas price...
    """

    def __init__(self, **kwargs):
        super(SettingsScreen, self).__init__(**kwargs)
        # Clock.schedule_once(self._after_init)

    @property
    def network(self):
        """
        Returns selected network.
        """
        if self.is_mainnet():
            return pyetheroll.ChainID.MAINNET
        return pyetheroll.ChainID.ROPSTEN

    def is_mainnet(self):
        return self.ids.mainnet_checkbox_id.active

    def is_testnet(self):
        return self.ids.testnet_checkbox_id.active


class AboutScreen(SubScreen):
    project_page_property = StringProperty(
        "https://github.com/AndreMiras/EtherollApp")
    about_text_property = StringProperty()

    def __init__(self, **kwargs):
        super(AboutScreen, self).__init__(**kwargs)
        Clock.schedule_once(lambda dt: self.load_about())

    def load_about(self):
        self.about_text_property = "" + \
            "EtherollApp version: %s\n" % (__version__) + \
            "Project source code and info available on GitHub at:\n" + \
            "[color=00BFFF][ref=github]" + \
            self.project_page_property + \
            "[/ref][/color]"


class RollResultsScreen(SubScreen):
    pass


class RollUnderRecap(BoxLayout):
    roll_under_property = NumericProperty()
    profit_property = NumericProperty()
    wager_property = NumericProperty()


class BetSize(BoxLayout):

    def __init__(self, **kwargs):
        super(BetSize, self).__init__(**kwargs)
        Clock.schedule_once(self._after_init)

    def _after_init(self, dt):
        """
        Binds events.
        """
        slider = self.ids.bet_size_slider_id
        inpt = self.ids.bet_size_input_id
        BetSize.bind_slider_input(slider, inpt)

    @staticmethod
    def bind_slider_input(slider, inpt, cast_to=float):
        """
        Binds slider <-> input both ways.
        """
        # slider -> input
        slider.bind(
            value=lambda instance, value:
            setattr(inpt, 'text', "{0:.{1}f}".format(
                cast_to(value), ROUND_DIGITS)))
        # input -> slider
        inpt.bind(
            on_text_validate=lambda instance:
            setattr(slider, 'value', cast_to(inpt.text)))
        # also when unfocused
        inpt.bind(
            focus=lambda instance, focused:
            inpt.dispatch('on_text_validate')
                if not focused else False)
        # synchronises values slider <-> input once
        inpt.dispatch('on_text_validate')

    @property
    def value(self):
        """
        Returns normalized bet size value.
        """
        try:
            return round(float(self.ids.bet_size_input_id.text), ROUND_DIGITS)
        except ValueError:
            return 0


class ChanceOfWinning(BoxLayout):

    def __init__(self, **kwargs):
        super(ChanceOfWinning, self).__init__(**kwargs)
        Clock.schedule_once(self._after_init)

    def _after_init(self, dt):
        """
        Binds events.
        """
        slider = self.ids.chances_slider_id
        inpt = self.ids.chances_input_id
        cast_to = int
        BetSize.bind_slider_input(slider, inpt, cast_to)

    @property
    def value(self):
        """
        Returns normalized chances value.
        """
        try:
            # `input_filter: 'int'` only verifies that we have a number
            # but doesn't convert to int
            chances = float(self.ids.chances_input_id.text)
            return int(chances)
        except ValueError:
            return 0


class RollScreen(Screen):

    def get_roll_input(self):
        """
        Returns bet size and chance of winning user input values.
        """
        bet_size = self.ids.bet_size_id
        chance_of_winning = self.ids.chance_of_winning_id
        return {
            "bet_size": bet_size.value,
            "chances": chance_of_winning.value,
        }


class Controller(FloatLayout):

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

    def _init_pyethapp(self, keystore_dir=None):
        if keystore_dir is None:
            keystore_dir = self.get_keystore_path()
        # must be imported after `patch_find_library_android()`
        from devp2p.app import BaseApp
        from pyethapp.accounts import AccountsService
        self.pyethapp = BaseApp(
            config=dict(accounts=dict(keystore_dir=keystore_dir)))
        AccountsService.register_with_app(self.pyethapp)

    @property
    def pyetheroll(self):
        """
        Gets or creates the Etheroll object.
        Also recreates the object if the chain_id changed.
        """
        chain_id = self.settings_screen.network
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
        keystore_dir = os.path.join(KEYSTORE_DIR_PREFIX, KEYSTORE_DIR_SUFFIX)
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
    def roll_screen(self):
        return self.ids.roll_screen_id

    @property
    def switch_account_screen(self):
        return self.ids.switch_account_screen_id

    @property
    def settings_screen(self):
        return self.ids.settings_screen_id

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
    def dialog_roll_success(tx_hash):
        title = "Rolled successfully"
        body = "Transaction hash:\n" + tx_hash.hex()
        dialog = Dialog.create_dialog(title, body)
        dialog.open()

    @staticmethod
    def dialog_roll_error(exception):
        title = "Error rolling"
        body = str(exception)
        dialog = Dialog.create_dialog(title, body)
        dialog.open()

    def roll(self):
        roll_input = self.roll_screen.get_roll_input()
        bet_size = roll_input['bet_size']
        chances = roll_input['chances']
        account = self.switch_account_screen.current_account
        if account is None:
            self.on_account_none()
            return
        wallet_path = account.path
        password = self.get_account_password(account)
        if password is not None:
            try:
                tx_hash = self.pyetheroll.player_roll_dice(
                    bet_size, chances, wallet_path, password)
            except ValueError as exception:
                self.dialog_roll_error(exception)
                return
            self.dialog_roll_success(tx_hash)


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
