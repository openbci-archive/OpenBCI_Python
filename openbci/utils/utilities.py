def get_raw_packet_type(stop_byte):
    return stop_byte & 0xF


def sample_number_normalize(sample_number=None):
    if sample_number is None:
        if sample_number > 255:
            sample_number = 255
    else:
        sample_number = 0x45

    return sample_number


def sample_packet(sample_number):
    return bytearray([0xA0, sample_number_normalize(sample_number), 0, 0, 1, 0, 0, 2, 0, 0, 3, 0, 0, 4, 0, 0, 5, 0, 0, 6, 0, 0, 7, 0, 0, 8, 0, 0, 0, 1, 0, 2, makeTailByteFromPacketType(k.OBCIStreamPacketStandardAccel)]);


def sample_packet_zero(sample_number):
    return bytearray([0xA0, sample_number_normalize(sample_number), 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, makeTailByteFromPacketType(k.OBCIStreamPacketStandardAccel)]);


def sample_packet_real(sample_number):
    return bytearray([0xA0, sample_number_normalize(sample_number), 0x8F, 0xF2, 0x40, 0x8F, 0xDF, 0xF4, 0x90, 0x2B, 0xB6, 0x8F, 0xBF, 0xBF, 0x7F, 0xFF, 0xFF, 0x7F, 0xFF, 0xFF, 0x94, 0x25, 0x34, 0x20, 0xB6, 0x7D, 0, 0xE0, 0, 0xE0, 0x0F, 0x70, makeTailByteFromPacketType(k.OBCIStreamPacketStandardAccel)]);


def sample_packet_standard_raw_aux(sample_number):
    return bytearray([0xA0, sample_number_normalize(sample_number), 0, 0, 1, 0, 0, 2, 0, 0, 3, 0, 0, 4, 0, 0, 5, 0, 0, 6, 0, 0, 7, 0, 0, 8, 0, 1, 2, 3, 4, 5, makeTailByteFromPacketType(k.OBCIStreamPacketStandardRawAux)]);


def sample_packet_accel_time_sync_set(sample_number):
    return bytearray([0xA0, sample_number_normalize(sample_number), 0, 0, 1, 0, 0, 2, 0, 0, 3, 0, 0, 4, 0, 0, 5, 0, 0, 6, 0, 0, 7, 0, 0, 8, 0, 1, 0, 0, 0, 1, makeTailByteFromPacketType(k.OBCIStreamPacketAccelTimeSyncSet)]);


def sample_packet_accel_time_synced(sample_number):
    return bytearray([0xA0, sample_number_normalize(sample_number), 0, 0, 1, 0, 0, 2, 0, 0, 3, 0, 0, 4, 0, 0, 5, 0, 0, 6, 0, 0, 7, 0, 0, 8, 0, 1, 0, 0, 0, 1, makeTailByteFromPacketType(k.OBCIStreamPacketAccelTimeSynced)]);


def sample_packet_raw_aux_time_sync_set(sample_number):
    return bytearray([0xA0, sample_number_normalize(sample_number), 0, 0, 1, 0, 0, 2, 0, 0, 3, 0, 0, 4, 0, 0, 5, 0, 0, 6, 0, 0, 7, 0, 0, 8, 0x00, 0x01, 0, 0, 0, 1, makeTailByteFromPacketType(k.OBCIStreamPacketRawAuxTimeSyncSet)]);


def sample_packet_raw_aux_time_synced(sample_number):
    return bytearray([0xA0, sample_number_normalize(sample_number), 0, 0, 1, 0, 0, 2, 0, 0, 3, 0, 0, 4, 0, 0, 5, 0, 0, 6, 0, 0, 7, 0, 0, 8, 0x00, 0x01, 0, 0, 0, 1, makeTailByteFromPacketType(k.OBCIStreamPacketRawAuxTimeSynced)]);


def sample_packet_impedance(channel_number):
    return bytearray([0xA0, channel_number, 54, 52, 49, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, makeTailByteFromPacketType(k.OBCIStreamPacketImpedance)]);


def sample_packet_user_defined():
    return bytearray([0xA0, 0x00, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, makeTailByteFromPacketType(k.OBCIStreamPacketUserDefinedType)]);
