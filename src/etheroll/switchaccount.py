from kivy.app import App
from kivy.clock import Clock
from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivymd.list import OneLineListItem

from etheroll.utils import Dialog, SubScreen, load_kv_from_py

load_kv_from_py(__file__)


class SwitchAccount(BoxLayout):

    def __init__(self, **kwargs):
        super(SwitchAccount, self).__init__(**kwargs)
        self.register_event_type('on_account_selected')

    def on_release(self, list_item):
        """
        Fires on_account_selected() event.
        """
        self.dispatch('on_account_selected', list_item.account)

    def on_account_selected(self, *args):
        """
        Default handler.
        """
        pass

    def create_item(self, account):
        """
        Creates an account list item from given account.
        """
        address = "0x" + account.address.hex()
        list_item = OneLineListItem(text=address)
        # makes sure the address doesn't overlap on small screen
        list_item.ids._lbl_primary.shorten = True
        list_item.account = account
        list_item.bind(on_release=lambda x: self.on_release(x))
        return list_item

    def load_account_list(self):
        """
        Fills account list widget from library account list.
        """
        self.controller = App.get_running_app().root
        account_list_id = self.ids.account_list_id
        account_list_id.clear_widgets()
        accounts = self.controller.account_utils.get_account_list()
        if len(accounts) == 0:
            self.on_empty_account_list()
        for account in accounts:
            list_item = self.create_item(account)
            account_list_id.add_widget(list_item)

    @staticmethod
    def on_empty_account_list():
        controller = App.get_running_app().root
        keystore_dir = controller.account_utils.keystore_dir
        title = "No account found"
        body = "No account found in:\n%s" % keystore_dir
        dialog = Dialog.create_dialog(title, body)
        dialog.open()


class SwitchAccountScreen(SubScreen):
    current_account = ObjectProperty(allownone=True)

    def __init__(self, **kwargs):
        super(SwitchAccountScreen, self).__init__(**kwargs)
        Clock.schedule_once(self._after_init)

    def _after_init(self, dt):
        """
        Binds SwitchAccount.on_account_selected() event.
        """
        switch_account = self.ids.switch_account_id
        switch_account.bind(
            on_account_selected=lambda
            instance, account: self.on_account_selected(account))

    def on_account_selected(self, account):
        """
        Sets current account and loads previous screen.
        """
        self.current_account = account
        self.on_back()
