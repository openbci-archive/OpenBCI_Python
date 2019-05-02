# Scripts that you can use with the OpenBCI Boards
import csv
import datetime


boards = {'Ganglion': [4, 200] ,'Cyton': [8, 250], 'CytonDaisy': [16, 125] }

def print_raw(sample):
    print(sample.channels_data)
    print(sample.aux_data)

def csv_collect(sample):
    file_name = 'OpenBCIData_' + sample.start_time
    data = [int(datetime.datetime.now().strftime("%H%M%S%f"))]
    data.append(sample.channels_data[:])
    data.append(sample.aux_data[:])
    with open(file_name, "a") as file:
        writer = csv.writer(file)
        writer.writerow(data)

def osc_streamer(sample):
    pass

def tcp_streamer(sample):
    pass

def udp_streamer(sample):
    pass
