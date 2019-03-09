from __future__ import print_function
import sys

sys.path.append('..')  # help python find cyton.py relative to scripts folder
from openbci import wifi as bci
import logging


def handle_streamed_data(sample):
    print(sample.sample_number)
    print(sample.channel_data)


if __name__ == '__main__':

    logging.basicConfig(filename="test.log", format='%(asctime)s - %(levelname)s : %(message)s', level=logging.DEBUG)
    logging.info('---------LOG START-------------')
    # If you don't know your IP Address, you can use shield name option
    # If you know IP, such as with wifi direct 192.168.4.1, then use ip_address='192.168.4.1'
    shield_name = 'OpenBCI-E218'
    sample_rate = 500
    ip_address='192.168.4.1'
    
    shield_wifi= bci.OpenBCIWiFi(ip_address=ip_address,
                             shield_name=shield_name,
                             sample_rate=sample_rate,
                             timeout=15,
                             max_packets_to_skip=10,
                             latency=5000,
                             high_speed=True,
                             ssdp_attempts=20,
                             auto_connect=False, 
                             micro_volts=True)
                             
 	print("WiFi Shield Instantiated")                            
    time.sleep(1)
    shield_wifi.connect()
    print("WiFi Shield Connected with board")   
    time.sleep(1)
    print("WiFi Shield streaming started...")   
    shield_wifi.start_streaming(handle_streamed_data)
    shield_wifi.loop()
    
    # Note: do this when you're finished streaming:
    # shield_wifi.stop()
    # shield_wifi.disconnect()
