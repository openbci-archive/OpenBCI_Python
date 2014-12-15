import open_bci_v3 as bci
import os
import time
import csv_collect

def printData(sample):
	#os.system('clear')
	print "----------------"
	print("%f" %(sample.id))
	print sample.channels
	print sample.aux_data
	print "----------------"



if __name__ == '__main__':
	port = '/dev/ttyUSB0'
	baud = 115200
	board = bci.OpenBCIBoard(port=port)

	#fun = printData;
	fun = csv_collect.csv_collect();

	print "User serial interface enabled..." 
	print "View command map at http://docs.openbci.com."
	print "Type start to run. Type exit to exit."

	#Start by restoring default settings
	s = 'd'

	while(s != "exit"):
		#Send char and wait for registers to set
		if s:
			board.ser.write(s[0])
		time.sleep(0.5)

		line = ''
		while board.ser.inWaiting():
			c = board.ser.read()
			line += c
			time.sleep(0.001)		
		print(line);

		#Take user input
		s = raw_input('--> ');
		if(s == "help"): print "View command map at http://docs.openbci.com.\n"
		elif(s == "start"): board.start(fun);