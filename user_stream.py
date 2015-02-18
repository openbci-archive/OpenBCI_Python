#!/usr/bin/env python2.7
import argparse # new in Python2.7
import open_bci_v3 as bci
import os
import time
import csv_collect
import string
import tcp_server
import streamer

# Transmit data to openvibe acquisition server (no interpolation)

# Listen to new connections every second

# FIXME: let user configure
SERVER_PORT=12345
SERVER_IP="localhost"
NB_CHANNELS=8

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
	# FIXME: first flag use wins
	parser.add_argument('-c', '--cvs', action="store_true",
				help="write cvs data")
	parser.add_argument('-s', '--stream', action="store_true",
				help="stream data to TCP")
		
	args = parser.parse_args()

	if args.cvs:
		print "selecting CSV export"
		fun = csv_collect.csv_collect()
	elif args.stream:
		print "selecting streaming"
		# init server
		server = tcp_server.TCPServer(ip=SERVER_IP, port=SERVER_PORT, nb_channels=NB_CHANNELS)
		monit = streamer.Streamer(server)
		# daemonize theard to terminate it altogether with the main when time will come
		monit.daemon = True
		fun = monit.send
		# launch monitor
		monit.start()
	else:
		print "Selecting printData"
		fun = printData
  
	print "User serial interface enabled..."
	print "Connecting to ", args.port

	board = bci.OpenBCIBoard(port=args.port, filter_data=False)

	print "View command map at http://docs.openbci.com."
	print "Type start to run. Type exit to exit."

	#Start by restoring default settings
	s = 'd'

	while(s != "exit"):
		#Send char and wait for registers to set
		if (not s): pass

		elif("help" in s): print "View command map at: \
			http://docs.openbci.com/software/01-OpenBCI_SDK.\n\
			For user interface, read README or view \
			https://github.com/OpenBCI/OpenBCI_Python"

		elif('/' == s[0]):
			s = s[1:]

			if("T:" in s):
				lapse = int(s[string.find(s,"T:")+2:])
			else:
				lapse = -1

			if("start" in s): 
				board.startStreaming(fun, lapse)

			elif(s == 'csv'):
				print("/start will run csv_collect")
				fun = csv_collect.csv_collect()

			elif('test' in s):
				test = int(s[string.find(s,"test")+4:])
				board.test_signal(test)

		
		elif s:
			for c in s:
				board.ser.write(c)
				time.sleep(0.100)

		line = ''
		time.sleep(0.1) #Wait to see if the board has anything to report
		while board.ser.inWaiting():
			c = board.ser.read()
			line += c
			time.sleep(0.001)	
			if (c == '\n'):
				print(line[:-1])
				line = ''
		print(line)

		#Take user input
		s = raw_input('--> ');

	board.disconnect()
