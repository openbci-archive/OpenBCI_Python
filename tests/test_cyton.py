import unittest
from openbci.cyton import OpenBCICyton

PORT = 'loop://'


class TestOpenBCICyton(unittest.TestCase):

    def setUp(self):
        self.cyton = OpenBCICyton(port=PORT)

    def tearDown(self):
        self.cyton.disconnect()

    def test_init(self):
        """After initialization, we send b'v' to initialize 32-bit board."""
        self.assertEqual(self.cyton.ser_read(), b'v',
                         "Expected initialization character")

    def test_filter_toggles(self):
        self.test_init()

        self.cyton.enable_filters()
        self.assertEqual(self.cyton.ser_read(), b'f',
                         "Expected enable filter character")
        self.assertTrue(self.cyton.filtering_data)

        self.cyton.disable_filters()
        self.assertEqual(self.cyton.ser_read(), b'g',
                         "Expected disable filter character")
        self.assertFalse(self.cyton.filtering_data)

    def test_test_signal(self):
        self.test_init()

        self.cyton.test_signal(0)
        self.assertEqual(self.cyton.ser_read(), b'0')
        self.cyton.test_signal(1)
        self.assertEqual(self.cyton.ser_read(), b'p')
        self.cyton.test_signal(2)
        self.assertEqual(self.cyton.ser_read(), b'-')
        self.cyton.test_signal(3)
        self.assertEqual(self.cyton.ser_read(), b'=')
        self.cyton.test_signal(4)
        self.assertEqual(self.cyton.ser_read(), b'[')
        self.cyton.test_signal(5)
        self.assertEqual(self.cyton.ser_read(), b']')

    def test_set_channel(self):
        self.test_init()
        self.cyton.daisy = True

        self.cyton.set_channel(channel=1, toggle_position=0)
        self.assertEqual(self.cyton.ser_read(), b'1')
        self.cyton.set_channel(channel=2, toggle_position=0)
        self.assertEqual(self.cyton.ser_read(), b'2')
        self.cyton.set_channel(channel=3, toggle_position=0)
        self.assertEqual(self.cyton.ser_read(), b'3')
        self.cyton.set_channel(channel=4, toggle_position=0)
        self.assertEqual(self.cyton.ser_read(), b'4')
        self.cyton.set_channel(channel=5, toggle_position=0)
        self.assertEqual(self.cyton.ser_read(), b'5')
        self.cyton.set_channel(channel=6, toggle_position=0)
        self.assertEqual(self.cyton.ser_read(), b'6')
        self.cyton.set_channel(channel=7, toggle_position=0)
        self.assertEqual(self.cyton.ser_read(), b'7')
        self.cyton.set_channel(channel=8, toggle_position=0)
        self.assertEqual(self.cyton.ser_read(), b'8')
        self.cyton.set_channel(channel=9, toggle_position=0)
        self.assertEqual(self.cyton.ser_read(), b'q')
        self.cyton.set_channel(channel=10, toggle_position=0)
        self.assertEqual(self.cyton.ser_read(), b'w')
        self.cyton.set_channel(channel=11, toggle_position=0)
        self.assertEqual(self.cyton.ser_read(), b'e')
        self.cyton.set_channel(channel=12, toggle_position=0)
        self.assertEqual(self.cyton.ser_read(), b'r')
        self.cyton.set_channel(channel=13, toggle_position=0)
        self.assertEqual(self.cyton.ser_read(), b't')
        self.cyton.set_channel(channel=14, toggle_position=0)
        self.assertEqual(self.cyton.ser_read(), b'y')
        self.cyton.set_channel(channel=15, toggle_position=0)
        self.assertEqual(self.cyton.ser_read(), b'u')
        self.cyton.set_channel(channel=16, toggle_position=0)
        self.assertEqual(self.cyton.ser_read(), b'i')

        self.cyton.set_channel(channel=1, toggle_position=1)
        self.assertEqual(self.cyton.ser_read(), b'!')
        self.cyton.set_channel(channel=2, toggle_position=1)
        self.assertEqual(self.cyton.ser_read(), b'@')
        self.cyton.set_channel(channel=3, toggle_position=1)
        self.assertEqual(self.cyton.ser_read(), b'#')
        self.cyton.set_channel(channel=4, toggle_position=1)
        self.assertEqual(self.cyton.ser_read(), b'$')
        self.cyton.set_channel(channel=5, toggle_position=1)
        self.assertEqual(self.cyton.ser_read(), b'%')
        self.cyton.set_channel(channel=6, toggle_position=1)
        self.assertEqual(self.cyton.ser_read(), b'^')
        self.cyton.set_channel(channel=7, toggle_position=1)
        self.assertEqual(self.cyton.ser_read(), b'&')
        self.cyton.set_channel(channel=8, toggle_position=1)
        self.assertEqual(self.cyton.ser_read(), b'*')
        self.cyton.set_channel(channel=9, toggle_position=1)
        self.assertEqual(self.cyton.ser_read(), b'Q')
        self.cyton.set_channel(channel=10, toggle_position=1)
        self.assertEqual(self.cyton.ser_read(), b'W')
        self.cyton.set_channel(channel=11, toggle_position=1)
        self.assertEqual(self.cyton.ser_read(), b'E')
        self.cyton.set_channel(channel=12, toggle_position=1)
        self.assertEqual(self.cyton.ser_read(), b'R')
        self.cyton.set_channel(channel=13, toggle_position=1)
        self.assertEqual(self.cyton.ser_read(), b'T')
        self.cyton.set_channel(channel=14, toggle_position=1)
        self.assertEqual(self.cyton.ser_read(), b'Y')
        self.cyton.set_channel(channel=15, toggle_position=1)
        self.assertEqual(self.cyton.ser_read(), b'U')
        self.cyton.set_channel(channel=16, toggle_position=1)
        self.assertEqual(self.cyton.ser_read(), b'I')


if __name__ == "__main__":
    unittest.main()
