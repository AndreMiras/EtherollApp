"""
The OSC app client connects to the OSC app server to communicate with the
application from another process.
OscAppClient -> OscAppServer -> App
"""
import argparse

from oscpy.client import OSCClient


class OscAppClient:
    """OSC client that talks to the OscAppServer to update the app process."""

    def __init__(self, address, port):
        self.address = address
        self.port = port
        self.osc = OSCClient(address, port)

    def send_ping(self):
        for i in range(10):
            self.osc.send_message(b'/ping', [i])

    def send_refresh_balance(self):
        self.osc.send_message(b'/refresh_balance', [])


def main():
    """Test main that sends a ping message to the specified server."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--host",  default='localhost')
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    osc_app_client = OscAppClient(args.host, args.port)
    osc_app_client.send_ping()


if __name__ == '__main__':
    main()
