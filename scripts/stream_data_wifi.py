import sys; sys.path.append('..') # help python find cyton.py relative to scripts folder
from openbci import wifi as bci
import logging


def printData(sample):
    print(sample.sample_number)
    print(sample.channel_data)


if __name__ == '__main__':
    shield_name = 'OpenBCI-E2B6'
    logging.basicConfig(filename="test.log",format='%(asctime)s - %(levelname)s : %(message)s',level=logging.DEBUG)
    logging.info('---------LOG START-------------')
    shield = bci.OpenBCIWiFi(shield_name=shield_name, log=True, high_speed=False)
    print("WiFi Shield Instantiated")
    shield.start_streaming(printData)

    shield.loop()
