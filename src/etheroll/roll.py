from kivy.app import App
from kivy.clock import Clock, mainthread
from kivy.properties import NumericProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen

import constants
from etheroll.layout_mixins import Add_Margin, MarginLayout
from etheroll.utils import load_kv_from_py, run_in_thread

load_kv_from_py(__file__)


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
    def bind_slider_input(
            slider, inpt, cast_to=float, round_digits=constants.ROUND_DIGITS):
        """
        Binds slider <-> input both ways.
        """
        # slider -> input
        slider.bind(
            value=lambda instance, value:
            setattr(inpt, 'text', "{0:.{1}f}".format(
                cast_to(value), round_digits)))
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
            return round(
                float(self.ids.bet_size_input_id.text), constants.ROUND_DIGITS)
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
        cast_to = self.cast_to
        BetSize.bind_slider_input(slider, inpt, cast_to, round_digits=0)

    @staticmethod
    def cast_to(value):
        return int(float(value))

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


class BoxLayoutMarginLayout(MarginLayout, BoxLayout):
    pass


class BoxLayoutAddMargin(Add_Margin, BoxLayout):
    pass


class RollScreen(Screen):

    current_account_string = StringProperty()
    balance_property = NumericProperty()

    def __init__(self, **kwargs):
        super(RollScreen, self).__init__(**kwargs)
        Clock.schedule_once(self._after_init)

    def _after_init(self, dt):
        """
        Binds `Controller.current_account` -> `RollScreen.current_account`.
        """
        controller = App.get_running_app().root
        controller.bind(current_account=self.on_current_account)

    def on_current_account(self, instance, account):
        """
        Sets current_account_string.
        """
        if account is None:
            return
        self.current_account_string = '0x' + account.address.hex()

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

    @mainthread
    def toggle_widgets(self, enabled):
        """
        Enables/disables widgets (useful during roll).
        """
        self.disabled = not enabled

    @property
    def pyetheroll(self):
        """
        We want to make sure we go through the `Controller.pyetheroll` property
        each time, because it recreates the Etheroll object on chain_id
        changes.
        """
        controller = App.get_running_app().root
        return controller.pyetheroll

    @mainthread
    def update_balance(self, balance):
        """
        Updates the property from main thread.
        """
        self.balance_property = balance

    @run_in_thread
    def fetch_update_balance(self):
        """
        Retrieves the balance and updates the property.
        """
        address = self.current_account_string
        if not address:
            return
        balance = self.pyetheroll.get_balance(address)
        self.update_balance(balance)
