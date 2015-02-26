#!/usr/bin/env python2.7
import argparse # new in Python2.7
import open_bci_v3 as bci
import os
import time
import string

from yapsy.PluginManager import PluginManager

import logging
logging.basicConfig(level=logging.DEBUG) 

# Load the plugins from the plugin directory.
manager = PluginManager()
manager.setPluginPlaces(["plugins"])
manager.collectPlugins()

if __name__ == '__main__':

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
		plug=manager.getPluginByName(plug_name)
		if plug == None:
			# eg: if an import fail inside a plugin, yapsy skip it
			print "Error: [", plug_name, "] not found or could not be loaded. Check name and requirements."
		else:
			print "yes"
	
	
	# Loop round the plugins and print their names.
	print "Found plugins:",
	for plugin in manager.getAllPlugins():
		print "[", plugin.name, "]",
	print
	
	
	print "Notch filtering:", args.filtering

	#  Configure number of output channels
	nb_channels=8
	if args.daisy:
		nb_channels=16
		print "Force daisy mode:", nb_channels, "channels."
	else:
		print "No daisy:", nb_channels, "channels."

	# Fetch plugins, try to activate them, add to the list if OK
	plug_list = []
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
			if not plug.plugin_object.activate(plug_args):
				print "Error while activating [", plug_name, "], check output for more info."
			else:
				print "Plugin [", plug_name, "] added to the list"
				plug_list.append(plug.plugin_object)

	if len(plug_list) == 0:
		print "WARNING: no plugin selected, you will only be able to communicate with the board."
		fun = None
	#TODO: a list of functions...
	else:
		fun = plug_list[0]
	
	print "User serial interface enabled..."
	print "Connecting to ", args.port
	
	board = bci.OpenBCIBoard(port=args.port, daisy=args.daisy, filter_data=args.filtering)

	print "View command map at http://docs.openbci.com."
	print "Type start to run. Type exit to exit."

	#Start by restoring default settings
	s = 'd'

	while(s != "exit"):
		#Send char and wait for registers to set
		if (not s): pass

		elif("help" in s): print "View command map at: \
			http://docs.openbci.com/software/01-OpenBCI_SDK.\n\
			For user interface, read README or view \
			https://github.com/OpenBCI/OpenBCI_Python"

		elif('/' == s[0]):
			s = s[1:]

			if("T:" in s):
				lapse = int(s[string.find(s,"T:")+2:])
			else:
				lapse = -1

			if("start" in s): 
				board.start_streaming(fun, lapse)

			elif('test' in s):
				test = int(s[string.find(s,"test")+4:])
				board.test_signal(test)
			
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
				print(line[:-1])
				line = ''
		print(line)

		#Take user input
		s = raw_input('--> ');

	# We're all set, disconnect board, switch off plugins
	board.disconnect()
	for plug in plug_list:
		plug.deactivate()
