import unittest
from unittest import mock

from pyetheroll.etherscan_utils import get_etherscan_api_key


class TestEtherscanlUtils(unittest.TestCase):

    def test_get_etherscan_api_key(self):
        """
        Verifies the key can be retrieved from either:
        1) environment
        2) file
        3) or fallbacks on default key
        """
        expected_key = '0102030405060708091011121314151617'
        # 1) environment
        with mock.patch.dict(
                'os.environ', {'ETHERSCAN_API_KEY': expected_key}):
            actual_key = get_etherscan_api_key()
        self.assertEqual(actual_key, expected_key)
        # 2) file
        read_data = '{ "key" : "%s" }' % (expected_key)
        with mock.patch('builtins.open', mock.mock_open(read_data=read_data)) \
                as m_open:
            actual_key = get_etherscan_api_key()
        self.assertEqual(expected_key, actual_key)
        # verifies the file was read
        self.assertTrue(
            m_open.call_args_list[0][0][0].endswith(
                'src/pyetheroll/api_key.json'))
        self.assertEqual(m_open.call_args_list[0][1], {'mode': 'r'})
        # 3) or fallbacks on default key
        with mock.patch('builtins.open') as m_open, \
                mock.patch('pyetheroll.etherscan_utils.logger') as m_logger:
            m_open.side_effect = FileNotFoundError
            actual_key = get_etherscan_api_key()
        self.assertEqual('YourApiKeyToken', actual_key)
        # verifies the fallback warning was logged
        self.assertTrue(
            'Cannot get Etherscan API key.'
            in m_logger.warning.call_args_list[0][0][0])
