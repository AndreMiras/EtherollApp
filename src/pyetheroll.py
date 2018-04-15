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
import requests
import requests_cache
from ethereum.abi import decode_abi
from ethereum.abi import method_id as get_abi_method_id
from ethereum.abi import normalize_name as normalize_abi_method_name
from ethereum.utils import checksum_encode, decode_hex, encode_int, zpad
from etherscan.accounts import Account as EtherscanAccount
from etherscan.contracts import Contract as EtherscanContract
from pyethapp.accounts import Account
from web3 import HTTPProvider, Web3
from web3.auto import w3
from web3.contract import Contract

from ethereum_utils import AccountUtils

requests_cache_params = {
    'cache_name': 'requests_cache',
    'backend': 'sqlite',
    'fast_save': True,
}


def get_etherscan_api_key():
    """
    Tries to retrieve etherscan API key from environment or from file.
    """
    ETHERSCAN_API_KEY = os.environ.get('ETHERSCAN_API_KEY')
    if ETHERSCAN_API_KEY is None:
        location = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__)))
        api_key_path = str(os.path.join(location, 'api_key.json'))
        with open(api_key_path, mode='r') as key_file:
            ETHERSCAN_API_KEY = json.loads(key_file.read())['key']
    return ETHERSCAN_API_KEY


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
    """
    Creates Contract class type depending on the chain ID.
    """

    CONTRACTS = {
        ChainID.MAINNET: EtherscanContract,
        ChainID.ROPSTEN: RopstenEtherscanContract,
    }

    @classmethod
    def create(cls, chain_id=ChainID.MAINNET):
        ChainEtherscanContract = cls.CONTRACTS[chain_id]
        return ChainEtherscanContract


class RopstenEtherscanAccount(EtherscanAccount):
    """
    https://github.com/corpetty/py-etherscan-api/issues/24
    """
    PREFIX = 'https://api-ropsten.etherscan.io/api?'


