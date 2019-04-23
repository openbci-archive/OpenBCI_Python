"""
Core OpenBCI object for handling connections and samples from the Ganglion board.

Note that the LIB will take care on its own to print incoming ASCII messages if any (FIXME, BTW).

EXAMPLE USE:

def handle_sample(sample):
  print(sample.channels_data)

board = OpenBCIBoard()
board.start(handle_sample)

TODO: support impedance
TODO: reset board with 'v'?
"""
from __future__ import print_function
import struct
import time
import timeit
import atexit
import logging
import numpy as np
import sys
import pdb
import glob
from bluepy.btle import Scanner, DefaultDelegate, Peripheral

SAMPLE_RATE = 200.0  # Hz
scale_fac_uVolts_per_count = 1200 / (8388607.0 * 1.5 * 51.0)
scale_fac_accel_G_per_count = 0.000016

# service for communication, as per docs
BLE_SERVICE = "fe84"
# characteristics of interest
BLE_CHAR_RECEIVE = "2d30c082f39f4ce6923f3484ea480596"
BLE_CHAR_SEND = "2d30c083f39f4ce6923f3484ea480596"
BLE_CHAR_DISCONNECT = "2d30c084f39f4ce6923f3484ea480596"

'''
#Commands for in SDK http://docs.openbci.com/Hardware/08-Ganglion_Data_Forma

command_stop = "s";
command_startBinary = "b";
'''


