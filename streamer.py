import time, timeit
import tcp_server
from threading import Thread

# Launch and monitor TCP server (incoming connections, current sampling rate).
class Streamer(Thread):
	# tcp_server: the TCPServer instance that will be used
	def __init__(self, tcp_server):
		Thread.__init__(self)
		self.nb_samples_out = 0
		self.last_samples_out = 0
		# Init time to compute sampling rate
		self.tick = timeit.default_timer()
		self.start_tick = self.tick
		# bind to server
		self.server = tcp_server
		# wait for first values before it computes sampling rate
		self.receiving = False
		

	def run(self):
		# run until we DIE
		while True:
			# check FPS + listen for new connections
			new_tick = timeit.default_timer()
			if self.receiving:
				# could be updated at the same time, retreived current value
				current_samples_out = self.nb_samples_out
				elapsed_time = new_tick - self.tick
				print "--- at t: ", (new_tick - self.start_tick), " ---"
				print "elapsed_time: ", elapsed_time
				print "nb_samples_out: ", current_samples_out - self.last_samples_out
				sampling_rate = (current_samples_out - self.last_samples_out)  / elapsed_time
				print "sampling rate: ", sampling_rate
				self.last_samples_out = current_samples_out
			self.tick = new_tick
			# time to watch for connection
			# FIXME: not so great with threads
			self.server.check_connections()
			time.sleep(1)
	
	# callback function to call with each sample received from the board
	def send(self, sample):
		# one more line to keep compability with current API...
		self.receiving = True
		# send to clients current sample
		self.server.broadcast_values(sample.channel_data)
		# update counter
		self.nb_samples_out = self.nb_samples_out + 1