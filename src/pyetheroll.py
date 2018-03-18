#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Python Etheroll library.
"""
from __future__ import print_function

import os
import json
from eth_abi import decode_abi
from eth_tester import EthereumTester
from web3 import Web3, HTTPProvider
from web3.contract import ConciseContract, Contract
from web3.providers.eth_tester import EthereumTesterProvider
from ethereum.abi import (
    decode_abi,
    normalize_name as normalize_abi_method_name,
    method_id as get_abi_method_id)
from ethereum.utils import encode_int, zpad, decode_hex

# def decode_contract_call(contract_abi: list, call_data: str):
def decode_contract_call(contract_abi, call_data):
    call_data = call_data.lower().deplace("0x", "")
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
        ethereum_tester = EthereumTester()
        # self.provider = EthereumTesterProvider(ethereum_tester)
        self.provider = HTTPProvider('https://ropsten.infura.io')
        # self.provider = HTTPProvider('https://api.myetherapi.com/rop')
        # self.provider = HTTPProvider('https://api.myetherapi.com/eth')
        self.web3 = Web3(self.provider)
        # print("blockNumber:", self.web3.eth.blockNumber)
        location = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
        contract_abi_path = str(os.path.join(location, 'contract_abi.json'))
        with open(contract_abi_path, 'r') as abi_definition:
          self.abi = json.load(abi_definition)
        contract_abi_path = str(os.path.join(location, 'oraclize_contract_abi.json'))
        with open(contract_abi_path, 'r') as abi_definition:
          self.oraclize_contract_abi = json.load(abi_definition)
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

    def events_infos(self, contract_abi):
        """
        List of infos for each events.
        """
        events_infos = {}
        events_abi = self.events_abi(contract_abi)
        for event_abi in events_abi:
            event_name = event_abi['name']
            types = ','.join([x['type'] for x in event_abi['inputs']])
            event_definition = "%s(%s)" % (event_name, types)
            event_sha3 = Web3.sha3(text=event_definition)
            event_info = {
                'definition': event_definition,
                'sha3': event_sha3,
                'abi': event_abi,
            }
            events_infos.update({event_name: event_info})
        return events_infos

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

    # TODO: this is not yet working as expected
    def decode_event(self, contract_abi, topic, log_data):
        """
        Given a topic and log data, decode the event.
        TODO:
        This is not yet working as expected. The `log_data` part is not
        decoded properly.
        """
        events_infos = self.events_infos(contract_abi)
        event_info = None
        for event, info in events_infos.iteritems():
            if info['sha3'].lower() == topic.lower():
                event_info = info
        event_inputs = event_info['abi']['inputs']
        types = [e_input['type'] for e_input in event_inputs]
        names = [e_input['name'] for e_input in event_inputs]
        print(event_info['definition'])
        values = decode_abi(types, log_data)
        call = {name: value for name, value in zip(names, values)}
        # print(call)


def play_with_contract():
    etheroll = Etheroll()
    contract_abi = etheroll.abi
    # contract_abi = etheroll.oraclize_contract_abi
    call_data_list = [
        # '0xdc6dd152000000000000000000000000000000000000000000000000000000000000001c',
    ]
    for call_data in call_data_list:
        method_name, args = decode_contract_call(contract_abi, call_data)
        print(method_name, args)
    # min_bet = etheroll.contract.call().minBet()
    # print("min_bet:", min_bet)
    # log_bet_events = etheroll.contract.pastEvents('LogBet').get(only_changes=False)
    # etheroll.web3.eth.filter({'address': Etheroll.CONTRACT_ADDRESS, 'topics': topics})
    # events_definitions = etheroll.events_definitions()
    # print(events_definitions)
    # events_signatures = etheroll.events_signatures()
    # # events_logs = etheroll.events_logs(['LogBet'])
    # print(events_signatures)
    # pending = etheroll.contract.call().playerWithdrawPendingTransactions()
    # print("pending:", pending)
    # topic = "0xb76d0edd90c6a07aa3ff7a222d7f5933e29c6acc660c059c97837f05c4ca1a84"
    topic = "0x1cb5bfc4e69cbacf65c8e05bdb84d7a327bd6bb4c034ff82359aefd7443775c4"
    log_data = [
            "b4fd1bd4b0a330a00f1d809c9a29c9aa2bba49e7af45dee70852e1e7e2eed543",
            "000000000000000000000000070ba449dba610303f928e35fd6c16c54b25d37a",
            "0000000000000000000000000000000000000000000000004fafae93dc4b0000",
            "0000000000000000000000000000000000000000000000002770cff143a90000",
            "000000000000000000000000000000000000000000000000283edea298a20000",
            "0000000000000000000000000000000000000000000000000000000000000033",
    ]
    log_data = "".join(log_data)
    etheroll.decode_event(contract_abi, topic, log_data)


def main():
    play_with_contract()

if __name__ == "__main__":
    main()
