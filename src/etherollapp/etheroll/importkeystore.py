from kivy.clock import Clock
from kivy.properties import StringProperty
from kivy.uix.boxlayout import BoxLayout

from etherollapp.etheroll.settings import Settings
from etherollapp.etheroll.ui_utils import load_kv_from_py

load_kv_from_py(__file__)


class ImportKeystore(BoxLayout):
    keystore_path = StringProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(self.load_keystore_path)

    def load_keystore_path(self, dt=None):
        """Updates keystore path displayed in the UI."""
        self.keystore_path = Settings.get_keystore_path()
