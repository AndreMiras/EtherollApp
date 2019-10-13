from kivy.app import App
from kivy.clock import Clock, mainthread
from kivy.properties import ListProperty
from kivymd.label import MDLabel
from kivymd.list import ILeftBody, ThreeLineAvatarListItem
from pyetheroll.constants import ROUND_DIGITS

from etherollapp.etheroll.ui_utils import Dialog, SubScreen, load_kv_from_py
from etherollapp.etheroll.utils import run_in_thread

load_kv_from_py(__file__)


class DiceResultWidget(ILeftBody, MDLabel):
    pass


class RollResultsScreen(SubScreen):

    roll_logs = ListProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # TODO: make it a property that starts/stops spinner on set
        self._fetching_results = False
        Clock.schedule_once(self._after_init)

    def _after_init(self, dt):
        """Binds events."""
        self.update_roll_list()

    # TODO: create a dedicated PullRefreshScrollView that handle all this
    def on_scroll_stop(self, scroll_y):
        """Refreshs roll results on overscroll."""
        # refresh if we hit the bottom or if we over pull
        # currently hitting the bottom will refresh last transactions only
        # rather than loading more ancient transactions
        if scroll_y == 0 or scroll_y >= 1.03:
            if not self._fetching_results:
                self.get_last_results()

    def toggle_spinner(self, show):
        spinner = self.ids.spinner_id
        spinner.toggle(show)

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
    def on_roll_logs(self, instance, value):
        """Updates UI using roll results list."""
        self.update_roll_list()

    @staticmethod
    @mainthread
    def on_connection_refused():
        title = 'No network'
        body = 'No network, could not retrieve roll history.'
        dialog = Dialog.create_dialog(title, body)
        dialog.open()

    @run_in_thread
    def get_last_results(self):
        """
        Gets last rolls & results using pyetheroll lib and updates `roll_logs`
        list property.
        """
        # lazy loading
        from etherscan.client import ConnectionRefused
        controller = App.get_running_app().root
        account = controller.current_account
        if not account:
            controller.on_account_none()
            self.on_back()
            return
        self._fetching_results = True
        self.toggle_spinner(show=True)
        address = "0x" + account.address.hex()
        try:
            self.roll_logs = self.pyetheroll.get_merged_logs(
                address=address)
        except ConnectionRefused:
            self.on_connection_refused()
        self.toggle_spinner(show=False)
        self._fetching_results = False

    @staticmethod
    def create_item_from_dict(roll_log):
        """Creates a roll list item from a roll log dictionary."""
        # lazy loading
        from pyetheroll.utils import EtherollUtils
        bet_log = roll_log['bet_log']
        bet_result = roll_log['bet_result']
        bet_value_ether = bet_log['bet_value_ether']
        roll_under = bet_log['roll_under']
        date_time = bet_log['datetime']
        # will keep default value on unresolved bets
        dice_result = '?'
        player_won = None
        sign = '?'
        win_color = (0, 1, 0, 1)
        loss_color = (1, 0, 0, 1)
        unresolved_color = (0.5, 0.5, 0.5, 1)
        text_color = unresolved_color
        profit_loss_str = '?'
        # resolved bets case
        if bet_result is not None:
            dice_result = bet_result['dice_result']
            player_won = dice_result < roll_under
            sign = '<' if player_won else '>'
            text_color = win_color if player_won else loss_color
            chances_win = roll_under - 1
            profit = EtherollUtils.compute_profit(bet_value_ether, chances_win)
            profit_loss = profit if player_won else -bet_value_ether
            profit_loss_str = (
                '{profit_loss:+.{round_digits}f}'
            ).format(**{
                'profit_loss': profit_loss,
                'round_digits': ROUND_DIGITS})
        text = ('{0} ETH').format(profit_loss_str)
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
        """Updates the roll results list widget."""
        roll_list = self.ids.roll_list_id
        roll_list.clear_widgets()
        roll_logs = reversed(self.roll_logs)
        for roll_log in roll_logs:
            list_item = self.create_item_from_dict(roll_log)
            roll_list.add_widget(list_item)
