import os
import threading
from typing import List

from kivy.app import App
from kivy.clock import mainthread
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen
from kivymd.dialog import MDDialog
from kivymd.label import MDLabel
from kivymd.snackbar import Snackbar
from layoutmargin import AddMargin, MarginLayout


def load_kv_from_py(f):
    """Loads file.kv for given file.py."""
    filename = os.path.basename(os.path.splitext(f)[0])
    Builder.load_file(
        os.path.join(
            os.path.dirname(os.path.abspath(f)),
            filename + '.kv'
        )
    )


class Dialog:

    # keeps track of all dialogs alive
    dialogs: List[MDDialog] = []
    __lock = threading.Lock()

    @staticmethod
    @mainthread
    def snackbar_message(text):
        Snackbar(text=text).show()

    @classmethod
    def show_invalid_form_dialog(cls):
        title = "Invalid form"
        body = "Please check form fields."
        dialog = cls.create_dialog(title, body)
        dialog.open()

    @classmethod
    def on_dialog_dismiss(cls, dialog):
        """Removes it from the dialogs track list."""
        with cls.__lock:
            try:
                cls.dialogs.remove(dialog)
            except ValueError:
                # fails silently if the dialog was dismissed twice, refs:
                # https://github.com/AndreMiras/PyWallet/issues/89
                pass

    @classmethod
    def dismiss_all_dialogs(cls):
        """Dispatches dismiss event for all dialogs."""
        # keeps a local copy since we're altering them as we iterate
        dialogs = cls.dialogs[:]
        for dialog in dialogs:
            dialog.dismiss()

    @classmethod
    def create_dialog_content_helper(cls, title, content):
        """
        Creates a dialog from given title and content.
        Adds it to the dialogs track list.
        """
        # TODO
        dialog = MDDialog(
                        title=title,
                        content=content,
                        size_hint=(.8, None),
                        height=dp(250),
                        auto_dismiss=False)
        dialog.bind(on_dismiss=cls.on_dialog_dismiss)
        with cls.__lock:
            cls.dialogs.append(dialog)
        return dialog

    @classmethod
    def create_dialog_helper(cls, title, body):
        """
        Creates a dialog from given title and body.
        Adds it to the dialogs track list.
        """
        content = MDLabel(
                    font_style='Body1',
                    theme_text_color='Secondary',
                    text=body,
                    size_hint_y=None,
                    valign='top')
        content.bind(texture_size=content.setter('size'))
        dialog = cls.create_dialog_content_helper(title, content)
        return dialog

    @classmethod
    def create_dialog(cls, title, body):
        """
        Creates a dialog from given title and body.
        Adds it to the dialogs track list.
        Appends dismiss action.
        """
        dialog = cls.create_dialog_helper(title, body)
        dialog.add_action_button(
                "Dismiss",
                action=lambda *x: dialog.dismiss())
        return dialog


class SubScreen(Screen):
    """Helper parent class for updating toolbar on enter/leave."""

    def on_back(self):
        self.manager.transition.direction = 'right'
        self.manager.current = 'roll_screen'

    def on_enter(self):
        """Loads the toolbar back button."""
        app = App.get_running_app()
        app.root.ids.toolbar_id.load_back_button(self.on_back)

    def on_leave(self):
        """Loads the toolbar default button."""
        app = App.get_running_app()
        app.root.ids.toolbar_id.load_default_buttons()


class BoxLayoutMarginLayout(MarginLayout, BoxLayout):
    pass


class BoxLayoutAddMargin(AddMargin, BoxLayout):
    pass
