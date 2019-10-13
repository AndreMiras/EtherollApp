from kivymd.spinner import MDSpinner

from etherollapp.etheroll.ui_utils import load_kv_from_py

load_kv_from_py(__file__)


class ScrollViewSpinder(MDSpinner):

    def toggle(self, show):
        """Actually shrinking and hidding it."""
        # by default it's in "shown" mode and doesn't have attributes saved
        if not hasattr(self, 'previous_size_hint'):
            self.previous_size_hint = self.size_hint.copy()
            self.previous_opacity = self.opacity
        elif show:
            self.size_hint = self.previous_size_hint
            self.opacity = self.previous_opacity
        else:
            self.size_hint = (0, 0)
            self.opacity = 0
