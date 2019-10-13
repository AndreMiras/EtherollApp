from kivy.app import App
from kivy.clock import Clock
from kivymd.toolbar import Toolbar

from etherollapp.etheroll.ui_utils import load_kv_from_py

load_kv_from_py(__file__)


class CustomToolbar(Toolbar):
    """Toolbar with helper method for loading default/back buttons."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(self.load_default_buttons)

    def load_default_buttons(self, dt=None):
        app = App.get_running_app()
        self.left_action_items = [
            ['menu', lambda x: app.root.navigation.toggle_nav_drawer()]]
        self.right_action_items = [[
                'dots-vertical',
                lambda x: app.root.navigation.toggle_nav_drawer()]]

    def load_back_button(self, function):
        self.left_action_items = [['arrow-left', lambda x: function()]]
