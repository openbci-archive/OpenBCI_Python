#!/usr/bin/env python2.7
import argparse # new in Python2.7
import open_bci_v3 as bci
import os
import time
import csv_collect
import string

def printData(sample):
	#os.system('clear')
	print "----------------"
	print("%f" %(sample.id))
	print sample.channel_data
	print sample.aux_data


if __name__ == '__main__':
	parser = argparse.ArgumentParser(description="OpenBCI 'user'")
	parser.add_argument('-p', '--port', required=True,
				help="Port to connect to OpenBCI Dongle " +
				"( ex /dev/ttyUSB0 or /dev/tty.usbserial-* )")
	# baud rate is not currently used
	parser.add_argument('-b', '--baud', default=115200, type=int,
				help="Baud rate (not currently used)")
	parser.add_argument('-c', '--cvs', action="store_true",
				help="write cvs data")
	args = parser.parse_args()

	if args.cvs:
		fun = csv_collect.csv_collect();
	else:
		fun = printData;

	print "User serial interface enabled..."
	print "Connecting to ", args.port

	board = bci.OpenBCIBoard(port=args.port)

	print "View command map at http://docs.openbci.com."
	print "Type start to run. Type exit to exit."

	#Start by restoring default settings
	s = 'd'

	while(s != "exit"):
		#Send char and wait for registers to set
		if("help" in s): print "View command map at: http://docs.openbci.com/software/01-OpenBCI_SDK.\nFor user interface, read README or view https://github.com/OpenBCI/OpenBCI_Python"
		elif(s == "/start"): board.startStreaming(fun);

		elif('test' in s):
			test = int(s[string.find(s,"test")+4:])
			board.test_signal(test);
		
		elif s:
			for c in s:
				board.ser.write(c)
				time.sleep(0.035)

		line = ''
		while board.ser.inWaiting():
			c = board.ser.read()
			line += c
			time.sleep(0.001)		
		print(line);

		#Take user input
		s = raw_input('--> ');
