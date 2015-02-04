import open_bci_v3 as bci
import os
import time

# Transmit data to openvibe acquisition server, intelpolating data (well, sort of) from 250Hz to 256Hz

NB_CHANNELS = 8

# typically 1.024 to go from 250Hz to 256Hz
SAMPLING_FACTOR = 1.024

# check packet drop
last_id = -1

# counter for sampling rate
nb_samples_in = -1
nb_samples_out = -1

# Init time to compute sampling rate
tick = time.time()
start_tick = tick

# last seen values for interpolation
last_values = [0] * NB_CHANNELS

# counter to trigger duplications...
leftover_duplications = 0

def printData(sample):
  new_tick = time.time()
    
  # check packet skipped
  global last_id
  # TODO: duplicate packet if skipped to stay sync
  if sample.id != last_id + 1:
    print "time", new_tick, ": paquet skipped!"
  if sample.id == 255:
    last_id = -1
  else:
    last_id = sample.id
    
  # save current values for possible interpolation
  global last_values
  last_values = list(sample.channel_data)
  
  #print "----------------"
  #print("%f" %(sample.id))
  #print sample.channel_data
  #print sample.aux_data
  #print "----------------"
  
  # update counters
  global nb_samples_in, nb_samples_out
  nb_samples_in = nb_samples_in + 1
  nb_samples_out = nb_samples_out + 1

  # check for duplication
  global leftover_duplications
  needed_duplications = SAMPLING_FACTOR + leftover_duplications
  nb_duplications = round(needed_duplications)
  leftover_duplications = needed_duplications - nb_duplications
  # If we need to insert values, will interpolate between current packet and last one
  # FIXME: ok, at the moment because we do packet per packet treatment, only handles nb_duplications == 1 or 2
  if (nb_duplications > 1):
    interpol_values = list(last_values)
    for i in range(0,len(interpol_values)):
      # OK, it's a very rough interpolation
      interpol_values[i] = (last_values[i] + sample.channel_data[i]) / 2
    print "  --"
    print "  last values: ", last_values
    print "  interpolation: ", interpol_values
    print "  current sample: ", sample.channel_data
    nb_samples_out = nb_samples_out + 1
    
  # check FPS
  global tick
  elapsed_time = new_tick - tick
  if elapsed_time >= 1:
    print "--- at t: ", (new_tick - start_tick), " ---"
    print "elapsed_time: ", elapsed_time
    print "nb_samples_in: ", nb_samples_in
    print "nb_samples_out: ", nb_samples_out
    tick = new_tick
    nb_samples_in = -1
    nb_samples_out = -1

if __name__ == '__main__':
  port = '/dev/ttyUSB0'
  baud = 115200
  board = bci.OpenBCIBoard(port=port, baud=baud, filter_data=False)
  board.startStreaming(printData)

