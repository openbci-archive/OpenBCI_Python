import open_bci_v3 as bci
import os

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
	board.start(printData)
