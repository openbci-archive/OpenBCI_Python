"""
Core OpenBCI object for handling connections and samples from the board.

EXAMPLE USE:

def handle_sample(sample):
  print(sample.channels)

board = OpenBCIBoard()
board.print_register_settings()
board.start(handle_sample)

NOTE: If daisy modules is enabled, the callback will occur every two samples, hence "packet_id" will only contain even numbers. As a side effect, the sampling rate will be divided by 2.

FIXME: at the moment we can just force daisy mode, do not check that the module is detected.


"""
import serial
import struct
import numpy as np
import time
import timeit
import atexit

SAMPLE_RATE = 250.0  # Hz
START_BYTE = bytes(0xA0)  # start of data packet
END_BYTE = bytes(0xC0)  # end of data packet
ADS1299_Vref = 4.5;  #reference voltage for ADC in ADS1299.  set by its hardware
ADS1299_gain = 24.0;  #assumed gain setting for ADS1299.  set by its Arduino code
scale_fac_uVolts_per_count = ADS1299_Vref/(pow(2,23)-1)/ADS1299_gain*1000000.;

'''
#Commands for in SDK http://docs.openbci.com/software/01-OpenBCI_SDK:

command_stop = "s";
command_startText = "x";
command_startBinary = "b";
command_startBinary_wAux = "n";
command_startBinary_4chan = "v";
command_activateFilters = "F";
command_deactivateFilters = "g";
command_deactivate_channel = {"1", "2", "3", "4", "5", "6", "7", "8"};
command_activate_channel = {"q", "w", "e", "r", "t", "y", "u", "i"};
command_activate_leadoffP_channel = {"!", "@", "#", "$", "%", "^", "&", "*"};  //shift + 1-8
command_deactivate_leadoffP_channel = {"Q", "W", "E", "R", "T", "Y", "U", "I"};   //letters (plus shift) right below 1-8
command_activate_leadoffN_channel = {"A", "S", "D", "F", "G", "H", "J", "K"}; //letters (plus shift) below the letters below 1-8
command_deactivate_leadoffN_channel = {"Z", "X", "C", "V", "B", "N", "M", "<"};   //letters (plus shift) below the letters below the letters below 1-8
command_biasAuto = "`";
command_biasFixed = "~";
'''

