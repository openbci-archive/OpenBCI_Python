import time
import struct

from openbci.utils.constants import Constants as k


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
                                                  scale_factors=self.scale_factors,
                                                  verbose=log)

    def is_stop_byte(self, byte):
        """
        Used to check and see if a byte adheres to the stop byte structure
            of 0xCx where x is the set of numbers from 0-F in hex of 0-15 in decimal.
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

    def get_channel_data_array(self, raw_data_to_sample):
        """

        :param raw_data_to_sample: RawDataToSample
        :return:
        """
        channel_data = []
        number_of_channels = len(raw_data_to_sample.scale_factors)
        daisy = number_of_channels == k.NUMBER_OF_CHANNELS_DAISY
        channels_in_packet = k.NUMBER_OF_CHANNELS_CYTON
        if not daisy:
            channels_in_packet = number_of_channels
        # Channel data arrays are always 8 long

        for i in range(channels_in_packet):
            counts = self.interpret_24_bit_as_int_32(
                raw_data_to_sample.raw_data_packet[
                    (i * 3) +
                    k.RAW_PACKET_POSITION_CHANNEL_DATA_START:(i * 3) +
                    k.RAW_PACKET_POSITION_CHANNEL_DATA_START + 3
                ]
            )
            channel_data.append(
                raw_data_to_sample.scale_factors[i] *
                counts if raw_data_to_sample.scale else counts
            )

        return channel_data

    def get_data_array_accel(self, raw_data_to_sample):
        accel_data = []
        for i in range(k.RAW_PACKET_ACCEL_NUMBER_AXIS):
            counts = self.interpret_16_bit_as_int_32(
                raw_data_to_sample.raw_data_packet[
                k.RAW_PACKET_POSITION_START_AUX +
                (i * 2): k.RAW_PACKET_POSITION_START_AUX + (i * 2) + 2])
            accel_data.append(k.CYTON_ACCEL_SCALE_FACTOR_GAIN *
                              counts if raw_data_to_sample.scale else counts)
        return accel_data

    def get_raw_packet_type(self, stop_byte):
        return stop_byte & 0xF

    def interpret_16_bit_as_int_32(self, two_byte_buffer):
        return struct.unpack('>h', two_byte_buffer)[0]

    def interpret_24_bit_as_int_32(self, three_byte_buffer):
        # 3 byte ints
        unpacked = struct.unpack('3B', three_byte_buffer)

        # 3byte int in 2s compliment
        if unpacked[0] > 127:
            pre_fix = bytes(bytearray.fromhex('FF'))
        else:
            pre_fix = bytes(bytearray.fromhex('00'))

        three_byte_buffer = pre_fix + three_byte_buffer

        # unpack little endian(>) signed integer(i) (makes unpacking platform independent)
        return struct.unpack('>i', three_byte_buffer)[0]

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
        if len(raw_data_to_sample.raw_data_packet) != k.RAW_PACKET_SIZE:
            raise RuntimeError(k.ERROR_INVALID_BYTE_LENGTH)

        # Verify the correct stop byte.
        if raw_data_to_sample.raw_data_packet[0] != k.RAW_BYTE_START:
            raise RuntimeError(k.ERROR_INVALID_BYTE_START)

        sample_object = OpenBCISample()

        sample_object.accel_data = self.get_data_array_accel(raw_data_to_sample)

        sample_object.channel_data = self.get_channel_data_array(raw_data_to_sample)

        sample_object.sample_number = raw_data_to_sample.raw_data_packet[
            k.RAW_PACKET_POSITION_SAMPLE_NUMBER
        ]
        sample_object.start_byte = raw_data_to_sample.raw_data_packet[
            k.RAW_PACKET_POSITION_START_BYTE
        ]
        sample_object.stop_byte = raw_data_to_sample.raw_data_packet[
            k.RAW_PACKET_POSITION_STOP_BYTE
        ]

        sample_object.valid = True

        now_ms = int(round(time.time() * 1000))

        sample_object.timestamp = now_ms
        sample_object.boardTime = 0

        return sample_object

    def parse_packet_standard_raw_aux(self, raw_data_to_sample):
        pass

    def parse_packet_time_synced_accel(self, raw_data_to_sample):
        pass

    def parse_packet_time_synced_raw_aux(self, raw_data_to_sample):
        pass

    def set_ads1299_scale_factors(self, gains, micro_volts=None):
        self.scale_factors = self.get_ads1299_scale_factors(gains, micro_volts=micro_volts)

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
            elif packet_type == k.RAW_PACKET_TYPE_ACCEL_TIME_SYNC_SET or \
                    packet_type == k.RAW_PACKET_TYPE_ACCEL_TIME_SYNCED:
                sample = self.parse_packet_time_synced_accel(self.raw_data_to_sample)
            elif packet_type == k.RAW_PACKET_TYPE_RAW_AUX_TIME_SYNC_SET or \
                    packet_type == k.RAW_PACKET_TYPE_RAW_AUX_TIME_SYNCED:
                sample = self.parse_packet_time_synced_raw_aux(self.raw_data_to_sample)
            else:
                sample = OpenBCISample()
                sample.error = 'This module does not support packet type %d' % packet_type
                sample.valid = False

            sample.packet_type = packet_type
        except BaseException as e:
            sample = OpenBCISample()
            if hasattr(e, 'message'):
                sample.error = e.message
            else:
                sample.error = e
            sample.valid = False

        return sample

    def make_daisy_sample_object_wifi(self, lower_sample_object, upper_sample_object):
        """
        /**
        * @description Used to make one sample object from two sample
        *      objects. The sample number of the new daisy sample will be the
        *      upperSampleObject's sample number divded by 2. This allows us
        *      to preserve consecutive sample numbers that flip over at 127
        *      instead of 255 for an 8 channel. The daisySampleObject will
        *      also have one `channelData` array with 16 elements inside it,
        *      with the lowerSampleObject in the lower indices and the
        *      upperSampleObject in the upper set of indices. The auxData from
        *      both channels shall be captured in an object called `auxData`
        *      which contains two arrays referenced by keys `lower` and
        *      `upper` for the `lowerSampleObject` and `upperSampleObject`,
        *      respectively. The timestamps shall be averaged and moved into
        *      an object called `timestamp`. Further, the un-averaged
        *      timestamps from the `lowerSampleObject` and `upperSampleObject`
        *      shall be placed into an object called `_timestamps` which shall
        *      contain two keys `lower` and `upper` which contain the original
        *      timestamps for their respective sampleObjects.
        * @param lowerSampleObject {Object} - Lower 8 channels with odd sample number
        * @param upperSampleObject {Object} - Upper 8 channels with even sample number
        * @returns {Object} - The new merged daisy sample object
        */
        """
        daisy_sample_object = OpenBCISample()

        if lower_sample_object.channel_data is not None:
            daisy_sample_object.channel_data = lower_sample_object.channel_data + \
                upper_sample_object.channel_data

        daisy_sample_object.sample_number = upper_sample_object.sample_number
        daisy_sample_object.id = daisy_sample_object.sample_number

        daisy_sample_object.aux_data = {
            'lower': lower_sample_object.aux_data,
            'upper': upper_sample_object.aux_data
        }

        if lower_sample_object.timestamp:
            daisy_sample_object.timestamp = lower_sample_object.timestamp

        daisy_sample_object.stop_byte = lower_sample_object.stop_byte

        daisy_sample_object._timestamps = {
            'lower': lower_sample_object.timestamp,
            'upper': upper_sample_object.timestamp
        }

        if lower_sample_object.accel_data:
            if lower_sample_object.accel_data[0] > 0 or lower_sample_object.accel_data[1] > 0 or \
                    lower_sample_object.accel_data[2] > 0:
                daisy_sample_object.accel_data = lower_sample_object.accel_data
            else:
                daisy_sample_object.accel_data = upper_sample_object.accel_data

        daisy_sample_object.valid = True

        return daisy_sample_object

    """
    /**
 * @description Used transform raw data packets into fully qualified packets
 * @param o {RawDataToSample} - Used to hold data and configuration settings
 * @return {Array} samples An array of {Sample}
 * @author AJ Keller (@aj-ptw)
 */
