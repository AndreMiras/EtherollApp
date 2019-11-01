"""
The OSC app server makes it possible to communicate with the application from
another process.
OscAppServer -> App
"""
from time import sleep

from oscpy.server import OSCThreadServer, ServerClass

osc = OSCThreadServer()


@ServerClass
class OscAppServer:
    """OSC server used to update the app process."""

    _osc_server = None

    def __init__(self, app=None):
        """app: instance of the application to talk to"""
        self.app = app

    @classmethod
    def get_or_create(cls, app=None):
        """
        Creates the OSC server and binds the app to it.
        app: instance of the application to talk to
        """
        if cls._osc_server is None:
            osc.listen(default=True)
            cls._osc_server = cls(app)
        sockname = osc.getaddress()
        return cls._osc_server, sockname

    @classmethod
    def stop(cls):
        osc.stop()
        cls._osc_server = None

    @osc.address_method(b'/ping')
    def _callback_ping(self, *args):
        """Test method that will reply with a pong to the sender."""
        print(f'OscAppServer.ping(): {args}')
        osc.answer(b'/pong')

    @osc.address_method(b'/pong')
    def _callback_pong(self, *args):
        """Test pong method."""
        print(f'OscAppServer.pong(): {args}')

    @osc.address_method(b'/refresh_balance')
    def _callback_refresh_balance(self, *args):
        """Refreshes roll screen balance."""
        print(f'OscAppServer.refresh_balance(): {args}')
        controller = self.app.root
        roll_screen = controller.roll_screen
        roll_screen.fetch_update_balance()


def main():
    """Test main for running the OSC app server."""
    osc_app_server, sockname = OscAppServer.get_or_create()
    print(sockname)
    sleep(100)


if __name__ == '__main__':
    main()
