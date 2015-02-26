OpenBCI_Python
==============

The Python software library designed to work with OpenBCI hardware.

Please direct any questions, suggestions and bug reports to the github repo at: https://github.com/OpenBCI/OpenBCI_Python

## Dependancies:

* Python 2.7 or later (https://www.python.org/download/releases/2.7/)
* Numpy 1.7 or later (http://www.numpy.org/)
* Yapsy -- if using pluging via `user.py` (http://yapsy.sourceforge.net/)

OpenBCI 8 and 32 bit board with 8 or 16 channels.

This library includes the main open_bci_v3 class definition that instantiates an OpenBCI Board object. This object will initialize communication with the board and get the environment ready for data streaming. This library is designed to work with iOS and Linux distributions. To use a Windows OS, change the __init__ function in open_bci_v3.py to establish a serial connection in Windows.

For additional details on connecting your board visit: http://docs.openbci.com/tutorials/01-GettingStarted

## Audience:

This python code is meant to be used by people familiar with python and programming in general. It's purpose is to allow for programmers to interface with OpenBCI technology directly, both to acquire data and to write programs that can use that data on a live setting, using python.

If this is not what you are looking for, you can visit http://openbci.com/downloads and browse other OpenBCI software that will fit your needs.

## Functionality

### Basic usage

The startStreaming function of the Board object takes a callback function and begins streaming data from the board. Each packet it receives is then parsed as an OpenBCISample which is passed to the callback function as an argument. 

OpenBCISample members:
-id:
	int from 0-255. Used to tell if packets were skipped.

-channel_data:
	8 int array with current voltage value of each channel (1-8)

-aux_data:
	3 int array with current auxiliary data. (0s by default)

### user.py

This code provides a simple user interface (called user.py) to handle various plugins and communicate with the board. To use it, connect the board to your computer using the dongle (see http://docs.openbci.com/tutorials/01-GettingStarted for details). 

Then simply run the code given as an argument the port your board is connected to:
Ex Linux:
> $python user.py -p /dev/ttyUSB0 

The program should establish a serial connection and reset the board to default settings. When a '-->' appears, you can type a character (character map http://docs.openbci.com/software/01-OpenBCI_SDK)  that will be sent to the board using ser.write. This allows you to change the settings on the board. 

A good first test is to try is to type '?':
>--> ?

This should output the current configuration settings on the board.

Another test would be to change the board settings so that all the pins in the board are internally connected to a test (square) wave. To do this, type:

>--> [

Alternatively, there are 6 test signals pre configured:

> --> /test1 (connect all pins to ground)

> --> /test2 (connect all pins to vcc)

> --> /test3 (Connecting pins to low frequency 1x amp signal)

> --> /test4 (Connecting pins to high frequency 1x amp signal)

> --> /test5 (Connecting pins to low frequency 2x amp signal)

> --> /test6 (Connecting pins to high frequency 2x amp signal)

The / is used in the interface to execute a pre-configured command. Writing anything without a preceding '/' will automatically write those characters, one by one, to the board.

For example, writing 
> -->x3020000X 
will do the following:

‘x’ enters Channel Settings mode. Channel 3 is set up to be powered up, with gain of 2, normal input, removed from BIAS generation, removed from SRB2, removed from SRB1. The final ‘X’ latches the settings to the ADS1299 channel settings register.

Pre-configured commands that use the / prefix are:

test (As explained above) 

> --> /test4

start selected plugins (see below)

> --> /start

Adding the argument "T:number" will set a timeout on the start command.

>-->/start T:5

#### Useful commands:

Writting to SD card a high frequency square wave (test5) for 3 seconds:
```
$ python user.py -p /dev/ttyUSB0
User serial interface enabled...
Connecting to  /dev/ttyUSB0
Serial established...
View command map at http://docs.openbci.com.
Type start to run. Type exit to exit.

--> 
OpenBCI V3 8bit Board
Setting ADS1299 Channel Values
ADS1299 Device ID: 0x3E
LIS3DH Device ID: 0x33
Free RAM: 447
$$$
--> /test5
Warning: Connecting pins to high frequency 2x amp signal

--> a
Corresponding SD file OBCI_18.TXT$$$
--> /start T:3

```

NOTES:

When writing to the board and expecting a response, give the board a second. It sometimes lags and requires
the user to hit enter on the user.py script until you get a response.

### Plugins

#### Use plugins

Select the print plugin:

> $python user.py -p /dev/ttyUSB0 --add print

Plugin with optional parameter:

> $python user.py -p /dev/ttyUSB0 --add csv_collect record.csv

Select several plugins, e.g. streaming to OSC and displaying effective sample rate:

> $python user.py -p /dev/ttyUSB0 --add streamer_osc --add sample_rate

Note: type `/start` to launch the selected plugins.

#### Create new plugins

Add new functionalities to user.py by creating new scripts inside the `plugins` folder. You class must inherit from yapsy.IPlugin, see below a minimal example with `print` plugin:

```python
	from yapsy.IPlugin import IPlugin

	class PluginPrint(IPlugin):
		# args: passed by command line
		def activate(self, args):
			print "I'm activated"
			# tell outside world that init went good
			return True
	    
		def deactivate(self):
			print "Goodbye"
		
		def show_help(self):
			print "I do not need any parameter, just printing stuff."
		
		# called with each new sample
		def __call__(self, sample):
			print "----------------"
			print("%f" %(sample.id))
			print sample.channel_data
			print sample.aux_data
```

Describe your plugin with a corresponding `print.yapsy-plugin`:

```
	[Core]
	Name = print
	Module = print

	[Documentation]
	Author = Various
	Version = 0.1
	Description = Print board values on stdout
```


You're done, your plugin should be automatically detected by `user.py`.

#### Existing plugins

##### csv_collect

Export data to a csv file.

##### print

Display sample values -- *verbose* output!

##### sample_rate

Print effective sampling rate averaged over XX seconds (default: 10).

##### streamer_tcp

Acts as a TCP server, using a "raw" protocol to send value. The stream can be acquired with [OpenViBE](http://openvibe.inria.fr/) acquisition server, selecting telnet, big endian, float 32 bits, forcing 250 sampling rate (125 if daisy mode is used).

Default IP: localhost, default port: 12345

##### streamer_osc

Data is sent through OSC (UDP layer).

Default IP: localhost, default port: 12345, default stream name: `/openbci`

Note: requires pyosc. On linux type either `pip install --pre pyosc` as root, or `pip install --pre --user`.

Type `python user.py --list` to list available plugins and `python user.py --help [plugin_name]` to get more information.


### Scripts

In the `scripts` folder you will find code snippets that use directly the `OpenBCIBoard` class from `open_bci_v3.py`.

Note: copy `open_bci_v3.py` there if you want to run the code -- no proper package yet.

* `test.py`: minimal example, printing values.
* `upd_server.py` and client: see https://github.com/OpenBCI/OpenBCI_Node for implementation example.
* `stream_data.py` a version of a TCP streaming server that somehow oversamples OpenBCI from 250 to 256Hz.
