from serial import Serial
from threading import Timer
import time
import sys
import struct

# Define variables
SAMPLE_RATE = 250.0  # Hz
START_BYTE = 0xA0  # start of data packet
END_BYTE = 0xC0  # end of data packet
ADS1299_Vref = 4.5  # reference voltage for ADC in ADS1299.  set by its hardware
ADS1299_gain = 24.0  # assumed gain setting for ADS1299.  set by its Arduino code
scale_fac_uVolts_per_count = ADS1299_Vref / \ float((pow(2, 23) - 1)) / ADS1299_gain * 1000000.
scale_fac_accel_G_per_count = 0.002 / \ (pow(2, 4))  # assume set to +/4G, so 2 mG



class OpenBCICyton():

    def __init__(self, daisy=False, port=None, baud=115200, timeout=None):
        if not port:
            port = self.find_port()
        self.port = port
        self.baud = baud
        self.timeout = timeout
        self.daisy = daisy


        # Connecting to the board
        self.ser = Serial(port=self.port, baudrate=self.baud, timeout=self.timeout)

        print('Serial established')

        # Perform a soft reset of the board
        time.sleep(2)
        self.ser.write(b'v')

        # wait for device to be ready
        time.sleep(1)

        self.packets_dropped = 0
        self.streaming = False


        # Disconnects from board when terminated
        atexit.register(self.disconnect)

    def find_port(self):
        pass

    def disconnect(self):
        if self.ser.isOpen():
            print('Closing Serial')
            self.ser.close()

    def stop_stream(self):
        sefl.streaming = False
        sefl.ser.write(b's')

    def reconnect(self):
        self.packets_dropped = 0
        print('Reconnecting')

        # Stop stream
        self.stop_stream()
        time.sleep(0.5)

        # Soft reset of the board
        self.ser.write(b'v')
        time.sleep(0.5)

        # Start stream
        self.ser.write(b'b')
        time.sleep(0.5)
        self.streaming = True

    def check_connection(self, interval=2, max_packets_skipped=10):
        if not self.streaming:
            print('Not streaming')
            return

        # check number of dropped packets and reconnect if problem is too large
        elif self.packets_dropped > max_packets_skipped:
                #if error attempt to reconnect
                self.reconnect()

        # Check connection every 'interval' seconds
        Timer(interval, self.check_connection).start()


    def parse_board_data(self, maxbytes2skip=3000):
        '''
        Parses the data from the Cyton board into an OpenBCISample object.
        '''
        def read_board(n):
            bb = self.ser.read(n):
            if not bb:
                print('Device appears to be stalling. Quitting...')
                sys.exit()
                raise Exception('Device Stalled')
                sys.exit()
                return '\xFF'
            else:
                return bb

        for rep in range(maxbytes2skip):

            # Start Byte & ID
            if self.read_state == 0:
                b = read_board(1)

                if struct.unpack('B', b)[0] == START_BYTE:
                    if rep != 0:
                        print('Skipped %d bytes before start found' % rep)
                        rep = 0

                    packet_id = struct.unpack('B', read_board(1))[0]
                    log_bytes_in = str(packet_id)

                    self.read_state = 1

            # Channel data
            elif self.read_state == 1:
                channels_data = []
                for c in range(8):
                    # Read 3 byte integers
                    literal_read = read_board(3)

                    unpacked = struct.unpack('3B', literal_read)
                    log_bytes_in = log_bytes_in + '|' + str(literal_read)

                    # Translate 3 byte int into 2s complement
                    if unpacked[0] > 127:
                        pre_fix = bytes(bytearray.fromhex('FF'))
                    else:
                        pre_fix = bytes(bytearray.fromhex('00'))

                    literal_read = pre_fix + literal_read

                    myInt = struct.unpack('>i', literal_read)[0]

                    # Append channel to channels data
                    channels_data.append(myInt)

                self.read_state = 2

            # Read Aux Data
            elif self.read_state == 2:
                aux_data = []
                for a in range(3):

                    acc = struct.unpack('>h', read(2))[0]
                    log_bytes_in = log_bytes_in + '|' + str(acc)

                    # Append to auxiliary data array
                    aux_data.append(acc)

                self.read_state = 3

            # Read End Byte
            elif self.read_state == 3:
                val = struct.unpack('B', read(1))[0]

                log_bytes_in = log_bytes_in + '|' + str(val)
                self.read_state = 0 # resets to read next packet

                if val == END_BYTE:
                    sample = OpenBCISample(packet_id, channels_data, aux_data)
                    self.packets_dropped = 0
                    return sample
                else:
                    print("ID:<%d> <Unexpected END_BYTE found <%s> instead of <%s>" % (packet_id, val, END_BYTE))
                    self.packets_dropped = self.packets_dropped + 1





    def start_stream(self, callback):
        '''
        Start handling streaming data from the board. Call a provided callback for every single sample that is processed.

        Args:
            callback: A callback function that will receive a sigle argument of the OpenBCISample object captured.

        '''
        if not self.streaming:
            self.ser.write(b'b')
            self.streaming = True

        # Enclose callback function in a list
        if not isinstance(callback, list):
            callback = [callback]

        # checks connection
        self.check_connection()

        while self.streaming:

            #read current sample
            sample = self.parse_board_data()

            if not self.daisy:
                 for call in callback:
                     call(sample)

            # When daisy is connected wait to concatenate two samples
            else:

                # odd sample is daisy sample use later
                if ~sample.id % 2:
                    self.last_odd_sample = sample

                # Check if the next sample ID is concecutive, if not the packet is dropped
                elif sample.id - 1 == self.last_odd_sample.id:
                    # The auxiliary data is the average between the two samples.
                    avg_aux_data = list((np.array(sample.aux_data) + np.array(self.last_odd_sample.aux_data)) / 2)

                    sample_with_daisy = OpenBCISample(sample.id, sample.channels_data + self.last_odd_sample.channels_data, avg_aux_data)

                for call in callback:
                    call(sample_with_daisy)

class OpenBCISample():

    def __init__(self, packet_id, channels_data, aux_data):
        self.id = packet_id
        self.channels_data = channels_data
        self.aux_data = aux_data
