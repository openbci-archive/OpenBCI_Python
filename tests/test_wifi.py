from unittest import TestCase, main, skip
import mock

import sys, os
sys.path.insert(1, os.path.join(sys.path[0], '..'))

from openbci import OpenBCIWiFi


class TestOpenBCIWiFi(TestCase):

    @mock.patch.object(OpenBCIWiFi, 'on_shield_found')
    def test_wifi_init(self, mock_on_shield_found):
        expected_ip_address = '192.168.0.1'
        expected_shield_name = 'OpenBCI-E218'
        expected_sample_rate = 500
        expected_log = False
        expected_timeout = 5
        expected_max_packets_to_skip = 10
        expected_latency = 5000
        expected_high_speed = False
        expected_ssdp_attempts = 2
        expected_aux_mode = 'analog'

        wifi = OpenBCIWiFi(ip_address=expected_ip_address,
                           shield_name=expected_shield_name,
                           sample_rate=expected_sample_rate,
                           log=expected_log,
                           timeout=expected_timeout,
                           max_packets_to_skip=expected_max_packets_to_skip,
                           latency=expected_latency,
                           high_speed=expected_high_speed,
                           ssdp_attempts=expected_ssdp_attempts,
                           aux_mode=expected_aux_mode)

        self.assertEqual(wifi.ip_address, expected_ip_address)
        self.assertEqual(wifi.shield_name, expected_shield_name)
        self.assertEqual(wifi.sample_rate, expected_sample_rate)
        self.assertEqual(wifi.log, expected_log)
        self.assertEqual(wifi.timeout, expected_timeout)
        self.assertEqual(wifi.max_packets_to_skip, expected_max_packets_to_skip)
        self.assertEqual(wifi.latency, expected_latency)
        self.assertEqual(wifi.high_speed, expected_high_speed)
        self.assertEqual(wifi.ssdp_attempts, expected_ssdp_attempts)
        self.assertEqual(wifi.aux_mode, expected_aux_mode)

        mock_on_shield_found.assert_called_with(expected_ip_address)


if __name__ == '__main__':
    main()
