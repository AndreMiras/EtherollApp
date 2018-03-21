import unittest

# from .. import pyetheroll
import pyetheroll


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
        topics = [
          '0xb76d0edd90c6a07aa3ff7a222d7f5933e29c6acc660c059c97837f05c4ca1a84']
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
        decoded_method = pyetheroll.decode_method(
            contract_abi, topics, log_data)
        # TODO: simplify that arg call for unit testing
        self.assertEqual(
            decoded_method['call'],
            {'arg': (
                '[URL] [\'json(https://api.random.org/json-rpc/1/invoke).resul'
                't.random["serialNumber","data"]\', \'\\n{"jsonrpc":"2.0","met'
                'hod":"generateSignedIntegers","params":{"apiKey":${[decrypt] '
                'BKg3TCs7lkzNr1kR6pxjPCM2SOejcFojUPMTOsBkC/47HHPf1sP2oxVLTjNBu'
                '+slR9SgZyqDtjVOV5Yzg12iUkbubp0DpcjCEdeJTHnGwC6gD729GUVoGvo96h'
                'uxwRoZlCjYO80rWq2WGYoR/LC3WampDuvv2Bo=},"n":1,"min":1,"max":1'
                '00,"replacement":true,"base":10${[identity] "}"},"id":1${[ide'
                'ntity] "}"}\']'),
                'cid': (
                    '\xb0#\n\xb7\x0bx\xe4pPv`\x89\xea3?/\xf7\xadA\xc6\xf3\x1e'
                    '\x8b\xed\x8c*\xcf\xcb\x8e\x91\x18A'),
                'datasource': 'nested',
                'gasPrice': 20000000000,
                'gaslimit': 235000,
                'proofType': '\x11',
                'sender': '0xfe8a5f3a7bb446e1cb4566717691cd3139289ed4',
                'timestamp': 0}
        )
        self.assertEqual(
          decoded_method['method_info']['definition'],
          'Log1(address,bytes32,uint256,string,string,uint256,bytes1,uint256)')
        self.assertEqual(
          decoded_method['method_info']['sha3'],
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
          '0x1cb5bfc4e69cbacf65c8e05bdb84d7a327bd6bb4c034ff82359aefd7443775c4',
          '0xb0230ab70b78e47050766089ea333f2ff7ad41c6f31e8bed8c2acfcb8e911841',
          '0x00000000000000000000000066d4bacfe61df23be813089a7a6d1a749a5c936a',
          '0x000000000000000000000000000000000000000000000000016a98b78c556c34',
        ]
        log_data = (
            '0x'
            '0000000000000000000000000000000000000000000000000007533f2ecb6c34'
            '000000000000000000000000000000000000000000000000016345785d8a0000'
            '0000000000000000000000000000000000000000000000000000000000000062')
        decoded_method = pyetheroll.decode_method(
            contract_abi, topics, log_data)
        self.assertEqual(
            decoded_method['call'],
            {'BetID': (
                '\xb0#\n\xb7\x0bx\xe4pPv`\x89\xea3?/\xf7\xadA\xc6\xf3\x1e\x8b'
                '\xed\x8c*\xcf\xcb\x8e\x91\x18A'),
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
          decoded_method['method_info']['sha3'],
          '0x1cb5bfc4e69cbacf65c8e05bdb84d7a327bd6bb4c034ff82359aefd7443775c4')
