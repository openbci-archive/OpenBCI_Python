from __future__ import print_function
import plugin_interface as plugintypes


class PluginPrint(plugintypes.IPluginExtended):
    def activate(self):
        print("Print activated")

    # called with each new sample
    def __call__(self, sample):
        if sample:
            # print impedance if supported
            if self.imp_channels > 0:
                sample_string = "ID: %f\n%s\n%s\n%s" %\
                                (sample.id, str(sample.channel_data)[1:-1],
                                 str(sample.aux_data)[1:-1], str(sample.imp_data)[1:-1])
            else:
                sample_string = "ID: %f\n%s\n%s" % (
                    sample.id, str(sample.channel_data)[1:-1], str(sample.aux_data)[1:-1])
            print("---------------------------------")
            print(sample_string)
            print("---------------------------------")

    # DEBBUGING
    # try:
    #     sample_string.decode('ascii')
    # except UnicodeDecodeError:
    #     print("Not a ascii-encoded unicode string")
    # else:
    #     print(sample_string)
