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
import ssdp
import urllib2
import xmltodict
import re
import asyncore
import socket
import requests
import json

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
                 max_packets_to_skip=20, latency=10000):
        # these one are used
        self.log = log  # print_incoming_text needs log
        self.streaming = False
        self.timeout = timeout
        self.max_packets_to_skip = max_packets_to_skip
        self.impedance = False
        self.ip_address = ip_address
        self.shield_name = shield_name
        self.sample_rate = sample_rate
        self.latency = latency

        # might be handy to know API
        self.board_type = "none"
        # number of EEG channels
        self.eeg_channels_per_sample = 0
        self.read_state = 0
        self.log_packet_count = 0
        self.packets_dropped = 0
        self.time_last_packet = 0

        if self.log:
            print("Welcome to OpenBCI Native WiFi Shield Driver - Please contribute code!")

        self.local_ip_address = self._get_local_ip_address()

        # Intentionally bind to port 0
        self.local_wifi_server = WiFiShieldServer(self.local_ip_address, 0)
        self.local_wifi_server_port = self.local_wifi_server.getsockname()[1]
        if self.log:
            print("Opened socket on %s:%d" % (self.local_ip_address, self.local_wifi_server_port))

        if ip_address is None:
            self.find_wifi_shield(wifi_shield_cb=self.on_shield_found)
        else:
            self.on_shield_found(ip_address)

    def on_shield_found(self, ip_address):
        self.ip_address = ip_address
        self.connect()
        # Disconnects from board when terminated
        atexit.register(self.disconnect)

    def loop(self):
        asyncore.loop()

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

        """
        Docs on these HTTP requests and more are found:
        https://app.swaggerhub.com/apis/pushtheworld/openbci-wifi-server/1.3.0
        """

        res_board = requests.get("http://%s/board" % self.ip_address)

        if res_board.status_code == 200:
            board_info = res_board.json()
            if not board_info['board_connected']:
                raise RuntimeError("No board connected to WiFi Shield. Learn at docs.openbci.com")
            self.board_type = board_info['board_type']
            self.eeg_channels_per_sample = board_info['num_channels']
            if self.log:
                print("Connected to %s with %s channels" % (self.board_type, self.eeg_channels_per_sample))

        res_tcp_post = requests.post("http://%s/tcp" % self.ip_address,
                          json={
                                'ip': self.local_ip_address,
                                'port': self.local_wifi_server_port,
                                'output': 'json',
                                'delimiter': True,
                                'latency': self.latency
                                })
        if res_tcp_post.status_code == 200:
            tcp_status = res_tcp_post.json()
            if tcp_status['connected']:
                if self.log:
                    print("WiFi Shield to Python TCP Socket Established")
            else:
                raise RuntimeWarning("WiFi Shield is not able to connect to local server. Please open an issue.")

    def init_streaming(self):
        """ Tell the board to record like crazy. """
        res_stream_start = requests.get("http://%s/stream/start" % self.ip_address)
        if res_stream_start.status_code == 200:
            self.streaming = True
            self.packets_dropped = 0
            self.time_last_packet = timeit.default_timer()
        else:
            raise EnvironmentError("Unable to start streaming. Check API for status code %d on /stream/start" % res_stream_start.status_code)

    def find_wifi_shield(self, shield_name=None, wifi_shield_cb=None):
        """Detects Ganglion board MAC address -- if more than 1 around, will select first. Needs root privilege."""

        if self.log:
            print("Try to find WiFi shields on your local wireless network")
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
            found_shield = True
            if shield_name is None:
                print("Found WiFi Shield %s with IP Address %s" % (cur_shield_name, cur_ip_address))
                if wifi_shield_cb is not None:
                    wifi_shield_cb(cur_ip_address)
            else:
                if shield_name == cur_shield_name:
                    if wifi_shield_cb is not None:
                        wifi_shield_cb(cur_ip_address)

        ssdp_hits = ssdp.discover("urn:schemas-upnp-org:device:Basic:1", timeout=3, wifi_found_cb=wifi_shield_found)

        nb_wifi_shields = len(list_id)

        if nb_wifi_shields < 1:
            print("No WiFi Shields found ;(")
            raise OSError('Cannot find OpenBCI WiFi Shield with local name')

        if nb_wifi_shields > 1:
            print(
                "Found " + str(nb_wifi_shields) +
                ", selecting first named: " + list_id[0] +
                " with IPV4: " + list_ip[0])
            return list_ip[0]

    def wifi_write(self, output):
        """
        Pass through commands from the WiFi Shield to the Carrier board
        :param output: 
        :return: 
        """
        res_command_post = requests.post("http://%s/command" % self.ip_address,
                                         json={'command': output})
        if res_command_post.status_code == 200:
            ret_val = res_command_post.text
            if self.log:
                print(ret_val)
            return ret_val
        else:
            if self.log:
                print("Error code: %d %s" % (res_command_post.status_code, res_command_post.text))
            raise RuntimeError("Error code: %d %s" % (res_command_post.status_code, res_command_post.text))

    def getSampleRate(self):
        return SAMPLE_RATE

    def getNbEEGChannels(self):
        """Will not get new data on impedance check."""
        return self.eeg_channels_per_sample

    def start_streaming(self, callback, lapse=-1):
        """
        Start handling streaming data from the board. Call a provided callback
        for every single sample that is processed

        Args:
          callback: A callback function -- or a list of functions -- that will receive a single argument of the
              OpenBCISample object captured.
        """
        start_time = timeit.default_timer()

        # Enclose callback funtion in a list if it comes alone
        if not isinstance(callback, list):
            self.local_wifi_server.set_callback(callback)
        else:
            self.local_wifi_server.set_callback(callback[0])

        if not self.streaming:
            self.init_streaming()

        # while self.streaming:
        #     # should the board get disconnected and we could not wait for notification anymore, a reco should be attempted through timeout mechanism
        #     try:
        #         # at most we will get one sample per packet
        #         self.waitForNotifications(1. / self.getSampleRate())
        #     except Exception as e:
        #         print("Something went wrong while waiting for a new sample: " + str(e))
        #     # retrieve current samples on the stack
        #     samples = self.delegate.getSamples()
        #     self.packets_dropped = self.delegate.getMaxPacketsDropped()
        #     if samples:
        #         self.time_last_packet = timeit.default_timer()
        #         for call in callback:
        #             for sample in samples:
        #                 call(sample)
        #
        #     if (lapse > 0 and timeit.default_timer() - start_time > lapse):
        #         self.stop();
        #     if self.log:
        #         self.log_packet_count = self.log_packet_count + 1;
        #
        #     # Checking connection -- timeout and packets dropped
        #     self.check_connection()

    def test_signal(self, signal):
        """ Enable / disable test signal """
        if signal == 0:
            self.warn("Disabling synthetic square wave")
            try:
                self.wifi_write(']')
            except Exception as e:
                print("Something went wrong while setting signal: " + str(e))
        elif signal == 1:
            self.warn("Eisabling synthetic square wave")
            try:
                self.wifi_write('[')
            except Exception as e:
                print("Something went wrong while setting signal: " + str(e))
        else:
            self.warn("%s is not a known test signal. Valid signal is 0-1" % signal)

    def set_channel(self, channel, toggle_position):
        """ Enable / disable channels """
        try:
            # Commands to set toggle to on position
            if toggle_position == 1:
                if channel is 1:
                    self.wifi_write('!')
                if channel is 2:
                    self.wifi_write('@')
                if channel is 3:
                    self.wifi_write('#')
                if channel is 4:
                    self.wifi_write('$')
            # Commands to set toggle to off position
            elif toggle_position == 0:
                if channel is 1:
                    self.wifi_write('1')
                if channel is 2:
                    self.wifi_write('2')
                if channel is 3:
                    self.wifi_write('3')
                if channel is 4:
                    self.wifi_write('4')
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
                self.wifi_write('Z')
            else:
                self.wifi_write('s')
        except Exception as e:
            print("Something went wrong while asking the board to stop streaming: " + str(e))
        if self.log:
            logging.warning('sent <s>: stopped streaming')

    def disconnect(self):
        if self.streaming:
            self.stop()

        # should not try to read/write anything after that, will crash

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


