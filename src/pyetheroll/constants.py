from enum import Enum

ROUND_DIGITS = 2
DEFAULT_GAS_PRICE_GWEI = 4


class ChainID(Enum):
    MAINNET = 1
    MORDEN = 2
    ROPSTEN = 3
