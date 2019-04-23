from __future__ import print_function
import timeit
import numpy as np
import plugin_interface as plugintypes


class PluginNoiseTest(plugintypes.IPluginExtended):
    # update counters value
    def __call__(self, sample):
        # keep tract of absolute value of
        self.diff = np.add(self.diff, np.absolute(np.asarray(sample.channel_data)))
        self.sample_count = self.sample_count + 1

        elapsed_time = timeit.default_timer() - self.last_report
        if elapsed_time > self.polling_interval:
            channel_noise_power = np.divide(self.diff, self.sample_count)

            print(channel_noise_power)
            self.diff = np.zeros(self.eeg_channels)
            self.last_report = timeit.default_timer()

    # # Instanciate "monitor" thread
    def activate(self):
        # The difference between the ref and incoming signal.
        # IMPORTANT: For noise tests, the reference and channel should have the same input signal.
        self.diff = np.zeros(self.eeg_channels)
        self.last_report = timeit.default_timer()
        self.sample_count = 0
        self.polling_interval = 1.0

        if len(self.args) > 0:
            self.polling_interval = float(self.args[0])

    def show_help(self):
        print("Optional argument: polling_interval -- in seconds, default: 10. \n \
        Returns the power of the system noise.\n \
        NOTE: The reference and channel should have the same input signal.")