class WiFiShieldHandler(asyncore.dispatcher_with_send):
    def __init__(self, sock, callback=None):
        asyncore.dispatcher_with_send.__init__(self, sock)

        self.callback = callback

    def handle_read(self):
        data = self.recv(3000)  # 3000 is the max data the WiFi shield is allowed to send over TCP
        if len(data) > 2:
            try:
                possible_chunks = data.split('\r\n')
                if len(possible_chunks) > 1:
                    possible_chunks = possible_chunks[:-1]
                for possible_chunk in possible_chunks:
                    if len(possible_chunk) > 2:
                        chunk_dict = json.loads(possible_chunk)
                        if 'chunk' in chunk_dict:
                            for sample in chunk_dict['chunk']:
                                if self.callback is not None:
                                    self.callback(sample)
                        else:
                            print("not a sample packet")
            except ValueError as e:
                print("failed to parse: %s" % data)
                print e
            except BaseException as e:
                print e


class WiFiShieldServer(asyncore.dispatcher):

    def __init__(self, host, port, callback=None):
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind((host, port))
        self.listen(5)
        self.callback = None
        self.handler = None

    def handle_accept(self):
        pair = self.accept()
        if pair is not None:
            sock, addr = pair
            print 'Incoming connection from %s' % repr(addr)
            self.handler = WiFiShieldHandler(sock, self.callback)

    def set_callback(self, callback):
        self.callback = callback
        if self.handler is not None:
            self.handler.callback = callback
