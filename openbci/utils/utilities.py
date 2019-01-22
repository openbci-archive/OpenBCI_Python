from openbci.utils.constants import Constants


def make_tail_byte_from_packet_type(packet_type):
    """
    Converts a packet type {Number} into a OpenBCI stop byte
    :param packet_type: {int} The number to smash on to the stop byte. Must be 0-15,
          out of bounds input will result in a 0
    :return: A properly formatted OpenBCI stop byte
    """
    if packet_type < 0 or packet_type > 15:
        packet_type = 0

    return Constants.RAW_BYTE_STOP | packet_type


def sample_number_normalize(sample_number=None):
    if sample_number is not None:
        if sample_number > Constants.SAMPLE_NUMBER_MAX_CYTON:
            sample_number = Constants.SAMPLE_NUMBER_MAX_CYTON
    else:
        sample_number = 0x45

    return sample_number


def sample_packet(sample_number=0x45):
    return bytearray(
        [0xA0, sample_number_normalize(sample_number), 0, 0, 1, 0, 0, 2, 0, 0, 3, 0, 0, 4, 0, 0, 5,
         0, 0, 6, 0, 0, 7, 0,
         0, 8, 0, 0, 0, 1, 0, 2,
         make_tail_byte_from_packet_type(Constants.RAW_PACKET_TYPE_STANDARD_ACCEL)])


def sample_packet_zero(sample_number):
    return bytearray(
        [0xA0, sample_number_normalize(sample_number), 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
         0, 0, 0, 0, 0, 0, 0,
         0, 0, 0, 0, 0, 0, 0, 0,
         make_tail_byte_from_packet_type(Constants.RAW_PACKET_TYPE_STANDARD_ACCEL)])


def sample_packet_real(sample_number):
    return bytearray(
        [0xA0, sample_number_normalize(sample_number), 0x8F, 0xF2, 0x40, 0x8F, 0xDF, 0xF4, 0x90,
         0x2B, 0xB6, 0x8F, 0xBF,
         0xBF, 0x7F, 0xFF, 0xFF, 0x7F, 0xFF, 0xFF, 0x94, 0x25, 0x34, 0x20, 0xB6, 0x7D, 0, 0xE0, 0,
         0xE0, 0x0F, 0x70,
         make_tail_byte_from_packet_type(Constants.RAW_PACKET_TYPE_STANDARD_ACCEL)])


def sample_packet_standard_raw_aux(sample_number):
    return bytearray(
        [0xA0, sample_number_normalize(sample_number), 0, 0, 1, 0, 0, 2, 0, 0, 3, 0, 0, 4, 0, 0, 5,
         0, 0, 6, 0, 0, 7, 0,
         0, 8, 0, 1, 2, 3, 4, 5,
         make_tail_byte_from_packet_type(Constants.RAW_PACKET_TYPE_STANDARD_RAW_AUX)])


def sample_packet_accel_time_sync_set(sample_number):
    return bytearray(
        [0xA0, sample_number_normalize(sample_number), 0, 0, 1, 0, 0, 2, 0, 0, 3, 0, 0, 4, 0, 0, 5,
         0, 0, 6, 0, 0, 7, 0,
         0, 8, 0, 1, 0, 0, 0, 1,
         make_tail_byte_from_packet_type(Constants.RAW_PACKET_TYPE_ACCEL_TIME_SYNC_SET)])


def sample_packet_accel_time_synced(sample_number):
    return bytearray(
        [0xA0, sample_number_normalize(sample_number), 0, 0, 1, 0, 0, 2, 0, 0, 3, 0, 0, 4, 0, 0, 5,
         0, 0, 6, 0, 0, 7, 0,
         0, 8, 0, 1, 0, 0, 0, 1,
         make_tail_byte_from_packet_type(Constants.RAW_PACKET_TYPE_ACCEL_TIME_SYNCED)])


def sample_packet_raw_aux_time_sync_set(sample_number):
    return bytearray(
        [0xA0, sample_number_normalize(sample_number), 0, 0, 1, 0, 0, 2, 0, 0, 3, 0, 0, 4, 0, 0, 5,
         0, 0, 6, 0, 0, 7, 0,
         0, 8, 0x00, 0x01, 0, 0, 0, 1,
         make_tail_byte_from_packet_type(Constants.RAW_PACKET_TYPE_RAW_AUX_TIME_SYNC_SET)])


def sample_packet_raw_aux_time_synced(sample_number):
    return bytearray(
        [0xA0, sample_number_normalize(sample_number), 0, 0, 1, 0, 0, 2, 0, 0, 3, 0, 0, 4, 0, 0, 5,
         0, 0, 6, 0, 0, 7, 0,
         0, 8, 0x00, 0x01, 0, 0, 0, 1,
         make_tail_byte_from_packet_type(Constants.RAW_PACKET_TYPE_RAW_AUX_TIME_SYNCED)])


def sample_packet_impedance(channel_number):
    return bytearray(
        [0xA0, channel_number, 54, 52, 49, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
         0, 0, 0, 0, 0, 0, 0,
         0, make_tail_byte_from_packet_type(Constants.RAW_PACKET_TYPE_IMPEDANCE)])


def sample_packet_user_defined():
    return bytearray(
        [0xA0, 0x00, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
         1, 1, 1, 1,
         make_tail_byte_from_packet_type(Constants.OBCIStreamPacketUserDefinedType)])
