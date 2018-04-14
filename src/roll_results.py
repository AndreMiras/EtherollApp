from kivy.clock import Clock
from kivymd.list import TwoLineListItem

from utils import SubScreen, load_kv_from_py

load_kv_from_py(__file__)


class RollResultsScreen(SubScreen):

    def __init__(self, **kwargs):
        super(RollResultsScreen, self).__init__(**kwargs)
        Clock.schedule_once(self._after_init)

    def _after_init(self, dt):
        """
        Binds events.
        """
        pass

    @classmethod
    def create_item_from_dict(cls, roll_dict):
        """
        Creates a roll list item from a roll dictionary.
        """
        # roll_under = roll_dict['roll_under']
        # roll_result = roll_dict['roll_result']
        reward_loss_eth = roll_dict['reward_loss_eth']
        bet_size_eth = roll_dict['bet_size_eth']
        # TODO
        text = '{} ETH, bet size {} ETH'.format(reward_loss_eth, bet_size_eth)
        secondary_text = text
        # TODO: custom LineListItem with big number to the left (actual result)
        list_item = TwoLineListItem(
            text=text, secondary_text=secondary_text)
        return list_item

    def update_roll_list(self):
        """
        Updates the roll list widget.
        """
        # TODO
        roll_result = {
            'roll_under': 50,
            'roll_result': 27,
            'reward_loss_eth': 0.98,
            'bet_size_eth': 1.5,
        }
        roll_results = []
        roll_results.append(roll_result)
        roll_results.append(roll_result)
        roll_list = self.ids.roll_list_id
        roll_list.clear_widgets()
        for roll_result in roll_results:
            list_item = self.create_item_from_dict(roll_result)
            roll_list.add_widget(list_item)
