import re

from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivymd.textfields import MDTextField

from etherollapp.etheroll.ui_utils import load_kv_from_py

load_kv_from_py(__file__)


def is_number(s):
    try:
        float(s)
    except ValueError:
        return False
    return True


class MDFloatInput(MDTextField):

    pat = re.compile('[^0-9]')

    def insert_text(self, substring, from_undo=False):
        pat = self.pat
        if '.' in self.text:
            s = re.sub(pat, '', substring)
        else:
            s = '.'.join([re.sub(pat, '', s) for s in substring.split('.', 1)])
        return super().insert_text(s, from_undo=from_undo)


class Send(BoxLayout):

    current_account = ObjectProperty(allownone=True)
    __events__ = ('on_send',)

    def on_send(self, address, amount_eth):
        pass

    def on_send_release(self):
        address = self.ids.send_to_id.text
        amount_eth = float(self.ids.amount_eth_id.text)
        self.dispatch('on_send', address, amount_eth)
