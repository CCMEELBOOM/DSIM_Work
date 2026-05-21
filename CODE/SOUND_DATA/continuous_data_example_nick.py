

"""This script uses a daqhat board to record and save microphone data.

We record sound data with a Bruel & Kjaer 1/4" type 4958 microphone.
We use a Measurement Computing DAQ board for data acquisition. The default
sampling rate is 51.2 kHz. Every sample is first converted into a pressure
value using the microphone's sensitivity value of 12.9 mV/Pa. Next, the 
data points are then nondimensionalized by dividing by the reference pressure
for air 20e-6 Pa. These nondimensionalized samples are then saved into a csv
file with the RAW tag within the turtlebot3_micarray directory. 

Use the link below to see the example code from the daqhats library
that was referenced when writing this script:
https://github.com/mccdaq/daqhats/blob/master
/examples/python/mcc172/continuous_scan.py

Note this script should be in the same directory as the
daqhats_utils script, which can be taken from the daqhats library.
"""
import os
import csv
import time
from sys import stdout
from time import sleep
from datetime import datetime
import numpy as np
from daqhats_utils import chan_list_to_mask
from daqhats import mcc172, OptionFlags, SourceType

def main():
    """Performs setup, then starts recording data from mic."""

    # Perform setup
    hat,daq_params = setup_mic()
    csv_params = setup_csv(daq_params[0])

    # Unpack params
    channel_mask = daq_params[1]
    samples_per_channel = daq_params[3]
    options = daq_params[4]

    # Since the continuous option is being used, the samples_per_channel
    # parameter is ignored if the value is less than the default internal
    # buffer size (10000 * num_channels in this case). If a larger internal
    # buffer size is desired, set the value of this parameter accordingly.

    # Start the scan
    hat.a_in_scan_start(channel_mask, samples_per_channel, options)
    print("\nMicrophone Active")
    try:
        read_data(hat, daq_params, csv_params)
    except KeyboardInterrupt:
        hat.a_in_scan_stop()
        hat.a_in_scan_cleanup()
        print("\nMicrophone Terminated")

def setup_csv(mic_info):
    """This function sets up the microphone log csv files.

    This function will write data into a csv file
    saved in the following location in the turtlebot:
    /home/pi/turtlebot3_micarray

    This script will write a header for the csv file which
    records the date & time, as well as the time the script started.
    """

    # Define the start time
    start_time = time.time()

    # Define the number of RMS samples
    sample_num = 0

    # Unpack list
    iepe_enable = mic_info[0]
    req_scan_rate = mic_info[1]
    actual_scan_rate = mic_info[2]

    # Filepath location for saving log files:
    now = datetime.now()
    date_time_str = now.strftime("%Y-%m-%d_%H-%M-%S")
    os.makedirs("plots", exist_ok=True)
    raw_file_path = "csv-data/RAW.csv"

    # Write the header row for RAW file
    with open(f"{raw_file_path}", mode="w", newline="", encoding="utf-8") as file:
        log = csv.writer(file)
        log.writerow(["Date Time String:"])
        log.writerow([date_time_str])
        log.writerow(["Start Time:"])
        log.writerow([start_time])
        log.writerow(["IEPE Power:"])
        if iepe_enable == 1:
            log.writerow(["ON"])
        else:
            log.writerow(["OFF"])
        log.writerow(["Requested Scan Rate: "+str(req_scan_rate)])
        log.writerow(["Actual Scan Rate: "+str(actual_scan_rate)])

        # Records the logger data in a list:
        # Index 0, timestamp
        # Index 1 and onward, raw voltage data
        header = ["Row: [Time Elapsed in index 0, Raw Voltage from index 1 to the lines end]"]
        log.writerow(header)

    # Save the csv information in a list
    csv_params = [start_time,sample_num,raw_file_path]
    return csv_params

