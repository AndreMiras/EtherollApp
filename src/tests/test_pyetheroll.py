import json
import os
import shutil
import unittest
from tempfile import mkdtemp
from unittest import mock

from ethereum.tools.keys import PBKDF2_CONSTANTS
from hexbytes.main import HexBytes
from pyethapp.accounts import Account
from web3.utils.datastructures import AttributeDict

from pyetheroll import (ChainID, Etheroll, TransactionDebugger,
                        decode_contract_call)


class TestUtils(unittest.TestCase):

    def test_decode_method_log1(self):
        """
        Trying to decode a `Log1()` event call.
        """
        # simplified contract ABI for tests
        contract_abi = [
            {'inputs': [], 'type': 'constructor', 'payable': False},
            {'payable': False, 'type': 'fallback'},
            {'inputs': [
                {'indexed': False, 'type': 'address', 'name': 'sender'},
                {'indexed': False, 'type': 'bytes32', 'name': 'cid'},
                {'indexed': False, 'type': 'uint256', 'name': 'timestamp'},
                {'indexed': False, 'type': 'string', 'name': 'datasource'},
                {'indexed': False, 'type': 'string', 'name': 'arg'},
                {'indexed': False, 'type': 'uint256', 'name': 'gaslimit'},
                {'indexed': False, 'type': 'bytes1', 'name': 'proofType'},
                {'indexed': False, 'type': 'uint256', 'name': 'gasPrice'}],
                'type': 'event', 'name': 'Log1', 'anonymous': False},
            {'inputs': [
                {'indexed': False, 'type': 'address', 'name': 'sender'},
                {'indexed': False, 'type': 'bytes32', 'name': 'cid'},
                {'indexed': False, 'type': 'uint256', 'name': 'timestamp'},
                {'indexed': False, 'type': 'string', 'name': 'datasource'},
                {'indexed': False, 'type': 'string', 'name': 'arg1'},
                {'indexed': False, 'type': 'string', 'name': 'arg2'},
                {'indexed': False, 'type': 'uint256', 'name': 'gaslimit'},
                {'indexed': False, 'type': 'bytes1', 'name': 'proofType'},
                {'indexed': False, 'type': 'uint256', 'name': 'gasPrice'}],
                'type': 'event', 'name': 'Log2', 'anonymous': False},
            {'inputs': [
                {'indexed': False, 'type': 'address', 'name': 'sender'},
                {'indexed': False, 'type': 'bytes32', 'name': 'cid'},
                {'indexed': False, 'type': 'uint256', 'name': 'timestamp'},
                {'indexed': False, 'type': 'string', 'name': 'datasource'},
                {'indexed': False, 'type': 'bytes', 'name': 'args'},
                {'indexed': False, 'type': 'uint256', 'name': 'gaslimit'},
                {'indexed': False, 'type': 'bytes1', 'name': 'proofType'},
                {'indexed': False, 'type': 'uint256', 'name': 'gasPrice'}],
                'type': 'event', 'name': 'LogN', 'anonymous': False}]
        topics = [HexBytes(
            'b76d0edd90c6a07aa3ff7a222d7f5933e29c6acc660c059c97837f05c4ca1a84'
        )]
        log_data = (
            "0x"
            "000000000000000000000000fe8a5f3a7bb446e1cb4566717691cd3139289ed4"
            "b0230ab70b78e47050766089ea333f2ff7ad41c6f31e8bed8c2acfcb8e911841"
            "0000000000000000000000000000000000000000000000000000000000000000"
            "0000000000000000000000000000000000000000000000000000000000000100"
            "0000000000000000000000000000000000000000000000000000000000000140"
            "00000000000000000000000000000000000000000000000000000000000395f8"
            "1100000000000000000000000000000000000000000000000000000000000000"
            "00000000000000000000000000000000000000000000000000000004a817c800"
            "0000000000000000000000000000000000000000000000000000000000000006"
            "6e65737465640000000000000000000000000000000000000000000000000000"
            "00000000000000000000000000000000000000000000000000000000000001b4"
            "5b55524c5d205b276a736f6e2868747470733a2f2f6170692e72616e646f6d2e"
            "6f72672f6a736f6e2d7270632f312f696e766f6b65292e726573756c742e7261"
            "6e646f6d5b2273657269616c4e756d626572222c2264617461225d272c20275c"
            "6e7b226a736f6e727063223a22322e30222c226d6574686f64223a2267656e65"
            "726174655369676e6564496e746567657273222c22706172616d73223a7b2261"
            "70694b6579223a247b5b646563727970745d20424b6733544373376c6b7a4e72"
            "316b523670786a50434d32534f656a63466f6a55504d544f73426b432f343748"
            "485066317350326f78564c546a4e42752b736c523953675a797144746a564f56"
            "35597a67313269556b62756270304470636a434564654a54486e477743366744"
            "3732394755566f47766f393668757877526f5a6c436a594f3830725771325747"
            "596f522f4c433357616d704475767632426f3d7d2c226e223a312c226d696e22"
            "3a312c226d6178223a3130302c227265706c6163656d656e74223a747275652c"
            "2262617365223a3130247b5b6964656e746974795d20227d227d2c226964223a"
            "31247b5b6964656e746974795d20227d227d275d000000000000000000000000")
        decoded_method = TransactionDebugger.decode_method(
            contract_abi, topics, log_data)
        # TODO: simplify that arg call for unit testing
        self.assertEqual(
            decoded_method['call'],
            {'arg': bytes(
                '[URL] [\'json(https://api.random.org/json-rpc/1/invoke).resul'
                't.random["serialNumber","data"]\', \'\\n{"jsonrpc":"2.0","met'
                'hod":"generateSignedIntegers","params":{"apiKey":${[decrypt] '
                'BKg3TCs7lkzNr1kR6pxjPCM2SOejcFojUPMTOsBkC/47HHPf1sP2oxVLTjNBu'
                '+slR9SgZyqDtjVOV5Yzg12iUkbubp0DpcjCEdeJTHnGwC6gD729GUVoGvo96h'
                'uxwRoZlCjYO80rWq2WGYoR/LC3WampDuvv2Bo=},"n":1,"min":1,"max":1'
                '00,"replacement":true,"base":10${[identity] "}"},"id":1${[ide'
                'ntity] "}"}\']', "utf8"),
                'cid': (
                    b'\xb0#\n\xb7\x0bx\xe4pPv`\x89\xea3?/\xf7\xadA\xc6\xf3\x1e'
                    b'\x8b\xed\x8c*\xcf\xcb\x8e\x91\x18A'),
                'datasource': b'nested',
                'gasPrice': 20000000000,
                'gaslimit': 235000,
                'proofType': b'\x11',
                'sender': '0xfe8a5f3a7bb446e1cb4566717691cd3139289ed4',
                'timestamp': 0}
        )
        self.assertEqual(
          decoded_method['method_info']['definition'],
          'Log1(address,bytes32,uint256,string,string,uint256,bytes1,uint256)')
        self.assertEqual(
          decoded_method['method_info']['sha3'].hex(),
          '0xb76d0edd90c6a07aa3ff7a222d7f5933e29c6acc660c059c97837f05c4ca1a84')

    def test_decode_method_log_bet(self):
        """
        Trying to decode a `LogBet()` event call.
        """
        # simplified contract ABI
        contract_abi = [
          {
            'inputs': [{'type': 'uint256', 'name': 'newMaxProfitAsPercent'}],
            'constant': False, 'name': 'ownerSetMaxProfitAsPercentOfHouse',
            'outputs': [], 'stateMutability': 'nonpayable',
            'payable': False, 'type': 'function'},
          {
            'inputs': [], 'constant': True, 'name': 'treasury',
            'outputs': [{'type': 'address', 'name': ''}],
            'stateMutability': 'view', 'payable': False, 'type': 'function'},
          {
            'inputs': [], 'constant': True, 'name': 'totalWeiWagered',
            'outputs': [{'type': 'uint256', 'name': ''}],
            'stateMutability': 'view', 'payable': False, 'type': 'function'},
          {
            'inputs': [{'type': 'uint256', 'name': 'newMinimumBet'}],
            'constant': False, 'name': 'ownerSetMinBet',
            'outputs': [], 'stateMutability': 'nonpayable',
            'payable': False, 'type': 'function'
          },
          {
            'stateMutability': 'nonpayable',
            'inputs': [],
            'type': 'constructor',
            'payable': False
          },
          {'stateMutability': 'payable', 'payable': True, 'type': 'fallback'},
          {
            'inputs': [
               {'indexed': True, 'type': 'bytes32', 'name': 'BetID'},
               {'indexed': True, 'type': 'address', 'name': 'PlayerAddress'},
               {'indexed': True, 'type': 'uint256', 'name': 'RewardValue'},
               {'indexed': False, 'type': 'uint256', 'name': 'ProfitValue'},
               {'indexed': False, 'type': 'uint256', 'name': 'BetValue'},
               {'indexed': False, 'type': 'uint256', 'name': 'PlayerNumber'}],
            'type': 'event', 'name': 'LogBet', 'anonymous': False},
        ]
        topics = [
          HexBytes(
            '1cb5bfc4e69cbacf65c8e05bdb84d7a327bd6bb4c034ff82359aefd7443775c4'
          ),
          HexBytes(
            'b0230ab70b78e47050766089ea333f2ff7ad41c6f31e8bed8c2acfcb8e911841'
          ),
          HexBytes(
            '00000000000000000000000066d4bacfe61df23be813089a7a6d1a749a5c936a'
          ),
          HexBytes(
            '000000000000000000000000000000000000000000000000016a98b78c556c34'
          ),
        ]
        log_data = (
            '0x'
            '0000000000000000000000000000000000000000000000000007533f2ecb6c34'
            '000000000000000000000000000000000000000000000000016345785d8a0000'
            '0000000000000000000000000000000000000000000000000000000000000062')
        decoded_method = TransactionDebugger.decode_method(
            contract_abi, topics, log_data)
        self.assertEqual(
            decoded_method['call'],
            {'BetID': (
                b'\xb0#\n\xb7\x0bx\xe4pPv`\x89\xea3?/\xf7\xadA\xc6\xf3\x1e\x8b'
                b'\xed\x8c*\xcf\xcb\x8e\x91\x18A'),
                'BetValue': 100000000000000000,
                'PlayerAddress':
                    '0x66d4bacfe61df23be813089a7a6d1a749a5c936a',
                'PlayerNumber': 98,
                'ProfitValue': 2061855670103092,
                'RewardValue': 102061855670103092})
        self.assertEqual(
            decoded_method['method_info']['definition'],
            'LogBet(bytes32,address,uint256,uint256,uint256,uint256)')
        self.assertEqual(
          decoded_method['method_info']['sha3'].hex(),
          '0x1cb5bfc4e69cbacf65c8e05bdb84d7a327bd6bb4c034ff82359aefd7443775c4')

    def test_decode_contract_call(self):
        """
        Uses actual data from:
        https://etherscan.io/tx/
        0xf7b7196ca9eab6e4fb6e7bce81aeb25a4edf04330e57b3c15bece9d260577e2b
        In its simplified form for tests.
        """
        json_abi = (
            '[{"constant":false,"inputs":[{"name":"_to","type":"address"},{"na'
            'me":"_value","type":"uint256"}],"name":"transfer","outputs":[{"na'
            'me":"success","type":"bool"}],"payable":false,"type":"function"}]'
        )
        contract_abi = json.loads(json_abi)
        call_data = (
            'a9059cbb000000000000000000000000'
            '67fa2c06c9c6d4332f330e14a66bdf18'
            '73ef3d2b000000000000000000000000'
            '0000000000000000000000000de0b6b3'
            'a7640000')
        method_name, args = decode_contract_call(contract_abi, call_data)
        self.assertEqual(method_name, 'transfer')
        self.assertEqual(
            args,
            ['0x67fa2c06c9c6d4332f330e14a66bdf1873ef3d2b', 1000000000000000000]
        )


