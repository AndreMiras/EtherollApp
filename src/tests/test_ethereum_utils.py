import os
import shutil
import unittest
from tempfile import mkdtemp

from ethereum_utils import AccountUtils

PASSWORD = "password"


class TestAccountUtils(unittest.TestCase):

    def setUp(self):
        self.keystore_dir = mkdtemp()
        self.account_utils = AccountUtils(self.keystore_dir)

    def tearDown(self):
        shutil.rmtree(self.keystore_dir, ignore_errors=True)

    def test_new_account(self):
        """
        Simple account creation test case.
        1) verifies the current account list is empty
        2) creates a new account and verify we can retrieve it
        3) tries to unlock the account
        """
        # 1) verifies the current account list is empty
        account_list = self.account_utils.get_account_list()
        self.assertEqual(len(account_list), 0)
        # 2) creates a new account and verify we can retrieve it
        password = PASSWORD
        account = self.account_utils.new_account(password)
        account_list = self.account_utils.get_account_list()
        self.assertEqual(len(account_list), 1)
        self.assertEqual(account, self.account_utils.get_account_list()[0])
        # 3) tries to unlock the account
        # it's unlocked by default after creation
        self.assertFalse(account.locked)
        # let's lock it and unlock it back
        account.lock()
        self.assertTrue(account.locked)
        account.unlock(password)
        self.assertFalse(account.locked)

    def test_deleted_account_dir(self):
        """
        The deleted_account_dir() helper method should be working
        with and without trailing slash.
        """
        expected_deleted_keystore_dir = '/tmp/keystore-deleted'
        keystore_dirs = [
            # without trailing slash
            '/tmp/keystore',
            # with one trailing slash
            '/tmp/keystore/',
            # with two trailing slashes
            '/tmp/keystore//',
        ]
        for keystore_dir in keystore_dirs:
            self.assertEqual(
                AccountUtils.deleted_account_dir(keystore_dir),
                expected_deleted_keystore_dir)

    def test_delete_account(self):
        """
        Creates a new account and delete it.
        Then verify we can load the account from the backup/trash location.
        """
        password = PASSWORD
        account = self.account_utils.new_account(password)
        address = account.address
        self.assertEqual(len(self.account_utils.get_account_list()), 1)
        # deletes the account and verifies it's not loaded anymore
        self.account_utils.delete_account(account)
        self.assertEqual(len(self.account_utils.get_account_list()), 0)
        # even recreating the AccountUtils object
        self.account_utils = AccountUtils(self.keystore_dir)
        self.assertEqual(len(self.account_utils.get_account_list()), 0)
        # tries to reload it from the backup/trash location
        deleted_keystore_dir = AccountUtils.deleted_account_dir(
            self.keystore_dir)
        self.account_utils = AccountUtils(deleted_keystore_dir)
        self.assertEqual(len(self.account_utils.get_account_list()), 1)
        self.assertEqual(
            self.account_utils.get_account_list()[0].address, address)

    def test_delete_account_already_exists(self):
        """
        If the destination (backup/trash) directory where the account is moved
        already exists, it should be handled gracefully.
        This could happens if the account gets deleted, then reimported and
        deleted again, refs:
        https://github.com/AndreMiras/PyWallet/issues/88
        """
        password = PASSWORD
        account = self.account_utils.new_account(password)
        # creates a file in the backup/trash folder that would conflict
        # with the deleted account
        deleted_keystore_dir = AccountUtils.deleted_account_dir(
            self.keystore_dir)
        os.makedirs(deleted_keystore_dir)
        account_filename = os.path.basename(account.path)
        deleted_account_path = os.path.join(
            deleted_keystore_dir, account_filename)
        # create that file
        open(deleted_account_path, 'a').close()
        # then deletes the account and verifies it worked
        self.assertEqual(len(self.account_utils.get_account_list()), 1)
        self.account_utils.delete_account(account)
        self.assertEqual(len(self.account_utils.get_account_list()), 0)
