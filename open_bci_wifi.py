"""
Core OpenBCI object for handling connections and samples from the WiFi Shield

Note that the LIB will take care on its own to print incoming ASCII messages if any (FIXME, BTW).

EXAMPLE USE:

def handle_sample(sample):
  print(sample.channels_data)

wifi = OpenBCIWifi()
wifi.start(handle_sample)

TODO: Cyton/Ganglion JSON
TODO: Ganglion Raw
TODO: Cyton Raw

"""
import struct
import time
import timeit
import atexit
import logging
import numpy as np
import sys
import pdb
import glob
import ssdp
import urllib2
import xmltodict
import re
import asyncore
import socket

SAMPLE_RATE = 0  # Hz

'''
#Commands for in SDK

command_stop = "s";
command_startBinary = "b";
'''


class OpenBCIWifi(object):
    """
    Handle a connection to an OpenBCI wifi shield.

    Args:
      ip_address: The IP address of the WiFi Shield, "None" to attempt auto-detect.
      shield_name: The unique name of the WiFi Shield, such as `OpenBCI-2AD4`, will use SSDP to get IP address still,
        if `shield_name` is "None" and `ip_address` is "None", will connect to the first WiFi Shield found using SSDP
      sample_rate: The sample rate to set the attached board to. If the sample rate picked is not a sample rate the attached
        board can support, i.e. you send 300 to Cyton, then error will be thrown.
      log:
      timeout: in seconds, disconnect / reconnect after a period without new data -- should be high if impedance check
      max_packets_to_skip: will try to disconnect / reconnect after too many packets are skipped
    """

    def __init__(self, ip_address=None, shield_name=None, sample_rate=None, log=True, timeout=2,
                 max_packets_to_skip=20):
        # these one are used
        self.log = log  # print_incoming_text needs log
        self.streaming = False
        self.timeout = timeout
        self.max_packets_to_skip = max_packets_to_skip
        self.impedance = False
        self.ip_address = ip_address
        self.shield_name = shield_name
        self.sample_rate = sample_rate

        # might be handy to know API
        self.board_type = "none"

        if self.log:
            print("Welcome to OpenBCI Native WiFi Shield Driver - Please contribute code!")
        if ip_address is None:
            self.ip_address = self.find_wifi_shield()

        self.local_ip_address = self._get_local_ip_address()

        # Intentionally bind to port 0
        self.local_wifi_server = WiFiShieldServer(self.local_ip_address, 0)
        asyncore.loop()
        if self.log:
            print("Opened socket on %s:%d" % (self.local_ip_address, self.local_wifi_server.getsockname()[1]))

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

    def _get_local_ip_address(self):
        """
        Gets the local ip address of this computer
        @returns str Local IP address
        """
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip_address = s.getsockname()[0]
        s.close()
        return local_ip_address

    def getBoardType(self):
        """ Returns the version of the board """
        return self.board_type

    def setImpedance(self, flag):
        """ Enable/disable impedance measure """
        self.impedance = bool(flag)

    def connect(self):
        """ Connect to the board and configure it. Note: recreates various objects upon call. """
        if self.ip_address is None:
            raise ValueError('self.ip_address cannot be None')

        if self.log:
            print ("Init WiFi connection with IP: " + self.ip_address)


        self.gang = Peripheral(self.port, 'random')  # ADDR_TYPE_RANDOM

        print ("Get mainservice...")
        self.service = self.gang.getServiceByUUID(BLE_SERVICE)
        print ("Got:" + str(self.service))

        print ("Get characteristics...")
        self.char_read = self.service.getCharacteristics(BLE_CHAR_RECEIVE)[0]
        print ("receive, properties: " + str(self.char_read.propertiesToString()) + ", supports read: " + str(
            self.char_read.supportsRead()))

        self.char_write = self.service.getCharacteristics(BLE_CHAR_SEND)[0]
        print ("write, properties: " + str(self.char_write.propertiesToString()) + ", supports read: " + str(
            self.char_write.supportsRead()))

        self.char_discon = self.service.getCharacteristics(BLE_CHAR_DISCONNECT)[0]
        print ("disconnect, properties: " + str(self.char_discon.propertiesToString()) + ", supports read: " + str(
            self.char_discon.supportsRead()))

        # set delegate to handle incoming data
        # self.delegate = GanglionDelegate(self.scaling_output)
        # self.gang.setDelegate(self.delegate)

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

    def find_wifi_shield(self, shield_name=None):
        """Detects Ganglion board MAC address -- if more than 1 around, will select first. Needs root privilege."""

        print("Try to find WiFi shields on your local wireless network")
        scan_time = 5
        print("Scanning for 5 seconds nearby devices...")

        list_ip = []
        list_id = []
        found_shield = False

        def wifi_shield_found(response):
            res = urllib2.urlopen(response.location).read()
            device_description = xmltodict.parse(res)
            cur_shield_name = str(device_description['root']['device']['serialNumber'])
            cur_base_url = str(device_description['root']['URLBase'])
            cur_ip_address = re.findall(r'[0-9]+(?:\.[0-9]+){3}', cur_base_url)[0]
            list_id.append(cur_shield_name)
            list_ip.append(cur_ip_address)
            if shield_name is not None:
                if shield_name == cur_shield_name:
                    found_shield = True
                    return cur_ip_address

        ssdp_hits = ssdp.discover("urn:schemas-upnp-org:device:Basic:1", timeout=3, wifi_found_cb=wifi_shield_found)

        nb_wifi_shields = 0
        if not found_shield:
            nb_wifi_shields = len(list_id)
        else:
            nb_wifi_shields = 1

        if nb_wifi_shields < 1:
            print("No WiFi Shield found ;(")
            raise OSError('Cannot find OpenBCI WiFi Shield with local name')

        if nb_wifi_shields > 1:
            print(
                "Found " + str(nb_wifi_shields) +
                ", selecting first named: " + list_id[0] +
                " with IPV4: " + list_ip[0])
            return list_ip[0]

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
          callback: A callback function -- or a list of functions -- that will receive a single argument of the
              OpenBCISample object captured.
        """
        if not self.streaming:
            self.init_streaming()

        start_time = timeit.default_timer()

        # Enclose callback funtion in a list if it comes alone
        if not isinstance(callback, list):
            callback = [callback]

        while self.streaming:
            # should the board get disconnected and we could not wait for notification anymore, a reco should be attempted through timeout mechanism
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
                self.stop();
            if self.log:
                self.log_packet_count = self.log_packet_count + 1;

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
            self.warn("%s is not a known test signal. Valid signal is 0-1" % (signal))

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
                logging.info('Data packets received:' + str(self.log_packet_count))
                self.log_packet_count = 0;
            logging.warning(text)
        print("Warning: %s" % text)

    def check_connection(self):
        """ Check connection quality in term of lag and number of packets drop. Reinit connection if necessary. FIXME: parameters given to the board will be lost."""
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
        """ In case of poor connection, will shut down and relaunch everything. FIXME: parameters given to the board will be lost."""
        self.warn('Reconnecting')
        self.stop()
        self.disconnect()
        self.connect()
        self.init_streaming()


class OpenBCISample(object):
    """Object encapulsating a single sample from the OpenBCI board."""

    def __init__(self, packet_id, channel_data, aux_data, imp_data):
        self.id = packet_id
        self.channel_data = channel_data
        self.aux_data = aux_data
        self.imp_data = imp_data


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


def conv8bitToInt8(byte):
    """ Convert one byte to signed value """

    if byte > 127:
        return (256 - byte) * (-1)
    else:
        return byte


class WiFiShieldHandler(asyncore.dispatcher_with_send):

    def handle_read(self):
        data = self.recv(8192)
        if data:
            print(data)


class WiFiShieldServer(asyncore.dispatcher):

    def __init__(self, host, port):
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind((host, port))
        self.listen(5)

    def handle_accept(self):
        pair = self.accept()
        if pair is not None:
            sock, addr = pair
            print 'Incoming connection from %s' % repr(addr)
            handler = WiFiShieldHandler(sock)
