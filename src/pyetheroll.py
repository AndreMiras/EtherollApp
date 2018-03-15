#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Python Etheroll library.
"""
import os
import json
from web3 import Web3, HTTPProvider, TestRPCProvider
from web3.contract import ConciseContract


class Etheroll:

    CONTRACT_ADDRESS = '0xddf0d0b9914d530e0b743808249d9af901f1bd01'

    def __init__(self):
        # self.web3 = Web3(RPCProvider(host='localhost', port='8545'))
        self.web3 = Web3(TestRPCProvider())
        location = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
        with open(str(os.path.join(location, 'contract_abi.json')), 'r') as abi_definition:
          self.abi = json.load(abi_definition)
        # self.contract = self.web3.eth.contract(abi=self.abi, address=self.CONTRACT_ADDRESS)
        self.contract = self.web3.eth.contract(
            abi=self.abi, address=self.CONTRACT_ADDRESS, ContractFactoryClass=ConciseContract)


def play_with_contract():
    etheroll = Etheroll()
    min_bet = etheroll.contract.minBet
    print("min_bet:", min_bet)
    pending = etheroll.contract.playerWithdrawPendingTransactions()
    print("pending:", pending)


def main():
    play_with_contract()

if __name__ == "__main__":
    main()
