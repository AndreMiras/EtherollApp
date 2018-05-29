import os


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
        accounts_service = self.app.services.accounts
        return accounts_service.accounts

    @staticmethod
    def get_private_key(wallet_path, wallet_password):
        """
        Given wallet path and password, returns private key.
        Made this way to workaround pyethapp slow account management:
        https://github.com/ethereum/pyethapp/issues/292
        """
        # lazy loading
        from web3.auto import w3
        encrypted_key = open(wallet_path).read()
        private_key = w3.eth.account.decrypt(encrypted_key, wallet_password)
        return private_key

    def new_account(self, password):
        """
        Creates an account on the disk and returns it.
        """
        # lazy loading
        from pyethapp.accounts import Account
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
        # lazy loading
        import eth_keyfile
        from ethereum.tools import keys
        from ethereum.utils import is_string, to_string
        keys.make_keystore_json = eth_keyfile.create_keyfile_json

        def decode_keyfile_json(raw_keyfile_json, password):
            if not is_string(password):
                password = to_string(password)
            return eth_keyfile.decode_keyfile_json(raw_keyfile_json, password)
        keys.decode_keystore_json = decode_keyfile_json

    @staticmethod
    def deleted_account_dir(keystore_dir):
        """
        Given a `keystore_dir`, returns the corresponding
        `deleted_keystore_dir`.
        >>> keystore_dir = '/tmp/keystore'
        >>> AccountUtils.deleted_account_dir(keystore_dir)
        u'/tmp/keystore-deleted'
        >>> keystore_dir = '/tmp/keystore/'
        >>> AccountUtils.deleted_account_dir(keystore_dir)
        u'/tmp/keystore-deleted'
        """
        keystore_dir = keystore_dir.rstrip('/')
        keystore_dir_name = os.path.basename(keystore_dir)
        deleted_keystore_dir_name = "%s-deleted" % (keystore_dir_name)
        deleted_keystore_dir = os.path.join(
            os.path.dirname(keystore_dir),
            deleted_keystore_dir_name)
        return deleted_keystore_dir

    def delete_account(self, account):
        """
        Deletes the given `account` from the `keystore_dir` directory.
        Then deletes it from the `AccountsService` account manager instance.
        In fact, moves it to another location; another directory at the same
        level.
        """
        # lazy loading
        import shutil
        keystore_dir = self.app.services.accounts.keystore_dir
        deleted_keystore_dir = self.deleted_account_dir(keystore_dir)
        # create the deleted account dir if required
        if not os.path.exists(deleted_keystore_dir):
            os.makedirs(deleted_keystore_dir)
        # "removes" it from the file system
        account_filename = os.path.basename(account.path)
        deleted_account_path = os.path.join(
            deleted_keystore_dir, account_filename)
        shutil.move(account.path, deleted_account_path)
        # deletes it from the `AccountsService` account manager instance
        accounts_service = self.app.services.accounts
        accounts_service.accounts.remove(account)
