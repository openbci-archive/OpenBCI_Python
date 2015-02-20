from streamer import Streamer
# requires pyosc
from OSC import OSCClient, OSCMessage

# Use OSC protocol to broadcast data (UDP layer), using "/openbci" stream. (NB. does not check numbers of channel as TCP server)

class StreamerOSC(Streamer):
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
    self.initialize()

  # the initialize method reads settings and outputs the first header
  def initialize(self):
    # init server
    self.client = OSCClient()
    self.client.connect( (self.ip, self.port) )

  # stub for API compability with streamer
  def check_connections(self):
    return
  
  # close connections, send message to client
  def uninitialize(self):
    self.client.send( OSCMessage("/quit") )
      
  # send channels values
  # as_string: many for debug, send values with a nice "[34.45, 30.4, -38.0]"-like format
  def broadcast_values(self, values):
    mes = OSCMessage(self.address)
    mes.append(values)
    self.client.send(mes )
