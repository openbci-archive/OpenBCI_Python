class Constants:
    """The constants!"""

    ADS1299_GAIN_1 = 1.0
    ADS1299_GAIN_2 = 2.0
    ADS1299_GAIN_4 = 4.0
    ADS1299_GAIN_6 = 6.0
    ADS1299_GAIN_8 = 8.0
    ADS1299_GAIN_12 = 12.0
    ADS1299_GAIN_24 = 24.0

    ADS1299_VREF = 4.5  # reference voltage for ADC in ADS1299.  set by its hardware

    BOARD_CYTON = 'cyton'
    BOARD_DAISY = 'daisy'
    BOARD_GANGLION = 'ganglion'
    BOARD_NONE = 'none'

    CYTON_ACCEL_SCALE_FACTOR_GAIN = 0.002 / (pow(2, 4))  # assume set to +/4G, so 2 mG

    """ Errors """
    ERROR_INVALID_BYTE_LENGTH = 'Invalid Packet Byte Length'
    ERROR_INVALID_BYTE_START = 'Invalid Start Byte'
    ERROR_INVALID_BYTE_STOP = 'Invalid Stop Byte'
    ERROR_INVALID_DATA = 'Invalid data - try again'
    ERROR_INVALID_TYPW = 'Invalid type - check comments for input type'
    ERROR_MISSING_REGISTER_SETTING = 'Missing register setting'
    ERROR_MISSING_REQUIRED_PROPERTY = 'Missing property in JSON'
    ERROR_TIME_SYNC_IS_NULL = "'this.sync.curSyncObj' must not be null"
    ERROR_TIME_SYNC_NO_COMMA = 'Missed the time sync sent confirmation. Try sync again'
    ERROR_UNDEFINED_OR_NULL_INPUT = 'Undefined or Null Input'

    """ Possible number of channels """

    NUMBER_OF_CHANNELS_CYTON = 8
    NUMBER_OF_CHANNELS_DAISY = 16
    NUMBER_OF_CHANNELS_GANGLION = 4

    """ Protocols """
    PROTOCOL_BLE = 'ble'
    PROTOCOL_SERIAL = 'serial'
    PROTOCOL_WIFI = 'wifi'

    RAW_BYTE_START = 0xA0
    RAW_BYTE_STOP = 0xC0
    RAW_PACKET_ACCEL_NUMBER_AXIS = 3
    RAW_PACKET_SIZE = 33
    """
    OpenBCI Raw Packet Positions
    0:[startByte] | 1:[sampleNumber] | 2:[Channel-1.1] | 3:[Channel-1.2] | 4:[Channel-1.3] | 5:[Channel-2.1] | 6:[Channel-2.2] | 7:[Channel-2.3] | 8:[Channel-3.1] | 9:[Channel-3.2] | 10:[Channel-3.3] | 11:[Channel-4.1] | 12:[Channel-4.2] | 13:[Channel-4.3] | 14:[Channel-5.1] | 15:[Channel-5.2] | 16:[Channel-5.3] | 17:[Channel-6.1] | 18:[Channel-6.2] | 19:[Channel-6.3] | 20:[Channel-7.1] | 21:[Channel-7.2] | 22:[Channel-7.3] | 23:[Channel-8.1] | 24:[Channel-8.2] | 25:[Channel-8.3] | 26:[Aux-1.1] | 27:[Aux-1.2] | 28:[Aux-2.1] | 29:[Aux-2.2] | 30:[Aux-3.1] | 31:[Aux-3.2] | 32:StopByte
    """
    RAW_PACKET_POSITION_CHANNEL_DATA_START = 2
    RAW_PACKET_POSITION_CHANNEL_DATA_STOP = 25
    RAW_PACKET_POSITION_SAMPLE_NUMBER = 1
    RAW_PACKET_POSITION_START_BYTE = 0
    RAW_PACKET_POSITION_STOP_BYTE = 32
    RAW_PACKET_POSITION_START_AUX = 26
    RAW_PACKET_POSITION_STOP_AUX = 31
    RAW_PACKET_POSITION_TIME_SYNC_AUX_START = 26
    RAW_PACKET_POSITION_TIME_SYNC_AUX_STOP = 28
    RAW_PACKET_POSITION_TIME_SYNC_TIME_START = 28
    RAW_PACKET_POSITION_TIME_SYNC_TIME_STOP = 32

    """ Stream packet types """
    RAW_PACKET_TYPE_STANDARD_ACCEL = 0  # 0000
    RAW_PACKET_TYPE_STANDARD_RAW_AUX = 1  # 0001
    RAW_PACKET_TYPE_USER_DEFINED_TYPE = 2  # 0010
    RAW_PACKET_TYPE_ACCEL_TIME_SYNC_SET = 3  # 0011
    RAW_PACKET_TYPE_ACCEL_TIME_SYNCED = 4  # 0100
    RAW_PACKET_TYPE_RAW_AUX_TIME_SYNC_SET = 5  # 0101
    RAW_PACKET_TYPE_RAW_AUX_TIME_SYNCED = 6  # 0110
    RAW_PACKET_TYPE_IMPEDANCE = 7  # 0111

    """ Max sample number """
    SAMPLE_NUMBER_MAX_CYTON = 255
    SAMPLE_NUMBER_MAX_GANGLION = 200

    """ Possible Sample Rates """
    SAMPLE_RATE_1000 = 1000
    SAMPLE_RATE_125 = 125
    SAMPLE_RATE_12800 = 12800
    SAMPLE_RATE_1600 = 1600
    SAMPLE_RATE_16000 = 16000
    SAMPLE_RATE_200 = 200
    SAMPLE_RATE_2000 = 2000
    SAMPLE_RATE_250 = 250
    SAMPLE_RATE_25600 = 25600
    SAMPLE_RATE_3200 = 3200
    SAMPLE_RATE_400 = 400
    SAMPLE_RATE_4000 = 4000
    SAMPLE_RATE_500 = 500
    SAMPLE_RATE_6400 = 6400
    SAMPLE_RATE_800 = 800
    SAMPLE_RATE_8000 = 8000
