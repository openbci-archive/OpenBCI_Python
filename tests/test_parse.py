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

    def test_parse_raw_standard_cyton_scaled(self):
        expected_sample_number = 3
        expected_board_type = k.BOARD_CYTON
        expected_scaled_output = False
        expected_log = True
        expected_gains = [24, 24, 24, 24, 24, 24, 24, 24]

        data = sample_packet(expected_sample_number)

        parser = ParseRaw(board_type=expected_board_type,
                          gains=expected_gains,
                          log=expected_log,
                          scaled_output=expected_scaled_output)

        actual_sample = parser.raw_to_sample(data)

        self.assertEqual(actual_sample.sample_number, expected_sample_number)

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
        data = sample_packet(0)

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



if __name__ == '__main__':
    main()
