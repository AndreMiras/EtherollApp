from kivy.app import App
from kivy.clock import mainthread
from kivy.properties import StringProperty
from kivy.uix.boxlayout import BoxLayout

from etherollapp.etheroll.ui_utils import Dialog, load_kv_from_py
from etherollapp.etheroll.utils import run_in_thread

load_kv_from_py(__file__)


class CreateNewAccount(BoxLayout):
    """Makes it possible to create json keyfiles."""

    new_password1 = StringProperty()
    new_password2 = StringProperty()

    def verify_password_field(self):
        """Makes sure passwords are matching and are not void."""
        passwords_matching = self.new_password1 == self.new_password2
        passwords_not_void = self.new_password1 != ''
        return passwords_matching and passwords_not_void

    def verify_fields(self):
        """Verifies password fields are valid."""
        return self.verify_password_field()

    @staticmethod
    def try_unlock(account, password):
        """
        Just as a security measure, verifies we can unlock
        the newly created account with provided password.
        """
        # making sure it's locked first
        account.lock()
        try:
            account.unlock(password)
        except ValueError:
            title = "Unlock error"
            body = ""
            body += "Couldn't unlock your account.\n"
            body += "The issue should be reported."
            dialog = Dialog.create_dialog(title, body)
            dialog.open()
            return

    @mainthread
    def on_account_created(self, account):
        """Switches to the newly created account. Clears the form."""
        # TODO:
        # it would be better design if only the Controller new about the
        # CreateNewAccount and not the opposite
        controller = App.get_running_app().root
        controller.current_account = account
        self.new_password1 = ''
        self.new_password2 = ''

    @mainthread
    def toggle_widgets(self, enabled):
        """Enables/disables account creation widgets."""
        self.disabled = not enabled

    @mainthread
    def show_redirect_dialog(self):
        title = "Account created, redirecting..."
        body = ""
        body += "Your account was created, "
        body += "you will be redirected to the overview."
        dialog = Dialog.create_dialog(title, body)
        dialog.open()

    def load_landing_page(self):
        """Returns to the landing page."""
        controller = App.get_running_app().root
        screen_manager = controller.screen_manager
        screen_manager.transition.direction = 'right'
        screen_manager.current = 'roll_screen'

    @run_in_thread
    def create_account(self):
        """
        Creates an account from provided form.
        Verify we can unlock it.
        Disables widgets during the process, so the user doesn't try
        to create another account during the process.
        """
        self.toggle_widgets(False)
        if not self.verify_fields():
            Dialog.show_invalid_form_dialog()
            self.toggle_widgets(True)
            return
        password = self.new_password1
        Dialog.snackbar_message("Creating account...")
        controller = App.get_running_app().root
        account = controller.account_utils.new_account(password=password)
        Dialog.snackbar_message("Created!")
        self.toggle_widgets(True)
        self.on_account_created(account)
        # CreateNewAccount.try_unlock(account, password)
        self.show_redirect_dialog()
        self.load_landing_page()
        return account