class OpenBCIGanglion(object):
    """
    Handle a connection to an OpenBCI board.

    Args:
      port: MAC address of the Ganglion Board. "None" to attempt auto-detect.
      aux: enable on not aux channels (i.e. switch to 18bit mode if set)
      impedance: measures impedance when start streaming
      timeout: in seconds, if set will try to disconnect / reconnect after a period without new data
       -- should be high if impedance check
      max_packets_to_skip: will try to disconnect / reconnect after too many packets are skipped
      baud, filter_data, daisy: Not used, for compatibility with v3
    """

    def __init__(self, port=None, baud=0, filter_data=False,
                 scaled_output=True, daisy=False, log=True, aux=False, impedance=False, timeout=2,
                 max_packets_to_skip=20):
        # unused, for compatibility with Cyton v3 API
        self.daisy = False
        # these one are used
        self.log = log  # print_incoming_text needs log
        self.aux = aux
        self.streaming = False
        self.timeout = timeout
        self.max_packets_to_skip = max_packets_to_skip
        self.scaling_output = scaled_output
        self.impedance = impedance

        # might be handy to know API
        self.board_type = "ganglion"

        print("Looking for Ganglion board")
        if port == None:
            port = self.find_port()
        self.port = port  # find_port might not return string

        self.connect()

        self.streaming = False
        # number of EEG channels and (optionally) accelerometer channel
        self.eeg_channels_per_sample = 4
        self.aux_channels_per_sample = 3
        self.imp_channels_per_sample = 5
        self.read_state = 0
        self.log_packet_count = 0
        self.packets_dropped = 0
        self.time_last_packet = 0

        # Disconnects from board when terminated
        atexit.register(self.disconnect)

    def getBoardType(self):
        """ Returns the version of the board """
        return self.board_type

    def setImpedance(self, flag):
        """ Enable/disable impedance measure """
        self.impedance = bool(flag)

    def connect(self):
        """ Connect to the board and configure it. Note: recreates various objects upon call. """
        print("Init BLE connection with MAC: " + self.port)
        print("NB: if it fails, try with root privileges.")
        self.gang = Peripheral(self.port, 'random')  # ADDR_TYPE_RANDOM

        print("Get mainservice...")
        self.service = self.gang.getServiceByUUID(BLE_SERVICE)
        print("Got:" + str(self.service))

        print("Get characteristics...")
        self.char_read = self.service.getCharacteristics(BLE_CHAR_RECEIVE)[0]
        print("receive, properties: " + str(self.char_read.propertiesToString()) +
              ", supports read: " + str(self.char_read.supportsRead()))

        self.char_write = self.service.getCharacteristics(BLE_CHAR_SEND)[0]
        print("write, properties: " + str(self.char_write.propertiesToString()) +
              ", supports read: " + str(self.char_write.supportsRead()))

        self.char_discon = self.service.getCharacteristics(BLE_CHAR_DISCONNECT)[0]
        print("disconnect, properties: " + str(self.char_discon.propertiesToString()) +
              ", supports read: " + str(self.char_discon.supportsRead()))

        # set delegate to handle incoming data
        self.delegate = GanglionDelegate(self.scaling_output)
        self.gang.setDelegate(self.delegate)

        # enable AUX channel
        if self.aux:
            print("Enabling AUX data...")
            try:
                self.ser_write(b'n')
            except Exception as e:
                print("Something went wrong while enabling aux channels: " + str(e))

        print("Turn on notifications")
        # nead up-to-date bluepy, cf https://github.com/IanHarvey/bluepy/issues/53
        self.desc_notify = self.char_read.getDescriptors(forUUID=0x2902)[0]
        try:
            self.desc_notify.write(b"\x01")
        except Exception as e:
            print("Something went wrong while trying to enable notification: " + str(e))

        print("Connection established")

    def init_streaming(self):
        """ Tell the board to record like crazy. """
        try:
            if self.impedance:
                print("Starting with impedance testing")
                self.ser_write(b'z')
            else:
                self.ser_write(b'b')
        except Exception as e:
            print("Something went wrong while asking the board to start streaming: " + str(e))
        self.streaming = True
        self.packets_dropped = 0
        self.time_last_packet = timeit.default_timer()

    def find_port(self):
        """Detects Ganglion board MAC address
        If more than 1 around, will select first. Needs root privilege.
        """

        print("Try to detect Ganglion MAC address. "
              "NB: Turn on bluetooth and run as root for this to work!"
              "Might not work with every BLE dongles.")
        scan_time = 5
        print("Scanning for 5 seconds nearby devices...")

        #   From bluepy example
        class ScanDelegate(DefaultDelegate):
            def __init__(self):
                DefaultDelegate.__init__(self)

            def handleDiscovery(self, dev, isNewDev, isNewData):
                if isNewDev:
                    print("Discovered device: " + dev.addr)
                elif isNewData:
                    print("Received new data from: " + dev.addr)

        scanner = Scanner().withDelegate(ScanDelegate())
        devices = scanner.scan(scan_time)

        nb_devices = len(devices)
        if nb_devices < 1:
            print("No BLE devices found. Check connectivity.")
            return ""
        else:
            print("Found " + str(nb_devices) + ", detecting Ganglion")
            list_mac = []
            list_id = []

            for dev in devices:
                # "Ganglion" should appear inside the "value" associated
                # to "Complete Local Name", e.g. "Ganglion-b2a6"
                for (adtype, desc, value) in dev.getScanData():
                    if desc == "Complete Local Name" and value.startswith("Ganglion"):
                        list_mac.append(dev.addr)
                        list_id.append(value)
                        print("Got Ganglion: " + value +
                              ", with MAC: " + dev.addr)
                        break
        nb_ganglions = len(list_mac)

        if nb_ganglions < 1:
            print("No Ganglion found ;(")
            raise OSError('Cannot find OpenBCI Ganglion MAC address')

        if nb_ganglions > 1:
            print("Found " + str(nb_ganglions) + ", selecting first")

        print("Selecting MAC address " + list_mac[0] + " for " + list_id[0])
        return list_mac[0]

    def ser_write(self, b):
        """Access serial port object for write"""
        self.char_write.write(b)

    def ser_read(self):
        """Access serial port object for read"""
        return self.char_read.read()

    def ser_inWaiting(self):
        """ Slightly different from Cyton API, return True if ASCII messages are incoming."""
        # FIXME: might have a slight problem with thread because of notifications...
        if self.delegate.receiving_ASCII:
            # in case the packet indicating the end of the message drops, we use a 1s timeout
            if timeit.default_timer() - self.delegate.time_last_ASCII > 2:
                self.delegate.receiving_ASCII = False
        return self.delegate.receiving_ASCII

    def getSampleRate(self):
        return SAMPLE_RATE

    def getNbEEGChannels(self):
        """Will not get new data on impedance check."""
        return self.eeg_channels_per_sample

    def getNbAUXChannels(self):
        """Might not be used depending on the mode."""
        return self.aux_channels_per_sample

    def getNbImpChannels(self):
        """Might not be used depending on the mode."""
        return self.imp_channels_per_sample

    def start_streaming(self, callback, lapse=-1):
        """
        Start handling streaming data from the board. Call a provided callback
        for every single sample that is processed

        Args:
          callback: A callback function or a list of functions that will receive a single argument
                    of the OpenBCISample object captured.
        """
        if not self.streaming:
            self.init_streaming()

        start_time = timeit.default_timer()

        # Enclose callback funtion in a list if it comes alone
        if not isinstance(callback, list):
            callback = [callback]

        while self.streaming:
            # should the board get disconnected and we could not wait for notification
            # anymore, a reco should be attempted through timeout mechanism
            try:
                # at most we will get one sample per packet
                self.waitForNotifications(1. / self.getSampleRate())
            except Exception as e:
                print("Something went wrong while waiting for a new sample: " + str(e))
            # retrieve current samples on the stack
            samples = self.delegate.getSamples()
            self.packets_dropped = self.delegate.getMaxPacketsDropped()
            if samples:
                self.time_last_packet = timeit.default_timer()
                for call in callback:
                    for sample in samples:
                        call(sample)

            if (lapse > 0 and timeit.default_timer() - start_time > lapse):
                self.stop()
            if self.log:
                self.log_packet_count = self.log_packet_count + 1

            # Checking connection -- timeout and packets dropped
            self.check_connection()

    def waitForNotifications(self, delay):
        """ Allow some time for the board to receive new data. """
        self.gang.waitForNotifications(delay)

    def test_signal(self, signal):
        """ Enable / disable test signal """
        if signal == 0:
            self.warn("Disabling synthetic square wave")
            try:
                self.char_write.write(b']')
            except Exception as e:
                print("Something went wrong while setting signal: " + str(e))
        elif signal == 1:
            self.warn("Eisabling synthetic square wave")
            try:
                self.char_write.write(b'[')
            except Exception as e:
                print("Something went wrong while setting signal: " + str(e))
        else:
            self.warn(
                "%s is not a known test signal. Valid signal is 0-1" % signal)

    def set_channel(self, channel, toggle_position):
        """ Enable / disable channels """
        try:
            # Commands to set toggle to on position
            if toggle_position == 1:
                if channel is 1:
                    self.ser.write(b'!')
                if channel is 2:
                    self.ser.write(b'@')
                if channel is 3:
                    self.ser.write(b'#')
                if channel is 4:
                    self.ser.write(b'$')
            # Commands to set toggle to off position
            elif toggle_position == 0:
                if channel is 1:
                    self.ser.write(b'1')
                if channel is 2:
                    self.ser.write(b'2')
                if channel is 3:
                    self.ser.write(b'3')
                if channel is 4:
                    self.ser.write(b'4')
        except Exception as e:
            print("Something went wrong while setting channels: " + str(e))

    """
  
    Clean Up (atexit)
  
    """

    def stop(self):
        print("Stopping streaming...")
        self.streaming = False
        # connection might be already down here
        try:
            if self.impedance:
                print("Stopping with impedance testing")
                self.ser_write(b'Z')
            else:
                self.ser_write(b's')
        except Exception as e:
            print("Something went wrong while asking the board to stop streaming: " + str(e))
        if self.log:
            logging.warning('sent <s>: stopped streaming')

    def disconnect(self):
        if (self.streaming == True):
            self.stop()
        print("Closing BLE..")
        try:
            self.char_discon.write(b' ')
        except Exception as e:
            print("Something went wrong while asking the board to disconnect: " + str(e))
        # should not try to read/write anything after that, will crash
        try:
            self.gang.disconnect()
        except Exception as e:
            print("Something went wrong while shutting down BLE link: " + str(e))
        logging.warning('BLE closed')

    """
  
        SETTINGS AND HELPERS
  
    """

    def warn(self, text):
        if self.log:
            # log how many packets where sent succesfully in between warnings
            if self.log_packet_count:
                logging.info('Data packets received:' +
                             str(self.log_packet_count))
                self.log_packet_count = 0
            logging.warning(text)
        print("Warning: %s" % text)

    def check_connection(self):
        """ Check connection quality in term of lag and number of packets drop.
         Reinit connection if necessary.
         FIXME: parameters given to the board will be lost.
         """
        # stop checking when we're no longer streaming
        if not self.streaming:
            return
        # check number of dropped packets and duration without new packets, deco/reco if too large
        if self.packets_dropped > self.max_packets_to_skip:
            self.warn("Too many packets dropped, attempt to reconnect")
            self.reconnect()
        elif self.timeout > 0 and timeit.default_timer() - self.time_last_packet > self.timeout:
            self.warn("Too long since got new data, attempt to reconnect")
            # if error, attempt to reconect
            self.reconnect()

    def reconnect(self):
        """ In case of poor connection, will shut down and relaunch everything.
        FIXME: parameters given to the board will be lost."""
        self.warn('Reconnecting')
        self.stop()
        self.disconnect()
        self.connect()
        self.init_streaming()


