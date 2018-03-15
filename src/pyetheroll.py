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
from web3.contract import ConciseContract
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
        with open(str(os.path.join(location, 'contract_abi.json')), 'r') as abi_definition:
          self.abi = json.load(abi_definition)
        # self.contract = self.web3.eth.contract(abi=self.abi, address=self.CONTRACT_ADDRESS)
        self.contract = self.web3.eth.contract(
            abi=self.abi, address=self.CONTRACT_ADDRESS, ContractFactoryClass=ConciseContract)


def play_with_contract():
    etheroll = Etheroll()
    min_bet = etheroll.contract.minBet()
    print("min_bet:", min_bet)
    pending = etheroll.contract.playerWithdrawPendingTransactions()
    print("pending:", pending)


def main():
    play_with_contract()

if __name__ == "__main__":
    main()
