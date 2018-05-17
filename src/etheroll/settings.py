import constants
import pyetheroll
from etheroll.utils import Store, SubScreen, load_kv_from_py

load_kv_from_py(__file__)


class SettingsScreen(SubScreen):
    """
    Screen for configuring network, gas price...
    """

    def __init__(self, **kwargs):
        super(SettingsScreen, self).__init__(**kwargs)

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

    def store_settings(self):
        """
        Stores settings to json store.
        """
        self.store_gas_price()
        self.store_network()

    def get_ui_network(self):
        """
        Retrieves network values from UI.
        """
        if self.is_ui_mainnet():
            network = pyetheroll.ChainID.MAINNET
        else:
            network = pyetheroll.ChainID.ROPSTEN
        return network

    def is_ui_mainnet(self):
        return self.ids.mainnet_checkbox_id.active

    def is_ui_testnet(self):
        return self.ids.testnet_checkbox_id.active

    @staticmethod
    def get_stored_network():
        """
        Retrieves last stored network value, defaults to Mainnet.
        """
        store = Store.get_store()
        try:
            network_dict = store['network']
        except KeyError:
            # creates store if doesn't yet exist
            store.put('network')
        network_dict = store['network']
        network_name = network_dict.get(
            'value', pyetheroll.ChainID.MAINNET.name)
        network = pyetheroll.ChainID[network_name]
        return network

    @classmethod
    def is_stored_mainnet(cls):
        network = cls.get_stored_network()
        return network == pyetheroll.ChainID.MAINNET

    @classmethod
    def is_stored_testnet(cls):
        network = cls.get_stored_network()
        return network == pyetheroll.ChainID.ROPSTEN

    def get_ui_gas_price(self):
        return self.ids.gas_price_slider_id.value

    @staticmethod
    def get_stored_gas_price():
        """
        Retrieves stored gas price value, defaults to DEFAULT_GAS_PRICE_GWEI.
        """
        store = Store.get_store()
        try:
            gas_price_dict = store['gas_price']
        except KeyError:
            # creates store if doesn't yet exist
            store.put('gas_price')
        gas_price_dict = store['gas_price']
        gas_price = gas_price_dict.get(
            'value', constants.DEFAULT_GAS_PRICE_GWEI)
        return gas_price
