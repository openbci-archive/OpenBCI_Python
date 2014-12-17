OpenBCI_Python
==============

The Python software library designed to work with OpenBCI hardware.

Please direct any questions, suggestions and bug reports to the github repo at: https://github.com/OpenBCI/OpenBCI_Python

Dependancies: ------------------------------------------------------------

Python 2.7 or later (https://www.python.org/download/releases/2.7/)	
Numpy 1.7 or later (http://www.numpy.org/)

OpenBCI 8 and 32 bit board with 8 channels.

This library includes the main open_bci_v3 class definition that instantiates an OpenBCI Board object. This object will initialize communication with the board and get the environment ready for data streaming. This library is designed to work with iOS and Linux distributions. To use a Windows OS, change the __init__ function in open_bci_v3.py to establish a serial connection in Windows. 

For additional details on connecting your board visit: http://docs.openbci.com/tutorials/01-GettingStarted


Functionality: ------------------------------------------------------------

The startStreaming function of the Board object takes a callback function and begins streaming data from the board. Each packet it receives is then parsed as an OpenBCISample which is passed to the callback function as an argument. 

OpenBCISample members:
-id:
	int from 0-255. Used to tell if packets were skipped.

-channel_data:
	8 int array with current voltage value of each channel (1-8)

-aux_data:
	3 int array with current auxiliary data. (0s by default)


What is this? --------------------------------------------------------------

As a getting started point, this code provides a simple user interface (called user.py). To use it, connect the board to your computer using the dongle (see http://docs.openbci.com/tutorials/01-GettingStarted for details). 

Then simply run the code with no arguments. 
The program should establish a serial connection and reset the board to default settings. When a '-->' appears, you can type a character (character map http://docs.openbci.com/software/01-OpenBCI_SDK)  that will be sent to the board using ser.write. This allows you to change the settings on the board. A good first test is to type:

--> ?

This should output the current configuration settings on the board.

Another test would be to change the board settings so that all the pins in the board are internally connected to a test (square) wave. To do this, type:

--> [

To view the current readings of your board type:

--> /start

The user interface will also accept a function “fun.” When the interface receives the “start” command, it will pass fun as a callback function to the openBCI board object. Every time the board gets a sample, function fun will be called and given that sample as an argument. The openBCISample object structure can be seen in open_bci_v3.py, keep this in mind when writing your own functions.

By default, this code runs the printData function defined in user.py, but also includes the csv_collect function that can be set to run by toggling lines 19 and 20:

fun = csv_collect.csv_collect();
#fun = printData;

Both these functions are good examples of how to write callback functions for OpenBCI.


