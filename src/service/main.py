import os
from time import sleep

from kivy.storage.jsonstore import JsonStore
from kivy.utils import platform
from plyer import notification

from ethereum_utils import AccountUtils
from etheroll.constants import KEYSTORE_DIR_SUFFIX
from etheroll.patches import patch_find_library_android
from pyetheroll.constants import ROUND_DIGITS, ChainID
from pyetheroll.etheroll import Etheroll

patch_find_library_android()
PULL_FREQUENCY_SECONDS = 10


class MonitorRollsService():

    def __init__(self):
        keystore_dir = self.get_keystore_path()
        self.account_utils = AccountUtils(keystore_dir=keystore_dir)
        self._pyetheroll = None
        # per address cached merged logs, used to compare with next pulls
        self.merged_logs = {}

    def start(self):
        """
        Blocking pull loop call.
        """
        while True:
            self.pull_accounts_rolls()
            sleep(PULL_FREQUENCY_SECONDS)

    @staticmethod
    def set_auto_restart_service(restart=True):
        """
        Makes sure the service restarts automatically on Android when killed.
        """
        if platform != 'android':
            return
        from jnius import autoclass
        PythonService = autoclass('org.kivy.android.PythonService')
        PythonService.mService.setAutoRestartService(restart)

    @property
    def pyetheroll(self):
        """
        Gets or creates the Etheroll object.
        Also recreates the object if the chain_id changed.
        """
        chain_id = self.get_stored_network()
        if self._pyetheroll is None or self._pyetheroll.chain_id != chain_id:
            self._pyetheroll = Etheroll(chain_id)
        return self._pyetheroll

    @staticmethod
    def user_data_dir():
        """
        Fakes kivy.app.App().user_data_dir behavior.
        On Android, `/sdcard/<app_name>` is returned.
        """
        # TODO: hardcoded
        app_name = 'etheroll'
        data_dir = os.path.join('/sdcard', app_name)
        data_dir = os.path.expanduser(data_dir)
        if not os.path.exists(data_dir):
            os.mkdir(data_dir)
        return data_dir

    # TODO: merge at least "store.json" const with src/etheroll/store.py
    @classmethod
    def get_store_path(cls):
        """
        Returns the full user store path.
        """
        user_data_dir = cls.user_data_dir()
        store_path = os.path.join(user_data_dir, 'store.json')
        return store_path

    @classmethod
    def get_store(cls):
        """
        Returns user Store object.
        """
        store_path = cls.get_store_path()
        store = JsonStore(store_path)
        return store

    # TODO: refactore and share the one from settings or somewhere
    @classmethod
    def get_stored_network(cls):
        """
        Retrieves last stored network value, defaults to Mainnet.
        """
        store = cls.get_store()
        try:
            network_dict = store['network']
        except KeyError:
            network_dict = {}
        network_name = network_dict.get(
            'value', ChainID.MAINNET.name)
        network = ChainID[network_name]
        return network

    @classmethod
    def get_keystore_path(cls):
        KEYSTORE_DIR_PREFIX = cls.user_data_dir()
        keystore_dir = os.path.join(
            KEYSTORE_DIR_PREFIX, KEYSTORE_DIR_SUFFIX)
        return keystore_dir

    def pull_account_rolls(self, account):
        """
        Retrieves the merged logs for the given account and compares it with
        existing cached value. If it differs notifies and updates cache.
        """
        address = "0x" + account.address.hex()
        merged_logs = self.pyetheroll.get_merged_logs(address=address)
        try:
            merged_logs_cached = self.merged_logs[address]
        except KeyError:
            # not yet cahed, let's cache it for the first time
            self.merged_logs[address] = merged_logs
            return
        if merged_logs_cached != merged_logs:
            # since it differs, updates the cache and notifies
            self.merged_logs[address] = merged_logs
            self.do_notify(merged_logs)

    def pull_accounts_rolls(self):
        accounts = self.account_utils.get_account_list()
        for account in accounts:
            self.pull_account_rolls(account)

    # TODO: should we show "dice_result sign roll_under" and/or value won/lost?
    def do_notify(self, merged_logs):
        """
        Notifies the with last roll.
        If the roll has no bet result, notifies it was just placed on the
        blockchain, but not yet resolved by the oracle.
        If it has a result, notifies it.
        """
        merged_log = merged_logs[-1]
        bet_log = merged_log['bet_log']
        bet_result = merged_log['bet_result']
        bet_value_ether = bet_log['bet_value_ether']
        roll_under = bet_log['roll_under']
        ticker = "Ticker"
        # the bet was just placed, but not resolved by the oracle
        if bet_result is None:
            title = "Bet confirmed on chain"
            message = (
                '{bet_value_ether:.{round_digits}f} ETH '
                'to roll under {roll_under}').format(**{
                    'bet_value_ether': bet_value_ether,
                    'round_digits': ROUND_DIGITS,
                    'roll_under': roll_under})
        else:
            dice_result = bet_result['dice_result']
            player_won = dice_result < roll_under
            sign = '<' if player_won else '>'
            title = 'You '
            title += 'won' if player_won else 'lost'
            message = '{0} {1} {2}'.format(
                dice_result, sign, roll_under)
        kwargs = {'title': title, 'message': message, 'ticker': ticker}
        notification.notify(**kwargs)


def main():
    service = MonitorRollsService()
    service.set_auto_restart_service()
    service.start()


if __name__ == '__main__':
    main()