class TestTransactionDebugger(unittest.TestCase):

    def m_get_abi(self, instance):
        """
        Mocked version of `web3.contract.Contract.get_abi()`.
        """
        # retrieves the original contract address
        address = instance.url_dict[instance.ADDRESS]
        abi1 = (
            '[{"anonymous":false,"inputs":[{"indexed":false,"name":"sender","t'
            'ype":"address"},{"indexed":false,"name":"cid","type":"bytes32"},{'
            '"indexed":false,"name":"timestamp","type":"uint256"},{"indexed":f'
            'alse,"name":"datasource","type":"string"},{"indexed":false,"name"'
            ':"arg","type":"string"},{"indexed":false,"name":"gaslimit","type"'
            ':"uint256"},{"indexed":false,"name":"proofType","type":"bytes1"},'
            '{"indexed":false,"name":"gasPrice","type":"uint256"}],"name":"Log'
            '1","type":"event"}]')
        abi2 = (
            '[{"anonymous":false,"inputs":[{"indexed":true,"name":"BetID","typ'
            'e":"bytes32"},{"indexed":true,"name":"PlayerAddress","type":"addr'
            'ess"},{"indexed":true,"name":"RewardValue","type":"uint256"},{"in'
            'dexed":false,"name":"ProfitValue","type":"uint256"},{"indexed":fa'
            'lse,"name":"BetValue","type":"uint256"},{"indexed":false,"name":"'
            'PlayerNumber","type":"uint256"}],"name":"LogBet","type":"event"}]'
        )
        if address.lower() == '0xcbf1735aad8c4b337903cd44b419efe6538aab40':
            return abi1
        elif address.lower() == '0xfe8a5f3a7bb446e1cb4566717691cd3139289ed4':
            return abi2
        return None

    def test_decode_transaction_logs(self):
        """
        Mocking `web3.eth.Eth.getTransactionReceipt()` response and verifies
        decoding transaction works as expected.
        """
        mocked_logs = [
          AttributeDict({
            'address': '0xCBf1735Aad8C4B337903cD44b419eFE6538aaB40',
            'topics': [
                HexBytes(
                    'b76d0edd90c6a07aa3ff7a222d7f5933'
                    'e29c6acc660c059c97837f05c4ca1a84'
                )
            ],
            'data':
            '000000000000000000000000fe8a5f3a7bb446e1cb4566717691cd3139289ed4'
            'b0230ab70b78e47050766089ea333f2ff7ad41c6f31e8bed8c2acfcb8e911841'
            '0000000000000000000000000000000000000000000000000000000000000000'
            '0000000000000000000000000000000000000000000000000000000000000100'
            '0000000000000000000000000000000000000000000000000000000000000140'
            '00000000000000000000000000000000000000000000000000000000000395f8'
            '1100000000000000000000000000000000000000000000000000000000000000'
            '00000000000000000000000000000000000000000000000000000004a817c800'
            '0000000000000000000000000000000000000000000000000000000000000006'
            '6e65737465640000000000000000000000000000000000000000000000000000'
            '00000000000000000000000000000000000000000000000000000000000001b4'
            '5b55524c5d205b276a736f6e2868747470733a2f2f6170692e72616e646f6d2e'
            '6f72672f6a736f6e2d7270632f312f696e766f6b65292e726573756c742e7261'
            '6e646f6d5b2273657269616c4e756d626572222c2264617461225d272c20275c'
            '6e7b226a736f6e727063223a22322e30222c226d6574686f64223a2267656e65'
            '726174655369676e6564496e746567657273222c22706172616d73223a7b2261'
            '70694b6579223a247b5b646563727970745d20424b6733544373376c6b7a4e72'
            '316b523670786a50434d32534f656a63466f6a55504d544f73426b432f343748'
            '485066317350326f78564c546a4e42752b736c523953675a797144746a564f56'
            '35597a67313269556b62756270304470636a434564654a54486e477743366744'
            '3732394755566f47766f393668757877526f5a6c436a594f3830725771325747'
            '596f522f4c433357616d704475767632426f3d7d2c226e223a312c226d696e22'
            '3a312c226d6178223a3130302c227265706c6163656d656e74223a747275652c'
            '2262617365223a3130247b5b6964656e746974795d20227d227d2c226964223a'
            '31247b5b6964656e746974795d20227d227d275d000000000000000000000000',
          }),
          AttributeDict({
            'address': '0xFE8a5f3a7Bb446e1cB4566717691cD3139289ED4',
            'topics': [
              HexBytes(
                '1cb5bfc4e69cbacf65c8e05bdb84d7a3'
                '27bd6bb4c034ff82359aefd7443775c4'),
              HexBytes(
                'b0230ab70b78e47050766089ea333f2f'
                'f7ad41c6f31e8bed8c2acfcb8e911841'),
              HexBytes(
                '00000000000000000000000066d4bacf'
                'e61df23be813089a7a6d1a749a5c936a'),
              HexBytes(
                '00000000000000000000000000000000'
                '0000000000000000016a98b78c556c34')
            ],
            'data':
            '0000000000000000000000000000000000000000000000000007533f2ecb6c34'
            '000000000000000000000000000000000000000000000000016345785d8a0000'
            '0000000000000000000000000000000000000000000000000000000000000062',
          })
        ]
        chain_id = ChainID.ROPSTEN
        transaction_debugger = TransactionDebugger(chain_id)
        transaction_hash = (
          "0x330df22df6543c9816d80e582a4213b1fc11992f317be71775f49c3d853ed5be")
        with \
                mock.patch('web3.eth.Eth.getTransactionReceipt') \
                as m_getTransactionReceipt, \
                mock.patch(
                    'etherscan.contracts.Contract.get_abi',
                    side_effect=self.m_get_abi, autospec=True):
            m_getTransactionReceipt.return_value.logs = mocked_logs
            decoded_methods = transaction_debugger.decode_transaction_logs(
                transaction_hash)
        self.assertEqual(len(decoded_methods), 2)
        decoded_method = decoded_methods[0]
        self.assertEqual(
          decoded_method['method_info']['definition'],
          'Log1(address,bytes32,uint256,string,string,uint256,bytes1,uint256)'
        )
        decoded_method = decoded_methods[1]
        self.assertEqual(
            decoded_method['method_info']['definition'],
            'LogBet(bytes32,address,uint256,uint256,uint256,uint256)'
        )


