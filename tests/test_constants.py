from unittest import TestCase, main, skip
import mock

from openbci.utils import Constants


class TestConstants(TestCase):

    def test_ads1299(self):
        self.assertEqual(Constants.ADS1299_GAIN_1, 1.0)
        self.assertEqual(Constants.ADS1299_GAIN_2, 2.0)
        self.assertEqual(Constants.ADS1299_GAIN_4, 4.0)
        self.assertEqual(Constants.ADS1299_GAIN_6, 6.0)
        self.assertEqual(Constants.ADS1299_GAIN_8, 8.0)
        self.assertEqual(Constants.ADS1299_GAIN_12, 12.0)
        self.assertEqual(Constants.ADS1299_GAIN_24, 24.0)
        self.assertEqual(Constants.ADS1299_VREF, 4.5)

    def test_board_types(self):
        self.assertEqual(Constants.BOARD_CYTON, 'cyton')
        self.assertEqual(Constants.BOARD_DAISY, 'daisy')
        self.assertEqual(Constants.BOARD_GANGLION, 'ganglion')
        self.assertEqual(Constants.BOARD_NONE, 'none')

    def test_cyton_variables(self):
        self.assertEqual(Constants.CYTON_ACCEL_SCALE_FACTOR_GAIN, 0.002 / (pow(2, 4)))

    def test_errors(self):
        self.assertEqual(Constants.ERROR_INVALID_BYTE_LENGTH, 'Invalid Packet Byte Length')
        self.assertEqual(Constants.ERROR_INVALID_BYTE_START, 'Invalid Start Byte')
        self.assertEqual(Constants.ERROR_INVALID_BYTE_STOP, 'Invalid Stop Byte')
        self.assertEqual(Constants.ERROR_INVALID_DATA, 'Invalid data - try again')
        self.assertEqual(Constants.ERROR_INVALID_TYPW, 'Invalid type - check comments for input type')
        self.assertEqual(Constants.ERROR_MISSING_REGISTER_SETTING, 'Missing register setting')
        self.assertEqual(Constants.ERROR_MISSING_REQUIRED_PROPERTY, 'Missing property in JSON')
        self.assertEqual(Constants.ERROR_TIME_SYNC_IS_NULL, "'this.sync.curSyncObj' must not be null")
        self.assertEqual(Constants.ERROR_TIME_SYNC_NO_COMMA, 'Missed the time sync sent confirmation. Try sync again')
        self.assertEqual(Constants.ERROR_UNDEFINED_OR_NULL_INPUT, 'Undefined or Null Input')

    def test_number_of_channels(self):
        self.assertEqual(Constants.NUMBER_OF_CHANNELS_CYTON, 8)
        self.assertEqual(Constants.NUMBER_OF_CHANNELS_DAISY, 16)
        self.assertEqual(Constants.NUMBER_OF_CHANNELS_GANGLION, 4)

    def test_protocols(self):
        """ Protocols """
        self.assertEqual(Constants.PROTOCOL_BLE, 'ble')
        self.assertEqual(Constants.PROTOCOL_SERIAL, 'serial')
        self.assertEqual(Constants.PROTOCOL_WIFI, 'wifi')

    def test_raw(self):
        self.assertEqual(Constants.RAW_BYTE_START, 0xA0)
        self.assertEqual(Constants.RAW_BYTE_STOP, 0xC0)
        self.assertEqual(Constants.RAW_PACKET_ACCEL_NUMBER_AXIS, 3)
        self.assertEqual(Constants.RAW_PACKET_SIZE, 33)
        self.assertEqual(Constants.RAW_PACKET_POSITION_CHANNEL_DATA_START, 2)
        self.assertEqual(Constants.RAW_PACKET_POSITION_CHANNEL_DATA_STOP, 25)
        self.assertEqual(Constants.RAW_PACKET_POSITION_SAMPLE_NUMBER, 1)
        self.assertEqual(Constants.RAW_PACKET_POSITION_START_BYTE, 0)
        self.assertEqual(Constants.RAW_PACKET_POSITION_STOP_BYTE, 32)
        self.assertEqual(Constants.RAW_PACKET_POSITION_START_AUX, 26)
        self.assertEqual(Constants.RAW_PACKET_POSITION_STOP_AUX, 31)
        self.assertEqual(Constants.RAW_PACKET_POSITION_TIME_SYNC_AUX_START, 26)
        self.assertEqual(Constants.RAW_PACKET_POSITION_TIME_SYNC_AUX_STOP, 28)
        self.assertEqual(Constants.RAW_PACKET_POSITION_TIME_SYNC_TIME_START, 28)
        self.assertEqual(Constants.RAW_PACKET_POSITION_TIME_SYNC_TIME_STOP, 32)
        self.assertEqual(Constants.RAW_PACKET_TYPE_STANDARD_ACCEL, 0)
        self.assertEqual(Constants.RAW_PACKET_TYPE_STANDARD_RAW_AUX, 1)
        self.assertEqual(Constants.RAW_PACKET_TYPE_USER_DEFINED_TYPE, 2)
        self.assertEqual(Constants.RAW_PACKET_TYPE_ACCEL_TIME_SYNC_SET, 3)
        self.assertEqual(Constants.RAW_PACKET_TYPE_ACCEL_TIME_SYNCED, 4)
        self.assertEqual(Constants.RAW_PACKET_TYPE_RAW_AUX_TIME_SYNC_SET, 5)
        self.assertEqual(Constants.RAW_PACKET_TYPE_RAW_AUX_TIME_SYNCED, 6)
        self.assertEqual(Constants.RAW_PACKET_TYPE_IMPEDANCE, 7)

    def test_sample_number_max(self):
        self.assertEqual(Constants.SAMPLE_NUMBER_MAX_CYTON, 255)
        self.assertEqual(Constants.SAMPLE_NUMBER_MAX_GANGLION, 200)

    def test_sample_rates(self):
        self.assertEqual(Constants.SAMPLE_RATE_1000, 1000)
        self.assertEqual(Constants.SAMPLE_RATE_125, 125)
        self.assertEqual(Constants.SAMPLE_RATE_12800, 12800)
        self.assertEqual(Constants.SAMPLE_RATE_1600, 1600)
        self.assertEqual(Constants.SAMPLE_RATE_16000, 16000)
        self.assertEqual(Constants.SAMPLE_RATE_200, 200)
        self.assertEqual(Constants.SAMPLE_RATE_2000, 2000)
        self.assertEqual(Constants.SAMPLE_RATE_250, 250)
        self.assertEqual(Constants.SAMPLE_RATE_25600, 25600)
        self.assertEqual(Constants.SAMPLE_RATE_3200, 3200)
        self.assertEqual(Constants.SAMPLE_RATE_400, 400)
        self.assertEqual(Constants.SAMPLE_RATE_4000, 4000)
        self.assertEqual(Constants.SAMPLE_RATE_500, 500)
        self.assertEqual(Constants.SAMPLE_RATE_6400, 6400)
        self.assertEqual(Constants.SAMPLE_RATE_800, 800)
        self.assertEqual(Constants.SAMPLE_RATE_8000, 8000)


if __name__ == '__main__':
    main()
