from streamer import Streamer, MonitorStreamer
# requires pyosc
from OSC import OSCClient, OSCMessage
from yapsy.IPlugin import IPlugin

# Use OSC protocol to broadcast data (UDP layer), using "/openbci" stream. (NB. does not check numbers of channel as TCP server)
# FIXME: no need of a "Streamer" entity anymore with multiple plugins activated

class StreamerOSC(Streamer, IPlugin):
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
	def activate(self, args):
		if len(args) > 0:
			self.ip = args[0]
		if len(args) > 1:
			self.port = args[1]
		if len(args) > 2:
			self.address = args[2]
		# init network
		print "Selecting OSC streaming. IP: ", self.ip, ", port: ", self.port, ", address: ", self.address
		self.client = OSCClient()
		self.client.connect( (self.ip, self.port) )
		
		# init the daemon that monitors connections
		
		self.monit = MonitorStreamer(self)
		self.monit.daemon = True
		# launch monitor
		self.monit.start()
			
			
		return True

	# From IPlugin: close connections, send message to client
	def deactivate(self):
		self.client.send(OSCMessage("/quit") )
	  
	# from Streamer: stub for API compability
	def check_connections(self):
		return
	    
	# from Streamer: send channels values
	# as_string: many for debug, send values with a nice "[34.45, 30.4, -38.0]"-like format
	def broadcast_values(self, values):
		mes = OSCMessage(self.address)
		mes.append(values)
		self.client.send(mes)
	
	# call MonitorStreamer, that will call Streamer, that will call in here
	def __call__(self, sample):
		self.monit.send(sample)
	
	def show_help(self):
	  	print """Optional arguments: [ip [port [address]]]
	  	\t ip: target IP address (default: 'localhost')
	  	\t port: target port (default: 12345)
	  	\t address: select target address (default: '/openbci')"""