class ChainEtherscanAccountFactory:
    """
    Creates Account class type depending on the chain ID.
    """

    ACCOUNTS = {
        ChainID.MAINNET: EtherscanAccount,
        ChainID.ROPSTEN: RopstenEtherscanAccount,
    }

    @classmethod
    def create(cls, chain_id=ChainID.MAINNET):
        ChainEtherscanAccount = cls.ACCOUNTS[chain_id]
        return ChainEtherscanAccount


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
        key = get_etherscan_api_key()
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
        self.etherscan_api_key = get_etherscan_api_key()
        ChainEtherscanContract = ChainEtherscanContractFactory.create(
            self.chain_id)
        self.ChainEtherscanAccount = ChainEtherscanAccountFactory.create(
            self.chain_id)
        # object construction needs to be within the context manager because
        # the requests.Session object to be patched is initialized in the
        # constructor
        with requests_cache.enabled(**requests_cache_params):
            self.etherscan_contract_api = ChainEtherscanContract(
                address=self.contract_address, api_key=self.etherscan_api_key)
            self.abi = json.loads(self.etherscan_contract_api.get_abi())
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
        Signs and broadcasts `playerRollDice` transaction.
        Returns transaction hash.
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
            'chainId': self.chain_id.value,
            'gas': gas,
            'gasPrice': gas_price,
            'nonce': nonce,
            'value': value_wei,
        }
        transaction = self.contract.functions.playerRollDice(
            roll_under).buildTransaction(transaction)
        private_key = AccountUtils.get_private_key(
            wallet_path, wallet_password)
        signed_tx = self.web3.eth.account.signTransaction(
            transaction, private_key)
        tx_hash = self.web3.eth.sendRawTransaction(signed_tx.rawTransaction)
        return tx_hash

    def get_transaction_page(
            self, address=None, page=1, offset=100, internal=False):
        """
        Retrieves all transactions related to the given address.
        """
        if address is None:
            address = self.contract_address
        # that one should not be cached, because we want the user to know
        # realtime what's happening with his transaction
        etherscan_account_api = self.ChainEtherscanAccount(
            address=address, api_key=self.etherscan_api_key)
        sort = 'desc'
        transactions = etherscan_account_api.get_transaction_page(
            page=page, offset=offset, sort=sort, internal=internal)
        return transactions

    def get_player_roll_dice_tx(self, address, page=1, offset=100):
        """
        Retrieves `address` last `playerRollDice` transactions associated with
        the Etheroll contract.
        """
        # last transactions from/to address
        transactions = self.get_transaction_page(
            address=address, page=page, offset=offset)
        # keeps only transactions sent to Etheroll contract
        transactions = filter(
            lambda t: t['to'].lower() == self.contract_address.lower(),
            transactions)
        # TODO: hardcoded methodID, retrieve it from contract ABI instead
        # keeps only transactions to `playerRollDice` methodID
        method_id = '0xdc6dd152'
        transactions = filter(
            lambda t: t['input'].lower().startswith(method_id),
            transactions)
        return transactions

    def get_last_bets(self, address=None, page=1, offset=100):
        """
        Retrieves `address` last bets and returns the list of bets with:
            - bet_size_ether
            - roll_under
        Does not return the actual roll result.
        """
        bets = []
        transactions = self.get_player_roll_dice_tx(
            address=address, page=page, offset=offset)
        for transaction in transactions:
            # from Wei to Ether
            bet_size_ether = int(transaction['value']) / pow(10, 18)
            # `playerRollDice(uint256 rollUnder)`, rollUnder is 256 bits
            # let's strip it from methodID and keep only 32 bytes
            roll_under = transaction['input'][-2*32:]
            roll_under = int(roll_under, 16)
            bet = {
                'bet_size_ether': bet_size_ether,
                'roll_under': roll_under,
            }
            bets.append(bet)
        return bets

    def get_logs_url(
            self, address, from_block, to_block='latest',
            topic0=None, topic1=None, topic2=None, topic3=None,
            topic_opr=None):
        """
        Builds the Etherscan API URL call for the `getLogs` action.
        """
        url = self.ChainEtherscanAccount.PREFIX
        url += 'module=logs&action=getLogs&'
        url += 'apikey={}&'.format(self.etherscan_api_key)
        url += 'address={}&'.format(address)
        url += 'fromBlock={}&'.format(from_block)
        url += 'toBlock={}&'.format(to_block)
        if topic0 is not None:
            url += 'topic0={}&'.format(topic0)
        if topic1 is not None:
            url += 'topic1={}&'.format(topic1)
        if topic2 is not None:
            url += 'topic2={}&'.format(topic2)
        if topic3 is not None:
            url += 'topic3={}&'.format(topic3)
        if topic_opr is not None:
            topic0_1_opr = topic_opr.get('topic0_1_opr')
            topic0_1_opr = 'topic0_1_opr={}&'.format(topic0_1_opr) \
                if topic0_1_opr is not None else ''
            topic1_2_opr = topic_opr.get('topic1_2_opr')
            topic1_2_opr += 'topic1_2_opr={}&'.format(topic1_2_opr) \
                if topic1_2_opr is not None else ''
            topic2_3_opr = topic_opr.get('topic2_3_opr')
            topic2_3_opr += 'topic2_3_opr={}&'.format(topic2_3_opr) \
                if topic2_3_opr is not None else ''
            topic0_2_opr = topic_opr.get('topic0_2_opr')
            topic0_2_opr += 'topic0_2_opr={}&'.format(topic0_2_opr) \
                if topic0_2_opr is not None else ''
            url += topic0_1_opr + topic1_2_opr + topic2_3_opr + topic0_2_opr
        return url

    # TODO: add some topics filtering (e.g. from_address)
    def get_logs(self, address, from_block, to_block='latest', topic0=None):
        """
        Currently py-etherscan-api doesn't provide support for event logs, see:
        https://github.com/corpetty/py-etherscan-api/issues/26
        """
        url = self.get_logs_url(address, from_block, to_block, topic0)
        response = requests.get(url)
        return response.json()
