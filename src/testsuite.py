import unittest

from tests import test_ethereum_utils, test_import
from tests.pyetheroll import (test_etheroll, test_etherscan_utils,
                              test_transaction_debugger, test_utils)


def suite():
    modules = [
        test_ethereum_utils, test_import, test_etheroll, test_etherscan_utils,
        test_transaction_debugger, test_utils
    ]
    test_suite = unittest.TestSuite()
    for module in modules:
        test_suite.addTest(unittest.TestLoader().loadTestsFromModule(module))
    return test_suite
