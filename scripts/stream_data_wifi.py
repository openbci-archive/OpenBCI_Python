import sys; sys.path.append('..') # help python find open_bci_v3.py relative to scripts folder
import open_bci_wifi as bci
import os
import logging
import time


def printData(sample):
    #os.system('clear')
    print "----------------"
    print("%f" %(sample.id))
    print sample.channel_data
    # print sample.aux_data
    print "----------------"


if __name__ == '__main__':
    shield_name = 'OpenBCI-E2B6'
    #port = '/dev/tty.OpenBCI-DN0096XA'
    # baud = 115200
    logging.basicConfig(filename="test.log",format='%(asctime)s - %(levelname)s : %(message)s',level=logging.DEBUG)
    logging.info('---------LOG START-------------')
    shield = bci.OpenBCIWifi(shield_name=shield_name, log=True)
    print("WiFi Shield Instantiated")
    # shield.stream_start()
    # board.ser.write('v')
    # time.sleep(10)
    shield.start_streaming(printData)

    shield.loop()
    # board.print_bytes_in()
