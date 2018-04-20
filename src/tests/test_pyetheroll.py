import json
import os
import shutil
import unittest
from datetime import datetime
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
                    'timestamp': '1523060626',
                    'datetime': datetime(4846, 10, 6, 13, 22, 46),
                    'transaction_hash': (
                        '0x0440f1013a5eafd88f16be6b5612b6e'
                        '051a4eb1b0b91a160c680295e7fab5bfe'),
                },
                {
                    'bet_size_ether': 0.45,
                    'roll_under': 2,
                    'block_number': '5394085',
                    'timestamp': '1523060494',
                    'datetime': datetime(4846, 10, 6, 13, 16, 4),
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
                mock.patch('etherscan.contracts.Contract.get_abi') \
                as m_get_abi, \
                mock.patch('pyetheroll.get_etherscan_api_key') \
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
                mock.patch('etherscan.contracts.Contract.get_abi') \
                as m_get_abi, \
                mock.patch('pyetheroll.get_etherscan_api_key') \
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
                mock.patch('etherscan.contracts.Contract.get_abi') \
                as m_get_abi, \
                mock.patch('pyetheroll.get_etherscan_api_key') \
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
                mock.patch('etherscan.contracts.Contract.get_abi') \
                as m_get_abi, \
                mock.patch('pyetheroll.get_etherscan_api_key') \
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
                mock.patch('etherscan.contracts.Contract.get_abi') \
                as m_get_abi, \
                mock.patch('pyetheroll.get_etherscan_api_key') \
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
                mock.patch('etherscan.contracts.Contract.get_abi') \
                as m_get_abi, \
                mock.patch('pyetheroll.get_etherscan_api_key') \
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
        with mock.patch('pyetheroll.Etheroll.get_log_bet_events') \
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
        with mock.patch('pyetheroll.Etheroll.get_log_result_events') \
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

    def test_get_last_bet_results_logs(self):
        # TODO
        # etheroll = Etheroll()
        # address = '0x46044beAa1E985C67767E04dE58181de5DAAA00F'
        # results = etheroll.get_last_bet_results_logs(address)
        pass

    def test_get_last_bets_blocks(self):
        # TODO
        # etheroll = Etheroll()
        # address = '0x46044beAa1E985C67767E04dE58181de5DAAA00F'
        # last_bets_blocks = etheroll.get_last_bets_blocks(address)
        pass

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

    def test_compute_profit(self):
        bet_size = 0.10
        chances_win = 34
        payout = Etheroll.compute_profit(bet_size, chances_win)
        self.assertEqual(payout, 0.19)
        bet_size = 0.10
        # chances of winning must be less than 100%
        chances_win = 100
        payout = Etheroll.compute_profit(bet_size, chances_win)
        self.assertEqual(payout, None)

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
                mock.patch('pyetheroll.Etheroll.get_last_bets_blocks') \
                as m_get_last_bets_blocks,\
                mock.patch('pyetheroll.Etheroll.get_bets_logs') \
                as m_get_bets_logs,\
                mock.patch('pyetheroll.Etheroll.get_bet_results_logs') \
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
