from pyetheroll.constants import ChainID

from etheroll.store import Store
from etheroll.ui_utils import SubScreen, load_kv_from_py
from etheroll.utils import (check_request_write_permission,
                            check_write_permission)

load_kv_from_py(__file__)


class SettingsScreen(SubScreen):
    """
    Screen for configuring network, gas price...
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def store_network(self):
        """
        Saves selected network to the store.
        """
        store = Store.get_store()
        network = self.get_ui_network()
        store.put('network', value=network.name)

    def store_gas_price(self):
        """
        Saves gas price value to the store.
        """
        store = Store.get_store()
        gas_price = self.get_ui_gas_price()
        store.put('gas_price', value=gas_price)

    def store_is_persistent_keystore(self):
        """
        Saves the persistency option to the store.
        Note that to save `True` we also check if we have write permissions.
        """
        store = Store.get_store()
        persist_keystore = self.is_ui_persistent_keystore()
        persist_keystore &= check_write_permission()
        store.put('persist_keystore', value=persist_keystore)

    def store_settings(self):
        """
        Stores settings to json store.
        """
        self.store_gas_price()
        self.store_network()
        self.store_is_persistent_keystore()

    def get_ui_network(self):
        """
        Retrieves network values from UI.
        """
        if self.is_ui_mainnet():
            network = ChainID.MAINNET
        else:
            network = ChainID.ROPSTEN
        return network

    def is_ui_mainnet(self):
        return self.ids.mainnet_checkbox_id.active

    def is_ui_testnet(self):
        return self.ids.testnet_checkbox_id.active

    def get_ui_gas_price(self):
        return self.ids.gas_price_slider_id.value

    def is_ui_persistent_keystore(self):
        return self.ids.persist_keystore_switch_id.active

    def check_request_write_permission(self):
        # previous state before the toggle
        if not self.is_ui_persistent_keystore():
            check_request_write_permission()
