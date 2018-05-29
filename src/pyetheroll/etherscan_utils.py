import json
import logging
import os

from etherscan.accounts import Account as EtherscanAccount
from etherscan.contracts import Contract as EtherscanContract

from pyetheroll.constants import ChainID

logger = logging.getLogger(__name__)


def get_etherscan_api_key():
    """
    Tries to retrieve etherscan API key from environment or from file.
    """
    ETHERSCAN_API_KEY = os.environ.get('ETHERSCAN_API_KEY')
    if ETHERSCAN_API_KEY is None:
        location = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__)))
        api_key_path = str(os.path.join(location, 'api_key.json'))
        try:
            with open(api_key_path, mode='r') as key_file:
                ETHERSCAN_API_KEY = json.loads(key_file.read())['key']
        except FileNotFoundError:
            ETHERSCAN_API_KEY = 'YourApiKeyToken'
            logger.warning(
                'Cannot get Etherscan API key. '
                'File {} not found, defaulting to `{}`.'.format(
                    api_key_path, ETHERSCAN_API_KEY))
    return ETHERSCAN_API_KEY


class RopstenEtherscanContract(EtherscanContract):
    """
    https://github.com/corpetty/py-etherscan-api/issues/24
    """
    PREFIX = 'https://api-ropsten.etherscan.io/api?'


class ChainEtherscanContractFactory:
    """
    Creates Contract class type depending on the chain ID.
    """

    CONTRACTS = {
        ChainID.MAINNET: EtherscanContract,
        ChainID.ROPSTEN: RopstenEtherscanContract,
    }

    @classmethod
    def create(cls, chain_id=ChainID.MAINNET):
        ChainEtherscanContract = cls.CONTRACTS[chain_id]
        return ChainEtherscanContract


class RopstenEtherscanAccount(EtherscanAccount):
    """
    https://github.com/corpetty/py-etherscan-api/issues/24
    """
    PREFIX = 'https://api-ropsten.etherscan.io/api?'


class ChainEtherscanAccountFactory:
    """
    Creates Account class type depending on the chain ID.
    """

    ACCOUNTS = {
        ChainID.MAINNET: EtherscanAccount,
        ChainID.ROPSTEN: RopstenEtherscanAccount,
    }

    @classmethod
    def create(cls, chain_id=ChainID.MAINNET):
        ChainEtherscanAccount = cls.ACCOUNTS[chain_id]
        return ChainEtherscanAccount
