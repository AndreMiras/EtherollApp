from kivy.properties import StringProperty
from kivy.uix.boxlayout import BoxLayout

from etherollapp.etheroll.ui_utils import Dialog, load_kv_from_py

load_kv_from_py(__file__)


class PasswordForm(BoxLayout):
    __events__ = ('on_unlock',)
    password = StringProperty()

    def on_unlock(self, instance, account, password):
        pass

    @classmethod
    def dialog(cls, account):
        """Prompt the password dialog."""
        title = "Enter your password"
        password_form = cls()
        password_form.ids.account_id.text = "0x" + account.address.hex()
        dialog = Dialog.create_dialog_content_helper(
                    title=title,
                    content=password_form)
        # workaround for MDDialog container size (too small by default)
        dialog.ids.container.size_hint_y = 1
        dialog.add_action_button(
            "Unlock",
            action=lambda *x: password_form.dispatch(
                'on_unlock', dialog, account, password_form.password))
        # hitting enter on the text should also submit
        password_form.ids.password_id.bind(
            on_text_validate=lambda *x: password_form.dispatch(
                'on_unlock', dialog, account, password_form.password))
        return dialog
