"""
Core OpenBCI object for handling connections and samples from the gnaglion board.

Note that the LIB will take care on its own to print incoming ASCII messages if any (FIXME, BTW).

EXAMPLE USE:

def handle_sample(sample):
  print(sample.channels_data)

board = OpenBCIBoard()
board.start(handle_sample)

TODO: Pick between several boards
TODO: support impedance
TODO: support accelerometer with n / N codes

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
# local bluepy should take precedence
import sys
sys.path.insert(0,"bluepy/bluepy")
from btle import Scanner, DefaultDelegate, Peripheral

SAMPLE_RATE = 200.0  # Hz
scale_fac_uVolts_per_count = 1200 * 8388607.0 * 1.5 * 51.0;

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

class OpenBCIBoard(object):
  """

  Handle a connection to an OpenBCI board.

  Args:
    port: MAC address of the Ganglion Board. "None" to attempt auto-detect.
    timeout: in seconds, if set will try to disconnect / reconnect after a period without new data
    max_packets_to_skip: will try to disconnect / reconnect after too many packets are skipped
    baud, filter_data, daisy: Not used, for compatibility with v3
  """

  def __init__(self, port=None, baud=0, filter_data=False,
    scaled_output=True, daisy=False, log=True, timeout=1, max_packets_to_skip=20):
    # unused, for compatibility with Cyton v3 API
    self.daisy = False
    
    self.log = log # print_incoming_text needs log
    self.streaming = False
    self.timeout = timeout
    self.max_packets_to_skip = max_packets_to_skip

    print("Looking for Ganglion board")
    if port == None:
      port = self.find_port()   
    self.port = port # find_port might not return string

    self.connect()

    self.streaming = False
    self.scaling_output = scaled_output
    self.eeg_channels_per_sample = 4 # number of EEG channels per sample *from the board*
    self.read_state = 0
    self.log_packet_count = 0
    self.packets_dropped = 0
    self.time_last_packet = 0

    # Disconnects from board when terminated
    atexit.register(self.disconnect)

  def connect(self):
    """ Connecting to board. Note: recreates various objects upon call. """
    print ("Init BLE connection with MAC: " + self.port)
    print ("NB: if it fails, try with root privileges.")
    self.gang = Peripheral(self.port, 'random') # ADDR_TYPE_RANDOM

    print ("Get mainservice...")
    self.service = self.gang.getServiceByUUID(BLE_SERVICE)
    print ("Got:" + str(self.service))
    
    print ("Get characteristics...")
    self.char_read = self.service.getCharacteristics(BLE_CHAR_RECEIVE)[0]
    print ("receive, properties: " + str(self.char_read.propertiesToString()) + ", supports read: " + str(self.char_read.supportsRead()))

    self.char_write = self.service.getCharacteristics(BLE_CHAR_SEND)[0]
    print ("write, properties: " + str(self.char_write.propertiesToString()) + ", supports read: " + str(self.char_write.supportsRead()))

    self.char_discon = self.service.getCharacteristics(BLE_CHAR_DISCONNECT)[0]
    print ("disconnect, properties: " + str(self.char_discon.propertiesToString()) + ", supports read: " + str(self.char_discon.supportsRead()))

    # set delegate to handle incoming data
    self.delegate = GanglionDelegate()
    self.gang.setDelegate(self.delegate)
    
    print("Turn on notifications")
    # nead up-to-date bluepy, cf https://github.com/IanHarvey/bluepy/issues/53
    self.desc_notify = self.char_read.getDescriptors(forUUID=0x2902)[0]
    try:
      self.desc_notify.write(b"\x01")
    except Exception as e:
      print("Something went wrong while trying to enable notification: " + str(e))
    
    print("Connection established")

  def init_steaming(self):
    """ Tell the board to record like crazy. """
    try:
      self.ser_write(b'b')
    except Exception as e:
      print("Something went wrong while asking the board to start streaming: " + str(e))
    self.streaming = True
    self.packets_dropped = 0
    self.time_last_packet = timeit.default_timer() 
    
  def find_port(self):
    """Detects Ganglion board MAC address -- if more than 1 around, will select first. Needs root privilege."""

    print("Try to detect Ganglion MAC address. NB: Turn on bluetooth and run as root for this to work! Might not work with every BLE dongles.")
    scan_time = 5
    print("Scanning for 5 seconds nearby devices...")

    #   From bluepy example
    class ScanDelegate(DefaultDelegate):
      def __init__(self):
        DefaultDelegate.__init__(self)

      def handleDiscovery(self, dev, isNewDev, isNewData):
        if isNewDev:
          print ("Discovered device: " + dev.addr)
        elif isNewData:
          print ("Received new data from: " + dev.addr)
  
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
        # "Ganglion" should appear inside the "value" associated to "Complete Local Name", e.g. "Ganglion-b2a6"
        for (adtype, desc, value) in dev.getScanData():
          if desc == "Complete Local Name" and   value.startswith("Ganglion"): 
            list_mac.append(dev.addr)
            list_id.append(value)
            print("Got Ganglion: " + value + ", with MAC: " + dev.addr)
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
      """Dummy function to emulate Cyton API, here we don't know a thing about input buffer."""
      return 0
  
  def getSampleRate(self):
      return SAMPLE_RATE
  
  def getNbEEGChannels(self):
      return self.eeg_channels_per_sample
  
  def getNbAUXChannels(self):
    """Not implemented on the Ganglion"""
    return 0 

  def start_streaming(self, callback, lapse=-1):
    """
    Start handling streaming data from the board. Call a provided callback
    for every single sample that is processed

    Args:
      callback: A callback function -- or a list of functions -- that will receive a single argument of the
          OpenBCISample object captured.
    """
    if not self.streaming:
      self.init_steaming()

    start_time = timeit.default_timer()

    # Enclose callback funtion in a list if it comes alone
    if not isinstance(callback, list):
      callback = [callback]

    while self.streaming:
      # should the board get disconnected and we could not wait for notification anymore, a reco should be attempted through timeout mechanism
      try:
        # at most we will get one sample per packet
        self.gang.waitForNotifications(1./self.getSampleRate())
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
      
      if(lapse > 0 and timeit.default_timer() - start_time > lapse):
        self.stop();
      if self.log:
        self.log_packet_count = self.log_packet_count + 1;
  
      # Checking connection -- timeout and packets dropped
      self.check_connection()

  
  """

  Clean Up (atexit)

  """
  def stop(self):
    print("Stopping streaming...")
    self.streaming = False
    # connection might be already down here
    try:
      self.ser_write(b's')
    except Exception as e:
      print("Something went wrong while asking the board to stop streaming: " + str(e))
    if self.log:
      logging.warning('sent <s>: stopped streaming')

  def disconnect(self):
    if(self.streaming == True):
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
      #log how many packets where sent succesfully in between warnings
      if self.log_packet_count:
        logging.info('Data packets received:'+str(self.log_packet_count))
        self.log_packet_count = 0;
      logging.warning(text)
    print("Warning: %s" % text)

  def check_connection(self):
    """ Check connection quality in term of lag and number of packets drop. Reinit connection if necessary. FIXME: parameters given to the board will be lost."""
    # stop checking when we're no longer streaming
    if not self.streaming:
      return
    #check number of dropped packets and duration without new packets, deco/reco if too large
    if self.packets_dropped > self.max_packets_to_skip:
      self.warn("Too many packets dropped, attempt to reconnect")
      self.reconnect()
    elif self.timeout > 0 and timeit.default_timer() - self.time_last_packet > self.timeout:
      self.warn("Too long since got new data, attempt to reconnect")
      #if error, attempt to reconect
      self.reconnect()

  def reconnect(self):
    """ In case of poor connection, will shut down and relaunch everything. FIXME: parameters given to the board will be lost."""
    self.warn('Reconnecting')
    self.stop()
    self.disconnect()
    self.connect()
    self.init_steaming()

