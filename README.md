# OpenBCI Python

<p align="center" href="">
  Provide a stable Python driver for all OpenBCI Biosensors
</p>

[![Build Status](https://travis-ci.org/OpenBCI/OpenBCI_Python.svg?branch=master)](https://travis-ci.org/OpenBCI/OpenBCI_Python)

Using this repo provides a building block for developing with Python. The goal for the Python library is to ***provide a stable Python driver for all OpenBCI Biosensors***, that:

* Allows Python users to install one module and use any board they choose
* Provides examples of using Python to port data to other apps like lab streaming layer
* Performs the heavy lifting when extracting and transforming raw binary byte streams
* Use unit tests to ensure perfect quality of core code

## Requirements

* Python 2.7 or 3.4+
* Currently the Cyton and Wifi Shield work on Windows, Linux, and MacOS.
* Ganglion works on Linux only.

## Installation

```python
pip install openbci
```

## Important notes

Currently the Ganglion board can only be used with a Linux OS. The WiFi shield is known to have reliability issues across different computer configurations. Using it effectively requires advanced technical skills and programming knowledge. Note that the code avaiable here has not been tested accross all platforms.

### Getting Started

First you need to initialize your board with one of the following commands:

#### For Cyton board:

```python
# For Windows replace '*' with the port number
board = OpenBCICyton(port='COM*')

# For MacOS and Linux replace '*' with the port number
board = OpenBCICyton(port='/dev/ttyUSB*')
```

#### For Cyton + Daisy:

```python
# For Windows replace '*' with the port number
board = OpenBCICyton(port='COM*', daisy=True)

# For MacOS and Linux replace '*' with the port number
board = OpenBCICyton(port='/dev/ttyUSB*', daisy=True)
```

#### For Ganglion:

```python
# For Windows replace '*' with the port number
board = OpenBCIGanglion(port='COM*', daisy=True)

# For MacOS and Linux replace '*' with the port number
board = OpenBCIGanglion(port='/dev/ttyUSB*', daisy=True)
```

#### For Wifi Shield:

```python
board = OpenBCIWifi(shield_name='OpenBCI-2254', sample_rate=200)
```

### Sending commands

Once you initialize the board you can use the commands on the OpenBCI SDKs ([Ganglion](https://docs.openbci.com/OpenBCI%20Software/06-OpenBCI_Ganglion_SDK), [Cyton](https://docs.openbci.com/OpenBCI%20Software/04-OpenBCI_Cyton_SDK), [Wifi Shield](https://docs.openbci.com/OpenBCI%20Software/08-OpenBCI_Wifi_SDK)) to send commands to the board using python (make sure your commands are strings).

```python

# Write commands to the board
board.write_command(command)
```

Here is a table of the most common ones:

|                               | Ganglion SDK | Cyton SDK       | Cyton & Daisy SDK (Additional Commands) | Wifi Shield SDK (Additional Commands)                                                                                                                                    |
|-------------------------------|--------------|-----------------|-----------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Turn Channels OFF             | 1 2 3 4      | 1 2 3 4 5 6 7 8 | q w e r t y u i                         |                                                                                                                                                                          |
| Turn Channels ON              |              | ! @ # $ % ^ & * | Q W E R T Y U I                         |                                                                                                                                                                          |
| Connect to internal GND       |              | 0               |                                         |                                                                                                                                                                          |
| Enable Synthetic Square Wave  | [            | [               |                                         |                                                                                                                                                                          |
| Disable Synthetic Square Wave | ]            | ]               |                                         |                                                                                                                                                                          |
| Connect to DC Signal          |              | p               |                                         |                                                                                                                                                                          |
| Set Channels to Default       |              | d               |                                         |                                                                                                                                                                          |
| Start Streaming Data          | b            | b               |                                         |                                                                                                                                                                          |
| Stop Streaming Data           | s            | s               |                                         |                                                                                                                                                                          |
| Soft Reset                    | v            | v               |                                         | ;                                                                                                                                                                        |
| Enable Accelerometer          | n            |                 |                                         |                                                                                                                                                                          |
| Disable Accelerometer         | N            |                 |                                         |                                                                                                                                                                          |


### Initializing Stream

To start your stream you can use the following command with a callback function. You can look at the examples folder for some pre-written callback functions.

```python
# Start stream
board.start_stream(callback)
```
The output of the start_stream function is the OpenBCISample on the callback function. The OpenBCISample object has the following attributes:

* packet_id = The ID of the incomming packet.
* channels_data = The raw EEG data of each channel. 4 for the Ganglion, 8 for the Cyton, and 16 for the Cyton + Daisy.
* aux_data = Accelerometer data.

Because the channels_data and aux_data is the raw data in counts read by the board, we need to multiply the data by a scale factor. There is a specific scale factor for each board:

#### For the Cyton and Cyton + Daisy boards:

Multiply uVolts_per_count to convert the channels_data to uVolts.

```python
uVolts_per_count = (4500000)/24/(2**23-1) #uV/count
```
Multiply accel_G_per_count to convert the aux_data to G.

```python
accel_G_per_count = 0.002 / (2**4) #G/count
```
#### For the Ganglion Board

Multiply Volts_per_count to convert the channels_data to Volts.

```python
Volts_per_count = 1.2 * 8388607.0 * 1.5 * 51.0 #V/count
```
Multiply accel_G_per_count to convert the aux_data to G.

```python
accel_G_per_count = 0.032 #G/count
```

### Example (Simple LSL Streamer)
```python

from openbci import OpenBCICyton
from pylsl import StreamInfo, StreamOutlet
import numpy as np

SCALE_FACTOR_EEG = (4500000)/24/(2**23-1) #uV/count
SCALE_FACTOR_AUX = 0.002 / (2**4)


print("Creating LSL stream for EEG. \nName: OpenBCIEEG\nID: OpenBCItestEEG\n")

info_eeg = StreamInfo('OpenBCIEEG', 'EEG', 8, 250, 'float32', 'OpenBCItestEEG')

print("Creating LSL stream for AUX. \nName: OpenBCIAUX\nID: OpenBCItestEEG\n")

info_aux = StreamInfo('OpenBCIAUX', 'AUX', 3, 250, 'float32', 'OpenBCItestAUX')

outlet_eeg = StreamOutlet(info_eeg)
outlet_aux = StreamOutlet(info_aux)

def lsl_streamers(sample):
    outlet_eeg.push_sample(np.array(sample.channels_data)*SCALE_FACTOR_EEG)
    outlet_aux.push_sample(np.array(sample.aux_data)*SCALE_FACTOR_AUX)

board = OpenBCICyton(port='COM5', daisy=False)

board.start_stream(lsl_streamers)

```
### Who are we?

The founder of the OpenBCI Python repository is Jermey Frey. The Python driver is one of the most popular repositories and has the most contributors!

The contributors to these repos are people using Python mainly for their data acquisition and analytics.


### Get involved

If you think you can help in any of the areas listed above (and we bet you can) or in any of the many areas that we haven't yet thought of (and here we're *sure* you can) then please check out our [contributors' guidelines](CONTRIBUTING.md) and our [roadmap](ROADMAP.md).

Please note that it's very important to us that we maintain a positive and supportive environment for everyone who wants to participate. When you join us we ask that you follow our [code of conduct](CODE_OF_CONDUCT.md) in all interactions both on and offline.

### Contact us

If you want to report a problem or suggest an enhancement we'd love for you to [open an issue](../../issues) at this github repository because then we can get right on it. But you can also contact [AJ][link_aj_keller] by email (pushtheworldllc AT gmail DOT com) or on [twitter](https://twitter.com/aj-ptw).

### Find out more

You might be interested in:

* Purchase a [Cyton][link_shop_cyton] | [Ganglion][link_shop_ganglion] | [WiFi Shield][link_shop_wifi_shield] from [OpenBCI][link_openbci]
* Get taught how to use OpenBCI devices by [Push The World][link_ptw] BCI Consulting

And of course, you'll want to know our:

* [Contributors' guidelines](CONTRIBUTING.md)
* [Roadmap](ROADMAP.md)

### Glossary

OpenBCI boards are commonly referred to as _biosensors_. A biosensor converts biological data into digital data. 

The [Ganglion][link_shop_ganglion] has 4 channels, meaning the Ganglion can take four simultaneous voltage readings.
 
The [Cyton][link_shop_cyton] has 8 channels and [Cyton with Daisy][link_shop_cyton_daisy] has 16 channels. 

Generally speaking, the Cyton records at a high quality with less noise. Noise is anything that is not signal.

### Thank you

Thank you so much (Danke schön! Merci beaucoup!) for visiting the project and we do hope that you'll join us on this amazing journey to make programming with OpenBCI fun and easy.

### <a name="license"></a> License:

MIT

[link_shop_wifi_shield]: https://shop.openbci.com/collections/frontpage/products/wifi-shield?variant=44534009550
[link_shop_ganglion]: https://shop.openbci.com/collections/frontpage/products/pre-order-ganglion-board
[link_shop_cyton]: https://shop.openbci.com/collections/frontpage/products/cyton-biosensing-board-8-channel
[link_shop_cyton_daisy]: https://shop.openbci.com/collections/frontpage/products/cyton-daisy-biosensing-boards-16-channel
[link_nodejs_cyton]: https://github.com/openbci/openbci_nodejs_cyton
[link_nodejs_ganglion]: https://github.com/openbci/openbci_nodejs_ganglion
[link_nodejs_wifi]: https://github.com/openbci/openbci_nodejs_wifi
[link_javascript_utilities]: https://github.com/OpenBCI/OpenBCI_JavaScript_Utilities
[link_openbci]: http://www.openbci.com
