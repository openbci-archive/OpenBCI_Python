import open_bci_v3 as bci
import time
import timeit
from threading import Thread

# counter for sampling rate
nb_samples_out = -1

# try to ease work for main loop
class Monitor(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.nb_samples_out = -1
        # Init time to compute sampling rate
        self.tick = timeit.default_timer()
        self.start_tick = self.tick

    def run(self):
      while True:
        # check FPS + listen for new connections
        new_tick = timeit.default_timer()
        elapsed_time = new_tick - self.tick
        current_samples_out = nb_samples_out
        print "--- at t: ", (new_tick - self.start_tick), " ---"
        print "elapsed_time: ", elapsed_time
        print "nb_samples_out: ", current_samples_out - self.nb_samples_out
        sampling_rate = (current_samples_out - self.nb_samples_out)  / elapsed_time
        print "sampling rate: ", sampling_rate
        self.tick = new_tick
        self.nb_samples_out = nb_samples_out
        time.sleep(10)


def count(sample):
  # update counters
  global nb_samples_out
  nb_samples_out = nb_samples_out + 1

if __name__ == '__main__':
  # init board
  port = '/dev/ttyUSB0'
  baud = 115200
  monit = Monitor()
  # daemonize thread to terminate it altogether with the main when time will come
  monit.daemon = True
  monit.start()
  board = bci.OpenBCIBoard(port=port, baud=baud, filter_data=False)
  board.startStreaming(count)