class OpenBCISample(object):
  """Object encapulsating a single sample from the OpenBCI board. Note for Ganglion board: since most of the time two samples are compressed in one BLE packet, two consecutive samples will likely have the same ID."""
  def __init__(self, packet_id, channel_data, aux_data):
    self.id = packet_id;
    self.channel_data = channel_data;
    self.aux_data = aux_data;


class GanglionDelegate(DefaultDelegate):
  """ Called by bluepy (handling BLE connection) when new data arrive, parses samples. """
  def __init__(self):
      DefaultDelegate.__init__(self)
      # holds samples until OpenBCIBoard claims them
      self.samples = []
      # detect gaps between packets
      self.last_id = -1
      self.packets_dropped = 0
      # save uncompressed data to compute deltas
      self.lastChannelData = [0, 0, 0, 0]

  def handleNotification(self, cHandle, data):
    if len(data) < 1:
      print('Warning: a packet should at least hold one byte...')
      return
    self.parse(data)

  """
    PARSER:
    Parses incoming data packet into OpenBCISample -- see docs. Will call the corresponding parse* function depending on the format of the packet.
  """
  def parse(self, packet):
    # bluepy returnds INT with python3 and STR with python2 
    if type(packet) is str:
      # convert a list of strings in bytes
      unpac = struct.unpack(str(len(packet)) + 'B', "".join(packet))
    else:
      unpac = packet
     
    start_byte = unpac[0]

    # Give the informative part of the packet to proper handler -- split between ID and data bytes
    # Raw uncompressed
    if start_byte == 0:
      self.parseRaw(start_byte, unpac[1:])
    # 18-bit compression with Accelerometer
    elif start_byte >= 1 and start_byte <= 100:
      print("Warning: data not handled: '18-bit compression with Accelerometer'.") 
    # 19-bit compression without Accelerometer
    elif start_byte >=101 and start_byte <= 200:
      self.parse19bit(start_byte-100, unpac[1:])
    # Impedance Channel
    elif start_byte >= 201 and start_byte <= 205:
      print("Warning: data not handled: 'Impedance Channel'.") 
    # Part of ASCII -- TODO: better formatting of incoming ASCII
    elif start_byte == 206:
      print("%\t" + str(packet[1:]))
    # End of ASCII message
    elif start_byte == 207:
      print("%\t" + str(packet[1:]))
      print ("$$$")
    else:
      print("Warning: unknown type of packet: " + str(start_byte))

  def parseRaw(self, sample_id, packet):
    """ Dealing with "Raw uncompressed" """
    if len(packet) != 19:
      print('Wrong size, for raw data' + str(len(data)) + ' instead of 19 bytes')
      return

    chan_data = []
    # 4 channels of 24bits, take values one by one
    for i in range(0,12,3):
      chan_data.append(conv24bitsToInt(packet[i:i+3]))
    # save uncompressed raw channel for future use and append whole sample
    sample = OpenBCISample(sample_id, chan_data, [])
    self.samples.append(sample)
    self.lastChannelData = chan_data
    self.updatePacketsCount(sample_id)

  def parse19bit(self, sample_id, packet):
    """ Dealing with "19-bit compression without Accelerometer" """
    if len(packet) != 19:
      print('Wrong size, for 19-bit compression data' + str(len(data)) + ' instead of 19 bytes')
      return

    # should get 2 by 4 arrays of uncompressed data
    deltas = decompressDeltas19Bit(packet)
    for delta in deltas:
      # 19bit packets hold deltas between two samples
      # TODO: use more broadly numpy
      full_data = list(np.array(self.lastChannelData) - np.array(delta))
      sample = OpenBCISample(sample_id, full_data, [])
      self.samples.append(sample)
      self.lastChannelData = full_data
    self.updatePacketsCount(sample_id)

  def updatePacketsCount(self, sample_id):
    """Update last packet ID and dropped packets"""
    if self.last_id == -1:
      self.last_id = sample_id
      self.packets_dropped  = 0
      return
    # ID loops every 101 packets
    if sample_id > self.last_id:
      self.packets_dropped = sample_id - self.last_id - 1
    else:
      self.packets_dropped = sample_id + 101 - self.last_id - 1
    self.last_id = sample_id
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

  #3byte int in 2s compliment
  if (unpacked[0] >= 127):
    pre_fix = bytes(bytearray.fromhex('FF')) 
  else:
    pre_fix = bytes(bytearray.fromhex('00'))

  literal_read = pre_fix + literal_read;

  #unpack little endian(>) signed integer(i) (makes unpacking platform independent)
  myInt = struct.unpack('>i', literal_read)[0]

  return myInt

def conv19bitToInt32 (threeByteBuffer):
  """ Convert 19bit data coded on 3 bytes to a proper integer """ 
  if len(threeByteBuffer) != 3:
    raise ValueError("Input should be 3 bytes long.")

  prefix = 0;

  # if LSB is 1, negative number, some hasty unsigned to signed conversion to do
  if threeByteBuffer[2] & 0x01 > 0:
    prefix = 0b1111111111111;
    return ((prefix << 19) | (threeByteBuffer[0] << 16) | (threeByteBuffer[1] << 8) | threeByteBuffer[2]) | ~0xFFFFFFFF
  else:
    return (prefix << 19) | (threeByteBuffer[0] << 16) | (threeByteBuffer[1] << 8) | threeByteBuffer[2]

def decompressDeltas19Bit(buffer):
  """
  Called to when a compressed packet is received.
  buffer: Just the data portion of the sample. So 19 bytes.
  return {Array} - An array of deltas of shape 2x4 (2 samples per packet and 4 channels per sample.)
  """ 
  if len(buffer) != 19:
    raise ValueError("Input should be 19 bytes long.")
  
  receivedDeltas = [[0, 0, 0, 0],[0, 0, 0, 0]]

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

  return receivedDeltas;
