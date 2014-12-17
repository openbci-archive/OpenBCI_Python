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
	port = '/dev/ttyUSB0'
	baud = 115200
	board = bci.OpenBCIBoard(port=port)

	#fun = csv_collect.csv_collect();
	fun = printData;

	print "User serial interface enabled..." 
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
		