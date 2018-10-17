# v1.0.1

### Bug Fixes

* user.py always loaded the ganglion and didnt work with the cyton any more.
* Multiple other fixes

# v1.0.0

### New Features

* High speed mode for WiFi shield sends raw data - #51
* Unit testing with Nosetests
* Continuous Integration with Travis.ci

### Breaking Changes

* Refactored library for pip
* Moved plugins folder into openbci dir so plugins can be imported when installed with pip


## Beta 0

* Adds high speed for Daisy over WiFi - now all boards are supported!

## Alpha 1

* Adds high speed for Ganglion over WiFi

## Alpha 0

* Adds high speed for Cyton over WiFi

# v0.1

## dev

Features:
  - Stream data over TCP (OpenViBE telnet reader format), OSC, UDP, LSL
  - 16 channels support (daisy module)
  - test sampling rate
  - plugin system
  - several different callback functions
  - start streaming in a separate thread so new commands can be issued

Bugfixes:
  - scale factor
  - timing for Windows OS
  - aux data endianness
  - reset board on startup

## 0.1 (2015-02-11)

First stable version. (?)
