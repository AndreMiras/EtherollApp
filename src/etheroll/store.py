import os

from kivy.app import App
from kivy.storage.jsonstore import JsonStore


class Store:

    @classmethod
    def get_store_path(cls, app=None):
        """
        Returns the full user store path.
        On Android, the store is purposely not stored on the sdcard.
        That way we don't need permission for handling user settings.
        Also losing it is not critical.
        """
        if app is None:
            app = App.get_running_app()
        user_data_dir = App.user_data_dir.fget(app)
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