class OpenBCISample(object):
    """Object encapsulating a single sample from the OpenBCI board."""

    def __init__(self, packet_id, channel_data, aux_data, imp_data):
        self.id = packet_id
        self.channel_data = channel_data
        self.aux_data = aux_data
        self.imp_data = imp_data


class GanglionDelegate(DefaultDelegate):
    """ Called by bluepy (handling BLE connection) when new data arrive, parses samples. """

    def __init__(self, scaling_output=True):
        DefaultDelegate.__init__(self)
        # holds samples until OpenBCIBoard claims them
        self.samples = []
        # detect gaps between packets
        self.last_id = -1
        self.packets_dropped = 0
        # save uncompressed data to compute deltas
        self.lastChannelData = [0, 0, 0, 0]
        # 18bit data got here and then accelerometer with it
        self.lastAcceleromoter = [0, 0, 0]
        # when the board is manually set in the right mode (z to start, Z to stop)
        # impedance will be measured. 4 channels + ref
        self.lastImpedance = [0, 0, 0, 0, 0]
        self.scaling_output = scaling_output
        # handling incoming ASCII messages
        self.receiving_ASCII = False
        self.time_last_ASCII = timeit.default_timer()

    def handleNotification(self, cHandle, data):
        if len(data) < 1:
            print('Warning: a packet should at least hold one byte...')
            return
        self.parse(data)

    """
      PARSER:
      Parses incoming data packet into OpenBCISample -- see docs. 
      Will call the corresponding parse* function depending on the format of the packet.
    """

    def parse(self, packet):
        # bluepy returns INT with python3 and STR with python2
        if type(packet) is str:
            # convert a list of strings in bytes
            unpac = struct.unpack(str(len(packet)) + 'B', "".join(packet))
        else:
            unpac = packet

        start_byte = unpac[0]

        # Give the informative part of the packet to proper handler
        # split between ID and data bytes
        # Raw uncompressed
        if start_byte == 0:
            self.receiving_ASCII = False
            self.parseRaw(start_byte, unpac[1:])
        # 18-bit compression with Accelerometer
        elif start_byte >= 1 and start_byte <= 100:
            self.receiving_ASCII = False
            self.parse18bit(start_byte, unpac[1:])
        # 19-bit compression without Accelerometer
        elif start_byte >= 101 and start_byte <= 200:
            self.receiving_ASCII = False
            self.parse19bit(start_byte - 100, unpac[1:])
        # Impedance Channel
        elif start_byte >= 201 and start_byte <= 205:
            self.receiving_ASCII = False
            self.parseImpedance(start_byte, packet[1:])
        # Part of ASCII -- TODO: better formatting of incoming ASCII
        elif start_byte == 206:
            print("%\t" + str(packet[1:]))
            self.receiving_ASCII = True
            self.time_last_ASCII = timeit.default_timer()

            # End of ASCII message
        elif start_byte == 207:
            print("%\t" + str(packet[1:]))
            print("$$$")
            self.receiving_ASCII = False
        else:
            print("Warning: unknown type of packet: " + str(start_byte))

    def parseRaw(self, packet_id, packet):
        """ Dealing with "Raw uncompressed" """
        if len(packet) != 19:
            print('Wrong size, for raw data' +
                  str(len(packet)) + ' instead of 19 bytes')
            return

        chan_data = []
        # 4 channels of 24bits, take values one by one
        for i in range(0, 12, 3):
            chan_data.append(conv24bitsToInt(packet[i:i + 3]))
        # save uncompressed raw channel for future use and append whole sample
        self.pushSample(packet_id, chan_data,
                        self.lastAcceleromoter, self.lastImpedance)
        self.lastChannelData = chan_data
        self.updatePacketsCount(packet_id)

    def parse19bit(self, packet_id, packet):
        """ Dealing with "19-bit compression without Accelerometer" """
        if len(packet) != 19:
            print('Wrong size, for 19-bit compression data' +
                  str(len(packet)) + ' instead of 19 bytes')
            return

        # should get 2 by 4 arrays of uncompressed data
        deltas = decompressDeltas19Bit(packet)
        # the sample_id will be shifted
        delta_id = 1
        for delta in deltas:
            # convert from packet to sample id
            sample_id = (packet_id - 1) * 2 + delta_id
            # 19bit packets hold deltas between two samples
            # TODO: use more broadly numpy
            full_data = list(np.array(self.lastChannelData) - np.array(delta))
            # NB: aux data updated only in 18bit mode, send values here only to be consistent
            self.pushSample(sample_id, full_data,
                            self.lastAcceleromoter, self.lastImpedance)
            self.lastChannelData = full_data
            delta_id += 1
        self.updatePacketsCount(packet_id)

    def parse18bit(self, packet_id, packet):
        """ Dealing with "18-bit compression without Accelerometer" """
        if len(packet) != 19:
            print('Wrong size, for 18-bit compression data' +
                  str(len(packet)) + ' instead of 19 bytes')
            return

        # accelerometer X
        if packet_id % 10 == 1:
            self.lastAcceleromoter[0] = conv8bitToInt8(packet[18])
        # accelerometer Y
        elif packet_id % 10 == 2:
            self.lastAcceleromoter[1] = conv8bitToInt8(packet[18])
        # accelerometer Z
        elif packet_id % 10 == 3:
            self.lastAcceleromoter[2] = conv8bitToInt8(packet[18])

        # deltas: should get 2 by 4 arrays of uncompressed data
        deltas = decompressDeltas18Bit(packet[:-1])
        # the sample_id will be shifted
        delta_id = 1
        for delta in deltas:
            # convert from packet to sample id
            sample_id = (packet_id - 1) * 2 + delta_id
            # 19bit packets hold deltas between two samples
            # TODO: use more broadly numpy
            full_data = list(np.array(self.lastChannelData) - np.array(delta))
            self.pushSample(sample_id, full_data,
                            self.lastAcceleromoter, self.lastImpedance)
            self.lastChannelData = full_data
            delta_id += 1
        self.updatePacketsCount(packet_id)

    def parseImpedance(self, packet_id, packet):
        """ Dealing with impedance data. packet: ASCII data.
        NB: will take few packet (seconds) to fill
        """
        if packet[-2:] != b"Z\n":
            print('Wrong format for impedance check, should be ASCII ending with "Z\\n"')

        # convert from ASCII to actual value
        imp_value = int(packet[:-2]) / 2
        # from 201 to 205 codes to the right array size
        self.lastImpedance[packet_id - 201] = imp_value
        self.pushSample(packet_id - 200, self.lastChannelData,
                        self.lastAcceleromoter, self.lastImpedance)

    def pushSample(self, sample_id, chan_data, aux_data, imp_data):
        """ Add a sample to inner stack, setting ID and dealing with scaling if necessary. """
        if self.scaling_output:
            chan_data = list(np.array(chan_data) * scale_fac_uVolts_per_count)
            aux_data = list(np.array(aux_data) * scale_fac_accel_G_per_count)
        sample = OpenBCISample(sample_id, chan_data, aux_data, imp_data)
        self.samples.append(sample)

    def updatePacketsCount(self, packet_id):
        """Update last packet ID and dropped packets"""
        if self.last_id == -1:
            self.last_id = packet_id
            self.packets_dropped = 0
            return
        # ID loops every 101 packets
        if packet_id > self.last_id:
            self.packets_dropped = packet_id - self.last_id - 1
        else:
            self.packets_dropped = packet_id + 101 - self.last_id - 1
        self.last_id = packet_id
        if self.packets_dropped > 0:
            print("Warning: dropped " + str(self.packets_dropped) + " packets.")

    def getSamples(self):
        """ Retrieve and remove from buffer last samples. """
        unstack_samples = self.samples
        self.samples = []
        return unstack_samples

    def getMaxPacketsDropped(self):
        """ While processing last samples, how many packets were dropped?"""
        # TODO: return max value of the last samples array?
        return self.packets_dropped


