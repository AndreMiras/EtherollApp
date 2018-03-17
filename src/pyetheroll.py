#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Python Etheroll library.
"""
from __future__ import print_function

import os
import json
from eth_tester import EthereumTester
from web3 import Web3, HTTPProvider
from web3.contract import ConciseContract, Contract
from web3.providers.eth_tester import EthereumTesterProvider


class Etheroll:

    CONTRACT_ADDRESS = '0xddf0d0b9914d530e0b743808249d9af901f1bd01'

    def __init__(self):
        ethereum_tester = EthereumTester()
        # self.provider = EthereumTesterProvider(ethereum_tester)
        # self.provider = HTTPProvider('https://ropsten.infura.io')
        self.provider = HTTPProvider('https://api.myetherapi.com/eth')
        self.web3 = Web3(self.provider)
        print("blockNumber:", self.web3.eth.blockNumber)
        location = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
        contract_abi_path = str(os.path.join(location, 'contract_abi.json'))
        with open(contract_abi_path, 'r') as abi_definition:
          self.abi = json.load(abi_definition)
        # contract_factory_class = ConciseContract
        contract_factory_class = Contract
        self.contract = self.web3.eth.contract(
            abi=self.abi, address=self.CONTRACT_ADDRESS,
            ContractFactoryClass=contract_factory_class)

    def events_definitions(self):
        """
        Returns all events definitions.
        """
        events_definitions = {
            "LogBet": "LogBet(bytes32,address,uint256,uint256,uint256,uint256)",
            "LogResult": "LogResult(uint256,bytes32,address,uint256,uint256,uint256,int256,bytes32,uint256)",
            "LogRefund": "LogRefund(bytes32,address,uint256)",
            "LogOwnerTransfer": "LogOwnerTransfer(address,uint256)",
        }
        return events_definitions

    def events_signatures(self):
        """
        Returns sha3 signature of all events.
        """
        events_signatures = {}
        events_definitions = self.events_definitions()
        for event in events_definitions:
            event_definition = events_definitions[event]
            event_signature = Web3.sha3(text=event_definition)
            events_signatures.update({event: event_signature})
        return events_signatures

    def events_logs(self, event_list):
        """
        Returns the logs of the given events.
        """
        events_signatures = self.events_signatures()
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
    min_bet = etheroll.contract.call().minBet()
    print("min_bet:", min_bet)
    log_bet_events = etheroll.contract.pastEvents('LogBet').get(only_changes=False)
    # etheroll.web3.eth.filter({'address': Etheroll.CONTRACT_ADDRESS, 'topics': topics})
    events_signatures = etheroll.events_signatures()
    events_logs = etheroll.events_logs(['LogBet'])
    pending = etheroll.contract.call().playerWithdrawPendingTransactions()
    print("pending:", pending)


def main():
    play_with_contract()

if __name__ == "__main__":
    main()
