import os

from kivy.app import App
from kivy.storage.jsonstore import JsonStore
from kivy.utils import platform

from etheroll.constants import KEYSTORE_DIR_SUFFIX


class Store:

    @classmethod
    def get_store_path(cls, app=None):
        """
        Returns the full user store path.
        """
        user_data_dir = cls.get_user_data_dir(app)
        store_path = os.path.join(user_data_dir, 'store.json')
        return store_path

    @classmethod
    def get_store(cls, app=None):
        """
        Returns user Store object.
        """
        store_path = cls.get_store_path(app)
        store = JsonStore(store_path)
        return store

    @staticmethod
    def get_user_data_dir(app=None):
        """
        Helper method to retrieve user_data_dir even when outside a running
        kivy app, e.g. a service.
        When called from a service, `app` must be defined and is an object with
        only a `name` attribute defined.
        """
        if app is None:
            app = App.get_running_app()
        return App.user_data_dir.fget(app)

    @classmethod
    def get_keystore_path(cls, app=None):
        """
        This is the Kivy default keystore path.
        """
        keystore_path = os.environ.get('KEYSTORE_PATH')
        if keystore_path is None:
            keystore_path = cls.get_default_keystore_path(app)
        return keystore_path

    @classmethod
    def get_default_keystore_path(cls, app=None):
        """
        Returns the keystore path, which is the same as the default pyethapp
        one.
        """
        # lazy loading
        KEYSTORE_DIR_PREFIX = os.path.expanduser("~")
        # uses kivy user_data_dir (/sdcard/<app_name>)
        if platform == "android":
            KEYSTORE_DIR_PREFIX = cls.get_user_data_dir(app)
        keystore_dir = os.path.join(
            KEYSTORE_DIR_PREFIX, KEYSTORE_DIR_SUFFIX)
        return keystore_dir