def setup_mic():
    """This script configures the daqhat to TB3-6's setup

    Reference:
    https://github.com/mccdaq/daqhats/blob/master
    /examples/python/mcc172/continuous_scan.py
    """

    # Enable IEPE for better results
    iepe_enable = 1  # 1 for on, 0 for off
    # Selecting the MCC_172 DAQ Hat (0 = bottom daq, 1 = top daq)
    address = 0
    # Define hat as the daq hat
    hat = mcc172(address)
    # Using only one channel on the MCC 172 daqhat
    # Sampling at channel 0 on the daq, 1 for channel 1
    channels = [0]
    num_channels = len(channels)
    # Needs this to tell scan what channel to read from
    channel_mask = chan_list_to_mask(channels)
    # Turns iepe on or off on channel 0
    hat.iepe_config_write(channels[0], iepe_enable)
    
    # The daqhat has its own default sensitivity of 1000 mV/mechanical unit
    # We want to set our own sensitivity so that every voltage datapoint (in mV)
    # is adjusted with our microphone's sensitivity, then nondimensionalized with
    # the reference pressure for air. This line effectively means that our daqhat will
    # take in the voltage data (in mV) from the microphone, and then return the 
    # nondimensionalized pressure data with hat.a_in_scan_read for us to save.
    pref = 20e-6    # Reference pressure for air in Pa
    mic_sensitivity = 12.9 # mV/Pa mic sensitivity
    hat.a_in_sensitivity_write(channels[0], mic_sensitivity*pref)

    # Initialize variables
    options = OptionFlags.CONTINUOUS
    samples_per_channel = 1600000    # change this to avoid buffer overruns
    sample_rate = 51.2e3  # samples/second

    # Configure the clock and wait for sync to complete
    hat.a_in_clock_config_write(SourceType.LOCAL, sample_rate)

    synced = False
    while not synced:
        (_source_type, actual_scan_rate, synced) = hat.a_in_clock_config_read()
        if not synced:
            sleep(0.005)

    # Save the IEPE mode, the requested sample rate
    # and the actual scan rate to print into log files
    mic_info = [iepe_enable,sample_rate,actual_scan_rate]

    # Save variables in a list called params
    params = [mic_info,channel_mask,num_channels,samples_per_channel,options]

    return hat,params

def read_data(hat, daq_params, csv_params):
    """Reads data from the daqhat, then saves the nondimensionalized data.

    Reads data from the specified channels on the specified DAQ HAT devices
    and writes the data to the csv file. The reads are executed in a loop 
    that continues until the user stops the scan or an overrun error is detected.

    Args:
        hat (mcc172): The mcc172 HAT device object.
        daq_params: A list of daqhat parameters.
        csv_params: A list of the csv file parameters.

    Returns:
        None
    """

    # Unpack list
    num_channels = daq_params[2]
    # Initialize variables
    read_all_available = -1
    read_request_size = read_all_available

    # When doing a continuous scan, the timeout value will be ignored in the
    # call to a_in_scan_read because we will be requesting that all available
    # samples (up to the default buffer size) be returned.
    timeout = 0.0

    # Read all of the available samples (up to the size of the read_buffer which
    # is specified by the user_buffer_size).  Since the read_request_size is set
    # to -1 (READ_ALL_AVAILABLE), this function returns immediately with
    # whatever samples are available (up to user_buffer_size) and the timeout
    # parameter is ignored.
    while True:
        read_result = hat.a_in_scan_read_numpy(read_request_size, timeout)

        # Check for an overrun error
        if read_result.hardware_overrun:
            print("\n\nHardware overrun\n")
            break
        if read_result.buffer_overrun:
            print("\n\nBuffer overrun\n")
            break

        samples_read_per_channel = int(len(read_result.data) / num_channels)
        save_to_log(read_result,samples_read_per_channel,csv_params)

def save_to_log(read_result,samples_read_per_channel,csv_params):
    """This function saves data to a log csv file.
    
    This data from the daqhat buffer is stored as a list, 
    this gets written into a new row in the csv file every
    time this function is called. 
    """

    # Unpack list
    file_path = csv_params[2]

    if samples_read_per_channel > 0:
        # Write to the RAW.csv file
        with open(f"{file_path}", mode="a", newline="", encoding="utf-8") as file:
            log = csv.writer(file)
            row = read_result.data
            log.writerow(row)

if __name__ == "__main__":
    main()

