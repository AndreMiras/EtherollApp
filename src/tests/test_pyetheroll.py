import json
import unittest
from unittest import mock

from hexbytes.main import HexBytes
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

    def test_init(self):
        """
        Verifies object initializes properly and contract methods are callable.
        """
        etheroll = Etheroll()
        min_bet = etheroll.contract.call().minBet()
        self.assertEqual(min_bet, 100000000000000000)
