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

        self.raw_data_to_sample = RawDataToSample(gains=gains,
                                                  scale=scaled_output,
                                                  verbose=log)


    def is_stop_byte(self, byte):
        """
        Used to check and see if a byte adheres to the stop byte structure of 0xCx where x is the set of numbers
            from 0-F in hex of 0-15 in decimal.
        :param byte: {int} - The number to test
        :return: {boolean} - True if `byte` follows the correct form
        """
        return (byte & 0xF0) == k.RAW_BYTE_STOP

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

    """
    /**
* @description Takes a buffer filled with 3 16 bit integers from an OpenBCI device and converts based on settings
*                  of the MPU, values are in ?
* @param dataBuf - Buffer that is 6 bytes long
* @returns {Array} - Array of floats 3 elements long
* @author AJ Keller (@aj-ptw)
*/
function getDataArrayAccel (dataBuf) {
  let accelData = [];
  for (let i = 0; i < ACCEL_NUMBER_AXIS; i++) {
    let index = i * 2;
    accelData.push(utilitiesModule.interpret16bitAsInt32(dataBuf.slice(index, index + 2)) * SCALE_FACTOR_ACCEL);
  }
  return accelData;
}
    """
    def get_data_array_accel(self, data):
        pass

    def get_data_array_accel_no_scale(self, data):
        pass



    def get_raw_packet_type(self, stop_byte):
        return stop_byte & 0xF

    def parse_packet_standard_accel(self, raw_data_to_sample):

        """

        :param raw_data_to_sample: RawDataToSample
        :return:
        """

        # Check to make sure data is not null.
        if raw_data_to_sample is None:
            raise RuntimeError(k.ERROR_UNDEFINED_OR_NULL_INPUT)
        if raw_data_to_sample.raw_data_packet is None:
            raise RuntimeError(k.ERROR_UNDEFINED_OR_NULL_INPUT)

        # Check to make sure the buffer is the right size.
        if len(raw_data_to_sample.rawDataPacket) != k.RAW_PACKET_SIZE:
            raise RuntimeError(k.ERROR_INVALID_BYTE_LENGTH)

        # Verify the correct stop byte.
        if raw_data_to_sample.rawDataPacket[0] != k.RAW_BYTE_START:
            raise RuntimeError(k.ERROR_INVALID_BYTE_START)

        sample_object = OpenBCISample()


        if raw_data_to_sample.scale: 
            sample_object.accel_data = self.get_data_array_accel(raw_data_to_sample.rawDataPacket[k.RAW_PACKET_POSITION_START_AUX:k.RAW_PACKET_POSITION_STOP_AUX + 1])
        else:
            sample_object.accel_data = self.get_data_array_accel_no_scale(raw_data_to_sample.rawDataPacket[k.RAW_PACKET_POSITION_START_AUX, k.RAW_PACKET_POSITION_STOP_AUX + 1])

        if (o.scale) sample_object.channelData = getChannelDataArray(o);
        else sample_object.channelDataCounts = getChannelDataArrayNoScale(o);

        sample_object.auxData = Buffer.
        from
        (o.rawDataPacket.slice(k.OBCIPacketPositionStartAux, k.OBCIPacketPositionStopAux + 1));

        sample_object.sampleNumber = o.rawDataPacket[k.OBCIPacketPositionSampleNumber];
        sample_object.startByte = o.rawDataPacket[0];
        sample_object.stopByte = o.rawDataPacket[k.OBCIPacketPositionStopByte];

        sample_object.valid = true;

        sample_object.timestamp = Date.now();
        sample_object.boardTime = 0;

        return sample_object;
        pass

    def parse_packet_standard_raw_aux(self, raw_data_to_sample):
        pass

    def parse_packet_time_synced_accel(self, raw_data_to_sample):
        pass

    def parse_packet_time_synced_raw_aux(self, raw_data_to_sample):
        pass

    def transform_raw_data_packet_to_sample(self, raw_data):
        """
        Used transform raw data packets into fully qualified packets
        :param raw_data:
        :return:
        """
        try:
            self.raw_data_to_sample.raw_data_packet = raw_data
            packet_type = self.get_raw_packet_type(raw_data[k.RAW_PACKET_POSITION_STOP_BYTE])
            if packet_type == k.RAW_PACKET_TYPE_STANDARD_ACCEL:
                sample = self.parse_packet_standard_accel(self.raw_data_to_sample)
            elif packet_type == k.RAW_PACKET_TYPE_STANDARD_RAW_AUX:
                sample = self.parse_packet_standard_raw_aux(self.raw_data_to_sample)
            elif packet_type == k.RAW_PACKET_TYPE_ACCEL_TIME_SYNC_SET or packet_type == k.RAW_PACKET_TYPE_ACCEL_TIME_SYNCED:
                sample = self.parse_packet_time_synced_accel(self.raw_data_to_sample)
            elif packet_type == k.RAW_PACKET_TYPE_RAW_AUX_TIME_SYNC_SET or packet_type == k.RAW_PACKET_TYPE_RAW_AUX_TIME_SYNCED:
                sample = self.parse_packet_time_synced_raw_aux(self.raw_data_to_sample)
            else:
                sample = OpenBCISample()
                sample.error = 'This module does not support packet type %d' % packet_type
                sample.valid = False

            sample.packet_type = packet_type
        except BaseException as e:
            sample = OpenBCISample()
            sample.error = e.message
            sample.valid = False

        return sample


class RawDataToSample(object):
    """Object encapulsating a parsing object."""
    def __init__(self,
                 accel_data=None,
                 gains=None,
                 last_sample_number=0,
                 raw_data_packets=None,
                 raw_data_packet=None,
                 scale=False,
                 time_offset=0,
                 verbose=False):
        """
        RawDataToSample
        :param accel_data: list
            The channel settings array
        :param gains: list
            The gains of each channel, this is used to derive number of channels
        :param last_sample_number: int
        :param raw_data_packets: list
            list of raw_data_packets
        :param raw_data_packet: bytearray
            A single raw data packet
        :param scale: boolean
            Default `true`. A gain of 24 for Cyton will be used and 51 for ganglion by default.
        :param time_offset: int
            For non time stamp use cases i.e. 0xC0 or 0xC1 (default and raw aux)
        :param verbose:
        """
        self.accel_data = accel_data if accel_data is not None else []
        self.gains = gains if gains is not None else []
        self.time_offset = time_offset
        self.last_sample_number = last_sample_number
        self.raw_data_packets = raw_data_packets if raw_data_packets is not None else []
        self.raw_data_packet = raw_data_packet
        self.scale = scale
        self.verbose = verbose


class OpenBCISample(object):
    """Object encapulsating a single sample from the OpenBCI board."""
    def __init__(self,
                 aux_data=None,
                 board_time=0,
                 channel_data=None,
                 error=None,
                 imp_data=None,
                 packet_type=k.RAW_PACKET_TYPE_STANDARD_ACCEL,
                 sample_number=0,
                 start_byte=0,
                 stop_byte=0,
                 valid=True):
        self.aux_data = aux_data if aux_data is not None else []
        self.channel_data = channel_data if aux_data is not None else []
        self.error = error
        self.id = sample_number
        self.imp_data = imp_data if aux_data is not None else []
        self.packet_type = packet_type
        self.sample_number = sample_number
        self.start_byte = start_byte
        self.stop_byte = stop_byte
        self.valid = valid
