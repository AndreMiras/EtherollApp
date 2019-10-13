import os

from etherollapp.pyethapp_accounts import Account


class AccountUtils:

    singleton = None

    def __init__(self, keystore_dir):
        self.keystore_dir = keystore_dir
        self._accounts = None
        os.makedirs(keystore_dir, exist_ok=True)

    @classmethod
    def get_or_create(cls, keystore_dir):
        """Gets or creates the AccountUtils object so it loads lazily."""
        if cls.singleton is None or \
                cls.singleton.keystore_dir != keystore_dir:
            cls.singleton = cls(keystore_dir=keystore_dir)
        return cls.singleton

    def get_account_list(self):
        """Returns the Account list."""
        if self._accounts is not None:
            return self._accounts
        keyfiles = []
        for item in os.listdir(self.keystore_dir):
            item_path = os.path.join(self.keystore_dir, item)
            if os.path.isfile(item_path):
                keyfiles.append(item_path)
        # starts caching after `listdir()` call so if it fails
        # (e.g. `PermissionError`) account list won't be empty next call
        self._accounts = []
        for keyfile in keyfiles:
            account = Account.load(path=keyfile)
            self._accounts.append(account)
        return self._accounts

    def new_account(self, password, iterations=None):
        """Creates an account on the disk and returns it."""
        account = Account.new(password, uuid=None, iterations=iterations)
        account.path = os.path.join(self.keystore_dir, account.address.hex())
        self.add_account(account)
        return account

    def add_account(self, account):
        with open(account.path, 'w') as f:
            f.write(account.dump())
        if self._accounts is None:
            self._accounts = []
        self._accounts.append(account)
        return account

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
        keystore_dir = self.keystore_dir
        deleted_keystore_dir = self.deleted_account_dir(keystore_dir)
        # create the deleted account dir if required
        if not os.path.exists(deleted_keystore_dir):
            os.makedirs(deleted_keystore_dir)
        # "removes" it from the file system
        account_filename = os.path.basename(account.path)
        deleted_account_path = os.path.join(
            deleted_keystore_dir, account_filename)
        shutil.move(account.path, deleted_account_path)
        self._accounts.remove(account)
