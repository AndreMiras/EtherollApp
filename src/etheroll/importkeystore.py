from kivy.clock import Clock
from kivy.properties import StringProperty
from kivy.uix.boxlayout import BoxLayout

from etheroll.store import Store
from etheroll.ui_utils import load_kv_from_py

load_kv_from_py(__file__)


class ImportKeystore(BoxLayout):
    keystore_path = StringProperty()

    def __init__(self, **kwargs):
        super(ImportKeystore, self).__init__(**kwargs)
        Clock.schedule_once(self._after_init)

    def _after_init(self, dt):
        """
        Sets keystore_path.
        """
        self.keystore_path = Store.get_keystore_path()
