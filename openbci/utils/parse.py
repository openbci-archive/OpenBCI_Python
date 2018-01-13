from constants import Constants as k


class ParseRaw(object):
    def __init__(self,
                 board_type=k.BOARD_CYTON,
                 gains=None,
                 log=False,
                 micro_volts=False,
                 scaled_output=True):
        self.board_type = board_type
        self.gains = gains
        self.log = log
        self.micro_volts = micro_volts
        self.scale_factors = []
        self.scaled_output = scaled_output

        if gains is not None:
            self.scale_factors = self.get_ads1299_scale_factors(self.gains, self.micro_volts)


    def is_stop_byte(self, byte):
        """
        Used to check and see if a byte adheres to the stop byte structure of 0xCx where x is the set of numbers
            from 0-F in hex of 0-15 in decimal.
        :param byte: {int} - The number to test
        :return: {boolean} - True if `byte` follows the correct form
        """
        return (byte & 0xF0) == k.RAW_BYTE_STOP


    def raw_to_sample(self, data):
        pass


    def get_ads1299_scale_factors(self, gains, micro_volts=None):
        out = []
        for gain in gains:
            scale_factor = k.ADS1299_VREF / float((pow(2, 23) - 1)) / float(gain)
            if micro_volts is None:
                if self.micro_volts:
                    scale_factor *= 1000000.
            else:
                if micro_volts:
                    scale_factor *= 1000000.

            out.append(scale_factor)
        return out

    def get_raw_packet_type(self, stop_byte):
        return stop_byte & 0xF




class OpenBCISample(object):
    """Object encapulsating a single sample from the OpenBCI board."""
    def __init__(self, packet_id, channel_data, aux_data, imp_data):
        self.id = packet_id
        self.channel_data = channel_data
        self.aux_data = aux_data
        self.imp_data = imp_data
