from streamer import Streamer
import socket, select, struct

# Simple TCP server to broadcast data to clients, handling deconnections. Binary format use network endianness (i.e., big-endian), float32

# TODO: does not listen for anything at the moment, could use it to set options

# let's define a new box class that inherits from OVBox
class StreamerTCPServer(Streamer):
  """

  Relay OpenBCI values to TCP clients

  Args:
    port: Port of the server
    IP: IP address of the server
    nb_channels: number of channels of the device
    
  """
      
  def __init__(self, ip='localhost', port=12345, nb_channels=8):
    # list of socket clients
    self.CONNECTION_LIST = []
    # connection infos
    self.ip = ip
    self.port = port
    self.nb_channels=nb_channels
    # format for binary data, network endian (big) and float (float32)
    self.packer = struct.Struct('!%sf' % self.nb_channels)
    self.initialize()

  # the initialize method reads settings and outputs the first header
  def initialize(self):
    # init server
    self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # this has no effect, why ?
    self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # create connection
    self.server_socket.bind((self.ip, self.port))
    self.server_socket.listen(1)
    print "Server started on port " + str(self.port)
      
  # To be called each time you're willing to accept new connections
  def check_connections(self):
    # First listen for new connections, and new connections only -- this is why we pass only server_socket
    read_sockets,write_sockets,error_sockets = select.select([self.server_socket],[],[], 0)
    for sock in read_sockets:
      # New connection
      sockfd, addr = self.server_socket.accept()
      self.CONNECTION_LIST.append(sockfd)
      print "Client (%s, %s) connected" % addr
    # and... don't bother with incoming messages
  
  # close sockets, send message to client
  def uninitialize(self):
    # close all remote connections
    for sock in self.CONNECTION_LIST:
      if sock != self.server_socket:
        try:
          sock.send("closing!\n")
        # at this point don't bother if message not sent
        except:
          continue
        sock.close();
    # close server socket
    self.server_socket.close();
      
  # broadcast channels values to all clients
  # as_string: many for debug, send values with a nice "[34.45, 30.4, -38.0]"-like format
  def broadcast_values(self, values, as_string=False):
    # We expect a certain amount of data to send in correct format
    # TODO: raise error
    if len(values) != self.nb_channels:
      print "ERROR: ", self.nb_channels, " channels configured but ", len(values), " values given"
      return
    # save sockets that are closed to remove them later on
    outdated_list = []
    for sock in self.CONNECTION_LIST:
      # If one error should happen, we remove socket from the list
      try:
        if as_string:
          sock.send(str(values) + "\n")
        else:
          # convert values to bytes
          packed_data = self.packer.pack(*values)
          sock.send(packed_data)
        # TODO: should check if the correct number of bytes passed through
      except:
        # sometimes (always?) it's only during the second write to a close socket that an error is raised?
        print "Something bad happened, will close socket"
        outdated_list.append(sock)
    # now we are outside of the main list, it's time to remove outdated sockets, if any
    for bad_sock in outdated_list:
      print "Removing socket..."
      self.CONNECTION_LIST.remove(bad_sock)
      # not very costly to be polite
      bad_sock.close()
 
