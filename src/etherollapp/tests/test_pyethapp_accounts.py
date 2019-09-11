"""
Adapted version of:
https://github.com/ethereum/pyethapp/blob/7fdec62/
pyethapp/tests/test_accounts.py
"""
import json
import unittest
from builtins import str
from uuid import uuid4

from eth_keys import keys
from eth_utils import remove_0x_prefix
from past.utils import old_div

from etherollapp.pyethapp_accounts import Account


class TestAccountUtils(unittest.TestCase):

    privkey = None
    password = None
    uuid = None
    account = None
    keystore = None

    @classmethod
    def setUpClass(cls):
        cls.privkey = bytes.fromhex(
            'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855')
        cls.password = 'secret'
        cls.uuid = str(uuid4())
        # keystore generation takes a while, so make this module scoped
        cls.account = Account.new(
            cls.password, cls.privkey, cls.uuid, iterations=1)
        # `account.keystore` might not contain address and id
        cls.keystore = json.loads(cls.account.dump())

    def test_account_creation(self):
        account = self.account
        privkey = self.privkey
        uuid = self.uuid
        assert not account.locked
        assert account.privkey == privkey
        pk = keys.PrivateKey(privkey)
        assert account.address.hex() == remove_0x_prefix(
            pk.public_key.to_address())
        assert account.uuid == uuid

    def test_locked(self):
        keystore = self.keystore
        uuid = self.uuid
        account = Account(keystore)
        assert account.locked
        assert account.address.hex() == remove_0x_prefix(keystore['address'])
        assert account.privkey is None
        assert account.pubkey is None
        assert account.uuid == uuid
        keystore2 = keystore.copy()
        keystore2.pop('address')
        account = Account(keystore2)
        assert account.locked
        assert account.address is None
        assert account.privkey is None
        assert account.pubkey is None
        assert account.uuid == uuid

    def test_unlock(self):
        keystore = self.keystore
        password = self.password
        privkey = self.privkey
        account = Account(keystore)
        assert account.locked
        account.unlock(password)
        assert not account.locked
        assert account.privkey == privkey
        pk = keys.PrivateKey(privkey)
        assert account.address.hex() == remove_0x_prefix(
            pk.public_key.to_address())

    def test_unlock_wrong(self):
        keystore = self.keystore
        password = self.password
        account = Account(keystore)
        assert account.locked
        with self.assertRaises(ValueError):
            account.unlock(password + '1234')
        assert account.locked
        with self.assertRaises(ValueError):
            account.unlock('4321' + password)
        assert account.locked
        with self.assertRaises(ValueError):
            account.unlock(password[:old_div(len(password), 2)])
        assert account.locked
        account.unlock(password)
        assert not account.locked
        account.unlock(password + 'asdf')
        assert not account.locked
        account.unlock(password + '1234')
        assert not account.locked

    def test_lock(self):
        account = self.account
        password = self.password
        privkey = self.privkey
        assert not account.locked
        pk = keys.PrivateKey(privkey)
        assert account.address.hex() == remove_0x_prefix(
            pk.public_key.to_address())
        assert account.privkey == privkey
        assert account.pubkey is not None
        account.unlock(password + 'fdsa')
        account.lock()
        assert account.locked
        pk = keys.PrivateKey(privkey)
        assert account.address.hex() == remove_0x_prefix(
            pk.public_key.to_address())
        assert account.privkey is None
        assert account.pubkey is None
        with self.assertRaises(ValueError):
            account.unlock(password + 'fdsa')
        account.unlock(password)

    def test_address(self):
        keystore = self.keystore
        password = self.password
        privkey = self.privkey
        keystore_wo_address = keystore.copy()
        keystore_wo_address.pop('address')
        account = Account(keystore_wo_address)
        assert account.address is None
        account.unlock(password)
        account.lock()
        pk = keys.PrivateKey(privkey)
        assert account.address.hex() == remove_0x_prefix(
            pk.public_key.to_address())

    def test_dump(self):
        account = self.account
        keystore = json.loads(
            account.dump(include_address=True, include_id=True))
        required_keys = set(['crypto', 'version'])
        assert set(keystore.keys()) == required_keys | set(['address', 'id'])
        assert remove_0x_prefix(keystore['address']) == account.address.hex()
        assert keystore['id'] == account.uuid
        keystore = json.loads(
            account.dump(include_address=False, include_id=True))
        assert set(keystore.keys()) == required_keys | set(['id'])
        assert keystore['id'] == account.uuid
        keystore = json.loads(
            account.dump(include_address=True, include_id=False))
        assert set(keystore.keys()) == required_keys | set(['address'])
        assert remove_0x_prefix(keystore['address']) == account.address.hex()
        keystore = json.loads(
            account.dump(include_address=False, include_id=False))
        assert set(keystore.keys()) == required_keys

    def test_uuid_setting(self):
        account = self.account
        uuid = account.uuid
        account.uuid = 'asdf'
        assert account.uuid == 'asdf'
        account.uuid = None
        assert account.uuid is None
        assert 'id' not in account.keystore
        account.uuid = uuid
        assert account.uuid == uuid
        assert account.keystore['id'] == uuid

    # TODO: not yet migrated
    # def test_sign(account, password):
    #     from ethereum.transactions import Transaction
    #     tx = Transaction(1, 0, 10**6, account.address, 0, '')
    #     account.sign_tx(tx)
    #     assert tx.sender == account.address
    #     account.lock()
    #     with pytest.raises(ValueError):
    #         account.sign_tx(tx)
    #     account.unlock(password)
