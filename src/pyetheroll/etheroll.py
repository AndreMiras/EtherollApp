#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Python Etheroll library.
"""
import json
from datetime import datetime

import requests
import requests_cache
from ethereum.utils import checksum_encode
from etherscan.client import EmptyResponse
from hexbytes.main import HexBytes
from pyethapp.accounts import Account
from web3 import Web3
from web3.auto import w3
from web3.contract import Contract

from ethereum_utils import AccountUtils
from pyetheroll.constants import DEFAULT_GAS_PRICE_GWEI, ROUND_DIGITS, ChainID
from pyetheroll.etherscan_utils import (ChainEtherscanAccountFactory,
                                        ChainEtherscanContractFactory,
                                        get_etherscan_api_key)
from pyetheroll.transaction_debugger import (HTTPProviderFactory,
                                             TransactionDebugger)

REQUESTS_CACHE_PARAMS = {
    'cache_name': 'requests_cache',
    'backend': 'sqlite',
    'fast_save': True,
    # we cache most of the request for a pretty long period, but not forever
    # as we still want some very outdate data to get wiped at some point
    'expire_after': 30*24*60*60,
}


class Etheroll:

    CONTRACT_ADDRESSES = {
        ChainID.MAINNET: '0xA52e014B3f5Cc48287c2D483A3E026C32cc76E6d',
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
            gas_price_gwei=DEFAULT_GAS_PRICE_GWEI):
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
                reward_value / 1e18, ROUND_DIGITS)
            profit_value = call['ProfitValue']
            profit_value_ether = round(
                profit_value / 1e18, ROUND_DIGITS)
            bet_value = call['BetValue']
            bet_value_ether = round(bet_value / 1e18, ROUND_DIGITS)
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
            bet_value_ether = round(bet_value / 1e18, ROUND_DIGITS)
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

    def get_balance(self, address):
        """
        Retrieves the Ether balance of the given account, refs:
        https://github.com/AndreMiras/EtherollApp/issues/8
        """
        etherscan_account_api = self.ChainEtherscanAccount(
            address=address, api_key=self.etherscan_api_key)
        balance_wei = int(etherscan_account_api.get_balance())
        balance_eth = round(balance_wei / 1e18, ROUND_DIGITS)
        return balance_eth