"""
  DATA conversion, for the most part courtesy of OpenBCI_NodeJS_Ganglion

"""


def conv24bitsToInt(unpacked):
    """ Convert 24bit data coded on 3 bytes to a proper integer """
    if len(unpacked) != 3:
        raise ValueError("Input should be 3 bytes long.")

    # FIXME: quick'n dirty, unpack wants strings later on
    literal_read = struct.pack('3B', unpacked[0], unpacked[1], unpacked[2])

    # 3byte int in 2s compliment
    if (unpacked[0] > 127):
        pre_fix = bytes(bytearray.fromhex('FF'))
    else:
        pre_fix = bytes(bytearray.fromhex('00'))

    literal_read = pre_fix + literal_read

    # unpack little endian(>) signed integer(i) (makes unpacking platform independent)
    myInt = struct.unpack('>i', literal_read)[0]

    return myInt


def conv19bitToInt32(threeByteBuffer):
    """ Convert 19bit data coded on 3 bytes to a proper integer (LSB bit 1 used as sign). """
    if len(threeByteBuffer) != 3:
        raise ValueError("Input should be 3 bytes long.")

    prefix = 0

    # if LSB is 1, negative number, some hasty unsigned to signed conversion to do
    if threeByteBuffer[2] & 0x01 > 0:
        prefix = 0b1111111111111
        return ((prefix << 19) | (threeByteBuffer[0] << 16) |
                (threeByteBuffer[1] << 8) | threeByteBuffer[2]) | ~0xFFFFFFFF
    else:
        return (prefix << 19) | (threeByteBuffer[0] << 16) |\
               (threeByteBuffer[1] << 8) | threeByteBuffer[2]