class OpenBCIBoard(object):
  """

  Handle a connection to an OpenBCI board.

  Args:
    port: The port to connect to.
    baud: The baud of the serial connection.
    daisy: Enable or disable daisy module and 16 chans readings
  """

  def __init__(self, port=None, baud=115200, filter_data=True,
    scaled_output=True, daisy=False):
    if not port:
      port = find_port()
      if not port:
        raise OSError('Cannot find OpenBCI port')

    print("Conencting to %s" %(port))
    self.ser = serial.Serial(port, baud)
    print("Serial established...")

    #Initialize 32-bit board, doesn't affect 8bit board
    self.ser.write('v');

    #wait for device to be ready
    time.sleep(1)
    self.print_incoming_text()

    self.streaming = False
    self.filtering_data = filter_data
    self.scaling_output = scaled_output
    self.channels = 8 # number of channels per sample *from the board*
    self.read_state = 0;
    self.daisy = daisy
    self.last_odd_sample = OpenBCISample(-1, [], []) # used for daisy

    #Disconnects from board when terminated
    atexit.register(self.disconnect)

  def start_streaming(self, callback, lapse=-1):
    """
    Start handling streaming data from the board. Call a provided callback
    for every single sample that is processed (every two samples with daisy module).

    Args:
      callback: A callback function -- or a list of functions -- that will receive a single argument of the
          OpenBCISample object captured.
    """
    if not self.streaming:
      self.ser.write('b')
      self.streaming = True

    start_time = timeit.default_timer()

    # Enclose callback funtion in a list if it comes alone
    if not isinstance(callback, list):
      callback = [callback]
    
    while self.streaming:
      # read current sample
      sample = self._read_serial_binary()
      # if a daisy module is attached, wait to concatenate two samples (main board + daisy) before passing it to callback
      if self.daisy:
        # odd sample: daisy sample, save for later
        if ~sample.id % 2:
          self.last_odd_sample = sample
        # even sample: concatenate and send if last sample was the fist part, otherwise drop the packet
        elif sample.id - 1 == self.last_odd_sample.id:
          # the aux data will be the average between the two samples, as the channel samples themselves have been averaged by the board
          avg_aux_data = list((np.array(sample.aux_data) + np.array(self.last_odd_sample.aux_data))/2)
          whole_sample = OpenBCISample(sample.id, sample.channel_data + self.last_odd_sample.channel_data, avg_aux_data)
          for call in callback:
            call(whole_sample)
      else:
        for call in callback:
          call(sample)
      if(lapse > 0 and timeit.default_timer() - start_time > lapse):
        self.stop();


  """

  Used by exit clean up function (atexit)

  """
  def warn(self, text):
    print("Warning: %s" % text)

  def stop(self):
    self.warn("Stopping streaming...\nWait for buffer to flush...")
    self.streaming = False
    self.ser.write('s')

  def disconnect(self):
    if(self.streaming == True):
      self.stop()
    if (self.ser.isOpen()):
      self.warn("Closing Serial...")
      self.ser.close()
  
  
  """
    PARSER:
    Parses incoming data packet into OpenBCISample.
    Incoming Packet Structure:
    Start Byte(1)|Sample ID(1)|Channel Data(24)|Aux Data(6)|End Byte(1)
    0xA0|0-255|8, 3-byte signed ints|3 2-byte signed ints|0xC0

  """
  def _read_serial_binary(self, max_bytes_to_skip=3000):
    def read(n):
      b = self.ser.read(n)
      # print bytes(b)
      return b

    for rep in xrange(max_bytes_to_skip):

      #Looking for start and save id when found
      if self.read_state == 0:
        b = read(1)
        if not b:
          if not self.ser.inWaiting():
              self.warn('Device appears to be stalled. Restarting...')
              self.ser.write('b\n')  # restart if it's stopped...
              time.sleep(.100)
              continue
        if bytes(struct.unpack('B', b)[0]) == START_BYTE:
          if(rep != 0):
            self.warn('Skipped %d bytes before start found' %(rep))
          packet_id = struct.unpack('B', read(1))[0] #packet id goes from 0-255

          self.read_state = 1

      elif self.read_state == 1:
        channel_data = []
        for c in xrange(self.channels):

          #3 byte ints
          literal_read = read(3)

          unpacked = struct.unpack('3B', literal_read)

          #3byte int in 2s compliment
          if (unpacked[0] >= 127):
            pre_fix = '\xFF'
          else:
            pre_fix = '\x00'


          literal_read = pre_fix + literal_read;

          #unpack little endian(>) signed integer(i) (makes unpacking platform independent)
          myInt = struct.unpack('>i', literal_read)[0]

          if self.scaling_output:
            channel_data.append(myInt*scale_fac_uVolts_per_count)
          else:
            channel_data.append(myInt)

        self.read_state = 2;


      elif self.read_state == 2:
        aux_data = []
        for a in xrange(3):

          #short = h
          acc = struct.unpack('h', read(2))[0]
          aux_data.append(acc)

        self.read_state = 3;

      elif self.read_state == 3:
        val = bytes(struct.unpack('B', read(1))[0])
        if (val == END_BYTE):
          sample = OpenBCISample(packet_id, channel_data, aux_data)
          self.read_state = 0 #read next packet
          return sample
        else:
          self.warn("Warning: Unexpected END_BYTE found <%s> instead of <%s>,\
            discarted packet with id <%d>"
            %(val, END_BYTE, packet_id))

  """

      SETTINGS AND HELPERS

  """

  def print_incoming_text(self):
    """

    When starting the connection, print all the debug data until
    we get to a line with the end sequence '$$$'.

    """
    line = ''
    #Wait for device to send data
    time.sleep(0.5)
    if self.ser.inWaiting():
      line = ''
      c = ''
     #Look for end sequence $$$
      while '$$$' not in line:
        c = self.ser.read()
        line += c
      print(line);

  def print_register_settings(self):
    self.ser.write('?')
    time.sleep(0.5)
    print_incoming_text();

  #DEBBUGING: Prints individual incoming bytes
  def print_bytes_in(self):
    if not self.streaming:
      self.ser.write('b')
      self.streaming = True
    while self.streaming:
      print(struct.unpack('B',self.ser.read())[0]);

  #Adds a filter at 60hz to cancel out ambient electrical noise
  def enable_filters(self):
    self.ser.write('f')
    self.filtering_data = True;

  def disable_filters(self):
    self.ser.write('g')
    self.filtering_data = False;

  def test_signal(self, signal):
    if signal == 0:
      self.ser.write('0')
      self.warn("Connecting all pins to ground")
    elif signal == 1:
      self.ser.write('p')
      self.warn("Connecting all pins to Vcc")
    elif signal == 2:
      self.ser.write('-')
      self.warn("Connecting pins to low frequency 1x amp signal")
    elif signal == 3:
      self.ser.write('=')
      self.warn("Connecting pins to high frequency 1x amp signal")
    elif signal == 4:
      self.ser.write('[')
      self.warn("Connecting pins to low frequency 2x amp signal")
    elif signal == 5:
      self.ser.write(']')
      self.warn("Connecting pins to high frequency 2x amp signal")
    else:
      self.warn("%s is not a known test signal. Valid signals go from 0-5" %(signal))

  def set_channel(self, channel, toggle_position):
    #Commands to set toggle to on position
    if toggle_position == 1:
      if channel is 1:
        self.ser.write('!')
      if channel is 2:
        self.ser.write('@')
      if channel is 3:
        self.ser.write('#')
      if channel is 4:
        self.ser.write('$')
      if channel is 5:
        self.ser.write('%')
      if channel is 6:
        self.ser.write('^')
      if channel is 7:
        self.ser.write('&')
      if channel is 8:
        self.ser.write('*')
      if channel is 9 and self.daisy:
        self.ser.write('Q')
      if channel is 10 and self.daisy:
        self.ser.write('W')
      if channel is 11 and self.daisy:
        self.ser.write('E')
      if channel is 12 and self.daisy:
        self.ser.write('R')
      if channel is 13 and self.daisy:
        self.ser.write('T')
      if channel is 14 and self.daisy:
        self.ser.write('Y')
      if channel is 15 and self.daisy:
        self.ser.write('U')
      if channel is 16 and self.daisy:
        self.ser.write('I')
    #Commands to set toggle to off position
    elif toggle_position == 0:
      if channel is 1:
        self.ser.write('1')
      if channel is 2:
        self.ser.write('2')
      if channel is 3:
        self.ser.write('3')
      if channel is 4:
        self.ser.write('4')
      if channel is 5:
        self.ser.write('5')
      if channel is 6:
        self.ser.write('6')
      if channel is 7:
        self.ser.write('7')
      if channel is 8:
        self.ser.write('8')
      if channel is 9 and self.daisy:
        self.ser.write('q')
      if channel is 10 and self.daisy:
        self.ser.write('w')
      if channel is 11 and self.daisy:
        self.ser.write('e')
      if channel is 12 and self.daisy:
        self.ser.write('r')
      if channel is 13 and self.daisy:
        self.ser.write('t')
      if channel is 14 and self.daisy:
        self.ser.write('y')
      if channel is 15 and self.daisy:
        self.ser.write('u')
      if channel is 16 and self.daisy:
        self.ser.write('i')

class OpenBCISample(object):
  """Object encapulsating a single sample from the OpenBCI board."""
  def __init__(self, packet_id, channel_data, aux_data):
    self.id = packet_id;
    self.channel_data = channel_data;
    self.aux_data = aux_data;



