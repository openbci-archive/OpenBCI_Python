import sys; sys.path.append('..') # help python find open_bci_v3.py relative to scripts folder
import open_bci_v3 as bci
import streamer_tcp_server
import time, timeit
from threading import Thread

# Transmit data to openvibe acquisition server, intelpolating data (well, sort of) from 250Hz to 256Hz
# Listen to new connections every second using a separate thread.

# NB: Left here for resampling algorithm, prefer the use of user.py.

NB_CHANNELS = 8

# If > 0 will interpolate based on samples count, typically 1.024 to go from 250Hz to 256Hz
SAMPLING_FACTOR = -1.024
# If > 0 will interbolate based on elapsed time
SAMPLING_RATE = 256

SERVER_PORT=12345
SERVER_IP="localhost"

DEBUG=False

# check packet drop
last_id = -1

# counter for sampling rate
nb_samples_in = -1
nb_samples_out = -1

# last seen values for interpolation
last_values = [0] * NB_CHANNELS

# counter to trigger duplications...
leftover_duplications = 0

tick=timeit.default_timer()

# try to ease work for main loop
class Monitor(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.nb_samples_in = -1
        self.nb_samples_out = -1
        # Init time to compute sampling rate
        self.tick = timeit.default_timer()
        self.start_tick = self.tick

    def run(self):
      while True:
        # check FPS + listen for new connections
        new_tick = timeit.default_timer()
        elapsed_time = new_tick - self.tick
        current_samples_in =  nb_samples_in
        current_samples_out = nb_samples_out
        print "--- at t: ", (new_tick - self.start_tick), " ---"
        print "elapsed_time: ", elapsed_time
        print "nb_samples_in: ", current_samples_in - self.nb_samples_in
        print "nb_samples_out: ", current_samples_out - self.nb_samples_out
        self.tick = new_tick
        self.nb_samples_in = nb_samples_in
        self.nb_samples_out = nb_samples_out
        # time to watch for connection
        # FIXME: not so great with threads
        server.check_connections()
        time.sleep(1)

def streamData(sample):
  
  global last_values
  
  global tick
      
  # check packet skipped
  global last_id
  # TODO: duplicate packet if skipped to stay sync
  if sample.id != last_id + 1:
    print "time", tick, ": paquet skipped!"
  if sample.id == 255:
    last_id = -1
  else:
    last_id = sample.id
  
  # update counters
  global nb_samples_in, nb_samples_out
  nb_samples_in = nb_samples_in + 1
  
  # check for duplication, by default 1 (...which is *no* duplication of the one current sample)
  global leftover_duplications
  
  # first method with sampling rate and elapsed time (depends on system clock accuracy)
  if (SAMPLING_RATE > 0):
    # elapsed time since last call, update tick
    now = timeit.default_timer()
    elapsed_time = now - tick;
    # now we have to compute how many times we should send data to keep up with sample rate (oversampling)
    leftover_duplications = SAMPLING_RATE * elapsed_time + leftover_duplications - 1
    tick = now
  # second method with a samplin factor (depends on openbci accuracy)
  elif SAMPLING_FACTOR > 0:
    leftover_duplications = SAMPLING_FACTOR + leftover_duplications - 1
  #print "needed_duplications: ", needed_duplications, "leftover_duplications: ", leftover_duplications
  # If we need to insert values, will interpolate between current packet and last one
  # FIXME: ok, at the moment because we do packet per packet treatment, only handles nb_duplications == 1 for more interpolation is bad and sends nothing
  if (leftover_duplications > 1):
    leftover_duplications = leftover_duplications - 1
    interpol_values = list(last_values)
    for i in range(0,len(interpol_values)):
      # OK, it's a very rough interpolation
      interpol_values[i] = (last_values[i] + sample.channel_data[i]) / 2
    if DEBUG:
      print "  --"
      print "  last values: ", last_values
      print "  interpolation: ", interpol_values
      print "  current sample: ", sample.channel_data
    # send to clients interpolated sample
    #leftover_duplications = 0
    server.broadcast_values(interpol_values)
    nb_samples_out = nb_samples_out + 1
    
  # send to clients current sample
  server.broadcast_values(sample.channel_data)
  nb_samples_out = nb_samples_out + 1
  
  # save current values for possible interpolation
  last_values = list(sample.channel_data)

if __name__ == '__main__':
  # init server
  server = streamer_tcp_server.StreamerTCPServer(ip=SERVER_IP, port=SERVER_PORT, nb_channels=NB_CHANNELS)
  # init board
  port = '/dev/ttyUSB1'
  baud = 115200
  monit = Monitor()
  # daemonize theard to terminate it altogether with the main when time will come
  monit.daemon = True
  monit.start()
  board = bci.OpenBCIBoard(port=port, baud=baud, filter_data=False)
  board.startStreaming(streamData)
