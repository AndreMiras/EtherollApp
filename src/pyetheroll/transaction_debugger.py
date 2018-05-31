import json

import eth_abi
from ethereum.abi import decode_abi
from ethereum.abi import method_id as get_abi_method_id
from ethereum.abi import normalize_name as normalize_abi_method_name
from ethereum.utils import decode_hex, encode_int, zpad
from web3 import HTTPProvider, Web3

from pyetheroll.constants import ChainID
from pyetheroll.etherscan_utils import (ChainEtherscanContractFactory,
                                        get_etherscan_api_key)


def decode_contract_call(contract_abi: list, call_data: str):
    """
    https://ethereum.stackexchange.com/a/33887/34898
    """
    call_data = call_data.lower().replace("0x", "")
    call_data_bin = decode_hex(call_data)
    method_signature = call_data_bin[:4]
    for description in contract_abi:
        if description.get('type') != 'function':
            continue
        method_name = normalize_abi_method_name(description['name'])
        arg_types = [item['type'] for item in description['inputs']]
        method_id = get_abi_method_id(method_name, arg_types)
        if zpad(encode_int(method_id), 4) == method_signature:
            try:
                # TODO: ethereum.abi.decode_abi vs eth_abi.decode_abi
                args = decode_abi(arg_types, call_data_bin[4:])
            except AssertionError:
                # Invalid args
                continue
            return method_name, args


class HTTPProviderFactory:

    PROVIDER_URLS = {
        ChainID.MAINNET: 'https://api.myetherapi.com/eth',
        # also https://api.myetherapi.com/rop
        ChainID.ROPSTEN: 'https://ropsten.infura.io',
    }

    @classmethod
    def create(cls, chain_id=ChainID.MAINNET):
        url = cls.PROVIDER_URLS[chain_id]
        return HTTPProvider(url)


class TransactionDebugger:

    def __init__(self, contract_abi):
        self.contract_abi = contract_abi
        self.methods_infos = None

    @staticmethod
    def get_contract_abi(chain_id, contract_address):
        """
        Given a contract address returns the contract ABI from Etherscan,
        refs #2
        """
        key = get_etherscan_api_key()
        ChainEtherscanContract = ChainEtherscanContractFactory.create(chain_id)
        api = ChainEtherscanContract(address=contract_address, api_key=key)
        json_abi = api.get_abi()
        abi = json.loads(json_abi)
        return abi

    @staticmethod
    def get_methods_infos(contract_abi):
        """
        List of infos for each events.
        """
        methods_infos = {}
        # only retrieves functions and events, other existing types are:
        # "fallback" and "constructor"
        types = ['function', 'event']
        methods = [a for a in contract_abi if a['type'] in types]
        for description in methods:
            method_name = description['name']
            types = ','.join([x['type'] for x in description['inputs']])
            event_definition = "%s(%s)" % (method_name, types)
            event_sha3 = Web3.sha3(text=event_definition)
            method_info = {
                'definition': event_definition,
                'sha3': event_sha3,
                'abi': description,
            }
            methods_infos.update({method_name: method_info})
        return methods_infos

    def decode_method(self, topics, log_data):
        """
        Given a topic and log data, decode the event.
        """
        topic = topics[0]
        # each indexed field generates a new topics and is excluded from data
        # hence we consider topics[1:] like data, assuming indexed fields
        # always come first
        # see https://codeburst.io/deep-dive-into-ethereum-logs-a8d2047c7371
        topics_log_data = b"".join(topics[1:])
        log_data = log_data.lower().replace("0x", "")
        log_data = bytes.fromhex(log_data)
        topics_log_data += log_data
        if self.methods_infos is None:
            self.methods_infos = self.get_methods_infos(self.contract_abi)
        method_info = None
        for event, info in self.methods_infos.items():
            if info['sha3'].lower() == topic.lower():
                method_info = info
        event_inputs = method_info['abi']['inputs']
        types = [e_input['type'] for e_input in event_inputs]
        # hot patching `bytes` type to replace it with bytes32 since the former
        # is crashing with `InsufficientDataBytes` during `LogResult` decoding.
        types = ['bytes32' if t == 'bytes' else t for t in types]
        names = [e_input['name'] for e_input in event_inputs]
        values = eth_abi.decode_abi(types, topics_log_data)
        call = {name: value for name, value in zip(names, values)}
        decoded_method = {
            'method_info': method_info,
            'call': call,
        }
        return decoded_method

    @classmethod
    def decode_transaction_log(cls, chain_id, log):
        """
        Given a transaction event log.
        1) downloads the ABI associated to the recipient address
        2) uses it to decode methods calls
        """
        contract_address = log.address
        contract_abi = cls.get_contract_abi(chain_id, contract_address)
        transaction_debugger = cls(contract_abi)
        topics = log.topics
        log_data = log.data
        decoded_method = transaction_debugger.decode_method(topics, log_data)
        return decoded_method

    @classmethod
    def decode_transaction_logs(cls, chain_id, transaction_hash):
        """
        Given a transaction hash, reads and decode the event log.
        """
        decoded_methods = []
        provider = HTTPProviderFactory.create(chain_id)
        web3 = Web3(provider)
        transaction_receipt = web3.eth.getTransactionReceipt(
            transaction_hash)
        logs = transaction_receipt.logs
        for log in logs:
            decoded_methods.append(cls.decode_transaction_log(chain_id, log))
        return decoded_methods
