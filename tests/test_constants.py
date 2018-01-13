from unittest import TestCase, main, skip
import mock

from openbci.utils import k


class TestConstants(TestCase):

    def test_ads1299(self):
        self.assertEqual(k.ADS1299_GAIN_1, 1.0)
        self.assertEqual(k.ADS1299_GAIN_2, 2.0)
        self.assertEqual(k.ADS1299_GAIN_4, 4.0)
        self.assertEqual(k.ADS1299_GAIN_6, 6.0)
        self.assertEqual(k.ADS1299_GAIN_8, 8.0)
        self.assertEqual(k.ADS1299_GAIN_12, 12.0)
        self.assertEqual(k.ADS1299_GAIN_24, 24.0)
        self.assertEqual(k.ADS1299_VREF, 4.5)

    def test_board_types(self):
        self.assertEqual(k.BOARD_CYTON, 'cyton')
        self.assertEqual(k.BOARD_DAISY, 'daisy')
        self.assertEqual(k.BOARD_GANGLION, 'ganglion')
        self.assertEqual(k.BOARD_NONE, 'none')

    def test_cyton_variables(self):
        self.assertEqual(k.CYTON_ACCEL_SCALE_FACTOR_GAIN, 0.002 / (pow(2, 4)))

    def test_number_of_channels(self):
        self.assertEqual(k.NUMBER_OF_CHANNELS_CYTON, 8)
        self.assertEqual(k.NUMBER_OF_CHANNELS_DAISY, 16)
        self.assertEqual(k.NUMBER_OF_CHANNELS_GANGLION, 4)

    def test_raw(self):
        self.assertEqual(k.RAW_BYTE_START, 0xA0)
        self.assertEqual(k.RAW_BYTE_STOP, 0xC0)
        self.assertEqual(k.RAW_PACKET_SIZE, 255)
        self.assertEqual(k.RAW_PACKET_POSITION_CHANNEL_DATA_START, 2)
        self.assertEqual(k.RAW_PACKET_POSITION_CHANNEL_DATA_STOP, 25)
        self.assertEqual(k.RAW_PACKET_POSITION_SAMPLE_NUMBER, 1)
        self.assertEqual(k.RAW_PACKET_POSITION_START_BYTE, 0)
        self.assertEqual(k.RAW_PACKET_POSITION_STOP_BYTE, 32)
        self.assertEqual(k.RAW_PACKET_POSITION_START_AUX, 26)
        self.assertEqual(k.RAW_PACKET_POSITION_STOP_AUX, 31)
        self.assertEqual(k.RAW_PACKET_POSITION_TIME_SYNC_AUX_START, 26)
        self.assertEqual(k.RAW_PACKET_POSITION_TIME_SYNC_AUX_STOP, 28)
        self.assertEqual(k.RAW_PACKET_POSITION_TIME_SYNC_TIME_START, 28)
        self.assertEqual(k.RAW_PACKET_POSITION_TIME_SYNC_TIME_STOP, 32)
        self.assertEqual(k.RAW_PACKET_TYPE_STANDARD_ACCEL, 0)
        self.assertEqual(k.RAW_PACKET_TYPE_STANDARD_RAW_AUX, 1)
        self.assertEqual(k.RAW_PACKET_TYPE_USER_DEFINED_TYPE, 2)
        self.assertEqual(k.RAW_PACKET_TYPE_ACCEL_TIME_SYNC_SET, 3)
        self.assertEqual(k.RAW_PACKET_TYPE_ACCEL_TIME_SYNCED, 4)
        self.assertEqual(k.RAW_PACKET_TYPE_RAW_AUX_TIME_SYNC_SET, 5)
        self.assertEqual(k.RAW_PACKET_TYPE_RAW_AUX_TIME_SYNCED, 6)
        self.assertEqual(k.RAW_PACKET_TYPE_IMPEDANCE, 7)

    def test_sample_number_max(self):
        self.assertEqual(k.SAMPLE_NUMBER_MAX_CYTON, 255)
        self.assertEqual(k.SAMPLE_NUMBER_MAX_GANGLION, 200)

    def test_sample_rates(self):
        self.assertEqual(k.SAMPLE_RATE_1000, 1000)
        self.assertEqual(k.SAMPLE_RATE_125, 125)
        self.assertEqual(k.SAMPLE_RATE_12800, 12800)
        self.assertEqual(k.SAMPLE_RATE_1600, 1600)
        self.assertEqual(k.SAMPLE_RATE_16000, 16000)
        self.assertEqual(k.SAMPLE_RATE_200, 200)
        self.assertEqual(k.SAMPLE_RATE_2000, 2000)
        self.assertEqual(k.SAMPLE_RATE_250, 250)
        self.assertEqual(k.SAMPLE_RATE_25600, 25600)
        self.assertEqual(k.SAMPLE_RATE_3200, 3200)
        self.assertEqual(k.SAMPLE_RATE_400, 400)
        self.assertEqual(k.SAMPLE_RATE_4000, 4000)
        self.assertEqual(k.SAMPLE_RATE_500, 500)
        self.assertEqual(k.SAMPLE_RATE_6400, 6400)
        self.assertEqual(k.SAMPLE_RATE_800, 800)
        self.assertEqual(k.SAMPLE_RATE_8000, 8000)

if __name__ == '__main__':
    main()
