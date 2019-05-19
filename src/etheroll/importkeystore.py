from kivy.clock import Clock
from kivy.properties import StringProperty
from kivy.uix.boxlayout import BoxLayout

from etheroll.settings import Settings
from etheroll.ui_utils import load_kv_from_py

load_kv_from_py(__file__)


class ImportKeystore(BoxLayout):
    keystore_path = StringProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(self._after_init)

    def _after_init(self, dt):
        """
        Sets keystore_path.
        """
        self.keystore_path = Settings.get_keystore_path()
