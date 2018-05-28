#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Python Etheroll library.
"""
import json
import logging
import os
from datetime import datetime
from enum import Enum

import eth_abi
import requests
import requests_cache
from ethereum.abi import decode_abi
from ethereum.abi import method_id as get_abi_method_id
from ethereum.abi import normalize_name as normalize_abi_method_name
from ethereum.utils import checksum_encode, decode_hex, encode_int, zpad
from etherscan.accounts import Account as EtherscanAccount
from etherscan.client import EmptyResponse
from etherscan.contracts import Contract as EtherscanContract
from hexbytes.main import HexBytes
from pyethapp.accounts import Account
from web3 import HTTPProvider, Web3
from web3.auto import w3
from web3.contract import Contract

import constants
from ethereum_utils import AccountUtils

logger = logging.getLogger(__name__)
REQUESTS_CACHE_PARAMS = {
    'cache_name': 'requests_cache',
    'backend': 'sqlite',
    'fast_save': True,
    # we cache most of the request for a pretty long period, but not forever
    # as we still want some very outdate data to get wiped at some point
    'expire_after': 30*24*60*60,
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
        try:
            with open(api_key_path, mode='r') as key_file:
                ETHERSCAN_API_KEY = json.loads(key_file.read())['key']
        except FileNotFoundError:
            ETHERSCAN_API_KEY = 'YourApiKeyToken'
            logger.warning(
                'Cannot get Etherscan API key. '
                'File {} not found, defaulting to `{}`.'.format(
                    api_key_path, ETHERSCAN_API_KEY))
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


class Etheroll:

    CONTRACT_ADDRESSES = {
        ChainID.MAINNET: '0x048717Ea892F23Fb0126F00640e2b18072efd9D2',
        ChainID.ROPSTEN: '0xe12c6dEb59f37011d2D9FdeC77A6f1A8f3B8B1e8',
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
        self.etherscan_api_key = get_etherscan_api_key()
        ChainEtherscanContract = ChainEtherscanContractFactory.create(
            self.chain_id)
        self.ChainEtherscanAccount = ChainEtherscanAccountFactory.create(
            self.chain_id)
        # object construction needs to be within the context manager because
        # the requests.Session object to be patched is initialized in the
        # constructor
        with requests_cache.enabled(**REQUESTS_CACHE_PARAMS):
            self.etherscan_contract_api = ChainEtherscanContract(
                address=self.contract_address, api_key=self.etherscan_api_key)
            self.contract_abi = json.loads(
                self.etherscan_contract_api.get_abi())
        # contract_factory_class = ConciseContract
        contract_factory_class = Contract
        self.contract = self.web3.eth.contract(
            abi=self.contract_abi, address=self.contract_address,
            ContractFactoryClass=contract_factory_class)
        # retrieve signatures
        self.events_signatures = self.get_events_signatures(self.contract_abi)
        self.functions_signatures = self.get_functions_signatures(
            self.contract_abi)

    def abi_definitions(self, contract_abi, typ):
        """
        Returns only ABI definitions of matching type.
        """
        return [a for a in contract_abi if a['type'] == typ]

    def definitions(self, contract_abi, typ):
        """
        Returns all events definitions (built from ABI definition).
        e.g.
        >>> {"LogRefund": "LogRefund(bytes32,address,uint256)"}
        """
        events_definitions = {}
        abi_definitions = self.abi_definitions(contract_abi, typ)
        for abi_definition in abi_definitions:
            name = abi_definition['name']
            types = ','.join([x['type'] for x in abi_definition['inputs']])
            definition = "%s(%s)" % (name, types)
            events_definitions.update({name: definition})
        return events_definitions

    def get_signatures(self, contract_abi, typ):
        """
        Returns sha3 signature of methods or events.
        e.g.
        >>> {'LogResult': '0x6883...5c88', 'LogBet': '0x1cb5...75c4'}
        """
        signatures = {}
        definitions = self.definitions(contract_abi, typ)
        for name in definitions:
            definition = definitions[name]
            signature = Web3.sha3(text=definition)
            signatures.update({name: signature})
        return signatures

    def get_events_signatures(self, contract_abi=None):
        """
        Returns sha3 signature of all events.
        e.g.
        >>> {'LogResult': '0x6883...5c88', 'LogBet': '0x1cb5...75c4'}
        """
        return self.get_signatures(contract_abi, 'event')

    def get_functions_signatures(self, contract_abi=None):
        """
        Returns sha3 signature of all functions.
        """
        return self.get_signatures(contract_abi, 'function')

    def events_logs(self, event_list):
        """
        Returns the logs of the given events.
        """
        events_signatures = self.events_signatures
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

    def player_roll_dice(
            self, bet_size_ether, chances, wallet_path, wallet_password,
            gas_price_gwei=constants.DEFAULT_GAS_PRICE_GWEI):
        """
        Signs and broadcasts `playerRollDice` transaction.
        Returns transaction hash.
        """
        roll_under = chances
        # `w3.toWei` one has some issues on Android, see:
        # https://github.com/AndreMiras/EtherollApp/issues/77
        # value_wei = w3.toWei(bet_size_ether, 'ether')
        value_wei = int(bet_size_ether * 1e18)
        gas = 310000
        gas_price = w3.toWei(gas_price_gwei, 'gwei')
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
        try:
            transactions = etherscan_account_api.get_transaction_page(
                page=page, offset=offset, sort=sort, internal=internal)
        except EmptyResponse:
            transactions = []
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
        # keeps only transactions to `playerRollDice` methodID
        method_id = self.functions_signatures['playerRollDice'].hex()[:10]
        self.functions_signatures
        transactions = filter(
            lambda t: t['input'].lower().startswith(method_id),
            transactions)
        # let's not keep it as an iterator
        transactions = list(transactions)
        return transactions

    def get_last_bets_transactions(self, address=None, page=1, offset=100):
        """
        Retrieves `address` last bets from transactions and returns the list
        of bets infos. Does not return the actual roll result.
        """
        bets = []
        transactions = self.get_player_roll_dice_tx(
            address=address, page=page, offset=offset)
        for transaction in transactions:
            # from Wei to Ether
            bet_size_ether = int(transaction['value']) / 1e18
            # `playerRollDice(uint256 rollUnder)`, rollUnder is 256 bits
            # let's strip it from methodID and keep only 32 bytes
            roll_under = transaction['input'][-2*32:]
            roll_under = int(roll_under, 16)
            block_number = transaction['blockNumber']
            timestamp = transaction['timeStamp']
            date_time = datetime.utcfromtimestamp(int(timestamp, 16))
            transaction_hash = transaction['hash']
            bet = {
                'bet_size_ether': bet_size_ether,
                'roll_under': roll_under,
                'block_number': block_number,
                'timestamp': timestamp,
                'datetime': date_time,
                'transaction_hash': transaction_hash,
            }
            bets.append(bet)
        return bets

    def get_bets_logs(self, address, from_block, to_block='latest'):
        """
        Retrieves `address` last bets from event logs and returns the list
        of bets with decoded info. Does not return the actual roll result.
        """
        bets = []
        bet_events = self.get_log_bet_events(address, from_block, to_block)
        transaction_debugger = TransactionDebugger(self.contract_abi)
        for bet_event in bet_events:
            topics = [HexBytes(topic) for topic in bet_event['topics']]
            log_data = bet_event['data']
            decoded_method = transaction_debugger.decode_method(
                topics, log_data)
            call = decoded_method['call']
            bet_id = call['BetID'].hex()
            reward_value = call['RewardValue']
            reward_value_ether = round(
                reward_value / 1e18, constants.ROUND_DIGITS)
            profit_value = call['ProfitValue']
            profit_value_ether = round(
                profit_value / 1e18, constants.ROUND_DIGITS)
            bet_value = call['BetValue']
            bet_value_ether = round(bet_value / 1e18, constants.ROUND_DIGITS)
            roll_under = call['PlayerNumber']
            timestamp = bet_event['timeStamp']
            date_time = datetime.utcfromtimestamp(int(timestamp, 16))
            transaction_hash = bet_event['transactionHash']
            bet = {
                'bet_id': bet_id,
                'reward_value_ether': reward_value_ether,
                'profit_value_ether': profit_value_ether,
                'bet_value_ether': bet_value_ether,
                'roll_under': roll_under,
                'timestamp': timestamp,
                'datetime': date_time,
                'transaction_hash': transaction_hash,
            }
            bets.append(bet)
        return bets

    def get_bet_results_logs(self, address, from_block, to_block='latest'):
        """
        Retrieves `address` bet results from event logs and returns the list of
        bet results with decoded info.
        """
        results = []
        result_events = self.get_log_result_events(
            address, from_block, to_block)
        transaction_debugger = TransactionDebugger(self.contract_abi)
        for result_event in result_events:
            topics = [HexBytes(topic) for topic in result_event['topics']]
            log_data = result_event['data']
            decoded_method = transaction_debugger.decode_method(
                topics, log_data)
            call = decoded_method['call']
            bet_id = call['BetID'].hex()
            roll_under = call['PlayerNumber']
            dice_result = call['DiceResult']
            # not to be mistaken with what the user bet here, in this case it's
            # what he will receive/loss as a result of his bet
            bet_value = call['Value']
            bet_value_ether = round(bet_value / 1e18, constants.ROUND_DIGITS)
            timestamp = result_event['timeStamp']
            date_time = datetime.utcfromtimestamp(int(timestamp, 16))
            transaction_hash = result_event['transactionHash']
            bet = {
                'bet_id': bet_id,
                'roll_under': roll_under,
                'dice_result': dice_result,
                'bet_value_ether': bet_value_ether,
                'timestamp': timestamp,
                'datetime': date_time,
                'transaction_hash': transaction_hash,
            }
            results.append(bet)
        return results

    def get_last_bets_blocks(self, address):
        """
        Returns a block range containing the "last" bets.
        """
        # retrieves recent `playerRollDice` transactions
        transactions = self.get_player_roll_dice_tx(address)
        if not transactions:
            return None
        # take the oldest block of the recent transactions
        oldest_tx = transactions[-1]
        from_block = int(oldest_tx['blockNumber'])
        # makes sure this block is included in the search
        from_block -= 1
        # take the most recent block of the recent transactions
        last_tx = transactions[0]
        to_block = int(last_tx['blockNumber'])
        # the result for the last roll is included in later blocks
        to_block += 100
        ret = {
            'from_block': from_block,
            'to_block': to_block,
        }
        return ret

    @staticmethod
    def merge_logs(bet_logs, bet_results_logs):
        """
        Merges bet logs (LogBet) with bet results logs (LogResult).
        """
        merged_logs = []
        # per bet ID dictionary
        bet_results_dict = {}
        for bet_result in bet_results_logs:
            bet_id = bet_result['bet_id']
            bet_results_dict.update({
                bet_id: bet_result
            })
        for bet_log in bet_logs:
            bet_id = bet_log['bet_id']
            bet_result = bet_results_dict.get(bet_id)
            merged_log = {
                'bet_log': bet_log,
                'bet_result': bet_result,
            }
            merged_logs.append(merged_log)
        return merged_logs

    def get_merged_logs(self, address):
        last_bets_blocks = self.get_last_bets_blocks(address)
        if last_bets_blocks is None:
            return []
        from_block = last_bets_blocks['from_block']
        to_block = last_bets_blocks['to_block']
        bet_logs = self.get_bets_logs(address, from_block, to_block)
        bet_results_logs = self.get_bet_results_logs(
            address, from_block, to_block)
        merged_logs = self.merge_logs(bet_logs, bet_results_logs)
        return merged_logs

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
            topic0_1_opr = topic_opr.get('topic0_1_opr', '')
            topic0_1_opr = 'topic0_1_opr={}&'.format(topic0_1_opr) \
                if topic0_1_opr else ''
            topic1_2_opr = topic_opr.get('topic1_2_opr', '')
            topic1_2_opr = 'topic1_2_opr={}&'.format(topic1_2_opr) \
                if topic1_2_opr else ''
            topic2_3_opr = topic_opr.get('topic2_3_opr', '')
            topic2_3_opr = 'topic2_3_opr={}&'.format(topic2_3_opr) \
                if topic2_3_opr else ''
            topic0_2_opr = topic_opr.get('topic0_2_opr', '')
            topic0_2_opr = 'topic0_2_opr={}&'.format(topic0_2_opr) \
                if topic0_2_opr else ''
            topic0_3_opr = topic_opr.get('topic0_3_opr', '')
            topic0_3_opr = 'topic0_3_opr={}&'.format(topic0_3_opr) \
                if topic0_3_opr else ''
            topic1_3_opr = topic_opr.get('topic1_3_opr', '')
            topic1_3_opr = 'topic1_3_opr={}&'.format(topic1_3_opr) \
                if topic1_3_opr else ''
            url += (
                topic0_1_opr + topic1_2_opr + topic2_3_opr + topic0_2_opr +
                topic0_3_opr + topic1_3_opr)
        return url

    def get_logs(
            self, address, from_block, to_block='latest',
            topic0=None, topic1=None, topic2=None, topic3=None,
            topic_opr=None):
        """
        Currently py-etherscan-api doesn't provide support for event logs, see:
        https://github.com/corpetty/py-etherscan-api/issues/26
        """
        url = self.get_logs_url(
            address, from_block, to_block, topic0, topic1, topic2, topic3,
            topic_opr)
        response = requests.get(url)
        response = response.json()
        logs = response['result']
        return logs

    def get_log_bet_events(
            self, player_address, from_block, to_block='latest'):
        """
        Retrieves all `LogBet` events associated with `player_address`
        between two blocks.
        """
        address = self.contract_address
        topic0 = self.events_signatures['LogBet'].hex()
        # adds zero padding to match topic format (32 bytes)
        topic2 = '0x' + player_address[2:].zfill(2*32)
        topic_opr = {
            'topic0_2_opr': 'and',
        }
        logs = self.get_logs(
            address, from_block, to_block, topic0, topic2=topic2,
            topic_opr=topic_opr)
        return logs

    def get_log_result_events(
            self, player_address, from_block, to_block='latest'):
        """
        Retrieves all `LogResult` events associated with `player_address`
        between two blocks.
        """
        log_result_signature = self.events_signatures['LogResult'].hex()
        address = self.contract_address
        topic0 = log_result_signature
        # adds zero padding to match topic format (32 bytes)
        topic3 = '0x' + player_address[2:].zfill(2*32)
        topic_opr = {
            'topic0_3_opr': 'and',
        }
        logs = self.get_logs(
            address, from_block, to_block, topic0, topic3=topic3,
            topic_opr=topic_opr)
        return logs

    @staticmethod
    def compute_profit(bet_size, chances_win):
        """
        Helper method to compute profit given a bet_size and chances_win.
        """
        if chances_win <= 0 or chances_win >= 100:
            return
        house_edge = 1.0 / 100
        chances_loss = 100 - chances_win
        payout = ((chances_loss / chances_win) * bet_size) + bet_size
        payout *= (1 - house_edge)
        profit = payout - bet_size
        profit = round(profit, constants.ROUND_DIGITS)
        return profit

    def get_balance(self, address):
        """
        Retrieves the Ether balance of the given account, refs:
        https://github.com/AndreMiras/EtherollApp/issues/8
        """
        etherscan_account_api = self.ChainEtherscanAccount(
            address=address, api_key=self.etherscan_api_key)
        balance_wei = int(etherscan_account_api.get_balance())
        balance_eth = round(balance_wei / 1e18, constants.ROUND_DIGITS)
        return balance_eth
