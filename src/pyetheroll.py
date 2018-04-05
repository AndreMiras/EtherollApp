#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Python Etheroll library.
"""
from __future__ import print_function

import json
import os
from enum import Enum

import eth_abi
from ethereum.abi import decode_abi
from ethereum.abi import method_id as get_abi_method_id
from ethereum.abi import normalize_name as normalize_abi_method_name
from ethereum.utils import checksum_encode, decode_hex, encode_int, zpad
from etherscan.contracts import Contract as EtherscanContract
from pyethapp.accounts import Account
from web3 import HTTPProvider, Web3
from web3.auto import w3
from web3.contract import Contract


class ChainID(Enum):
    MAINNET = 1
    MORDEN = 2
    ROPSTEN = 3


class RopstenEtherscanContract(EtherscanContract):
    """
    https://github.com/corpetty/py-etherscan-api/issues/24
    """
    PREFIX = 'https://api-ropsten.etherscan.io/api?'


class ChainEtherscanContractFactory:

    CONTRACTS = {
        ChainID.MAINNET: EtherscanContract,
        ChainID.ROPSTEN: RopstenEtherscanContract,
    }

    @classmethod
    def create(cls, chain_id=ChainID.MAINNET):
        ChainEtherscanContract = cls.CONTRACTS[chain_id]
        return ChainEtherscanContract


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

    def __init__(self, chain_id=ChainID.MAINNET):
        self.chain_id = chain_id
        self.provider = HTTPProviderFactory.create(chain_id)
        self.web3 = Web3(self.provider)
        # print("blockNumber:", self.web3.eth.blockNumber)

    def get_contract_abi(self, contract_address):
        """
        Given a contract address returns the contract ABI from Etherscan,
        refs #2
        """
        location = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__)))
        api_key_path = str(os.path.join(location, 'api_key.json'))
        with open(api_key_path, mode='r') as key_file:
            key = json.loads(key_file.read())['key']
        ChainEtherscanContract = ChainEtherscanContractFactory.create(
            self.chain_id)
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

    @classmethod
    def decode_method(cls, contract_abi, topics, log_data):
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
        methods_infos = cls.get_methods_infos(contract_abi)
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

    def decode_transaction_log(self, log):
        """
        Given a transaction event log.
        1) downloads the ABI associated to the recipient address
        2) uses it to decode methods calls
        """
        contract_address = log.address
        contract_abi = self.get_contract_abi(contract_address)
        topics = log.topics
        log_data = log.data
        decoded_method = self.decode_method(contract_abi, topics, log_data)
        # pprint(decoded_method)
        return decoded_method

    def decode_transaction_logs(self, transaction_hash):
        """
        Given a transaction hash, reads and decode the event log.
        Params:
        eth: web3.eth.Eth instance
        """
        decoded_methods = []
        transaction_receipt = self.web3.eth.getTransactionReceipt(
            transaction_hash)
        logs = transaction_receipt.logs
        for log in logs:
            decoded_methods.append(self.decode_transaction_log(log))
        return decoded_methods


# TODO: move somewhere and unit test
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

    CONTRACT_ADDRESSES = {
        ChainID.MAINNET: '0x048717Ea892F23Fb0126F00640e2b18072efd9D2',
        ChainID.ROPSTEN: '0xFE8a5f3a7Bb446e1cB4566717691cD3139289ED4',
    }

    def __init__(self, chain_id=ChainID.MAINNET, contract_address=None):
        if contract_address is None:
            contract_address = self.CONTRACT_ADDRESSES[chain_id]
        self.contract_address = contract_address
        self.chain_id = chain_id
        self.contract_address = contract_address
        # ethereum_tester = EthereumTester()
        # self.provider = EthereumTesterProvider(ethereum_tester)
        self.provider = HTTPProviderFactory.create(self.chain_id)
        self.web3 = Web3(self.provider)
        # print("blockNumber:", self.web3.eth.blockNumber)
        # TODO: hardcoded contract ABI
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
            abi=self.abi, address=self.contract_address,
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
            "address": self.contract_address,
            "topics": topics,
        })
        events_logs = event_filter.get(False)
        return events_logs

    @staticmethod
    def play_with_contract():
        """
        This is just a test method that should go away at some point.
        """
        etheroll = Etheroll()
        min_bet = etheroll.contract.call().minBet()
        print("min_bet:", min_bet)
        # events_definitions = etheroll.events_definitions()
        # print(events_definitions)
        # events_signatures = etheroll.events_signatures()
        # # events_logs = etheroll.events_logs(['LogBet'])
        # print(events_signatures)
        # pending = etheroll.contract.call(
        #     ).playerWithdrawPendingTransactions()
        # print("pending:", pending)

    def player_roll_dice(
            self, bet_size_ether, chances, wallet_path, wallet_password):
        """
        Work in progress:
        https://github.com/AndreMiras/EtherollApp/issues/1
        """
        roll_under = chances
        value_wei = w3.toWei(bet_size_ether, 'ether')
        gas = 310000
        gas_price = w3.toWei(4, 'gwei')
        # since Account.load is hanging while decrypting the password
        # we set password to None and use `w3.eth.account.decrypt` instead
        account = Account.load(wallet_path, password=None)
        from_address_normalized = checksum_encode(account.address)
        nonce = self.web3.eth.getTransactionCount(from_address_normalized)
        transaction = {
            # 'chainId': ChainID.ROPSTEN.value,
            'chainId': int(self.web3.net.version),
            'gas': gas,
            'gasPrice': gas_price,
            'nonce': nonce,
            'value': value_wei,
        }
        transaction = self.contract.functions.playerRollDice(
            roll_under).buildTransaction(transaction)
        encrypted_key = open(wallet_path).read()
        private_key = w3.eth.account.decrypt(encrypted_key, wallet_password)
        signed_tx = self.web3.eth.account.signTransaction(
            transaction, private_key)
        tx_hash = self.web3.eth.sendRawTransaction(signed_tx.rawTransaction)
        print("tx_hash:", tx_hash.hex())
        return tx_hash
