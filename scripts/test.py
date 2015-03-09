import sys; sys.path.append('..') # help python find open_bci_v3.py relative to scripts folder
import open_bci_v3 as bci
import os

def printData(sample):
	#os.system('clear')
	print "----------------"
	print("%f" %(sample.id))
	print sample.channel_data
	print sample.aux_data
	print "----------------"



if __name__ == '__main__':
	port = '/dev/ttyUSB0'
	baud = 115200
	board = bci.OpenBCIBoard(port=port)
	board.start_streaming(printData)
