from kivy.app import App
from kivy.clock import Clock, mainthread
from kivy.properties import ListProperty
from kivymd.list import TwoLineListItem

from utils import SubScreen, load_kv_from_py, run_in_thread

load_kv_from_py(__file__)


class RollResultsScreen(SubScreen):

    bets = ListProperty()

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
    def on_bets(self, instance, value):
        """
        Updates UI using bets list.
        """
        self.update_roll_list()

    @run_in_thread
    def get_last_bets(self):
        """
        Gets last bets using pyetheroll lib and updates `bets` list property.
        """
        controller = self.controller
        account = controller.switch_account_screen.current_account
        if not account:
            controller.on_account_none()
            return
        address = "0x" + account.address.hex()
        self.bets = self.pyetheroll.get_last_bets(address=address)

    @staticmethod
    def create_item_from_dict(roll_dict):
        """
        Creates a roll list item from a roll dictionary.
        """
        bet_size_ether = roll_dict['bet_size_ether']
        roll_under = roll_dict['roll_under']
        text = 'roll under: {}, bet size: {} ETH'.format(
            roll_under, bet_size_ether)
        secondary_text = text
        list_item = TwoLineListItem(
            text=text, secondary_text=secondary_text)
        return list_item

    def update_roll_list(self):
        """
        Updates the roll list widget.
        """
        roll_list = self.ids.roll_list_id
        roll_list.clear_widgets()
        for bet in self.bets:
            list_item = self.create_item_from_dict(bet)
            roll_list.add_widget(list_item)
