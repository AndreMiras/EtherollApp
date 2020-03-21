import logging
import threading
from io import StringIO

from kivy.utils import platform

logger = logging.getLogger(__name__)


def run_in_thread(fn):
    """
    Decorator to run a function in a thread.
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


def check_write_permission():
    """Android runtime storage permission check."""
    if platform != "android":
        return True
    from android.permissions import Permission, check_permission
    permission = Permission.WRITE_EXTERNAL_STORAGE
    return check_permission(permission)


def check_request_write_permission():
    """Android runtime storage permission check & request."""
    had_permission = check_write_permission()
    if not had_permission:
        from android.permissions import Permission, request_permission
        permission = Permission.WRITE_EXTERNAL_STORAGE
        request_permission(permission)
    return had_permission


class StringIOCBWrite(StringIO):
    """Inherits StringIO, provides callback on write."""

    def __init__(self, initial_value='', newline='\n', callback_write=None):
        """
        Overloads the StringIO.__init__() makes it possible to hook a callback
        for write operations.
        """
        self.callback_write = callback_write
        super().__init__(initial_value, newline)

    def write(self, s):
        """
        Calls the StringIO.write() method then the callback_write with
        given string parameter.
        """
        super().write(s)
        if self.callback_write is not None:
            self.callback_write(s)
