"""A sample client for the OpenBCI UDP server."""

import argparse
import cPickle as pickle
import json
import sys; sys.path.append('..') # help python find open_bci_v3.py relative to scripts folder
import open_bci_v3 as open_bci
import socket


parser = argparse.ArgumentParser(
    description='Run a UDP client listening for streaming OpenBCI data.')
parser.add_argument(
    '--json',
    action='store_true',
    help='Handle JSON data rather than pickled Python objects.')
parser.add_argument(
    '--host',
    help='The host to listen on.',
    default='127.0.0.1')
parser.add_argument(
    '--port',
    help='The port to listen on.',
    default='8888')


class UDPClient(object):

  def __init__(self, ip, port, json):
    self.ip = ip
    self.port = port
    self.json = json
    self.client = socket.socket(
        socket.AF_INET, # Internet
        socket.SOCK_DGRAM)
    self.client.bind((ip, port))

  def start_listening(self, callback=None):
    while True:
      data, addr = self.client.recvfrom(1024)
      print("data")
      if self.json:
        sample = json.loads(data)
        # In JSON mode we only recieve channel data.
        print data
      else:
        sample = pickle.loads(data)
        # Note that sample is an OpenBCISample object.
        print sample.id
        print sample.channel_data


args = parser.parse_args()
client = UDPClient(args.host, int(args.port), args.json)
client.start_listening()
