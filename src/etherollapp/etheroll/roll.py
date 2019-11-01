from etherscan.client import ConnectionRefused
from kivy.app import App
from kivy.clock import Clock, mainthread
from kivy.properties import NumericProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import Screen
from pyetheroll.constants import ROUND_DIGITS
from requests.exceptions import ConnectionError

from etherollapp.etheroll.ui_utils import Dialog, load_kv_from_py
from etherollapp.etheroll.utils import run_in_thread

load_kv_from_py(__file__)
DEFAULT_MIN_BET = 0.10


class RollUnderRecap(GridLayout):
    roll_under_property = NumericProperty()
    profit_property = NumericProperty()
    wager_property = NumericProperty()


class BetSize(BoxLayout):
    min_bet_property = NumericProperty(DEFAULT_MIN_BET)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(self._after_init)

    def _after_init(self, dt):
        """Binds events."""
        slider = self.ids.bet_size_slider_id
        inpt = self.ids.bet_size_input_id
        cast_to = float
        # shows less digits than the constant default to keep the input tiny
        round_digits = 2
        BetSize.bind_slider_input(slider, inpt, cast_to, round_digits)
        self.pull_min_bet_from_contract()

    @run_in_thread
    def pull_min_bet_from_contract(self):
        """
        Retrieves (async) the minimum bet size by calling the contract.
        On network error fallback to default minimum bet.
        """
        controller = App.get_running_app().root
        pyetheroll = controller.pyetheroll
        min_bet = DEFAULT_MIN_BET
        try:
            min_bet_wei = pyetheroll.contract.functions.minBet().call()
            min_bet = round(min_bet_wei / 1e18, ROUND_DIGITS)
        except ConnectionError:
            pass
        self.set_min_bet(min_bet)

    @mainthread
    def set_min_bet(self, min_bet):
        self.min_bet_property = min_bet

    @staticmethod
    def bind_slider_input(
            slider, inpt, cast_to=float, round_digits=ROUND_DIGITS):
        """Binds slider <-> input both ways."""
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
        """Returns normalized bet size value."""
        try:
            return round(
                float(self.ids.bet_size_input_id.text), ROUND_DIGITS)
        except ValueError:
            return 0


class ChanceOfWinning(BoxLayout):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(self._after_init)

    def _after_init(self, dt):
        """Binds events."""
        slider = self.ids.chances_slider_id
        inpt = self.ids.chances_input_id
        cast_to = self.cast_to
        round_digits = 0
        BetSize.bind_slider_input(slider, inpt, cast_to, round_digits)

    @staticmethod
    def cast_to(value):
        return int(float(value))

    @property
    def value(self):
        """Returns normalized chances value."""
        try:
            # `input_filter: 'int'` only verifies that we have a number
            # but doesn't convert to int
            chances = float(self.ids.chances_input_id.text)
            return int(chances)
        except ValueError:
            return 0


class RollScreen(Screen):

    current_account_string = StringProperty(allownone=True)
    balance_property = NumericProperty()

    def get_roll_input(self):
        """Returns bet size and chance of winning user input values."""
        bet_size = self.ids.bet_size_id
        chance_of_winning = self.ids.chance_of_winning_id
        return {
            "bet_size": bet_size.value,
            "chances": chance_of_winning.value,
        }

    @mainthread
    def toggle_widgets(self, enabled):
        """Enables/disables widgets (useful during roll)."""
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
        """Updates the property from main thread."""
        self.balance_property = balance

    @staticmethod
    @mainthread
    def on_connection_refused():
        title = 'No network'
        body = 'No network, could not retrieve account balance.'
        dialog = Dialog.create_dialog(title, body)
        dialog.open()

    @run_in_thread
    def fetch_update_balance(self):
        """Retrieves the balance and updates the property."""
        address = self.current_account_string
        if not address:
            return
        try:
            balance = self.pyetheroll.get_balance(address)
        except ConnectionRefused:
            self.on_connection_refused()
            return
        self.update_balance(balance)
