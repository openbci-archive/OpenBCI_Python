from unittest import TestCase, main, skip
import mock

from openbci.utils import (k,
                           ParseRaw,
                           sample_packet)


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


if __name__ == '__main__':
    main()
