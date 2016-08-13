#!/usr/bin/env python2.7
import argparse  # new in Python2.7
import os
import time
import string
import atexit
import threading
import logging
import sys

from yapsy.PluginManager import PluginManager

# Load the plugins from the plugin directory.
manager = PluginManager()
manager.setPluginPlaces(["plugins"])
manager.collectPlugins()

# OPENBCI FUNCTIONS
def set_up_parser():
    '''
        Returns a parser object to set up OpenBCI.
        :return: argparse.Namespace
    '''
    parser = argparse.ArgumentParser(description="OpenBCI 'user'")
    parser.add_argument('--board', default=3, type=int)
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
    parser.add_argument('--no-filtering', dest='filtering',
                        action='store_false',
                        help="Disable notch filtering")
    parser.set_defaults(filtering=True)
    parser.add_argument('-d', '--daisy', dest='daisy',
                        action='store_true',
                        help="Force daisy mode (beta feature)")
    # first argument: plugin name, then parameters for plugin
    parser.add_argument('-a', '--add', metavar=('PLUGIN', 'PARAM'),
                        action='append', nargs='+',
                        help="Select which plugins to activate and set parameters.")
    parser.add_argument('--log', dest='log', action='store_true',
                        help="Log program")
    parser.set_defaults(daisy=False, log=False)

def set_logging(args):
    '''
    Sets up logging capability
    :param args: argparse.Namespace
    :return: None
    '''
    if args.log:
        print("Logging Enabled: " + str(args.log))
        logging.basicConfig(filename="OBCI.log",
                            format='%(asctime)s - %(levelname)s : %(message)s',
                            level=logging.DEBUG)
        logging.getLogger('yapsy').setLevel(logging.DEBUG)
        logging.info('---------LOG START-------------')
        logging.info(args)
    else:
        print("user.py: Logging Disabled.")

def add_plugin(plugin_name, plugin_args, board, plugin_list, callback_list):
    #TODO: what type is plugin_args?
    '''
    Find and activate plugin listed, and add it to the plugin list
    :param plugin_name: string
    :param plugin_args:
    :param board: bci.OpenBCIBoard
    :param plugin_list: list
    :param callback_list: list
    :return:
    '''
    plug_name = plugin_name
    plug_args = plugin_args
    plug = manager.getPluginByName(plug_name)
    if plug == None:
        # eg: if an import fail inside a plugin, yapsy skip it
        print ("Error: [", plug_name,
               "] not found or could not be loaded. Check name and requirements.")
    else:
        print ("\nActivating [", plug_name, "] plugin...")
        if not plug.plugin_object.pre_activate(plug_args,
                                               sample_rate=board.getSampleRate(),
                                               eeg_channels=board.getNbEEGChannels(),
                                               aux_channels=board.getNbAUXChannels()):
            print ("Error while activating [", plug_name,
                   "], check output for more info.")
        else:
            print ("Plugin [", plug_name, "] added to the list")
            plugin_list.append(plug.plugin_object)
            callback_list.append(plug.plugin_object)

