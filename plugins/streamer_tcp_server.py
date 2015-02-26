from threading import Thread
import socket, select, struct, time
from yapsy.IPlugin import IPlugin

# Simple TCP server to "broadcast" data to clients, handling deconnections. Binary format use network endianness (i.e., big-endian), float32

# TODO: does not listen for anything at the moment, could use it to set options

# Handling new client in separate thread
class MonitorStreamer(Thread):
	"""Launch and monitor a "Streamer" entity (incoming connections if implemented, current sampling rate)."""
	# tcp_server: the TCPServer instance that will be used
	def __init__(self, streamer):
		Thread.__init__(self)
		# bind to Streamer entity
		self.server = streamer
	
	def run(self):
		# run until we DIE
		while True:
			# check FPS + listen for new connections
			# FIXME: not so great with threads -- use a lock?
			# TODO: configure interval
			self.server.check_connections()
			time.sleep(1)


class StreamerTCPServer(IPlugin):
	"""

	Relay OpenBCI values to TCP clients

	Args:
	  port: Port of the server
	  ip: IP address of the server
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

	# From IPlugin
	def activate(self, args):
		if len(args) > 0:
			self.ip = args[0]
		if len(args) > 1:
			self.port = args[1]
		
		# init network
		print "Selecting raw TCP streaming. IP: ", self.ip, ", port: ", self.port
		self.initialize()
		
		# init the daemon that monitors connections
		self.monit = MonitorStreamer(self)
		self.monit.daemon = True
		# launch monitor
		self.monit.start()
			
		return True

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
      
	# From Streamer, to be called each time we're willing to accept new connections
	def check_connections(self):
		# First listen for new connections, and new connections only -- this is why we pass only server_socket
		read_sockets,write_sockets,error_sockets = select.select([self.server_socket],[],[], 0)
		for sock in read_sockets:
			# New connection
			sockfd, addr = self.server_socket.accept()
			self.CONNECTION_LIST.append(sockfd)
			print "Client (%s, %s) connected" % addr
		# and... don't bother with incoming messages
  
	# From IPlugin: close sockets, send message to client
	def deactivate(self):
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
	def __call__(self, sample, as_string=False):
		values=sample.channel_data
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
	
	def show_help(self):
	  	print """Optional arguments: [ip [port]]
	  	\t ip: target IP address (default: 'localhost')
	  	\t port: target port (default: 12345)"""
