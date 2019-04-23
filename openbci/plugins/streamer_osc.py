from __future__ import print_function
# requires python-osc
from pythonosc import osc_message_builder
from pythonosc import udp_client
import plugin_interface as plugintypes


# Use OSC protocol to broadcast data (UDP layer), using "/openbci" stream.
# (NB. does not check numbers of channel as TCP server)

class StreamerOSC(plugintypes.IPluginExtended):
    """
    Relay OpenBCI values to OSC clients

    Args:
      port: Port of the server
      ip: IP address of the server
      address: name of the stream
    """

    def __init__(self, ip='localhost', port=12345, address="/openbci"):
        # connection infos
        self.ip = ip
        self.port = port
        self.address = address

    # From IPlugin
    def activate(self):
        if len(self.args) > 0:
            self.ip = self.args[0]
        if len(self.args) > 1:
            self.port = int(self.args[1])
        if len(self.args) > 2:
            self.address = self.args[2]
        # init network
        print("Selecting OSC streaming. IP: " + self.ip + ", port: " +
              str(self.port) + ", address: " + self.address)
        self.client = udp_client.SimpleUDPClient(self.ip, self.port)

    # From IPlugin: close connections, send message to client
    def deactivate(self):
        self.client.send_message("/quit")

    # send channels values
    def __call__(self, sample):
        # silently pass if connection drops
        try:
            self.client.send_message(self.address, sample.channel_data)
        except:
            return

    def show_help(self):
        print("""Optional arguments: [ip [port [address]]]
        \t ip: target IP address (default: 'localhost')
        \t port: target port (default: 12345)
        \t address: select target address (default: '/openbci')""")
