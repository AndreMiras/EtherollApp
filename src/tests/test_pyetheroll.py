import unittest
# from .. import pyetheroll
import pyetheroll

class TestUtils(unittest.TestCase):

    def test_decode_method(self):
        # simplified contract ABI for tests
        contract_abi = [
            {u'inputs': [], u'type': u'constructor', u'payable': False},
            {u'payable': False, u'type': u'fallback'},
            {u'inputs': [
                {u'indexed': False, u'type': u'address', u'name': u'sender'},
                {u'indexed': False, u'type': u'bytes32', u'name': u'cid'},
                {u'indexed': False, u'type': u'uint256', u'name': u'timestamp'},
                {u'indexed': False, u'type': u'string', u'name': u'datasource'},
                {u'indexed': False, u'type': u'string', u'name': u'arg'},
                {u'indexed': False, u'type': u'uint256', u'name': u'gaslimit'},
                {u'indexed': False, u'type': u'bytes1', u'name': u'proofType'},
                {u'indexed': False, u'type': u'uint256', u'name': u'gasPrice'}],
                u'type': u'event', u'name': u'Log1', u'anonymous': False},
            {u'inputs': [
                {u'indexed': False, u'type': u'address', u'name': u'sender'},
                {u'indexed': False, u'type': u'bytes32', u'name': u'cid'},
                {u'indexed': False, u'type': u'uint256', u'name': u'timestamp'},
                {u'indexed': False, u'type': u'string', u'name': u'datasource'},
                {u'indexed': False, u'type': u'string', u'name': u'arg1'},
                {u'indexed': False, u'type': u'string', u'name': u'arg2'},
                {u'indexed': False, u'type': u'uint256', u'name': u'gaslimit'},
                {u'indexed': False, u'type': u'bytes1', u'name': u'proofType'},
                {u'indexed': False, u'type': u'uint256', u'name': u'gasPrice'}],
                u'type': u'event', u'name': u'Log2', u'anonymous': False},
            {u'inputs': [
                {u'indexed': False, u'type': u'address', u'name': u'sender'},
                {u'indexed': False, u'type': u'bytes32', u'name': u'cid'},
                {u'indexed': False, u'type': u'uint256', u'name': u'timestamp'},
                {u'indexed': False, u'type': u'string', u'name': u'datasource'},
                {u'indexed': False, u'type': u'bytes', u'name': u'args'},
                {u'indexed': False, u'type': u'uint256', u'name': u'gaslimit'},
                {u'indexed': False, u'type': u'bytes1', u'name': u'proofType'},
                {u'indexed': False, u'type': u'uint256', u'name': u'gasPrice'}],
                u'type': u'event', u'name': u'LogN',u'anonymous': False}]
        topics = ['0xb76d0edd90c6a07aa3ff7a222d7f5933e29c6acc660c059c97837f05c4ca1a84']
        log_data = ("0x"
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
        decoded_method = pyetheroll.decode_method(contract_abi, topics, log_data)
        # TODO: simplify that arg call for unit testing
        self.assertEqual(
            decoded_method['call'],
            {u'arg': (
                '[URL] [\'json(https://api.random.org/json-rpc/1/invoke).resul'
                't.random["serialNumber","data"]\', \'\\n{"jsonrpc":"2.0","met'
                'hod":"generateSignedIntegers","params":{"apiKey":${[decrypt] '
                'BKg3TCs7lkzNr1kR6pxjPCM2SOejcFojUPMTOsBkC/47HHPf1sP2oxVLTjNBu'
                '+slR9SgZyqDtjVOV5Yzg12iUkbubp0DpcjCEdeJTHnGwC6gD729GUVoGvo96h'
                'uxwRoZlCjYO80rWq2WGYoR/LC3WampDuvv2Bo=},"n":1,"min":1,"max":1'
                '00,"replacement":true,"base":10${[identity] "}"},"id":1${[ide'
                'ntity] "}"}\']'),
                u'cid': (
                    '\xb0#\n\xb7\x0bx\xe4pPv`\x89\xea3?/\xf7\xadA\xc6\xf3\x1e'
                    '\x8b\xed\x8c*\xcf\xcb\x8e\x91\x18A'),
                u'datasource': 'nested',
                u'gasPrice': 20000000000,
                u'gaslimit': 235000,
                u'proofType': '\x11',
                u'sender': u'0xfe8a5f3a7bb446e1cb4566717691cd3139289ed4',
                u'timestamp': 0}
        )
        self.assertEqual(
            decoded_method['method_info']['definition'],
            'Log1(address,bytes32,uint256,string,string,uint256,bytes1,uint256)')
        self.assertEqual(
            decoded_method['method_info']['sha3'],
            '0xb76d0edd90c6a07aa3ff7a222d7f5933e29c6acc660c059c97837f05c4ca1a84')
