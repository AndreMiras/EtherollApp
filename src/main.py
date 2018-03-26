#!/usr/bin/env python
from __future__ import print_function, unicode_literals

import os
from os.path import expanduser

from devp2p.app import BaseApp
from kivy.app import App
from kivy.clock import Clock
from kivy.properties import (NumericProperty, ObjectProperty,
                             StringProperty)
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import Screen
from kivymd.list import OneLineListItem
from kivymd.theming import ThemeManager
from kivymd.toolbar import Toolbar
from pyethapp.accounts import AccountsService

import pyetheroll
from utils import Dialog
from version import __version__

KEYSTORE_DIR_PREFIX = expanduser("~")
# default pyethapp keystore path
KEYSTORE_DIR_SUFFIX = ".config/pyethapp/keystore/"


class SwitchAccount(BoxLayout):

    def on_release(self, list_item):
        """
        Sets current_account and switches to previous screen.
        """
        # sets current_account
        self.selected_list_item = list_item
        self.parent.current_account = list_item.account
        # switches to previous screen
        self.parent.on_back()

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


class SwitchAccountScreen(SubScreen):

    current_account = ObjectProperty()

    def get_config(self):
        """
        Returns wallet path and encryption password user input values.
        """
        return {
            "path": self.current_account.path,
            # TODO
            "password": self.ids.password_id.text,
        }


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

        BetSize.bind_slider_input(slider, inpt, self.cast_to)

    @staticmethod
    def bind_slider_input(slider, inpt, cast_to=float):
        """
        Binds slider <-> input both ways.
        """
        # slider -> input
        slider.bind(
            value=lambda instance, value:
            setattr(inpt, 'text', str(cast_to(value))))
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

    @staticmethod
    def cast_to(value):
        try:
            return round(float(value), 1)
        except ValueError:
            return 0

    @property
    def value(self):
        """
        Returns normalized bet size value.
        """
        try:
            return self.cast_to(self.ids.bet_size_input_id.text)
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
            return int(self.ids.chances_input_id.text)
        except ValueError:
            return 0


class RollScreen(Screen):

    def get_roll_input(self):
        """
        Returns bet size and chance of winning user input values.
        """
        # bet size
        bet_size = self.ids.bet_size_id
        bet_size_input = bet_size.ids.bet_size_input_id
        bet_size_value = float(bet_size_input.text)
        # chance of winning
        chance_of_winning = self.ids.chance_of_winning_id
        chances_input = chance_of_winning.ids.chances_input_id
        chances_value = int(chances_input.text)
        return {
            "bet_size": bet_size_value,
            "chances": chances_value,
        }


class Controller(FloatLayout):

    def __init__(self, **kwargs):
        super(Controller, self).__init__(**kwargs)
        Clock.schedule_once(self._after_init)
        self._init_pyethapp()

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
            keystore_dir = self.get_default_keystore_path()
        self.pyethapp = BaseApp(
            config=dict(accounts=dict(keystore_dir=keystore_dir)))
        AccountsService.register_with_app(self.pyethapp)

    @staticmethod
    def get_default_keystore_path():
        """
        Returns the keystore path, which is the same as the default pyethapp
        one.
        """
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

    def roll(self):
        roll_input = self.roll_screen.get_roll_input()
        # TODO:
        wallet_config = self.switch_account_screen.get_config()
        bet_size = roll_input['bet_size']
        chances = roll_input['chances']
        wallet_path = wallet_config['path']
        wallet_password = wallet_config['password']
        print("roll_input:", roll_input)
        print("wallet_config:", wallet_config)
        pyetheroll.player_roll_dice(
            bet_size, chances, wallet_path, wallet_password)


class MainApp(App):

    theme_cls = ThemeManager()

    def build(self):
        self.icon = "docs/images/icon.png"


if __name__ == '__main__':
    MainApp().run()
