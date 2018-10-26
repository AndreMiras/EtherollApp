import os
import threading
from io import StringIO

from kivy.app import App
from kivy.clock import mainthread
from kivy.lang import Builder
from kivy.logger import LOG_LEVELS
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen
from kivy.utils import platform
from kivymd.dialog import MDDialog
from kivymd.label import MDLabel
from kivymd.snackbar import Snackbar
from layoutmargin import AddMargin, MarginLayout
from raven import Client
from raven.conf import setup_logging
from raven.handlers.logging import SentryHandler

from version import __version__


def run_in_thread(fn):
    """
    Decorator to run a function in a thread.
    >>> 1 + 1
    2
    >>> @run_in_thread
    ... def threaded_sleep(seconds):
    ...     from time import sleep
    ...     sleep(seconds)
    >>> thread = threaded_sleep(0.1)
    >>> type(thread)
    <class 'threading.Thread'>
    >>> thread.is_alive()
    True
    >>> thread.join()
    >>> thread.is_alive()
    False
    """
    def run(*k, **kw):
        t = threading.Thread(target=fn, args=k, kwargs=kw)
        t.start()
        return t
    return run


def load_kv_from_py(f):
    """
    Loads file.kv for given file.py.
    """
    filename = os.path.basename(os.path.splitext(f)[0])
    Builder.load_file(
        os.path.join(
            os.path.dirname(os.path.abspath(f)),
            filename + '.kv'
        )
    )


def configure_sentry(in_debug=False):
    """
    Configure the Raven client, or create a dummy one if `in_debug` is `True`.
    """
    key = 'b290ecc8934f4cb599e6fa6af6cc5cc2'
    # the public DSN URL is not available on the Python client
    # so we're exposing the secret and will be revoking it on abuse
    # https://github.com/getsentry/raven-python/issues/569
    secret = '0ae02bcb5a75467d9b4431042bb98cb9'
    project_id = '1111738'
    dsn = 'https://{key}:{secret}@sentry.io/{project_id}'.format(
        key=key, secret=secret, project_id=project_id)
    if in_debug:
        client = DebugRavenClient()
    else:
        client = Client(dsn=dsn, release=__version__)
        # adds context for Android devices
        if platform == 'android':
            from jnius import autoclass
            Build = autoclass("android.os.Build")
            VERSION = autoclass('android.os.Build$VERSION')
            android_os_build = {
                'model': Build.MODEL,
                'brand': Build.BRAND,
                'device': Build.DEVICE,
                'manufacturer': Build.MANUFACTURER,
                'version_release': VERSION.RELEASE,
            }
            client.user_context({'android_os_build': android_os_build})
        # Logger.error() to Sentry
        # https://docs.sentry.io/clients/python/integrations/logging/
        handler = SentryHandler(client)
        handler.setLevel(LOG_LEVELS.get('error'))
        setup_logging(handler)
    return client


class DebugRavenClient(object):
    """
    The DebugRavenClient should be used in debug mode, it just raises
    the exception rather than capturing it.
    """

    def captureException(self):
        raise


class StringIOCBWrite(StringIO):
    """
    Inherits StringIO, provides callback on write.
    """

    def __init__(self, initial_value='', newline='\n', callback_write=None):
        """
        Overloads the StringIO.__init__() makes it possible to hook a callback
        for write operations.
        """
        self.callback_write = callback_write
        super(StringIOCBWrite, self).__init__(initial_value, newline)

    def write(self, s):
        """
        Calls the StringIO.write() method then the callback_write with
        given string parameter.
        """
        super(StringIOCBWrite, self).write(s)
        if self.callback_write is not None:
            self.callback_write(s)


class Dialog(object):

    # keeps track of all dialogs alive
    dialogs = []
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
        """
        Removes it from the dialogs track list.
        """
        with cls.__lock:
            try:
                cls.dialogs.remove(dialog)
            except ValueError:
                # fails silently if the dialog was dismissed twice, refs:
                # https://github.com/AndreMiras/PyWallet/issues/89
                pass

    @classmethod
    def dismiss_all_dialogs(cls):
        """
        Dispatches dismiss event for all dialogs.
        """
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
    """
    Helper parent class for updating toolbar on enter/leave.
    """

    def on_back(self):
        self.manager.transition.direction = 'right'
        self.manager.current = 'roll_screen'

    def on_enter(self):
        """
        Loads the toolbar back button.
        """
        app = App.get_running_app()
        app.root.ids.toolbar_id.load_back_button(self.on_back)

    def on_leave(self):
        """
        Loads the toolbar default button.
        """
        app = App.get_running_app()
        app.root.ids.toolbar_id.load_default_buttons()


class BoxLayoutMarginLayout(MarginLayout, BoxLayout):
    pass


class BoxLayoutAddMargin(AddMargin, BoxLayout):
    pass
