**THIS REPOSITORY IS NOW DEPRECATED AND NO LONGER IN ACTIVE DEVELOPMENT. PLEASE REFER TO ["FOR DEVELOPERS" IN THE DOCS](11ForDevelopers/01-SoftwareDevelopment.md) SECTION FOR INFORMATION ON [BRAINFLOW-PYTHON](https://brainflow.readthedocs.io/en/stable/BuildBrainFlow.html#python).**



# OpenBCI Python

<p align="center">
  <img alt="banner" src="/images/openbci_large.png/" width="400">
</p>
<p align="center" href="">
  Provide a stable Python driver for all OpenBCI Biosensors
</p>

[![Build Status](https://travis-ci.org/OpenBCI/OpenBCI_Python.svg?branch=master)](https://travis-ci.org/OpenBCI/OpenBCI_Python)

## Welcome!

First and foremost, Welcome! :tada: Willkommen! :confetti_ball: Bienvenue! :balloon::balloon::balloon:

Thank you for visiting the OpenBCI Python repository. This python code is meant to be used by people familiar with python and programming in general. It's purpose is to allow for programmers to interface with OpenBCI technology directly, both to acquire data and to write programs that can use that data on a live setting, using python.

This document (the README file) is a hub to give you some information about the project. Jump straight to one of the sections below, or just scroll down to find out more.

* [What are we doing? (And why?)](#what-are-we-doing)
* [Who are we?](#who-are-we)
* [What do we need?](#what-do-we-need)
* [How can you get involved?](#get-involved)
* [Get in touch](#contact-us)
* [Find out more](#find-out-more)
* [Glossary](#glossary)
* [Dependencies](#dependencies)
* [Install](#install)
* [Functionality](#functionality)

## What are we doing?

### The problem

* OpenBCI is an incredible biosensor that can be challenging to work with
* Data comes into the computer very quickly
* Complex byte streams
* Lot's of things can go wrong when dealing with a raw serial byte stream
* The boards all use different physical technologies to move data to computers such as bluetooth or wifi
* Developers want to integrate OpenBCI with other platforms and interfaces

So, if even the very best developers want to use Python with their OpenBCI boards, they are left scratching their heads with where to begin.

### The solution

The OpenBCI Python  will:

* Allow Python users to install one module and use any board they choose
* Provide examples of using Python to port data to other apps like lab streaming layer
* Perform the heavy lifting when extracting and transforming raw binary byte streams
* Use unit tests to ensure perfect quality of core code

Using this repo provides a building block for developing with Python. The goal for the Python library is to ***provide a stable Python driver for all OpenBCI Biosensors***

## Who are we?

The founder of the OpenBCI Python repository is Jermey Frey. The Python driver is one of the most popular repositories and has the most contributors!

The contributors to these repos are people using Python mainly for their data acquisition and analytics.

## What do we need?

**You**! In whatever way you can help.

We need expertise in programming, user experience, software sustainability, documentation and technical writing and project management.

We'd love your feedback along the way.

Our primary goal is to provide a stable Python driver for all OpenBCI Biosensors, and we're excited to support the professional development of any and all of our contributors. If you're looking to learn to code, try out working collaboratively, or translate you skills to the digital domain, we're here to help.

## Get involved

If you think you can help in any of the areas listed above (and we bet you can) or in any of the many areas that we haven't yet thought of (and here we're *sure* you can) then please check out our [contributors' guidelines](CONTRIBUTING.md) and our [roadmap](ROADMAP.md).

Please note that it's very important to us that we maintain a positive and supportive environment for everyone who wants to participate. When you join us we ask that you follow our [code of conduct](CODE_OF_CONDUCT.md) in all interactions both on and offline.

## Contact us

If you want to report a problem or suggest an enhancement we'd love for you to [open an issue](../../issues) at this github repository because then we can get right on it.

## Find out more

You might be interested in:

* Purchase a [Cyton][link_shop_cyton] | [Ganglion][link_shop_ganglion] | [WiFi Shield][link_shop_wifi_shield] from [OpenBCI][link_openbci]
* contact us at *contact@openbci.com*

And of course, you'll want to know our:

* [Contributors' guidelines](CONTRIBUTING.md)
* [Roadmap](ROADMAP.md)

## Glossary

OpenBCI boards are commonly referred to as _biosensors_. A biosensor converts biological data into digital data. 

The [Ganglion][link_shop_ganglion] has 4 channels, meaning the Ganglion can take four simultaneous voltage readings.
 
The [Cyton][link_shop_cyton] has 8 channels and [Cyton with Daisy][link_shop_cyton_daisy] has 16 channels. 

Generally speaking, the Cyton records at a high quality with less noise. Noise is anything that is not signal.

## Thank you

Thank you so much (Danke schön! Merci beaucoup!) for visiting the project and we do hope that you'll join us on this amazing journey to make programming with OpenBCI fun and easy.

## Dependencies

* Python 2.7 or later (https://www.python.org/download/releases/2.7/)
* Numpy 1.7 or later (http://www.numpy.org/)
* Yapsy -- if using pluging via `user.py` (http://yapsy.sourceforge.net/)

NOTE: For comprehensive list see requirments.txt: (https://github.com/OpenBCI/OpenBCI_Python/blob/master/requirements.txt)

OpenBCI 8 and 32 bit board with 8 or 16 channels.

This library includes the OpenBCICyton and OpenBCIGanglion classes which are drivers for their respective devices. The OpenBCICyton class is designed to work on all systems, while the OpenBCIGanglion class relies on a Bluetooth driver that is only available on Linux, discussed in the next section.

For additional details on connecting your Cyton board visit: http://docs.openbci.com/Hardware/02-Cyton

### Ganglion Board

The Ganglion board relies on Bluetooth Low Energy connectivity (BLE), and our code relies on the BluePy library to communicate with it. The BluePy library currently only works on Linux-based operating systems. To use Ganglion you will need to install it:

`pip install bluepy`

You may be able to use the Ganglion board from a virtual machine (VM) running Linux on other operating systems, such as MacOS or Windows. See [this thread](https://github.com/OpenBCI/OpenBCI_Python/issues/68) for advice.

You may need to alter the settings of your Bluetooth adapter in order to reduce latency and avoid packet drops -- e.g. if the terminal spams "Warning: Dropped 1 packets" several times a seconds, DO THAT.

On Linux, assuming `hci0` is the name of your bluetooth adapter:

`sudo bash -c 'echo 9 > /sys/kernel/debug/bluetooth/hci0/conn_min_interval'`

`sudo bash -c 'echo 10 > /sys/kernel/debug/bluetooth/hci0/conn_max_interval'`

## Install

### Using PyPI

```
pip install openbci-python
```

Anaconda is not currently supported, if you want to use anaconda, you need to create a virtual environment in anaconda, activate it and use the above command to install it.

### From sources

For the latest version, you can install the package from the sources using the setup.py script

```
python setup.py install
```

or in developer mode to be able to modify the sources.

```
python setup.py develop
```

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

> --> /start T:5

Stop the steam to issue new commands

> --> /stop

#### Useful commands:

Writting to SD card a high frequency square wave (test5) for 3 seconds:
```
$ python user.py -p /dev/ttyUSB0
User serial interface enabled...
Connecting to  /dev/ttyUSB0
Serial established...
View command map at http://docs.openbci.com.
Type start to run. Type /exit to exit.

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

#### Ganglion

The Ganglion board is currently supported only on Linux. The communication is made directly through bluetooth (BLE), instead of using a dongle through a serial port. To launch the script, auto-detect the bluetooth MAC address of the nearby board and print values upon `/start`:

> $sudo python user.py --board ganglion --add print

Note that if you want to configure manually the board, the API differs from the Cyton, refer to the proper documentation, i.e. http://docs.openbci.com/OpenBCI%20Software/06-OpenBCI_Ganglion_SDK

### Plugins

#### Use plugins

Select the print plugin:

> $python user.py -p /dev/ttyUSB0 --add print

Plugin with optional parameter:

> $python user.py -p /dev/ttyUSB0 --add csv_collect record.csv

Select several plugins, e.g. streaming to OSC and displaying effective sample rate:

> $python user.py -p /dev/ttyUSB0 --add streamer_osc --add sample_rate

Change the plugin path:

> $python user.py -p /dev/ttyUSB0 --add print --plugins-path /home/user/my_plugins

Note: type `/start` to launch the selected plugins.

#### Create new plugins

Add new functionalities to user.py by creating new scripts inside the `plugins` folder. You class must inherit from yapsy.IPlugin, see below a minimal example with `print` plugin:

```python
import plugin_interface as plugintypes

class PluginPrint(plugintypes.IPluginExtended):
    def activate(self):
        print("Print activated")

    def deactivate(self):
        print("Goodbye")

    def show_help(self):
        print("I do not need any parameter, just printing stuff.")

    # called with each new sample
    def __call__(self, sample):
        print("----------------")
        print("%f" % sample.id)
        print(sample.channel_data)
        print(sample.aux_data)
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

* `print`: Display sample values -- *verbose* output!

* `csv_collect`: Export data to a csv file.

* `sample_rate`: Print effective sampling rate averaged over XX seconds (default: 10).

* `streamer_tcp`: Acts as a TCP server, using a "raw" protocol to send value.
	* The stream can be acquired with [OpenViBE](http://openvibe.inria.fr/) acquisition server, selecting telnet, big endian, float 32 bits, forcing 250 sampling rate (125 if daisy mode is used).
	* Default IP: localhost, default port: 12345

* `streamer_osc`: Data is sent through OSC (UDP layer).
	* Default IP: localhost, default port: 12345, default stream name: `/openbci`
	* Requires pyosc. On linux type either `pip install --pre pyosc` as root, or `pip install --pre --user`.

* `udp_server`: Very simple UDP server that sends data as json. Made to work with: https://github.com/OpenBCI/OpenBCI_Node
	* Default IP: 127.0.0.1, default port: 8888

* `streamer_lsl`: Data is sent through [LSL](https://github.com/sccn/labstreaminglayer/).
	* Default EEG stream name "OpenBCI_EEG", ID "openbci_eeg_id1"; default AUX stream name "OpenBCI_AUX", ID "openbci_aux_id1".
	* Requires LSL library. Download last version from offcial site, e.g., ftp://sccn.ucsd.edu/pub/software/LSL/SDK/liblsl-Python-1.10.2.zip and unzip files in a "lib" folder at the same level as `user.py`.

Tip: Type `python user.py --list` to list available plugins and `python user.py --help [plugin_name]` to get more information.

### Scripts

In the `scripts` folder you will find code snippets that use directly the `OpenBCIBoard` class from `open_bci_v3.py`.

Note: copy `open_bci_v3.py` there if you want to run the code -- no proper package yet.

* `test.py`: minimal example, printing values.
* `stream_data.py` a version of a TCP streaming server that somehow oversamples OpenBCI from 250 to 256Hz.
* `upd_server.py` *DEPRECATED* (Use Plugin): see https://github.com/OpenBCI/OpenBCI_Node for implementation example.

## <a name="license"></a> License:

MIT

[link_aj_keller]: https://github.com/aj-ptw
[link_shop_wifi_shield]: https://shop.openbci.com/collections/frontpage/products/wifi-shield?variant=44534009550
[link_shop_ganglion]: https://shop.openbci.com/collections/frontpage/products/pre-order-ganglion-board
[link_shop_cyton]: https://shop.openbci.com/collections/frontpage/products/cyton-biosensing-board-8-channel
[link_shop_cyton_daisy]: https://shop.openbci.com/collections/frontpage/products/cyton-daisy-biosensing-boards-16-channel
[link_nodejs_cyton]: https://github.com/openbci/openbci_nodejs_cyton
[link_nodejs_ganglion]: https://github.com/openbci/openbci_nodejs_ganglion
[link_nodejs_wifi]: https://github.com/openbci/openbci_nodejs_wifi
[link_javascript_utilities]: https://github.com/OpenBCI/OpenBCI_JavaScript_Utilities
[link_openbci]: http://www.openbci.com
