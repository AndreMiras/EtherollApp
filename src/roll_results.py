from kivy.app import App
from kivy.clock import Clock, mainthread
from kivy.properties import ListProperty
from kivymd.label import MDLabel
from kivymd.list import ILeftBody, ThreeLineAvatarListItem

import constants
from utils import SubScreen, load_kv_from_py, run_in_thread

load_kv_from_py(__file__)


class DiceResultWidget(ILeftBody, MDLabel):
    pass


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
        self.update_roll_list()

    @property
    def pyetheroll(self):
        """
        We want to make sure we go through the `Controller.pyetheroll` property
        each time, because it recreates the Etheroll object on chain_id
        changes.
        """
        return self.controller.pyetheroll

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
        # bet_value_ether is quiet confusing here, it's the actual payout
        # that will be received in case of win
        bet_value_ether = roll_dict['bet_value_ether']
        roll_under = roll_dict['roll_under']
        dice_result = roll_dict['dice_result']
        date_time = roll_dict['datetime']
        # chances_win = roll_under - 1
        # profit = Etheroll.compute_profit(bet_value_ether, chances_win)
        player_won = dice_result < roll_under
        profit_loss = bet_value_ether if player_won else -bet_value_ether
        sign = '<' if player_won else '>'
        win_color = (0, 1, 0, 1)
        loss_color = (1, 0, 0, 1)
        text_color = win_color if player_won else loss_color
        text = '{0} ETH, bet size: {1:.{2}f} ETH'.format(
            profit_loss, bet_value_ether, constants.ROUND_DIGITS)
        secondary_text = '{0} {1} {2}'.format(
            dice_result, sign, roll_under)
        tertiary_text = date_time.strftime("%Y-%m-%d %H:%M:%S")
        # tertiary_text is in fact embedded in secondary_text with new line
        secondary_text += '\n' + tertiary_text
        avatar_sample_widget = DiceResultWidget(
            text=str(dice_result), font_style='Title',
            theme_text_color='Custom', text_color=text_color)
        list_item = ThreeLineAvatarListItem(
            text=text, secondary_text=secondary_text)
        list_item.add_widget(avatar_sample_widget)
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
