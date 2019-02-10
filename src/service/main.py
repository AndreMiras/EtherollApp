#!/usr/bin/env python
"""
Roll pulling service script.
Monitors the chain on regular basis and send notifications on change.
Also updates the App UI via OSC:
MonitorRollsService -> OscAppClient -> OscAppServer -> App

On Linux run with:
```sh
PYTHONPATH=src/
PYTHON_SERVICE_ARGUMENT='{"osc_server_port": PORT}'
./src/service/main.py
```
"""
import json
import os
from time import sleep, time
from types import SimpleNamespace

from kivy.logger import Logger
from kivy.utils import platform
from plyer import notification
from pyetheroll.constants import ROUND_DIGITS, ChainID
from pyetheroll.etheroll import Etheroll
from raven import Client

from ethereum_utils import AccountUtils
from etheroll.constants import API_KEY_PATH, KEYSTORE_DIR_SUFFIX
from etheroll.patches import patch_find_library_android
from etheroll.store import Store
from osc.osc_app_client import OscAppClient
from sentry_utils import configure_sentry

patch_find_library_android()
PULL_FREQUENCY_SECONDS = 10
# time before the service shuts down if no roll activity
NO_ROLL_ACTIVITY_PERDIOD_SECONDS = 5 * 60


class MonitorRollsService():

    def __init__(self, osc_server_port=None):
        """
        Set `osc_server_port` to enable UI synchronization with service.
        """
        keystore_dir = self.get_keystore_path()
        self.account_utils = AccountUtils(keystore_dir=keystore_dir)
        self._pyetheroll = None
        # per address cached merged logs, used to compare with next pulls
        self.merged_logs = {}
        self.last_roll_activity = None
        self.osc_app_client = None
        if osc_server_port is not None:
            self.osc_app_client = OscAppClient('localhost', osc_server_port)

    def run(self):
        """
        Blocking pull loop call.
        Service will stop after a period of time with no roll activity.
        """
        self.last_roll_activity = time()
        elapsed = (time() - self.last_roll_activity)
        while elapsed < NO_ROLL_ACTIVITY_PERDIOD_SECONDS:
            self.pull_accounts_rolls()
            sleep(PULL_FREQUENCY_SECONDS)
            elapsed = (time() - self.last_roll_activity)
        # service decided to die naturally after no roll activity
        self.set_auto_restart_service(False)

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
            self._pyetheroll = Etheroll(API_KEY_PATH, chain_id)
        return self._pyetheroll

    @staticmethod
    def get_running_app():
        """
        Fakes the get_running_app() behavior and returns an app with only
        `App.name` setup.
        """
        app_name = 'etheroll'
        return SimpleNamespace(name=app_name)

    @classmethod
    def user_data_dir(cls):
        app = cls.get_running_app()
        return Store.get_user_data_dir(app)

    # TODO: refactore and share the one from settings or somewhere
    @classmethod
    def get_stored_network(cls):
        """
        Retrieves last stored network value, defaults to Mainnet.
        """
        app = cls.get_running_app()
        store = Store.get_store(app)
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
        KEYSTORE_DIR_PREFIX = os.path.expanduser("~")
        # uses kivy user_data_dir (/sdcard/<app_name>)
        if platform == "android":
            # KEYSTORE_DIR_PREFIX = App.get_running_app().user_data_dir
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
            self.last_roll_activity = time()

    def pull_accounts_rolls(self):
        accounts = []
        try:
            accounts = self.account_utils.get_account_list()
        except PermissionError:
            # happens in e.g. Android runtime permission check, refs #125
            pass
        print(f'accounts: {accounts}')
        for account in accounts:
            self.pull_account_rolls(account)

    def do_notify(self, merged_logs):
        """
        Notifies the with last roll.
        If the roll has no bet result, notifies it was just placed on the
        blockchain, but not yet resolved by the oracle.
        If it has a result, notifies it.
        Also notifies the app process via OSC so it can refresh balance.
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
        if self.osc_app_client is not None:
            self.osc_app_client.send_refresh_balance()
        notification.notify(**kwargs)


def main():
    # only send Android errors to Sentry
    in_debug = platform != "android"
    client = configure_sentry(in_debug)
    argument = os.environ.get('PYTHON_SERVICE_ARGUMENT', 'null')
    argument = json.loads(argument)
    argument = {} if argument is None else argument
    osc_server_port = argument.get('osc_server_port')
    service = MonitorRollsService(osc_server_port)
    try:
        service.set_auto_restart_service()
        service.run()
    except Exception:
        # avoid auto-restart loop
        service.set_auto_restart_service(False)
        if type(client) == Client:
            Logger.info(
                'Errors will be sent to Sentry, run with "--debug" if you '
                'are a developper and want to the error in the shell.')
        client.captureException()


if __name__ == '__main__':
    main()
