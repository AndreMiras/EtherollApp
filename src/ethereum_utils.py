import os

import eth_keyfile
from ethereum.tools import keys
from ethereum.utils import is_string, to_string
from pyethapp.accounts import Account
from web3.auto import w3


class AccountUtils():

    def __init__(self, keystore_dir):
        # must be imported after `patch_find_library_android()`
        from devp2p.app import BaseApp
        from pyethapp.accounts import AccountsService
        self.keystore_dir = keystore_dir
        self.app = BaseApp(
            config=dict(accounts=dict(keystore_dir=self.keystore_dir)))
        AccountsService.register_with_app(self.app)
        self.patch_ethereum_tools_keys()

    def get_account_list(self):
        """
        Returns the Account list.
        """
        accounts = self.app.services.accounts
        return accounts

    @staticmethod
    def get_private_key(wallet_path, wallet_password):
        """
        Given wallet path and password, returns private key.
        Made this way to workaround pyethapp slow account management:
        https://github.com/ethereum/pyethapp/issues/292
        """
        encrypted_key = open(wallet_path).read()
        private_key = w3.eth.account.decrypt(encrypted_key, wallet_password)
        return private_key

    def new_account(self, password):
        """
        Creates an account on the disk and returns it.
        """
        account = Account.new(password, uuid=None)
        account.path = os.path.join(
            self.app.services.accounts.keystore_dir,
            account.address.hex())
        self.app.services.accounts.add_account(account)
        return account

    @staticmethod
    def patch_ethereum_tools_keys():
        """
        Patches `make_keystore_json()` to use `create_keyfile_json()`, see:
        https://github.com/ethereum/pyethapp/issues/292
        """
        keys.make_keystore_json = eth_keyfile.create_keyfile_json

        def decode_keyfile_json(raw_keyfile_json, password):
            if not is_string(password):
                password = to_string(password)
            return eth_keyfile.decode_keyfile_json(raw_keyfile_json, password)
        keys.decode_keystore_json = decode_keyfile_json
