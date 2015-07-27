import serial
import struct
import numpy as np
import time
import timeit
import atexit
import logging
import threading
import sys
import pdb

port = '/dev/tty.OpenBCI-DN008VTF'
#port = '/dev/tty.OpenBCI-DN0096XA'
baud = 115200
ser = serial.Serial(port= port, baudrate = baud, timeout = None)
pdb.set_trace()