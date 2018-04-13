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
