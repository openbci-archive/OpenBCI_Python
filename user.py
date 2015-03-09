#!/usr/bin/env python2.7
import argparse # new in Python2.7
import open_bci_v3 as bci
import os
import time
import string
import atexit

from yapsy.PluginManager import PluginManager

import logging
logging.basicConfig(level=logging.CRITICAL) # DEBUG for dev

# Load the plugins from the plugin directory.
manager = PluginManager()
manager.setPluginPlaces(["plugins"])
manager.collectPlugins()

if __name__ == '__main__':

	print "			USER.py"	
	parser = argparse.ArgumentParser(description="OpenBCI 'user'")
	parser.add_argument('-l', '--list', action='store_true',
				help="List available plugins.")
	parser.add_argument('-i', '--info', metavar='PLUGIN',
				help="Show more information about a plugin.")
	parser.add_argument('-p', '--port',
				help="Port to connect to OpenBCI Dongle " +
				"( ex /dev/ttyUSB0 or /dev/tty.usbserial-* )")
	# baud rate is not currently used
	parser.add_argument('-b', '--baud', default=115200, type=int,
				help="Baud rate (not currently used)")
	parser.add_argument('--no-filtering', dest='filtering', action='store_false',
				help="Disable notch filtering")
	parser.set_defaults(filtering=True)
	parser.add_argument('-d', '--daisy', dest='daisy', action='store_true',
				help="Force daisy mode (beta feature)")
	parser.set_defaults(daisy=False)
	# first argument: plugin name, then parameters for plugin
	parser.add_argument('-a', '--add', metavar=('PLUGIN', 'PARAM'), action='append', nargs='+',
			help="Select which plugins to activate and set parameters.")
	
	args = parser.parse_args()
	
	if not (args.port or args.list or args.info):
		parser.error('No action requested. Use `--port serial_port` to connect to the bord; `--list` to show available plugins or `--info [plugin_name]` to get more information.')
	
	# Print list of available plugins and exit
	if args.list:
		print "Available plugins:"
		for plugin in manager.getAllPlugins():
			print "\t-", plugin.name
		exit()
	
	# User wants more info about a plugin...
	if args.info:
		plugin=manager.getPluginByName(args.info)
		if plugin == None:
			# eg: if an import fail inside a plugin, yapsy skip it
			print "Error: [", args.info, "] not found or could not be loaded. Check name and requirements."
		else:
			print plugin.description
			plugin.plugin_object.show_help()
		exit()
	
	print "\n------------PLUGINS--------------"
	# Loop round the plugins and print their names.
	print "Found plugins:",
	for plugin in manager.getAllPlugins():
		print "[", plugin.name, "]",
	print
	

	# Fetch plugins, try to activate them, add to the list if OK
	plug_list = []
	callback_list = []
	if args.add:
		for plug_candidate in args.add:
			# first value: plugin name, then optional arguments
			plug_name=plug_candidate[0]
			plug_args=plug_candidate[1:]
			# Try to find name
			plug=manager.getPluginByName(plug_name)
			if plug == None:
				# eg: if an import fail inside a plugin, yapsy skip it
				print "Error: [", plug_name, "] not found or could not be loaded. Check name and requirements."
			else:
				print "\nActivating [", plug_name, "] plugin..."
				if not plug.plugin_object.pre_activate(plug_args, sample_rate=250, eeg_channels=8, aux_channels=3):
					print "Error while activating [", plug_name, "], check output for more info."
				else:
					print "Plugin [", plug_name, "] added to the list"
					plug_list.append(plug.plugin_object)
					callback_list.append(plug.plugin_object)

	if len(plug_list) == 0:
		print "WARNING: no plugin selected, you will only be able to communicate with the board."
		fun = None
	else:
		fun = callback_list

	print "\n------------SETTINGS-------------"
	print "Notch filtering:", args.filtering

	print "\n-------INSTANTIATING BOARD-------"
	board = bci.OpenBCIBoard(port=args.port, daisy=args.daisy, filter_data=args.filtering)
	
	#  Info about effective number of channels and sampling rate
	if board.daisy:
		print "Force daisy mode:",
	else:
		print "No daisy:",
	print board.getNbEEGChannels(), "EEG channels and", board.getNbAUXChannels(), "AUX channels at", board.getSampleRate(), "Hz."
	
	def cleanUp():
		board.disconnect()
		print "Deactivating Plugins..."
		for plug in plug_list:
			plug.deactivate()
		print "User.py exiting..."

	atexit.register(cleanUp)
	
	print "--------------INFO---------------"
	print "User serial interface enabled...\n\
View command map at http://docs.openbci.com.\n\
Type start to run. Type /exit to exit. \n\
Board outputs are automatically printed as: \n\
%  <tab>  message\n\
$$$ signals end of message"

	print("\n-------------BEGIN---------------")

	#Start by restoring default settings
	s = 'd'

	while(s != "/exit"):
		#Send char and wait for registers to set
		if (not s): pass

		elif("help" in s): print "View command map at: \
http://docs.openbci.com/software/01-OpenBCI_SDK.\n\
For user interface: read README or view \
https://github.com/OpenBCI/OpenBCI_Python"

		elif('/' == s[0]):
			s = s[1:]
			rec = False

			if("T:" in s):
				lapse = int(s[string.find(s,"T:")+2:])
				rec = True
			elif("t:" in s):
				lapse = int(s[string.find(s,"t:")+2:])
				rec = True
			else:
				lapse = -1

			if("start" in s): 
				if(fun != None):
					board.start_streaming(fun, lapse)
				else:
					print "No function loaded"
				rec = True


			elif('test' in s):
				test = int(s[string.find(s,"test")+4:])
				board.test_signal(test)
				rec = True

			if rec == False:
				print("Command not recognized...")
			
		elif s:
			for c in s:
				board.ser.write(c)
				time.sleep(0.100)

		line = ''
		time.sleep(0.1) #Wait to see if the board has anything to report
		while board.ser.inWaiting():
			c = board.ser.read()
			line += c
			time.sleep(0.001)	
			if (c == '\n'):
				print('%\t'+line[:-1])
				line = ''
		print(line)

		#Take user input
		s = raw_input('--> ');
