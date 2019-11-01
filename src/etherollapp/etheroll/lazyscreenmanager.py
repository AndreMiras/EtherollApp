from kivy.uix.screenmanager import ScreenManager


class LazyScreenManager(ScreenManager):

    __events__ = ('on_pre_add_widget', 'on_add_widget')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._screen_types = {}

    def on_add_widget(self, screen):
        pass

    def on_pre_add_widget(self, screen):
        pass

    def register_screen(self, cls, name):
        self._screen_types[name] = cls

    def on_current(self, instance, value):
        # creates the Screen object if it doesn't exist
        if not self.has_screen(value):
            screen = self._screen_types[value](name=value)
            self.add_widget(screen)
        super().on_current(instance, value)

    def add_widget(self, screen):
        """
        Overrides `ScreenManager.add_widget()` dispatches `on_pre_add_widget`
        and `on_add_widget` events.
        """
        self.dispatch('on_pre_add_widget', screen)
        super().add_widget(screen)
        self.dispatch('on_add_widget', screen)