def execute_plugins(board):
    '''
    Streams data from OpenBCI and runs plugins
    :param board: bci.OpenBCIBoard
    :return:
    '''
    print ("--------------INFO---------------")
    print ("User serial interface enabled...\n\
    View command map at http://docs.openbci.com.\n\
    Type /start to run -- and /stop before issuing new commands afterwards.\n\
    Type /exit to exit. \n\
    Board outputs are automatically printed as: \n\
    %  <tab>  message\n\
    $$$ signals end of message")

    print("\n-------------BEGIN---------------")
    # Init board state
    # s: stop board streaming; v: soft reset of the 32-bit board (no effect with 8bit board)
    s = 'sv'
    # Tell the board to enable or not daisy module
    if board.daisy:
        s = s + 'C'
    else:
        s = s + 'c'
    # d: Channels settings back to default
    s = s + 'd'

    while (s != "/exit"):
        # Send char and wait for registers to set
        if (not s):
            pass
        elif ("help" in s):
            print ("View command map at: \
    http://docs.openbci.com/software/01-OpenBCI_SDK.\n\
    For user interface: read README or view \
    https://github.com/OpenBCI/OpenBCI_Python")

        elif board.streaming and s != "/stop":
            print (
            "Error: the board is currently streaming data, please type '/stop' before issuing new commands.")
        else:
            # read silently incoming packet if set (used when stream is stopped)
            flush = False

            if ('/' == s[0]):
                s = s[1:]
                rec = False  # current command is recognized or fot

                if ("T:" in s):
                    lapse = int(s[string.find(s, "T:") + 2:])
                    rec = True
                elif ("t:" in s):
                    lapse = int(s[string.find(s, "t:") + 2:])
                    rec = True
                else:
                    lapse = -1

                if ("start" in s):
                    if (fun != None):
                        # start streaming in a separate thread so we could always send commands in here
                        boardThread = threading.Thread(
                            target=board.start_streaming, args=(fun, lapse))
                        boardThread.daemon = True  # will stop on exit
                        try:
                            boardThread.start()
                        except:
                            raise
                    else:
                        print ("No function loaded")
                    rec = True
                elif ('test' in s):
                    test = int(s[s.find("test") + 4:])
                    board.test_signal(test)
                    rec = True
                elif ('stop' in s):
                    board.stop()
                    rec = True
                    flush = True
                if rec == False:
                    print("Command not recognized...")

            elif s:
                for c in s:
                    if sys.hexversion > 0x03000000:
                        board.ser.write(bytes(c, 'utf-8'))
                    else:
                        board.ser.write(bytes(c))
                    time.sleep(0.100)

            line = ''
            time.sleep(0.1)  # Wait to see if the board has anything to report
            while board.ser.inWaiting():
                c = board.ser.read().decode('utf-8')
                line += c
                time.sleep(0.001)
                if (c == '\n') and not flush:
                    print('%\t' + line[:-1])
                    line = ''

            if not flush:
                print(line)

        # Take user input
        # s = input('--> ')
        if sys.hexversion > 0x03000000:
            s = input('--> ')
        else:
            s = raw_input('--> ')


if __name__ == '__main__':

    print ("            USER.py")
    # ADD ARGUMENTS
    parser = set_up_parser()
    args = parser.parse_args()

    if not (args.port or args.list or args.info):
        parser.error(
            'No action requested. Use `--port serial_port` to connect to the bord; `--list` to show available plugins or `--info [plugin_name]` to get more information.')

    # DECIDE WHICH VERSION OF OPENBCI BOARD IS BEING USED
    if args.board == 3:
        print("main.py: open_bci_v3...")
        import open_bci_v3 as bci
    elif args.board == 4:
        print("main.py: open_bci_v_ganglion...")
        import open_bci_v_ganglion as bci
    else:
        logging.warn('Board type not recognized')

    # Print list of available plugins and exit
    if args.list:
        print ("Available plugins:")
        for plugin in manager.getAllPlugins():
            print ("\t-", plugin.name)
        exit()

    # User wants more info about a plugin...
    if args.info:
        plugin = manager.getPluginByName(args.info)
        if plugin == None:
            # eg: if an import fail inside a plugin, yapsy skip it
            print ("Error: [", args.info, "] not found or could not be loaded. Check name and requirements.")
        else:
            print (plugin.description)
            plugin.plugin_object.show_help()
        exit()

    print ("\n------------SETTINGS-------------")
    print ("Notch filtering:", args.filtering)

    # LOGGING
    set_logging(args)

    print ("\n-------INSTANTIATING BOARD-------")
    board = bci.OpenBCIBoard(port=args.port,
                             daisy=args.daisy,
                             filter_data=args.filtering,
                             scaled_output=True,
                             log=args.log)

    #  Info about effective number of channels and sampling rate
    if board.daisy:
        print ("Force daisy mode:")
    else:
        print ("No daisy:")
        print (board.getNbEEGChannels(), "EEG channels and", board.getNbAUXChannels(), "AUX channels at", board.getSampleRate(), "Hz.")

    print ("\n------------PLUGINS--------------")
    # Loop round the plugins and print their names.
    print ("Found plugins:")
    for plugin in manager.getAllPlugins():
        print ("[", plugin.name, "]")
    print()


    # Fetch plugins, try to activate them, add to the list if OK
    plug_list = []
    callback_list = []
    if args.add:
        for plug_candidate in args.add:
            # first value: plugin name, then optional arguments
            plug_name = plug_candidate[0]
            plug_args = plug_candidate[1:]
            # Try to find name
            plug = manager.getPluginByName(plug_name)

            # Add plugin
            add_plugin(plug_name, plug_args, board, plug_list, callback_list)


    if len(plug_list) == 0:
        print ("WARNING: no plugin selected, you will only be able to communicate with the board.")
        fun = None
    else:
        fun = callback_list

    def cleanUp():
        board.disconnect()
        print ("Deactivating Plugins...")
        for plug in plug_list:
            plug.deactivate()
        print ("User.py exiting...")

    atexit.register(cleanUp)

    execute_plugins(board)