def conv18bitToInt32(threeByteBuffer):
    """ Convert 18bit data coded on 3 bytes to a proper integer (LSB bit 1 used as sign) """
    if len(threeByteBuffer) != 3:
        raise ValueError("Input should be 3 bytes long.")

    prefix = 0

    # if LSB is 1, negative number, some hasty unsigned to signed conversion to do
    if threeByteBuffer[2] & 0x01 > 0:
        prefix = 0b11111111111111
        return ((prefix << 18) | (threeByteBuffer[0] << 16) |
                (threeByteBuffer[1] << 8) | threeByteBuffer[2]) | ~0xFFFFFFFF
    else:
        return (prefix << 18) | (threeByteBuffer[0] << 16) |\
               (threeByteBuffer[1] << 8) | threeByteBuffer[2]


def conv8bitToInt8(byte):
    """ Convert one byte to signed value """

    if byte > 127:
        return (256 - byte) * (-1)
    else:
        return byte


def decompressDeltas19Bit(buffer):
    """
    Called to when a compressed packet is received.
    buffer: Just the data portion of the sample. So 19 bytes.
    return {Array} - An array of deltas of shape 2x4
    (2 samples per packet and 4 channels per sample.)
    """
    if len(buffer) != 19:
        raise ValueError("Input should be 19 bytes long.")

    receivedDeltas = [[0, 0, 0, 0], [0, 0, 0, 0]]

    # Sample 1 - Channel 1
    miniBuf = [
        (buffer[0] >> 5),
        ((buffer[0] & 0x1F) << 3 & 0xFF) | (buffer[1] >> 5),
        ((buffer[1] & 0x1F) << 3 & 0xFF) | (buffer[2] >> 5)
    ]

    receivedDeltas[0][0] = conv19bitToInt32(miniBuf)

    # Sample 1 - Channel 2
    miniBuf = [
        (buffer[2] & 0x1F) >> 2,
        (buffer[2] << 6 & 0xFF) | (buffer[3] >> 2),
        (buffer[3] << 6 & 0xFF) | (buffer[4] >> 2)
    ]
    receivedDeltas[0][1] = conv19bitToInt32(miniBuf)

    # Sample 1 - Channel 3
    miniBuf = [
        ((buffer[4] & 0x03) << 1 & 0xFF) | (buffer[5] >> 7),
        ((buffer[5] & 0x7F) << 1 & 0xFF) | (buffer[6] >> 7),
        ((buffer[6] & 0x7F) << 1 & 0xFF) | (buffer[7] >> 7)
    ]
    receivedDeltas[0][2] = conv19bitToInt32(miniBuf)

    # Sample 1 - Channel 4
    miniBuf = [
        ((buffer[7] & 0x7F) >> 4),
        ((buffer[7] & 0x0F) << 4 & 0xFF) | (buffer[8] >> 4),
        ((buffer[8] & 0x0F) << 4 & 0xFF) | (buffer[9] >> 4)
    ]
    receivedDeltas[0][3] = conv19bitToInt32(miniBuf)

    # Sample 2 - Channel 1
    miniBuf = [
        ((buffer[9] & 0x0F) >> 1),
        (buffer[9] << 7 & 0xFF) | (buffer[10] >> 1),
        (buffer[10] << 7 & 0xFF) | (buffer[11] >> 1)
    ]
    receivedDeltas[1][0] = conv19bitToInt32(miniBuf)

    # Sample 2 - Channel 2
    miniBuf = [
        ((buffer[11] & 0x01) << 2 & 0xFF) | (buffer[12] >> 6),
        (buffer[12] << 2 & 0xFF) | (buffer[13] >> 6),
        (buffer[13] << 2 & 0xFF) | (buffer[14] >> 6)
    ]
    receivedDeltas[1][1] = conv19bitToInt32(miniBuf)

    # Sample 2 - Channel 3
    miniBuf = [
        ((buffer[14] & 0x38) >> 3),
        ((buffer[14] & 0x07) << 5 & 0xFF) | ((buffer[15] & 0xF8) >> 3),
        ((buffer[15] & 0x07) << 5 & 0xFF) | ((buffer[16] & 0xF8) >> 3)
    ]
    receivedDeltas[1][2] = conv19bitToInt32(miniBuf)

    # Sample 2 - Channel 4
    miniBuf = [(buffer[16] & 0x07), buffer[17], buffer[18]]
    receivedDeltas[1][3] = conv19bitToInt32(miniBuf)

    return receivedDeltas


