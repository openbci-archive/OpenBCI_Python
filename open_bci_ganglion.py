"""
Core OpenBCI object for handling connections and samples from the gnaglion board.

EXAMPLE USE:

def handle_sample(sample):
  print(sample.channels)

board = OpenBCIBoard()
board.start(handle_sample)

TODO: Pick between several boards

"""
import struct
import numpy as np
import time
import timeit
import atexit
import logging
import threading
import sys
import pdb
import glob
import bluepy

SAMPLE_RATE = 100.0  # Hz
scale_fac_uVolts_per_count = 1200 * 8388607.0 * 1.5 * 51.0;

BLE_SERVICE = "fe84"
BLE_RECEIVE = "2d30c082f39f4ce6923f3484ea480596"
BLE_SEND = "2d30c083f39f4ce6923f3484ea480596"
BLE_DISCONNECT = "2d30c084f39f4ce6923f3484ea48059"

'''
#Commands for in SDK http://docs.openbci.com/Hardware/08-Ganglion_Data_Forma

command_stop = "s";
command_startBinary = "b";
'''

class OpenBCIBoard(object):
  """

  Handle a connection to an OpenBCI board.

  Args:
    port, baud, filter_data, daisy: Not used, for compatibility with v3
  """

  def __init__(self, port=None, baud=0, filter_data=False,
    scaled_output=True, daisy=False, log=True, timeout=None):
    self.log = log # print_incoming_text needs log
    self.streaming = False
    self.timeout = timeout

    print("Connecting to V3 at port %s" %(port))
    self.ser = serial.Serial(port= port, baudrate = baud, timeout=timeout)

    print("Serial established...")

    time.sleep(2)
    #Initialize 32-bit board, doesn't affect 8bit board
    self.ser.write(b'v');


    #wait for device to be ready
    time.sleep(1)
    self.print_incoming_text()

    self.streaming = False
    self.filtering_data = filter_data
    self.scaling_output = scaled_output
    self.eeg_channels_per_sample = 4 # number of EEG channels per sample *from the board*
    self.read_state = 0
    self.log_packet_count = 0
    self.last_reconnect = 0
    self.reconnect_freq = 5
    self.packets_dropped = 0

    #Disconnects from board when terminated
    atexit.register(self.disconnect)
    
  def ser_write(self, b):
    """Access serial port object for write""" 
    self.ser.write(b)

  def ser_read(self):
    """Access serial port object for read""" 
    return self.ser.read()

  def ser_inWaiting(self):
    """Access serial port object for inWaiting""" 
    return self.ser.inWaiting();
    
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
      self.ser.write(b'b')
      self.streaming = True

    start_time = timeit.default_timer()

    # Enclose callback funtion in a list if it comes alone
    if not isinstance(callback, list):
      callback = [callback]
    

    #Initialize check connection
    self.check_connection()

    while self.streaming:

      # read current sample
      sample = self._read_serial_binary()
      for call in callback:
          call(sample)
      
      if(lapse > 0 and timeit.default_timer() - start_time > lapse):
        self.stop();
      if self.log:
        self.log_packet_count = self.log_packet_count + 1;
  
  
  """
    PARSER:
    Parses incoming data packet into OpenBCISample.
    Incoming Packet Structure:
    Start Byte(1)|Sample ID(1)|Channel Data(24)|Aux Data(6)|End Byte(1)
    0xA0|0-255|8, 3-byte signed ints|3 2-byte signed ints|0xC0

  """
  def _read_serial_binary(self, max_bytes_to_skip=3000):
    def read(n):
      bb = self.ser.read(n)
      if not bb:
        self.warn('Device appears to be stalled. Quitting...')
        sys.exit()
        raise Exception('Device Stalled')
        sys.exit()
        return '\xFF'
      else:
        return bb

    for rep in range(max_bytes_to_skip):

      #---------Start Byte & ID---------
      if self.read_state == 0:
        
        b = read(1)
        
        if struct.unpack('B', b)[0] == START_BYTE:
          if(rep != 0):
            self.warn('Skipped %d bytes before start found' %(rep))
            rep = 0;
          packet_id = struct.unpack('B', read(1))[0] #packet id goes from 0-255
          log_bytes_in = str(packet_id);

          self.read_state = 1

      #---------Channel Data---------
      elif self.read_state == 1:
        channel_data = []
        for c in range(self.eeg_channels_per_sample):

          #3 byte ints
          literal_read = read(3)

          unpacked = struct.unpack('3B', literal_read)
          log_bytes_in = log_bytes_in + '|' + str(literal_read);

          #3byte int in 2s compliment
          if (unpacked[0] >= 127):
            pre_fix = bytes(bytearray.fromhex('FF')) 
          else:
            pre_fix = bytes(bytearray.fromhex('00'))


          literal_read = pre_fix + literal_read;

          #unpack little endian(>) signed integer(i) (makes unpacking platform independent)
          myInt = struct.unpack('>i', literal_read)[0]

          if self.scaling_output:
            channel_data.append(myInt*scale_fac_uVolts_per_count)
          else:
            channel_data.append(myInt)

        self.read_state = 2;

      #---------Accelerometer Data---------
      elif self.read_state == 2:
        aux_data = []
        for a in range(self.aux_channels_per_sample):

          #short = h
          acc = struct.unpack('>h', read(2))[0]
          log_bytes_in = log_bytes_in + '|' + str(acc);

          if self.scaling_output:
            aux_data.append(acc*scale_fac_accel_G_per_count)
          else:
              aux_data.append(acc)

        self.read_state = 3;
      #---------End Byte---------
      elif self.read_state == 3:
        val = struct.unpack('B', read(1))[0]
        log_bytes_in = log_bytes_in + '|' + str(val);
        self.read_state = 0 #read next packet
        if (val == END_BYTE):
          sample = OpenBCISample(packet_id, channel_data, aux_data)
          self.packets_dropped = 0
          return sample
        else:
          self.warn("ID:<%d> <Unexpected END_BYTE found <%s> instead of <%s>"      
            %(packet_id, val, END_BYTE))
          logging.debug(log_bytes_in);
          self.packets_dropped = self.packets_dropped + 1
  
  """

  Clean Up (atexit)

  """
  def stop(self):
    print("Stopping streaming...\nWait for buffer to flush...")
    self.streaming = False
    self.ser.write(b's')
    if self.log:
      logging.warning('sent <s>: stopped streaming')

  def disconnect(self):
    if(self.streaming == True):
      self.stop()
    if (self.ser.isOpen()):
      print("Closing Serial...")
      self.ser.close()
      logging.warning('serial closed')
       

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


  def print_incoming_text(self):
    """

    When starting the connection, print all the debug data until
    we get to a line with the end sequence '$$$'.

    """
    line = ''
    #Wait for device to send data
    time.sleep(1)
    
    if self.ser.inWaiting():
      line = ''
      c = ''
     #Look for end sequence $$$
      while '$$$' not in line:
        c = self.ser.read().decode('utf-8', errors='replace') # we're supposed to get UTF8 text, but the board might behave otherwise
        line += c
      print(line);
    else:
      self.warn("No Message")

  def check_connection(self, interval = 2, max_packets_to_skip=10):
    # stop checking when we're no longer streaming
    if not self.streaming:
      return
    #check number of dropped packages and establish connection problem if too large
    if self.packets_dropped > max_packets_to_skip:
      #if error, attempt to reconect
      self.reconnect()
    # check again again in 2 seconds
    threading.Timer(interval, self.check_connection).start()

  def reconnect(self):
    self.packets_dropped = 0
    self.warn('Reconnecting')
    self.stop()
    time.sleep(0.5)
    self.ser.write(b'b')
    time.sleep(0.5)
    self.streaming = True
    #self.attempt_reconnect = False


class OpenBCISample(object):
  """Object encapulsating a single sample from the OpenBCI board."""
  def __init__(self, packet_id, channel_data, aux_data):
    self.id = packet_id;
    self.channel_data = channel_data;
    self.aux_data = aux_data;

