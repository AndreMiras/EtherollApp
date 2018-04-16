from kivy.app import App
from kivy.clock import Clock, mainthread
from kivy.properties import ListProperty
from kivymd.list import TwoLineListItem

import constants
from utils import SubScreen, load_kv_from_py, run_in_thread

load_kv_from_py(__file__)


class RollResultsScreen(SubScreen):

    roll_results = ListProperty()

    def __init__(self, **kwargs):
        super(RollResultsScreen, self).__init__(**kwargs)
        Clock.schedule_once(self._after_init)

    def _after_init(self, dt):
        """
        Binds events.
        """
        self.controller = App.get_running_app().root
        self.pyetheroll = self.controller.pyetheroll
        self.update_roll_list()

    @mainthread
    def on_roll_results(self, instance, value):
        """
        Updates UI using roll results list.
        """
        self.update_roll_list()

    @run_in_thread
    def get_last_results(self):
        """
        Gets last roll results using pyetheroll lib and updates `roll_results`
        list property.
        """
        controller = self.controller
        account = controller.switch_account_screen.current_account
        if not account:
            controller.on_account_none()
            return
        address = "0x" + account.address.hex()
        self.roll_results = self.pyetheroll.get_last_bets_results_logs(
            address=address)

    @staticmethod
    def create_item_from_dict(roll_dict):
        """
        Creates a roll list item from a roll dictionary.
        """
        bet_value_ether = roll_dict['bet_value_ether']
        roll_under = roll_dict['roll_under']
        dice_result = roll_dict['dice_result']
        roll_under = roll_dict['roll_under']
        player_won = roll_under < dice_result
        sign = '>' if player_won else '<'
        text = '{0} {1} {2}, bet size: {3:.{4}f} ETH'.format(
            dice_result, sign, roll_under, bet_value_ether,
            constants.ROUND_DIGITS)
        secondary_text = text
        list_item = TwoLineListItem(
            text=text, secondary_text=secondary_text)
        return list_item

    def update_roll_list(self):
        """
        Updates the roll results list widget.
        """
        roll_list = self.ids.roll_list_id
        roll_list.clear_widgets()
        roll_results = reversed(self.roll_results)
        for roll_result in roll_results:
            list_item = self.create_item_from_dict(roll_result)
            roll_list.add_widget(list_item)
