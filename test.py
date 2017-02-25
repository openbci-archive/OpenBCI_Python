
# testing ganglion board connectivity

import open_bci_ganglion as bci

def handle_sample(sample):
  print(sample.channels)

board = bci.OpenBCIBoard()
board.start(handle_sample)