class TestEtheroll(unittest.TestCase):

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
        with mock.patch('etherscan.contracts.Contract.get_abi') \
                as m_get_abi:
            m_get_abi.return_value = (
                '[{"constant":true,"inputs":[],"name":"minBet","outputs":[{"na'
                'me":"","type":"uint256"}],"payable":false,"stateMutability":"'
                'view","type":"function"},{"constant":false,"inputs":[{"name":'
                '"rollUnder","type":"uint256"}],"name":"playerRollDice","outpu'
                'ts":[],"payable":true,"stateMutability":"payable","type":"fun'
                'ction"}]')
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
        # the nonce was retrieved
        self.assertTrue(m_getTransactionCount.called)
        # the transaction was sent
        self.assertTrue(m_sendRawTransaction.called)
        # the transaction should be built that way
        expected_transaction = {
            'nonce': 0, 'chainId': 1,
            'to': Etheroll.CONTRACT_ADDRESSES[ChainID.MAINNET],
            'data': (
                    '0xdc6dd152000000000000000000000000000'
                    '0000000000000000000000000000000000032'),
            'gas': 310000,
            'value': 100000000000000000, 'gasPrice': 4000000000
        }
        expected_call = ((expected_transaction, account.privkey),)
        # the method should have been called only once
        expected_calls = [expected_call]
        self.assertEqual(m_signTransaction.call_args_list, expected_calls)

    def test_get_last_bets(self):
        """
        Verifies `get_last_bets()` performs the correct calls to underlying
        libraries, and verifies it handle their inputs correctly.
        """
        # we want this unit test to still pass even if the Etheroll contract
        # address changes, so let's make it explicit
        contract_address = '0x048717Ea892F23Fb0126F00640e2b18072efd9D2'
        with mock.patch('etherscan.contracts.Contract.get_abi') as m_get_abi:
            m_get_abi.return_value = '[]'
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
                'timeStamp': '1523060626',
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
                'timeStamp': '1523060494',
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
            bets = etheroll.get_last_bets(
                address=address, page=page, offset=offset)
            # we should have only two bets returns as the first transaction
            # was not made to the Etheroll contract
            self.assertEqual(
                bets,
                [
                    {'bet_size_ether': 0.5, 'roll_under': 14},
                    {'bet_size_ether': 0.45, 'roll_under': 2},
                ]
            )
            # makes sure underlying library was used properly
            expected_call = mock.call(
                internal=False, offset=3, page=1, sort='desc')
            # the method should have been called only once
            expected_calls = [expected_call]
            self.assertEqual(
                m_get_transaction_page.call_args_list, expected_calls)
