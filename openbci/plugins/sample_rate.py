from __future__ import print_function
import time
import timeit
from threading import Thread

import plugin_interface as plugintypes

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
        self.polling_interval = 10

    def run(self):
        while True:
            # check FPS + listen for new connections
            new_tick = timeit.default_timer()
            elapsed_time = new_tick - self.tick
            current_samples_out = nb_samples_out
            print("--- at t: " + str(new_tick - self.start_tick) + " ---")
            print("elapsed_time: " + str(elapsed_time))
            print("nb_samples_out: " + str(current_samples_out - self.nb_samples_out))
            sampling_rate = (current_samples_out - self.nb_samples_out) / elapsed_time
            print("sampling rate: " + str(sampling_rate))
            self.tick = new_tick
            self.nb_samples_out = nb_samples_out
            time.sleep(self.polling_interval)


class PluginSampleRate(plugintypes.IPluginExtended):
    # update counters value
    def __call__(self, sample):
        global nb_samples_out
        nb_samples_out = nb_samples_out + 1

    # Instanciate "monitor" thread
    def activate(self):
        monit = Monitor()
        if len(self.args) > 0:
            monit.polling_interval = float(self.args[0])
        # daemonize thread to terminate it altogether with the main when time will come
        monit.daemon = True
        monit.start()

    def show_help(self):
        print("Optional argument: polling_interval -- in seconds, default: 10.")
