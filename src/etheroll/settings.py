import pyetheroll
from etheroll.utils import SubScreen, load_kv_from_py

load_kv_from_py(__file__)


class SettingsScreen(SubScreen):
    """
    Screen for configuring network, gas price...
    """

    def __init__(self, **kwargs):
        super(SettingsScreen, self).__init__(**kwargs)

    @property
    def network(self):
        """
        Returns selected network.
        """
        if self.is_mainnet():
            return pyetheroll.ChainID.MAINNET
        return pyetheroll.ChainID.ROPSTEN

    def is_mainnet(self):
        return self.ids.mainnet_checkbox_id.active

    def is_testnet(self):
        return self.ids.testnet_checkbox_id.active
