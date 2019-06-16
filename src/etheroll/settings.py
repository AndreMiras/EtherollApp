import os

from kivy.app import App
from kivy.utils import platform
from pyetheroll.constants import DEFAULT_GAS_PRICE_GWEI, ChainID

from etheroll.constants import KEYSTORE_DIR_SUFFIX
from etheroll.store import Store


class Settings:
    """
    Screen for configuring network, gas price...
    """

    @classmethod
    def get_stored_network(cls):
        """
        Retrieves last stored network value, defaults to Mainnet.
        """
        store = Store.get_store()
        try:
            network_dict = store['network']
        except KeyError:
            network_dict = {}
        network_name = network_dict.get(
            'value', ChainID.MAINNET.name)
        network = ChainID[network_name]
        return network

    @classmethod
    def is_stored_mainnet(cls):
        network = cls.get_stored_network()
        return network == ChainID.MAINNET

    @classmethod
    def is_stored_testnet(cls):
        network = cls.get_stored_network()
        return network == ChainID.ROPSTEN

    @classmethod
    def get_stored_gas_price(cls):
        """
        Retrieves stored gas price value, defaults to DEFAULT_GAS_PRICE_GWEI.
        """
        store = Store.get_store()
        try:
            gas_price_dict = store['gas_price']
        except KeyError:
            gas_price_dict = {}
        gas_price = gas_price_dict.get(
            'value', DEFAULT_GAS_PRICE_GWEI)
        return gas_price

    @classmethod
    def is_persistent_keystore(cls):
        """
        Retrieves the settings value regarding the keystore persistency.
        Defaults to False.
        """
        store = Store.get_store()
        try:
            persist_keystore_dict = store['persist_keystore']
        except KeyError:
            persist_keystore_dict = {}
        persist_keystore = persist_keystore_dict.get(
            'value', False)
        return persist_keystore

    @classmethod
    def _get_android_keystore_prefix(cls):
        """
        Returns the Android keystore path prefix.
        The location differs based on the persistency user settings.
        """
        app = App.get_running_app()
        if cls.is_persistent_keystore():
            # TODO: hardcoded path, refs:
            # https://github.com/AndreMiras/EtherollApp/issues/145
            keystore_dir_prefix = os.path.join('/sdcard', app.name)
        else:
            keystore_dir_prefix = app.user_data_dir
        return keystore_dir_prefix

    @classmethod
    def get_keystore_path(cls):
        """
        Returns the keystore directory path.
        This can be overriden by the `KEYSTORE_PATH` environment variable.
        """
        keystore_path = os.environ.get('KEYSTORE_PATH')
        if keystore_path is not None:
            return keystore_path
        KEYSTORE_DIR_PREFIX = os.path.expanduser("~")
        if platform == "android":
            KEYSTORE_DIR_PREFIX = cls._get_android_keystore_prefix()
        keystore_path = os.path.join(
            KEYSTORE_DIR_PREFIX, KEYSTORE_DIR_SUFFIX)
        return keystore_path
