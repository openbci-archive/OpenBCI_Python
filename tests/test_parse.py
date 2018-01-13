from unittest import TestCase, main, skip
import mock

from openbci.utils import ParseRaw, k


class TestParseRaw(TestCase):

    def test_parse_raw_init(self):
        expected_board_type = k.BOARD_DAISY
        expected_scaled_output = False
        expected_log = True

        parser = ParseRaw(board_type=expected_board_type,
                          scaled_output=expected_scaled_output,
                          log=expected_log)

        self.assertEqual(parser.board_type, expected_board_type)
        self.assertEqual(parser.scaled_output, expected_scaled_output)
        self.assertEqual(parser.log, expected_log)


if __name__ == '__main__':
    main()
