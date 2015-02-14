import open_bci_v3 as bci
import tcp_server
import time
from threading import Thread

# Transmit data to openvibe acquisition server (no interpolation)

# Listen to new connections every second

SERVER_PORT=12345
SERVER_IP="localhost"
NB_CHANNELS=8

# counter for sampling rate
nb_samples_out = -1

tick=time.time()

# try to ease work for main loop
class Monitor(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.nb_samples_out = -1
        # Init time to compute sampling rate
        self.tick = time.time()
        self.start_tick = self.tick

    def run(self):
      while True:
        # check FPS + listen for new connections
        new_tick = time.time()
        elapsed_time = new_tick - self.tick
        current_samples_out = nb_samples_out
        print "--- at t: ", (new_tick - self.start_tick), " ---"
        print "elapsed_time: ", elapsed_time
        print "nb_samples_out: ", current_samples_out - self.nb_samples_out
        sampling_rate = (current_samples_out - self.nb_samples_out)  / elapsed_time
        print "sampling rate: ", sampling_rate
        self.tick = new_tick
        self.nb_samples_out = nb_samples_out
        # time to watch for connection
        # FIXME: not so great with threads
        server.check_connections()
        time.sleep(1)

def streamData(sample):
  # update counters
  global nb_samples_out
  # send to clients current sample
  server.broadcast_values(sample.channel_data)
  nb_samples_out = nb_samples_out + 1


if __name__ == '__main__':
  # init server
  server = tcp_server.TCPServer(ip=SERVER_IP, port=SERVER_PORT, nb_channels=NB_CHANNELS)
  # init board
  port = '/dev/ttyUSB0'
  baud = 115200
  monit = Monitor()
  # daemonize theard to terminate it altogether with the main when time will come
  monit.daemon = True
  monit.start()
  board = bci.OpenBCIBoard(port=port, baud=baud, filter_data=False)
  board.startStreaming(streamData)
