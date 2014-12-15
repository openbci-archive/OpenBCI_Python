OpenBCI_Python
==============

The Python software library designed to work with OpenBCI hardware.

Dependancies: ------------------------------------------------------------

Python 2.7 or later (https://www.python.org/download/releases/2.7/)	
Numpy 1.7 or later (http://www.numpy.org/)

OpenBCI 8 and 32 bit board with 8 channels.

This library includes the main open_bci_v3 class definition that instantiates an OpenBCI Board object. This object will initialize communiction with the board and get the enviornment ready for data streaming. This library is designed to work with iOS and Linux distrubitions. To use a Windows OS, change the __init__ function in open_bci_v3.py to establish a serial connection in Windows. 

For additional details on connecting your board visit: http://docs.openbci.com/tutorials/01-GettingStarted


Functionality: ------------------------------------------------------------

The start function of the Board object takes a callback function and begins streaming data from the board. Each packet it receives is then parsed as an OpenBCISample which is passed to the callback function as an argument. 

OpenBCISample members:
-id:
	int from 0-255. Used to tell if packets were skipped.

-channel_data:
	8 int array with current voltage value of each channel (1-8)

-aux_data:
	3 int array with current auxiliary data. (0s by default)
