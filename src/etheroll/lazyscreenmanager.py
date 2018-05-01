from kivy.uix.screenmanager import ScreenManager


class LazyScreenManager(ScreenManager):

    def __init__(self, **kwargs):
        super(LazyScreenManager, self).__init__(**kwargs)
        self._screen_types = {}

    def register_screen(self, cls, name):
        self._screen_types[name] = cls

    def on_current(self, instance, value):
        """
        TODO
        """
        # creates the Screen object if it doesn't exist
        if not self.has_screen(value):
            screen = self._screen_types[value](name=value)
            self.add_widget(screen)
        super(LazyScreenManager, self).on_current(instance, value)
