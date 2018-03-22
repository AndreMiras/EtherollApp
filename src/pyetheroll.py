#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Python Etheroll library.
"""
from __future__ import print_function

import json
import os
from pprint import pprint

import eth_abi
from ethereum.abi import decode_abi
from ethereum.abi import method_id as get_abi_method_id
from ethereum.abi import normalize_name as normalize_abi_method_name
from ethereum.utils import decode_hex, encode_int, zpad
from etherscan.contracts import Contract as EtherscanContract
from web3 import HTTPProvider, Web3
from web3.contract import Contract


class RopstenContract(EtherscanContract):
    """
    https://github.com/corpetty/py-etherscan-api/issues/24
    """
    PREFIX = 'https://api-ropsten.etherscan.io/api?'


# TODO: handle both mainnet and testnet
def get_contract_abi(contract_address):
    """
    Given a contract address returns the contract ABI from Etherscan, refs #2.
    """
    location = os.path.realpath(
        os.path.join(os.getcwd(), os.path.dirname(__file__)))
    api_key_path = str(os.path.join(location, 'api_key.json'))
    with open(api_key_path, mode='r') as key_file:
        key = json.loads(key_file.read())['key']
    api = RopstenContract(address=contract_address, api_key=key)
    json_abi = api.get_abi()
    abi = json.loads(json_abi)
    return abi


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


def decode_method(contract_abi, topics, log_data):
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
    methods_infos = get_methods_infos(contract_abi)
    method_info = None
    for event, info in methods_infos.items():
        if info['sha3'].lower() == topic.lower():
            method_info = info
    event_inputs = method_info['abi']['inputs']
    types = [e_input['type'] for e_input in event_inputs]
    names = [e_input['name'] for e_input in event_inputs]
    values = eth_abi.decode_abi(types, topics_log_data)
    call = {name: value for name, value in zip(names, values)}
    decoded_method = {
        'method_info': method_info,
        'call': call,
    }
    return decoded_method


def decode_transaction_log(log):
    """
    Given a transaction event log.
    1) downloads the ABI associated to the recipient address
    2) uses it to decode methods calls
    """
    contract_address = log.address
    contract_abi = get_contract_abi(contract_address)
    topics = log.topics
    log_data = log.data
    decoded_method = decode_method(contract_abi, topics, log_data)
    pprint(decoded_method)


def decode_transaction_logs(eth, transaction_hash):
    """
    Given a transaction hash, reads and decode the event log.
    Params:
    eth: web3.eth.Eth instance
    """
    transaction_receipt = eth.getTransactionReceipt(transaction_hash)
    logs = transaction_receipt.logs
    # TODO: currently only handles the first log
    for log in logs:
        decode_transaction_log(log)


# def decode_contract_call(contract_abi: list, call_data: str):
def decode_contract_call(contract_abi, call_data):
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


class Etheroll:

    # Main network
    # CONTRACT_ADDRESS = '0xddf0d0b9914d530e0b743808249d9af901f1bd01'
    # Testnet
    CONTRACT_ADDRESS = '0xFE8a5f3a7Bb446e1cB4566717691cD3139289ED4'

    def __init__(self):
        # ethereum_tester = EthereumTester()
        # self.provider = EthereumTesterProvider(ethereum_tester)
        self.provider = HTTPProvider('https://ropsten.infura.io')
        # self.provider = HTTPProvider('https://api.myetherapi.com/rop')
        # self.provider = HTTPProvider('https://api.myetherapi.com/eth')
        self.web3 = Web3(self.provider)
        # print("blockNumber:", self.web3.eth.blockNumber)
        location = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__)))
        contract_abi_path = str(os.path.join(location, 'contract_abi.json'))
        with open(contract_abi_path, 'r') as abi_definition:
            self.abi = json.load(abi_definition)
        contract_abi_path = str(
            os.path.join(location, 'oraclize_contract_abi.json'))
        with open(contract_abi_path, 'r') as abi_definition:
            self.oraclize_contract_abi = json.load(abi_definition)
        contract_abi_path = str(
            os.path.join(location, 'oraclize2_contract_abi.json'))
        with open(contract_abi_path, 'r') as abi_definition:
            self.oraclize2_contract_abi = json.load(abi_definition)
        # contract_factory_class = ConciseContract
        contract_factory_class = Contract
        self.contract = self.web3.eth.contract(
            abi=self.abi, address=self.CONTRACT_ADDRESS,
            ContractFactoryClass=contract_factory_class)

    def events_abi(self, contract_abi=None):
        """
        Returns only ABI definition of type "event".
        """
        if contract_abi is None:
            contract_abi = self.abi
        return [a for a in contract_abi if a['type'] == 'event']

    def events_definitions(self, contract_abi=None):
        """
        Returns all events definitions (built from ABI definition).
        e.g.
        >>> {"LogRefund": "LogRefund(bytes32,address,uint256)"}
        """
        events_definitions = {}
        events_abi = self.events_abi(contract_abi)
        for event_abi in events_abi:
            event_name = event_abi['name']
            types = ','.join([x['type'] for x in event_abi['inputs']])
            event_definition = "%s(%s)" % (event_name, types)
            events_definitions.update({event_name: event_definition})
        return events_definitions

    def events_signatures(self, contract_abi=None):
        """
        Returns sha3 signature of all events.
        e.g.
        >>> {'LogResult': '0x6883...5c88', 'LogBet': '0x1cb5...75c4'}
        """
        events_signatures = {}
        events_definitions = self.events_definitions(contract_abi)
        for event in events_definitions:
            event_definition = events_definitions[event]
            event_signature = Web3.sha3(text=event_definition)
            events_signatures.update({event: event_signature})
        return events_signatures

    def events_logs(self, event_list):
        """
        Returns the logs of the given events.
        """
        contract_abi = self.contract_abi
        events_signatures = self.events_signatures(contract_abi)
        topics = []
        for event in event_list:
            topics.append(events_signatures[event])
        event_filter = self.web3.eth.filter({
            "fromBlock": "earliest",
            "toBlock": "latest",
            "address": self.CONTRACT_ADDRESS,
            "topics": topics,
        })
        events_logs = event_filter.get(False)
        return events_logs


def play_with_contract():
    etheroll = Etheroll()
    contract_abi = etheroll.abi
    contract_abi = etheroll.oraclize_contract_abi
    contract_abi = etheroll.oraclize2_contract_abi
    transaction_hash = (
        "0x330df22df6543c9816d80e582a4213b1fc11992f317be71775f49c3d853ed5be")
    decode_transaction_logs(etheroll.web3.eth, transaction_hash)
    return
    print("contract_abi:")
    print(contract_abi)
    # method_name, args = decode_contract_call(contract_abi, call_data)
    # print(method_name, args)

    # min_bet = etheroll.contract.call().minBet()
    # print("min_bet:", min_bet)
    # events_definitions = etheroll.events_definitions()
    # print(events_definitions)
    # events_signatures = etheroll.events_signatures()
    # # events_logs = etheroll.events_logs(['LogBet'])
    # print(events_signatures)
    # pending = etheroll.contract.call().playerWithdrawPendingTransactions()
    # print("pending:", pending)


def main():
    play_with_contract()


if __name__ == "__main__":
    main()
