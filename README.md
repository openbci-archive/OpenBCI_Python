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

Currently the Ganglion board can only be used with a Linux OS.

## Boards Commands

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
board = OpenBCIWifi()
```

Once you initialize the board you can use the following commands:

```python

# Write commands to the board
board.write_command(command)

# Start stream
board.start_stream()
```


## Examples



## Other useful commands

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
