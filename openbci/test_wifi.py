from wifi import OpenBCIWiFi

wifi = OpenBCIWiFi(shield_name='OpenBCI-2254', sample_rate=200)

def printdata(sample):
    print(sample.channel_data)

wifi.start_streaming(printdata)
wifi.loop()
