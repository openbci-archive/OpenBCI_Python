from constants import Constants as k


class ParseRaw(object):
    def __init__(self, board_type=k.BOARD_CYTON, scaled_output=True, log=False):
        self.board_type = board_type
        self.log = log
        self.scaled_output = scaled_output


class OpenBCISample(object):
    """Object encapulsating a single sample from the OpenBCI board."""
    def __init__(self, packet_id, channel_data, aux_data, imp_data):
        self.id = packet_id
        self.channel_data = channel_data
        self.aux_data = aux_data
        self.imp_data = imp_data