def decompressDeltas18Bit(buffer):
    """
    Called to when a compressed packet is received.
    buffer: Just the data portion of the sample. So 19 bytes.
    return {Array} - An array of deltas of shape 2x4
    (2 samples per packet and 4 channels per sample.)
    """
    if len(buffer) != 18:
        raise ValueError("Input should be 18 bytes long.")

    receivedDeltas = [[0, 0, 0, 0], [0, 0, 0, 0]]

    # Sample 1 - Channel 1
    miniBuf = [
        (buffer[0] >> 6),
        ((buffer[0] & 0x3F) << 2 & 0xFF) | (buffer[1] >> 6),
        ((buffer[1] & 0x3F) << 2 & 0xFF) | (buffer[2] >> 6)
    ]
    receivedDeltas[0][0] = conv18bitToInt32(miniBuf)

    # Sample 1 - Channel 2
    miniBuf = [
        (buffer[2] & 0x3F) >> 4,
        (buffer[2] << 4 & 0xFF) | (buffer[3] >> 4),
        (buffer[3] << 4 & 0xFF) | (buffer[4] >> 4)
    ]
    receivedDeltas[0][1] = conv18bitToInt32(miniBuf)

    # Sample 1 - Channel 3
    miniBuf = [
        (buffer[4] & 0x0F) >> 2,
        (buffer[4] << 6 & 0xFF) | (buffer[5] >> 2),
        (buffer[5] << 6 & 0xFF) | (buffer[6] >> 2)
    ]
    receivedDeltas[0][2] = conv18bitToInt32(miniBuf)

    # Sample 1 - Channel 4
    miniBuf = [
        (buffer[6] & 0x03),
        buffer[7],
        buffer[8]
    ]
    receivedDeltas[0][3] = conv18bitToInt32(miniBuf)

    # Sample 2 - Channel 1
    miniBuf = [
        (buffer[9] >> 6),
        ((buffer[9] & 0x3F) << 2 & 0xFF) | (buffer[10] >> 6),
        ((buffer[10] & 0x3F) << 2 & 0xFF) | (buffer[11] >> 6)
    ]
    receivedDeltas[1][0] = conv18bitToInt32(miniBuf)

    # Sample 2 - Channel 2
    miniBuf = [
        (buffer[11] & 0x3F) >> 4,
        (buffer[11] << 4 & 0xFF) | (buffer[12] >> 4),
        (buffer[12] << 4 & 0xFF) | (buffer[13] >> 4)
    ]
    receivedDeltas[1][1] = conv18bitToInt32(miniBuf)

    # Sample 2 - Channel 3
    miniBuf = [
        (buffer[13] & 0x0F) >> 2,
        (buffer[13] << 6 & 0xFF) | (buffer[14] >> 2),
        (buffer[14] << 6 & 0xFF) | (buffer[15] >> 2)
    ]
    receivedDeltas[1][2] = conv18bitToInt32(miniBuf)

    # Sample 2 - Channel 4
    miniBuf = [
        (buffer[15] & 0x03),
        buffer[16],
        buffer[17]
    ]
    receivedDeltas[1][3] = conv18bitToInt32(miniBuf)

    return receivedDeltas
