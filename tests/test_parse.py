from unittest import TestCase, main, skip
import mock

from openbci.utils import (k,
                           ParseRaw,
                           sample_packet,
                           sample_packet_standard_raw_aux,
                           sample_packet_accel_time_sync_set,
                           sample_packet_accel_time_synced,
                           sample_packet_raw_aux_time_sync_set,
                           sample_packet_raw_aux_time_synced,
                           RawDataToSample)


class TestParseRaw(TestCase):

    def test_get_channel_data_array(self):
        expected_gains = [24, 24, 24, 24, 24, 24, 24, 24]
        expected_sample_number = 0

        data = sample_packet(expected_sample_number)

        parser = ParseRaw(gains=expected_gains, scaled_output=True)

        scale_factors = parser.get_ads1299_scale_factors(expected_gains)

        expected_channel_data = []
        for i in range(k.NUMBER_OF_CHANNELS_CYTON):
            expected_channel_data.append(scale_factors[i] * (i + 1))

        parser.raw_data_to_sample.raw_data_packet = data

        actual_channel_data = parser.get_channel_data_array(parser.raw_data_to_sample)

        self.assertListEqual(actual_channel_data, expected_channel_data)

    def test_get_data_array_accel(self):
        expected_sample_number = 0

        data = sample_packet(expected_sample_number)

        parser = ParseRaw(gains=[24, 24, 24, 24, 24, 24, 24, 24], scaled_output=True)

        expected_accel_data = []
        for i in range(k.RAW_PACKET_ACCEL_NUMBER_AXIS):
            expected_accel_data.append(k.CYTON_ACCEL_SCALE_FACTOR_GAIN * i)

        parser.raw_data_to_sample.raw_data_packet = data

        actual_accel_data = parser.get_data_array_accel(parser.raw_data_to_sample)

        self.assertListEqual(actual_accel_data, expected_accel_data)

    def test_interpret_16_bit_as_int_32(self):

        parser = ParseRaw()

        # 0x0690 === 1680
        self.assertEqual(parser.interpret_16_bit_as_int_32(bytearray([0x06, 0x90])),
                         1680,
                         'converts a small positive number')

        # 0x02C0 === 704
        self.assertEqual(parser.interpret_16_bit_as_int_32(bytearray([0x02, 0xC0])),
                         704,
                         'converts a large positive number')

        # 0xFFFF === -1
        self.assertEqual(parser.interpret_16_bit_as_int_32(bytearray([0xFF, 0xFF])),
                         -1,
                         'converts a small negative number')

        # 0x81A1 === -32351
        self.assertEqual(parser.interpret_16_bit_as_int_32(bytearray([0x81, 0xA1])),
                         -32351,
                         'converts a large negative number')

    def test_interpret_24_bit_as_int_32(self):

        parser = ParseRaw()

        # 0x000690 === 1680
        expected_value = 1680
        actual_value = parser.interpret_24_bit_as_int_32(bytearray([0x00, 0x06, 0x90]))
        self.assertEqual(actual_value,
                         expected_value,
                         'converts a small positive number')

        # 0x02C001 === 180225
        expected_value = 180225
        actual_value = parser.interpret_24_bit_as_int_32(bytearray([0x02, 0xC0, 0x01]))
        self.assertEqual(actual_value,
                         expected_value,
                         'converts a large positive number')

        # 0xFFFFFF === -1
        expected_value = -1
        actual_value = parser.interpret_24_bit_as_int_32(bytearray([0xFF, 0xFF, 0xFF]))
        self.assertEqual(actual_value,
                         expected_value,
                         'converts a small negative number')

        # 0x81A101 === -8281855
        expected_value = -8281855
        actual_value = parser.interpret_24_bit_as_int_32(bytearray([0x81, 0xA1, 0x01]))
        self.assertEqual(actual_value,
                         expected_value,
                         'converts a large negative number')

    def test_parse_raw_init(self):
        expected_board_type = k.BOARD_DAISY
        expected_gains = [24, 24, 24, 24, 24, 24, 24, 24]
        expected_log = True
        expected_micro_volts = True
        expected_scaled_output = False

        parser = ParseRaw(board_type=expected_board_type,
                          gains=expected_gains,
                          log=expected_log,
                          micro_volts=expected_micro_volts,
                          scaled_output=expected_scaled_output)

        self.assertEqual(parser.board_type, expected_board_type)
        self.assertEqual(parser.scaled_output, expected_scaled_output)
        self.assertEqual(parser.log, expected_log)

    def test_get_ads1299_scale_factors_volts(self):
        gains = [24, 24, 24, 24, 24, 24, 24, 24]
        expected_scale_factors = []
        for gain in gains:
            scale_factor = 4.5 / float((pow(2, 23) - 1)) / float(gain)
            expected_scale_factors.append(scale_factor)

        parser = ParseRaw()

        actual_scale_factors = parser.get_ads1299_scale_factors(gains)

        self.assertEqual(actual_scale_factors,
                         expected_scale_factors,
                         "should be able to get scale factors for gains in volts")

    def test_get_ads1299_scale_factors_micro_volts(self):
        gains = [24, 24, 24, 24, 24, 24, 24, 24]
        micro_volts = True
        expected_scale_factors = []
        for gain in gains:
            scale_factor = 4.5 / float((pow(2, 23) - 1)) / float(gain) * 1000000.
            expected_scale_factors.append(scale_factor)

        parser = ParseRaw()

        actual_scale_factors = parser.get_ads1299_scale_factors(gains, micro_volts)

        self.assertEqual(actual_scale_factors,
                         expected_scale_factors,
                         "should be able to get scale factors for gains in volts")

    def test_parse_packet_standard_accel(self):
        data = sample_packet()

        expected_scale_factor = 4.5 / 24 / (pow(2, 23) - 1)

        parser = ParseRaw(gains=[24, 24, 24, 24, 24, 24, 24, 24], scaled_output=True)

        parser.raw_data_to_sample.raw_data_packet = data

        sample = parser.parse_packet_standard_accel(parser.raw_data_to_sample)

        self.assertIsNotNone(sample)
        for i in range(len(sample.channel_data)):
            self.assertEqual(sample.channel_data[i], expected_scale_factor * (i + 1))
        for i in range(len(sample.accel_data)):
            self.assertEqual(sample.accel_data[i], k.CYTON_ACCEL_SCALE_FACTOR_GAIN * i)
        self.assertEqual(sample.packet_type, k.RAW_PACKET_TYPE_STANDARD_ACCEL)
        self.assertEqual(sample.sample_number, 0x45)
        self.assertEqual(sample.start_byte, 0xA0)
        self.assertEqual(sample.stop_byte, 0xC0)
        self.assertTrue(sample.valid)

    @mock.patch.object(ParseRaw, 'parse_packet_standard_accel')
    def test_transform_raw_data_packet_to_sample_accel(self, mock_parse_packet_standard_accel):
        data = sample_packet(0)

        parser = ParseRaw()

        parser.transform_raw_data_packet_to_sample(data)

        mock_parse_packet_standard_accel.assert_called_once()

    @mock.patch.object(ParseRaw, 'parse_packet_standard_raw_aux')
    def test_transform_raw_data_packet_to_sample_raw_aux(self, mock_parse_packet_standard_raw_aux):
        data = sample_packet_standard_raw_aux(0)

        parser = ParseRaw()

        parser.transform_raw_data_packet_to_sample(data)

        mock_parse_packet_standard_raw_aux.assert_called_once()

    @mock.patch.object(ParseRaw, 'parse_packet_time_synced_accel')
    def test_transform_raw_data_packet_to_sample_time_sync_accel(self, mock_parse_packet_time_synced_accel):
        data = sample_packet_accel_time_sync_set(0)

        parser = ParseRaw()

        parser.transform_raw_data_packet_to_sample(data)

        mock_parse_packet_time_synced_accel.assert_called_once()

        mock_parse_packet_time_synced_accel.reset_mock()

        data = sample_packet_accel_time_synced(0)

        parser.transform_raw_data_packet_to_sample(data)

        mock_parse_packet_time_synced_accel.assert_called_once()

    @mock.patch.object(ParseRaw, 'parse_packet_time_synced_raw_aux')
    def test_transform_raw_data_packet_to_sample_time_sync_raw(self, mock_parse_packet_time_synced_raw_aux):
        data = sample_packet_raw_aux_time_sync_set(0)

        parser = ParseRaw()

        parser.transform_raw_data_packet_to_sample(data)

        mock_parse_packet_time_synced_raw_aux.assert_called_once()

        mock_parse_packet_time_synced_raw_aux.reset_mock()

        data = sample_packet_raw_aux_time_synced(0)

        parser.transform_raw_data_packet_to_sample(data)

        mock_parse_packet_time_synced_raw_aux.assert_called_once()

    def test_transform_raw_data_packets_to_sample(self):
        datas = [sample_packet(0), sample_packet(1), sample_packet(2)]

        parser = ParseRaw(gains=[24, 24, 24, 24, 24, 24, 24, 24])

        samples = parser.transform_raw_data_packets_to_sample(datas)

        self.assertEqual(len(samples), len(datas))

        for i in range(len(samples)):
            self.assertEqual(samples[i].sample_number, i)


if __name__ == '__main__':
    main()
