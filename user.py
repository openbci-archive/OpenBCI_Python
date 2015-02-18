#!/usr/bin/env python2.7
import argparse # new in Python2.7
import open_bci_v3 as bci
import os
import time
import csv_collect
import string
import tcp_server
import streamer

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
	parser.add_argument('--no-filtering', dest='filtering', action='store_false',
				help="Disable notch filtering")
	parser.set_defaults(filtering=True)
	parser.add_argument('-d', '--daisy', dest='daisy', action='store_true',
				help="Force daisy mode (beta feature)")
	parser.set_defaults(daisy=False)
	# callback selection. FIXME: first flag tested wins
	parser.add_argument('-c', '--cvs', action="store_true",
				help="write cvs data")
	parser.add_argument('-s', '--stream', action="store_true",
				help="stream data to TCP")
	# options for streaming server
	parser.add_argument('-si', '--stream-ip', default="localhost",
			help="IP address for TCP streaming server " +
			"(default: localhost)")
	parser.add_argument('-sp', '--stream-port', default=12345, type=int,
			help="Port for TCP streaming server " +
			"(default: 12345)")
	
	args = parser.parse_args()
	
	print "Notch filtering:", args.filtering
	
	#  Configure number of output channels
	nb_channels=8
	if args.daisy:
	  nb_channels=16
	  print "Force daisy mode:", nb_channels, "channels."
	else:
	  print "No daisy:", nb_channels, "channels."
	  
	if args.cvs:
		print "selecting CSV export"
		fun = csv_collect.csv_collect()
	elif args.stream:
		print "Selecting streaming. IP: ", args.stream_ip, ", port: ", args.stream_port
		# init server
		server = tcp_server.TCPServer(ip=args.stream_ip, port=args.stream_port, nb_channels=nb_channels)
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
	
	board = bci.OpenBCIBoard(port=args.port, daisy=args.daisy, filter_data=args.filtering)

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
