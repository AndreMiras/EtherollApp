import json
import logging
import os
import threading
from io import StringIO

from kivy.utils import platform

logger = logging.getLogger(__name__)


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


def get_etherscan_api_key(api_key_path: str = None) -> str:
    """
    Tries to retrieve etherscan API key from path or from environment.
    The files content should be in the form:
    ```json
    { "key" : "YourApiKeyToken" }
    ```
    """
    DEFAULT_API_KEY_TOKEN = "YourApiKeyToken"
    etherscan_api_key = os.environ.get("ETHERSCAN_API_KEY")
    if etherscan_api_key is not None:
        return etherscan_api_key
    elif api_key_path is None:
        logger.warning(
            "Cannot get Etherscan API key. "
            f"No path provided, defaulting to {DEFAULT_API_KEY_TOKEN}."
        )
        return DEFAULT_API_KEY_TOKEN
    else:
        try:
            with open(api_key_path, mode="r") as key_file:
                etherscan_api_key = json.loads(key_file.read())["key"]
        except FileNotFoundError:
            logger.warning(
                f"Cannot get Etherscan API key. File {api_key_path} not found,"
                f" defaulting to {DEFAULT_API_KEY_TOKEN}."
            )
            return DEFAULT_API_KEY_TOKEN
    return etherscan_api_key


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
