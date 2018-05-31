import json
import os
import shutil
import unittest
from datetime import datetime
from tempfile import mkdtemp
from unittest import mock

from eth_account.internal.transactions import assert_valid_fields
from ethereum.tools.keys import PBKDF2_CONSTANTS
from pyethapp.accounts import Account

from pyetheroll.constants import ChainID
from pyetheroll.etheroll import Etheroll


class TestEtheroll(unittest.TestCase):

    log_bet_abi = {
        'inputs': [
          {'indexed': True, 'type': 'bytes32', 'name': 'BetID'},
          {'indexed': True, 'type': 'address', 'name': 'PlayerAddress'},
          {'indexed': True, 'type': 'uint256', 'name': 'RewardValue'},
          {'indexed': False, 'type': 'uint256', 'name': 'ProfitValue'},
          {'indexed': False, 'type': 'uint256', 'name': 'BetValue'},
          {'indexed': False, 'type': 'uint256', 'name': 'PlayerNumber'},
          {'indexed': False, 'type': 'uint256', 'name': 'RandomQueryID'},
        ],
        'type': 'event', 'name': 'LogBet', 'anonymous': False
      }

    log_result_abi = {
        'name': 'LogResult',
        'inputs': [
            {'name': 'ResultSerialNumber', 'indexed': True, 'type': 'uint256'},
            {'name': 'BetID', 'indexed': True, 'type': 'bytes32'},
            {'name': 'PlayerAddress', 'indexed': True, 'type': 'address'},
            {'name': 'PlayerNumber', 'indexed': False, 'type': 'uint256'},
            {'name': 'DiceResult', 'indexed': False, 'type': 'uint256'},
            {'name': 'Value', 'indexed': False, 'type': 'uint256'},
            {'name': 'Status', 'indexed': False, 'type': 'int256'},
            {'name': 'Proof', 'indexed': False, 'type': 'bytes'},
        ],
        'anonymous': False, 'type': 'event',
    }

    player_roll_dice_abi = {
        'constant': False,
        'inputs': [{'name': 'rollUnder', 'type': 'uint256'}],
        'name': 'playerRollDice',
        'outputs': [],
        'payable': True,
        'stateMutability': 'payable',
        'type': 'function',
    }

    bet_logs = [
        {
            'bet_id': (
                '15e007148ec621d996c886de0f2b88a0'
                '3af083aa819e851a51133dc17b6e0e5b'),
            'bet_value_ether': 0.45,
            'datetime': datetime(2018, 4, 7, 0, 17, 6),
            'profit_value_ether': 44.1,
            'reward_value_ether': 44.55,
            'roll_under': 2,
            'timestamp': '0x5ac80e02',
            'transaction_hash': (
                '0xf363906a9278c4dd300c50a3c9a2790'
                '0bb85df60596c49f7833c232f2944d1cb')
        },
        {
            'bet_id': (
                '14bae6b4711bdc5e3db19983307a9208'
                '1e2e7c1d45161117bdf7b8b509d1abbe'),
            'bet_value_ether': 0.45,
            'datetime': datetime(2018, 4, 7, 0, 20, 14),
            'profit_value_ether': 6.97,
            'reward_value_ether': 7.42,
            'roll_under': 7,
            'timestamp': '0x5ac80ebe',
            'transaction_hash': (
                '0x0df8789552248edf1dd9d06a7a90726'
                'f1bc83a9c39f315b04efb6128f0d02146')
        },
        {
            # that one would not have been yet resolved (no `LogResult`)
            'bet_id': (
                'c2997a1bad35841b2c30ca95eea9cb08'
                'c7b101bc14d5aa8b1b8a0facea793e05'),
            'bet_value_ether': 0.5,
            'datetime': datetime(2018, 4, 7, 0, 23, 46),
            'profit_value_ether': 3.31,
            'reward_value_ether': 3.81,
            'roll_under': 14,
            'timestamp': '0x5ac80f92',
            'transaction_hash': (
                '0x0440f1013a5eafd88f16be6b5612b6e'
                '051a4eb1b0b91a160c680295e7fab5bfe')
        }
    ]

    bet_results_logs = [
        {
            'bet_id': (
                '15e007148ec621d996c886de0f2b88a0'
                '3af083aa819e851a51133dc17b6e0e5b'),
            'bet_value_ether': 0.45,
            'datetime': datetime(2018, 4, 7, 0, 17, 55),
            'dice_result': 86,
            'roll_under': 2,
            'timestamp': '0x5ac80e33',
            'transaction_hash': (
                '0x3505de688dc20748eb5f6b3efd6e6d3'
                '66ea7f0737b4ab17035c6b60ab4329f2a')
        },
        {
            'bet_id': (
                '14bae6b4711bdc5e3db19983307a9208'
                '1e2e7c1d45161117bdf7b8b509d1abbe'),
            'bet_value_ether': 0.45,
            'datetime': datetime(2018, 4, 7, 0, 20, 54),
            'dice_result': 51,
            'roll_under': 7,
            'timestamp': '0x5ac80ee6',
            'transaction_hash': (
                '0x42df3e3136957bcc64226206ed177d5'
                '7ac9c31e116290c8778c97474226d3092')
        },
    ]

    def setUp(self):
        self.keystore_dir = mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.keystore_dir, ignore_errors=True)

    def test_init(self):
        """
        Verifies object initializes properly and contract methods are callable.
        """
        with mock.patch('etherscan.contracts.Contract.get_abi') \
                as m_get_abi:
            m_get_abi.return_value = (
                '[{"constant":true,"inputs":[],"name":"minBet","outputs":[{"na'
                'me":"","type":"uint256"}],"payable":false,"stateMutability":"'
                'view","type":"function"}]')
            etheroll = Etheroll()
        self.assertIsNotNone(etheroll.contract)

    def create_account_helper(self, password):
        # reduces key derivation iterations to speed up creation
        PBKDF2_CONSTANTS['c'] = 1
        wallet_path = os.path.join(self.keystore_dir, 'wallet.json')
        account = Account.new(password, path=wallet_path)
        with open(account.path, 'w') as f:
            f.write(account.dump())
        return account

    def test_player_roll_dice(self):
        """
        Verifies the transaction is properly built and sent.
        """
        # simplified contract ABI
        contract_abi = [self.player_roll_dice_abi]
        with mock.patch('etherscan.contracts.Contract.get_abi') \
                as m_get_abi:
            m_get_abi.return_value = json.dumps(contract_abi)
            etheroll = Etheroll()
        bet_size_ether = 0.1
        chances = 50
        wallet_password = 'password'
        account = self.create_account_helper(wallet_password)
        wallet_path = account.path
        with \
                mock.patch('web3.eth.Eth.sendRawTransaction') \
                as m_sendRawTransaction, mock.patch(
                    'web3.eth.Eth.getTransactionCount'
                    ) as m_getTransactionCount, mock.patch(
                        'eth_account.account.Account.signTransaction'
                    ) as m_signTransaction:
            m_getTransactionCount.return_value = 0
            transaction = etheroll.player_roll_dice(
                bet_size_ether, chances, wallet_path, wallet_password)
            # the method should return a transaction hash
            self.assertIsNotNone(transaction)
            # a second one with custom gas (in gwei), refs #23
            gas_price_gwei = 12
            transaction = etheroll.player_roll_dice(
                bet_size_ether, chances, wallet_path, wallet_password,
                gas_price_gwei)
            self.assertIsNotNone(transaction)
        # the nonce was retrieved
        self.assertTrue(m_getTransactionCount.called)
        # the transaction was sent
        self.assertTrue(m_sendRawTransaction.called)
        # the transaction should be built that way
        expected_transaction1 = {
            'nonce': 0, 'chainId': 1,
            'to': Etheroll.CONTRACT_ADDRESSES[ChainID.MAINNET],
            'data': (
                    '0xdc6dd152000000000000000000000000000'
                    '0000000000000000000000000000000000032'),
            'gas': 310000,
            'value': 100000000000000000, 'gasPrice': 4000000000
        }
        expected_transaction2 = expected_transaction1.copy()
        expected_transaction2['gasPrice'] = 12*1e9
        expected_call1 = mock.call(expected_transaction1, account.privkey)
        expected_call2 = mock.call(expected_transaction2, account.privkey)
        # the method should have been called only once
        expected_calls = [expected_call1, expected_call2]
        self.assertEqual(m_signTransaction.call_args_list, expected_calls)
        # also make sure the transaction dict is passing the validation
        # e.g. scientific notation 1e+17 is not accepted
        transaction_dict = m_signTransaction.call_args[0][0]
        assert_valid_fields(transaction_dict)
        # even though below values are equal
        self.assertTrue(transaction_dict['value'] == 0.1 * 1e18 == 1e17)
        # this is not accepted by `assert_valid_fields()`
        transaction_dict['value'] = 0.1 * 1e18
        with self.assertRaises(TypeError):
            assert_valid_fields(transaction_dict)
        # because float are not accepted
        self.assertEqual(type(transaction_dict['value']), float)

    def test_get_last_bets_transactions(self):
        """
        Verifies `get_last_bets_transactions()` performs the correct calls to
        underlying libraries, and verifies it handle their inputs correctly.
        """
        # simplified contract ABI
        contract_abi = [self.player_roll_dice_abi]
        # we want this unit test to still pass even if the Etheroll contract
        # address changes, so let's make it explicit
        contract_address = '0x048717Ea892F23Fb0126F00640e2b18072efd9D2'
        with mock.patch('etherscan.contracts.Contract.get_abi') as m_get_abi:
            m_get_abi.return_value = json.dumps(contract_abi)
            etheroll = Etheroll(contract_address=contract_address)

        # simplified version of `get_transaction_page()` return
        transactions = [
            {
                'blockHash': (
                        '0xd0e85045f06f2ac6419ce6a3edf51b0'
                        '3c67fc78ffe92594e29f4aeddeab67476'),
                'blockNumber': '5442078',
                # this transactions has the correct `from` address, but is not
                'from': '0x46044beaa1e985c67767e04de58181de5daaa00f',
                'hash': (
                        '0x6191c2f77e4dee0d9677c77613c2e8d'
                        '2785d43bc6082bf5b5b67cbd9e0eb2b54'),
                'input': '0x',
                'timeStamp': '1523753147',
                # sent `to` Etheroll contract address
                'to': '0x00e695c5d7b2f6a2e83e1b34db1390f89e2741ef',
                'value': '197996051600000005'
            },
            {
                'blockHash': (
                        '0x9814be792821e5d98b639e211fbe8f4'
                        'b1930b8f12fa28aeb9ecf4737e749626b'),
                'blockNumber': '5394094',
                'from': '0x46044beaa1e985c67767e04de58181de5daaa00f',
                'hash': (
                        '0x0440f1013a5eafd88f16be6b5612b6e'
                        '051a4eb1b0b91a160c680295e7fab5bfe'),
                'input': (
                        '0xdc6dd152000000000000000000000000000'
                        '000000000000000000000000000000000000e'),
                'timeStamp': '0x5ac80f92',
                'to': '0x048717ea892f23fb0126f00640e2b18072efd9d2',
                'value': '500000000000000000',
            },
            {
                'blockHash': (
                        '0xbf5776b12ee403b3a99c03d560cd709'
                        'a389f8342b03133c4eb9ae8fa58b5acfe'),
                'blockNumber': '5394085',
                'from': '0x46044beaa1e985c67767e04de58181de5daaa00f',
                'hash': (
                        '0x72def66d60ecc85268c714e71929953'
                        'ef94fd4fae37632a5f56ea49bee44dd59'),
                'input': (
                        '0xdc6dd152000000000000000000000000000'
                        '0000000000000000000000000000000000002'),
                'timeStamp': '0x5ac80f0e',
                'to': '0x048717ea892f23fb0126f00640e2b18072efd9d2',
                'value': '450000000000000000',
            },
        ]
        address = '0x46044beaa1e985c67767e04de58181de5daaa00f'
        page = 1
        offset = 3
        with mock.patch('etherscan.accounts.Account.get_transaction_page') \
                as m_get_transaction_page:
            m_get_transaction_page.return_value = transactions
            bets = etheroll.get_last_bets_transactions(
                address=address, page=page, offset=offset)
        # we should have only two bets returns as the first transaction
        # was not made to the Etheroll contract
        self.assertEqual(
            bets,
            [
                {
                    'bet_size_ether': 0.5,
                    'roll_under': 14,
                    'block_number': '5394094',
                    'timestamp': '0x5ac80f92',
                    'datetime': datetime(2018, 4, 7, 0, 23, 46),
                    'transaction_hash': (
                        '0x0440f1013a5eafd88f16be6b5612b6e'
                        '051a4eb1b0b91a160c680295e7fab5bfe'),
                },
                {
                    'bet_size_ether': 0.45,
                    'roll_under': 2,
                    'block_number': '5394085',
                    'timestamp': '0x5ac80f0e',
                    'datetime': datetime(2018, 4, 7, 0, 21, 34),
                    'transaction_hash': (
                        '0x72def66d60ecc85268c714e71929953'
                        'ef94fd4fae37632a5f56ea49bee44dd59'),
                },
            ]
        )
        # makes sure underlying library was used properly
        expected_call = mock.call(
            internal=False, offset=3, page=1, sort='desc')
        # the method should have been called only once
        expected_calls = [expected_call]
        self.assertEqual(m_get_transaction_page.call_args_list, expected_calls)

    def test_get_logs_url(self):
        with \
                mock.patch(
                'etherscan.contracts.Contract.get_abi') as m_get_abi, \
                mock.patch(
                'pyetheroll.etheroll.get_etherscan_api_key') \
                as m_get_etherscan_api_key:
            m_get_abi.return_value = '[]'
            m_get_etherscan_api_key.return_value = 'apikey'
            etheroll = Etheroll()
        address = '0x048717Ea892F23Fb0126F00640e2b18072efd9D2'
        from_block = 1
        logs_url = etheroll.get_logs_url(
            address=address, from_block=from_block)
        self.assertEqual(
            logs_url,
            (
                'https://api.etherscan.io/api?'
                'module=logs&action=getLogs&apikey=apikey'
                '&address=0x048717Ea892F23Fb0126F00640e2b18072efd9D2&'
                'fromBlock=1&toBlock=latest&'
            )
        )
        # makes sure Testnet is also supported
        with \
                mock.patch(
                'etherscan.contracts.Contract.get_abi') as m_get_abi, \
                mock.patch(
                'pyetheroll.etheroll.get_etherscan_api_key') \
                as m_get_etherscan_api_key:
            m_get_abi.return_value = '[]'
            m_get_etherscan_api_key.return_value = 'apikey'
            etheroll = Etheroll(chain_id=ChainID.ROPSTEN)
        address = '0x048717Ea892F23Fb0126F00640e2b18072efd9D2'
        from_block = 1
        logs_url = etheroll.get_logs_url(
            address=address, from_block=from_block)
        self.assertEqual(
            logs_url,
            (
                'https://api-ropsten.etherscan.io/api?'
                'module=logs&action=getLogs&apikey=apikey&'
                'address=0x048717Ea892F23Fb0126F00640e2b18072efd9D2&'
                'fromBlock=1&toBlock=latest&'
            )
        )

    def test_get_logs_url_topics(self):
        """
        More advanced tests for topic support.
        """
        with \
                mock.patch(
                'etherscan.contracts.Contract.get_abi') as m_get_abi, \
                mock.patch(
                'pyetheroll.etheroll.get_etherscan_api_key') \
                as m_get_etherscan_api_key:
            m_get_abi.return_value = '[]'
            m_get_etherscan_api_key.return_value = 'apikey'
            etheroll = Etheroll()
        address = '0x048717Ea892F23Fb0126F00640e2b18072efd9D2'
        from_block = 1
        logs_url = etheroll.get_logs_url(
            address=address, from_block=from_block)
        self.assertEqual(
            logs_url,
            (
                'https://api.etherscan.io/api?'
                'module=logs&action=getLogs&apikey=apikey'
                '&address=0x048717Ea892F23Fb0126F00640e2b18072efd9D2&'
                'fromBlock=1&toBlock=latest&'
            )
        )
        # makes sure Testnet is also supported
        with \
                mock.patch(
                'etherscan.contracts.Contract.get_abi') as m_get_abi, \
                mock.patch(
                'pyetheroll.etheroll.get_etherscan_api_key') \
                as m_get_etherscan_api_key:
            m_get_abi.return_value = '[]'
            m_get_etherscan_api_key.return_value = 'apikey'
            etheroll = Etheroll(chain_id=ChainID.ROPSTEN)
        address = '0x048717Ea892F23Fb0126F00640e2b18072efd9D2'
        from_block = 1
        topic0 = 'topic0'
        topic1 = 'topic1'
        topic2 = 'topic2'
        topic3 = 'topic3'
        topic_opr = {
            'topic0_1_opr': 'and',
            'topic1_2_opr': 'or',
            'topic2_3_opr': 'and',
            'topic0_2_opr': 'or',
        }
        logs_url = etheroll.get_logs_url(
            address=address, from_block=from_block,
            topic0=topic0, topic1=topic1, topic2=topic2, topic3=topic3,
            topic_opr=topic_opr)
        self.assertEqual(
            logs_url,
            (
                'https://api-ropsten.etherscan.io/api?'
                'module=logs&action=getLogs&apikey=apikey&'
                'address=0x048717Ea892F23Fb0126F00640e2b18072efd9D2&'
                'fromBlock=1&toBlock=latest&'
                'topic0=topic0&topic1=topic1&topic2=topic2&topic3=topic3&'
                'topic0_1_opr=and&topic1_2_opr=or&topic2_3_opr=and&'
                'topic0_2_opr=or&'
            )
        )

    def test_get_log_bet_events(self):
        """
        Makes sure the Etherscan getLogs API is called correctly for LogBet.
        """
        # simplified contract ABI
        contract_abi = [self.log_bet_abi]
        with \
                mock.patch(
                'etherscan.contracts.Contract.get_abi') as m_get_abi, \
                mock.patch(
                'pyetheroll.etheroll.get_etherscan_api_key') \
                as m_get_etherscan_api_key:
            m_get_abi.return_value = json.dumps(contract_abi)
            m_get_etherscan_api_key.return_value = 'apikey'
            etheroll = Etheroll()
        player_address = '0x46044beaa1e985c67767e04de58181de5daaa00f'
        from_block = 5394085
        to_block = 5442078
        with mock.patch('requests.get') as m_get:
            etheroll.get_log_bet_events(
                player_address, from_block, to_block)
        expected_call = mock.call(
            'https://api.etherscan.io/api?module=logs&action=getLogs'
            '&apikey=apikey'
            '&address=0x048717Ea892F23Fb0126F00640e2b18072efd9D2'
            '&fromBlock=5394085&toBlock=5442078&topic0=0x'
            '56b3f1a6cd856076d6f8adbf8170c43a0b0f532fc5696a2699a0e0cabc704163'
            '&topic2=0x'
            '00000000000000000000000046044beaa1e985c67767e04de58181de5daaa00f'
            '&topic0_2_opr=and&')
        expected_calls = [expected_call]
        self.assertEqual(m_get.call_args_list, expected_calls)

    def test_get_log_result_events(self):
        """
        Makes sure the Etherscan getLogs API is called correctly for LogBet.
        """
        # simplified contract ABI
        contract_abi = [self.log_result_abi]
        with \
                mock.patch(
                'etherscan.contracts.Contract.get_abi') as m_get_abi, \
                mock.patch(
                'pyetheroll.etheroll.get_etherscan_api_key') \
                as m_get_etherscan_api_key:
            m_get_abi.return_value = json.dumps(contract_abi)
            m_get_etherscan_api_key.return_value = 'apikey'
            etheroll = Etheroll()
        player_address = '0x46044beaa1e985c67767e04de58181de5daaa00f'
        from_block = 5394085
        to_block = 5442078
        with mock.patch('requests.get') as m_get:
            etheroll.get_log_result_events(
                player_address, from_block, to_block)
        expected_call = mock.call(
            'https://api.etherscan.io/api?module=logs&action=getLogs'
            '&apikey=apikey'
            '&address=0x048717Ea892F23Fb0126F00640e2b18072efd9D2'
            '&fromBlock=5394085&toBlock=5442078'
            '&topic0=0x'
            '8dd0b145385d04711e29558ceab40b456976a2b9a7d648cc1bcd416161bf97b9'
            '&topic3=0x'
            '00000000000000000000000046044beaa1e985c67767e04de58181de5daaa00f'
            '&topic0_3_opr=and&'
        )
        expected_calls = [expected_call]
        self.assertEqual(m_get.call_args_list, expected_calls)

    def test_get_bets_logs(self):
        """
        Verifies `get_bets_logs()` can retrieve bet info out from the logs.
        """
        # simplified contract ABI
        contract_abi = [self.log_bet_abi]
        # simplified (a bit) for tests
        get_log_bet_events = [
         {
          'address': '0x048717ea892f23fb0126f00640e2b18072efd9d2',
          'blockNumber': '0x524e94',
          'data': (
            '0x0000000000000000000000000000000000000000000000026402ac5922ba000'
            '0000000000000000000000000000000000000000000000000063eb89da4ed0000'
            '00000000000000000000000000000000000000000000000000000000000000020'
            '000000000000000000000000000000000000000000000000000000000002aea'),
          'logIndex': '0x2a',
          'timeStamp': '0x5ac80e02',
          'topics': [
           '56b3f1a6cd856076d6f8adbf8170c43a0b0f532fc5696a2699a0e0cabc704163',
           '15e007148ec621d996c886de0f2b88a03af083aa819e851a51133dc17b6e0e5b',
           '00000000000000000000000046044beaa1e985c67767e04de58181de5daaa00f',
           '0000000000000000000000000000000000000000000000026a4164f6c7a70000',
          ],
          'transactionHash': (
           '0xf363906a9278c4dd300c50a3c9a2790'
           '0bb85df60596c49f7833c232f2944d1cb'),
         },
         {
          'address': '0x048717ea892f23fb0126f00640e2b18072efd9d2',
          'blockNumber': '0x524eae',
          'data': (
           '0x0000000000000000000000000000000000000000000000002de748a1024ac4eb'
           '00000000000000000000000000000000000000000000000006f05b59d3b2000000'
           '0000000000000000000000000000000000000000000000000000000000000e0000'
           '000000000000000000000000000000000000000000000000000000002af9'),
          'logIndex': '0x1c',
          'timeStamp': '0x5ac80f92',
          'topics': [
           '56b3f1a6cd856076d6f8adbf8170c43a0b0f532fc5696a2699a0e0cabc704163',
           'c2997a1bad35841b2c30ca95eea9cb08c7b101bc14d5aa8b1b8a0facea793e05',
           '00000000000000000000000046044beaa1e985c67767e04de58181de5daaa00f',
           '00000000000000000000000000000000000000000000000034d7a3fad5fcc4eb',
          ],
          'transactionHash': (
           '0x0440f1013a5eafd88f16be6b5612b6e'
           '051a4eb1b0b91a160c680295e7fab5bfe'),
         }
        ]
        with mock.patch('etherscan.contracts.Contract.get_abi') \
                as m_get_abi:
            m_get_abi.return_value = json.dumps(contract_abi)
            etheroll = Etheroll()
        address = '0x46044beAa1E985C67767E04dE58181de5DAAA00F'
        from_block = 5394067
        to_block = 5394095
        with mock.patch('pyetheroll.etheroll.Etheroll.get_log_bet_events') \
                as m_get_log_bet_events:
            m_get_log_bet_events.return_value = get_log_bet_events
            logs = etheroll.get_bets_logs(address, from_block, to_block)
        expected_logs = [
            {
                'bet_id': (
                    '15e007148ec621d996c886de0f2b88a0'
                    '3af083aa819e851a51133dc17b6e0e5b'),
                'bet_value_ether': 0.45,
                'profit_value_ether': 44.1,
                'reward_value_ether': 44.55,
                'roll_under': 2,
                'timestamp': '0x5ac80e02',
                'datetime': datetime(2018, 4, 7, 0, 17, 6),
                'transaction_hash': (
                    '0xf363906a9278c4dd300c50a3c9a2790'
                    '0bb85df60596c49f7833c232f2944d1cb'),
            },
            {
                'bet_id': (
                    'c2997a1bad35841b2c30ca95eea9cb08'
                    'c7b101bc14d5aa8b1b8a0facea793e05'),
                'bet_value_ether': 0.5,
                'profit_value_ether': 3.31,
                'reward_value_ether': 3.81,
                'roll_under': 14,
                'timestamp': '0x5ac80f92',
                'datetime': datetime(2018, 4, 7, 0, 23, 46),
                'transaction_hash': (
                    '0x0440f1013a5eafd88f16be6b5612b6e'
                    '051a4eb1b0b91a160c680295e7fab5bfe'),
            },
        ]
        self.assertEqual(logs, expected_logs)

    def test_get_bet_results_logs(self):
        """
        Checks `get_bet_results_logs()` can retrieve bet info from the logs.
        """
        # simplified contract ABI
        contract_abi = [self.log_result_abi]
        # simplified (a bit) for tests
        get_log_result_events = [
         {
          'address': '0x048717ea892f23fb0126f00640e2b18072efd9d2',
          'blockNumber': '0x524e97',
          'data': (
           '0x0000000000000000000000000000000000000000000000000000000000000002'
           '000000000000000000000000000000000000000000000000000000000000005600'
           '0000000000000000000000000000000000000000000000063eb89da4ed00000000'
           '000000000000000000000000000000000000000000000000000000000000000000'
           '00000000000000000000000000000000000000000000000000000000a000000000'
           '0000000000000000000000000000000000000000000000000000002212209856f6'
           '9aa7983168979d4b0c41978807202b14cc7ffc6e31a17d443f017fcdff00000000'
           '0000000000000000000000000000000000000000000000000000'),
          'logIndex': '0xc',
          'timeStamp': '0x5ac80e33',
          'topics': [
           '8dd0b145385d04711e29558ceab40b456976a2b9a7d648cc1bcd416161bf97b9',
           '000000000000000000000000000000000000000000000000000000000004511d',
           '15e007148ec621d996c886de0f2b88a03af083aa819e851a51133dc17b6e0e5b',
           '00000000000000000000000046044beaa1e985c67767e04de58181de5daaa00f',
          ],
          'transactionHash': (
           '0x3505de688dc20748eb5f6b3efd6e6d3'
           '66ea7f0737b4ab17035c6b60ab4329f2a'),
         },
         {
          'address': '0x048717ea892f23fb0126f00640e2b18072efd9d2',
          'blockNumber': '0x524eaa',
          'data': (
           '0x0000000000000000000000000000000000000000000000000000000000000002'
           '000000000000000000000000000000000000000000000000000000000000000400'
           '0000000000000000000000000000000000000000000000063eb89da4ed00000000'
           '000000000000000000000000000000000000000000000000000000000000000000'
           '00000000000000000000000000000000000000000000000000000000a000000000'
           '0000000000000000000000000000000000000000000000000000002212205a95b8'
           '96176efeb912d5d4937c541ee511092aced04eb764eab4e9629c613c3c00000000'
           '0000000000000000000000000000000000000000000000000000'),
          'logIndex': '0x4f',
          'timeStamp': '0x5ac80f38',
          'topics': [
           '8dd0b145385d04711e29558ceab40b456976a2b9a7d648cc1bcd416161bf97b9',
           '000000000000000000000000000000000000000000000000000000000004512b',
           'f2fb7902894213d47c482fb155cafd9677286d930fba1a1434265be0dbe80e66',
           '00000000000000000000000046044beaa1e985c67767e04de58181de5daaa00f',
          ],
          'transactionHash': (
           '0x6123e2a19f649df79c6cf2dfbe99811'
           '530d0770ade8e2c71488b8eb881ad20e9'),
         }
        ]
        with mock.patch('etherscan.contracts.Contract.get_abi') \
                as m_get_abi:
            m_get_abi.return_value = json.dumps(contract_abi)
            etheroll = Etheroll()
        address = '0x46044beAa1E985C67767E04dE58181de5DAAA00F'
        from_block = 5394067
        to_block = 5394095
        with mock.patch('pyetheroll.etheroll.Etheroll.get_log_result_events') \
                as m_get_log_result_events:
            m_get_log_result_events.return_value = get_log_result_events
            results = etheroll.get_bet_results_logs(
                address, from_block, to_block)
        expected_results = [
            {
                'bet_id': (
                    '15e007148ec621d996c886de0f2b88a0'
                    '3af083aa819e851a51133dc17b6e0e5b'),
                'bet_value_ether': 0.45,
                'dice_result': 86,
                'roll_under': 2,
                'timestamp': '0x5ac80e33',
                'datetime': datetime(2018, 4, 7, 0, 17, 55),
                'transaction_hash': (
                    '0x3505de688dc20748eb5f6b3efd6e6d3'
                    '66ea7f0737b4ab17035c6b60ab4329f2a'),
            },
            {
                'bet_id': (
                    'f2fb7902894213d47c482fb155cafd96'
                    '77286d930fba1a1434265be0dbe80e66'),
                'bet_value_ether': 0.45,
                'dice_result': 4,
                'roll_under': 2,
                'timestamp': '0x5ac80f38',
                'datetime': datetime(2018, 4, 7, 0, 22, 16),
                'transaction_hash': (
                    '0x6123e2a19f649df79c6cf2dfbe99811'
                    '530d0770ade8e2c71488b8eb881ad20e9'),
            },
        ]
        self.assertEqual(results, expected_results)

    def test_get_last_bets_blocks(self):
        transactions = [
            {
                'blockHash': (
                    '0x9814be792821e5d98b639e211fbe8f4'
                    'b1930b8f12fa28aeb9ecf4737e749626b'),
                'blockNumber': '5394094',
                'confirmations': '81252',
                'contractAddress': '',
                'cumulativeGasUsed': '2619957',
                'from': '0x46044beaa1e985c67767e04de58181de5daaa00f',
                'gas': '250000',
                'gasPrice': '2000000000',
                'gasUsed': '177773',
                'hash': (
                    '0x0440f1013a5eafd88f16be6b5612b6e'
                    '051a4eb1b0b91a160c680295e7fab5bfe'),
                'input': (
                    '0xdc6dd152000000000000000000000000000'
                    '000000000000000000000000000000000000e'),
                'isError': '0',
                'nonce': '9485',
                'timeStamp': '1523060626',
                'to': '0x048717ea892f23fb0126f00640e2b18072efd9d2',
                'transactionIndex': '42',
                'txreceipt_status': '1',
                'value': '500000000000000000'},
            {
                'blockHash': (
                    '0x0f74b07fe04dd447b2a48c7aee6998a'
                    'c97cf7c12b4fd46ef781f00652abe4642'),
                'blockNumber': '5394068',
                'confirmations': '81278',
                'contractAddress': '',
                'cumulativeGasUsed': '4388802',
                'from': '0x46044beaa1e985c67767e04de58181de5daaa00f',
                'gas': '250000',
                'gasPrice': '2200000000',
                'gasUsed': '177773',
                'hash': (
                    '0xf363906a9278c4dd300c50a3c9a2790'
                    '0bb85df60596c49f7833c232f2944d1cb'),
                'input': (
                    '0xdc6dd152000000000000000000000000000'
                    '0000000000000000000000000000000000002'),
                'isError': '0',
                'nonce': '9481',
                'timeStamp': '1523060226',
                'to': '0x048717ea892f23fb0126f00640e2b18072efd9d2',
                'transactionIndex': '150',
                'txreceipt_status': '1',
                'value': '450000000000000000'
            }
        ]
        contract_address = '0x048717Ea892F23Fb0126F00640e2b18072efd9D2'
        contract_abi = []
        address = '0x46044beAa1E985C67767E04dE58181de5DAAA00F'
        with mock.patch('etherscan.contracts.Contract.get_abi') as m_get_abi:
            m_get_abi.return_value = json.dumps(contract_abi)
            etheroll = Etheroll(contract_address=contract_address)
        with mock.patch(
                'pyetheroll.etheroll.Etheroll.get_player_roll_dice_tx') \
                as m_get_player_roll_dice_tx:
            m_get_player_roll_dice_tx.return_value = transactions
            last_bets_blocks = etheroll.get_last_bets_blocks(address)
        self.assertEqual(
            last_bets_blocks, {'from_block': 5394067, 'to_block': 5394194})

    def test_merge_logs(self):
        bet_logs = self.bet_logs
        bet_results_logs = self.bet_results_logs
        expected_merged_logs = [
            {'bet_log': bet_logs[0], 'bet_result': bet_results_logs[0]},
            {'bet_log': bet_logs[1], 'bet_result': bet_results_logs[1]},
            # not yet resolved (no `LogResult`)
            {'bet_log': bet_logs[2], 'bet_result': None},
        ]
        merged_logs = Etheroll.merge_logs(bet_logs, bet_results_logs)
        self.assertEqual(merged_logs, expected_merged_logs)

    def test_get_merged_logs(self):
        """
        Checking we can merge both `LogBet` and `LogResult` events.
        We have 3 `LogBet` here and only 2 matching `LogResult` since the
        last bet is not yet resolved.
        """
        contract_abi = [
            self.log_bet_abi, self.log_result_abi, self.player_roll_dice_abi]
        contract_address = '0x048717Ea892F23Fb0126F00640e2b18072efd9D2'
        last_bets_blocks = {'from_block': 5394067, 'to_block': 5394194}
        bet_logs = self.bet_logs
        bet_results_logs = self.bet_results_logs
        with mock.patch('etherscan.contracts.Contract.get_abi') as m_get_abi:
            m_get_abi.return_value = json.dumps(contract_abi)
            etheroll = Etheroll(contract_address=contract_address)
        address = '0x46044beAa1E985C67767E04dE58181de5DAAA00F'
        with \
                mock.patch(
                'pyetheroll.etheroll.Etheroll.get_last_bets_blocks') \
                as m_get_last_bets_blocks,\
                mock.patch('pyetheroll.etheroll.Etheroll.get_bets_logs') \
                as m_get_bets_logs,\
                mock.patch(
                'pyetheroll.etheroll.Etheroll.get_bet_results_logs') \
                as m_get_bet_results_logs:
            m_get_last_bets_blocks.return_value = last_bets_blocks
            m_get_bets_logs.return_value = bet_logs
            m_get_bet_results_logs.return_value = bet_results_logs
            merged_logs = etheroll.get_merged_logs(address)
        expected_merged_logs = [
            {'bet_log': bet_logs[0], 'bet_result': bet_results_logs[0]},
            {'bet_log': bet_logs[1], 'bet_result': bet_results_logs[1]},
            # not yet resolved (no `LogResult`)
            {'bet_log': bet_logs[2], 'bet_result': None},
        ]
        self.assertEqual(merged_logs, expected_merged_logs)

    def test_get_merged_logs_empty_tx(self):
        """
        Empty transaction history should not crash the application, refs:
        https://github.com/AndreMiras/EtherollApp/issues/67
        """
        contract_abi = [self.player_roll_dice_abi]
        contract_address = '0x048717Ea892F23Fb0126F00640e2b18072efd9D2'
        with mock.patch('etherscan.contracts.Contract.get_abi') as m_get_abi:
            m_get_abi.return_value = json.dumps(contract_abi)
            etheroll = Etheroll(contract_address=contract_address)
        address = '0x7aBE7DdD94DB8feb6BE426e53cA090b94F15d73E'
        with mock.patch('requests.sessions.Session.get') as m_get:
            # this is what etherscan.io would return on empty tx history
            m_get.return_value.status_code = 200
            m_get.return_value.text = (
                '{"status":"0","message":"No transactions found","result":[]}')
            m_get.return_value.json.return_value = json.loads(
                m_get.return_value.text)
            # the library should not crash but return an empty list
            merged_logs = etheroll.get_merged_logs(address)
        self.assertEqual(merged_logs, [])

    def test_get_merged_logs_no_matching_tx(self):
        """
        Makes sure no matching transactions doesn't crash the app, refs:
        https://github.com/AndreMiras/EtherollApp/issues/87
        """
        contract_abi = [self.player_roll_dice_abi]
        contract_address = '0xe12c6dEb59f37011d2D9FdeC77A6f1A8f3B8B1e8'
        with mock.patch('etherscan.contracts.Contract.get_abi') as m_get_abi:
            m_get_abi.return_value = json.dumps(contract_abi)
            etheroll = Etheroll(
                chain_id=ChainID.ROPSTEN, contract_address=contract_address)
        address = '0x4F4b934af9Bb3656daDD4c7C7d8dD348AC4f787A'
        with mock.patch('requests.sessions.Session.get') as m_get:
            # there's a transaction, but it's not matching the expected ones
            m_get.return_value.status_code = 200
            m_get.return_value.text = (
                '{"status":"1","message":"OK","result":[{"blockNumber":"306526'
                '5","timeStamp":"1524087170","hash":"0x93bf3cff2c334d15e96b07e'
                '362240e09255b9e8728d855741e5970110d5a8a6d","nonce":"13","bloc'
                'kHash":"0x9625ece7c2bbca90c15628a970d962b8d0f1e57221e1f3ded6c'
                '24f25df834d62","transactionIndex":"51","from":"0x66d4bacfe61d'
                'f23be813089a7a6d1a749a5c936a","to":"0x4f4b934af9bb3656dadd4c7'
                'c7d8dd348ac4f787a","value":"2000000000000000000","gas":"21000'
                '","gasPrice":"1000000000","isError":"0","txreceipt_status":"1'
                '","input":"0x","contractAddress":"","cumulativeGasUsed":"1871'
                '849","gasUsed":"21000","confirmations":"161389"}]}')
            m_get.return_value.json.return_value = json.loads(
                m_get.return_value.text)
            merged_logs = etheroll.get_merged_logs(address)
        # merged logs should simply be empty
        self.assertEqual(merged_logs, [])

    def test_get_balance(self):
        """
        Makes sure proper Etherscan API call is made.
        https://github.com/AndreMiras/EtherollApp/issues/67
        """
        contract_abi = []
        contract_address = '0x048717Ea892F23Fb0126F00640e2b18072efd9D2'
        with mock.patch('etherscan.contracts.Contract.get_abi') as m_get_abi, \
                mock.patch(
                'pyetheroll.etheroll.get_etherscan_api_key') \
                as m_get_etherscan_api_key:
            m_get_abi.return_value = json.dumps(contract_abi)
            m_get_etherscan_api_key.return_value = 'apikey'
            etheroll = Etheroll(contract_address=contract_address)
        address = '0xAb5801a7D398351b8bE11C439e05C5B3259aeC9B'
        with mock.patch('requests.sessions.Session.get') as m_get:
            # this is what etherscan.io would return on empty tx history
            m_get.return_value.status_code = 200
            m_get.return_value.text = (
                '{"status":"1","message":"OK",'
                '"result":"365003278106457867877843"}')
            m_get.return_value.json.return_value = json.loads(
                m_get.return_value.text)
            # but this crashes the library with an exit
            balance = etheroll.get_balance(address)
        # makes sure the Etherscan API was called and parsed properly
        expected_url = (
            'https://api.etherscan.io/api?module=account'
            '&address=0xAb5801a7D398351b8bE11C439e05C5B3259aeC9B'
            '&tag=latest&apikey=apikey'
            '&action=balance')
        expected_call = mock.call(expected_url)
        expected_calls = [expected_call]
        self.assertEqual(m_get.call_args_list, expected_calls)
        self.assertEqual(balance, 365003.28)
