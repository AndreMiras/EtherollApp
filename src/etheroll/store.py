import os

from kivy.app import App
from kivy.storage.jsonstore import JsonStore


class Store:

    @staticmethod
    def get_store_path():
        """
        Returns the full user store path.
        """
        user_data_dir = App.get_running_app().user_data_dir
        store_path = os.path.join(user_data_dir, 'store.json')
        return store_path

    @classmethod
    def get_store(cls):
        """
        Returns user Store object.
        """
        store_path = cls.get_store_path()
        store = JsonStore(store_path)
        return store