function transformRawDataPacketsToSample (o) {
  let samples = [];
  for (let i = 0; i < o.rawDataPackets.length; i++) {
    o.rawDataPacket = o.rawDataPackets[i];
    const sample = transformRawDataPacketToSample(o);
    samples.push(sample);
    if (sample.hasOwnProperty('sampleNumber')) {
      o['lastSampleNumber'] = sample.sampleNumber;
    } else if (!sample.hasOwnProperty('impedanceValue')) {
      o['lastSampleNumber'] = o.rawDataPacket[k.OBCIPacketPositionSampleNumber];
    }
  }
  return samples;
}
    """

    def transform_raw_data_packets_to_sample(self, raw_data_packets):
        samples = []

        for raw_data_packet in raw_data_packets:
            sample = self.transform_raw_data_packet_to_sample(raw_data_packet)
            samples.append(sample)
            self.raw_data_to_sample.last_sample_number = sample.sample_number

        return samples


class RawDataToSample(object):
    """Object encapulsating a parsing object."""

    def __init__(self,
                 accel_data=None,
                 gains=None,
                 last_sample_number=0,
                 raw_data_packets=None,
                 raw_data_packet=None,
                 scale=True,
                 scale_factors=None,
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
        :param scale_factors: list
            Calculated scale factors
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
        self.scale_factors = scale_factors if scale_factors is not None else []
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
                 protocol=k.PROTOCOL_WIFI,
                 sample_number=0,
                 start_byte=0,
                 stop_byte=0,
                 valid=True,
                 accel_data=None):
        self.aux_data = aux_data if aux_data is not None else []
        self.board_time = board_time
        self.channel_data = channel_data if aux_data is not None else []
        self.error = error
        self.id = sample_number
        self.imp_data = imp_data if aux_data is not None else []
        self.packet_type = packet_type
        self.protocol = protocol
        self.sample_number = sample_number
        self.start_byte = start_byte
        self.stop_byte = stop_byte
        self.timestamp = 0
        self._timestamps = {}
        self.valid = valid
        self.accel_data = accel_data if accel_data is not None else []
