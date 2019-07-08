"""
Run the shift algo by supplying a directory name
"""
import datetime as dt
import helper_functions as hf
import numpy as np
import os
import re
import shift_algo


def parse_files(f):
    """
    Controls the data parsing process

    :param list[str] f: A list of all the filenames to process
    :return: The experiment date, a list containing the CCNC data, a list containing the SMPS data
    :rtype: (str, list[list[str]], list[list[str]])
    """
    ccnc_csv_files = []  # Should be hourly files  # TODO Add error handling
    smps_txt_files = []  # Should be one file  # TODO Add error handling
    # Acquire the smps and ccnc files from the input files
    for a_file in f:
        if a_file.lower().endswith('.csv'):
            ccnc_csv_files.append(a_file)
        elif a_file.lower().endswith('.txt'):
            smps_txt_files.append(a_file)
    # Stringify each item in the list
    ccnc_csv_files = [str(val) for val in ccnc_csv_files]
    smps_txt_files = [str(val) for val in smps_txt_files]
    # Turn smps to a str instead of a list - Assumes only one file
    smps_txt_files = smps_txt_files[0]
    exp_date, ccnc_dat = hf.process_csv_files(ccnc_csv_files)
    smps_dat = hf.process_tab_sep_files(smps_txt_files)
    return exp_date, ccnc_dat, smps_dat


def get_smps_counts(smps_dat, c2c):
    """
    Finds the basic SMPS counts data

    :param list[list[str]] smps_dat: The raw SMPS data
    :param float c2c: The flow rate conversion factor
    :return: The raw SMPS counts
    :rtype: list[float]
    """
    # Determine where data is in file
    scan_start_times = smps_dat[0]
    # create an empy list of the length needed.
    # noinspection PyUnusedLocal
    raw_smps_cts = [[] for j in range(len(scan_start_times))]

    start_line_index = 0
    end_line_index = len(smps_dat) - 1
    # Find where second data section begins
    for j in range(3, len(smps_dat)):
        # Find beginning of middle text section
        if re.search('[a-zA-Z]', smps_dat[j][0]):
            for k in range(j + 1, len(smps_dat)):
                # Find end of middle text section
                if not re.search('[a-zA-Z]', smps_dat[k][0]):
                    start_line_index = k
                    break
            break

    target_time = 1
    curr_line_index = start_line_index
    count_by_scans = [0] * len(scan_start_times)
    # Find values and update scans
    while True:
        curr_time = float(smps_dat[curr_line_index][0])
        for j in range(0, len(scan_start_times)):
            count = int(smps_dat[curr_line_index][j * 2 + 2])
            count_by_scans[j] += count
        if hf.are_floats_equal(curr_time, target_time) or curr_line_index == end_line_index:
            target_time += 1
            for j in range(0, len(scan_start_times)):
                # self.scans[j].add_to_raw_smps_counts(count_by_scans[j])
                raw_smps_cts[j].append(count_by_scans[j] * c2c)
            count_by_scans = [0] * len(scan_start_times)
        curr_line_index += 1
        if curr_line_index >= end_line_index:
            break
    return raw_smps_cts


def get_ccnc_counts(ccnc_dat, smps_dat):
    """
    Finds the basic CCNC counts data

    :param list[list[str]] ccnc_dat: The raw CCNC data
    :param list[list[str]] smps_dat: The raw SMPS data
    :return: The raw CCNC counts
    :rtype: list[float]
    """
    scan_start_times = smps_dat[0]
    # noinspection PyUnusedLocal
    raw_ccnc_cts = [[] for j in range(len(scan_start_times))]
    # Get the first position of CCNC count in the ccnc file
    scan_number = 0
    curr_scan_start_time = dt.datetime.strptime(scan_start_times[scan_number], "%H:%M:%S")
    # the index at which ccnc data is in sync with smps data
    ccnc_index = 0
    while True:
        curr_ccnc_time = dt.datetime.strptime(ccnc_dat[ccnc_index][0], "%H:%M:%S")
        if curr_ccnc_time > curr_scan_start_time:
            scan_number += 1
            curr_scan_start_time = dt.datetime.strptime(scan_start_times[scan_number], "%H:%M:%S")
        elif curr_ccnc_time < curr_scan_start_time:
            ccnc_index += 1
        else:  # the current ccnc_index is where ccnc starts being in sync with smps
            break
    finish_scanning_ccnc_dat = False
    while not finish_scanning_ccnc_dat:
        finish_scanning_ccnc_dat = False
        duration = 135
        # we do one thing at a time
        for j in range(duration + duration // 4):  # RESEARCH not evenly div by 4 - what's this?
            curr_ccnc_index = ccnc_index + j
            # if we reach out of ccnc data bound
            if curr_ccnc_index >= len(ccnc_dat):
                # stop scanning ccnc data
                finish_scanning_ccnc_dat = True
                break
            # collect a bunch of data from ccnc file
            ccnc_count = ccnc_dat[curr_ccnc_index][-3]
            raw_ccnc_cts[scan_number].append(ccnc_count)

        scan_number += 1
        # if we run of out scans to compare with ccnc data, stop scanning ccnc data
        if scan_number >= len(scan_start_times):
            break
        # find the next ccnc_index
        # we got to based on the start time, since the duration values are always off
        next_scan_start_time = dt.datetime.strptime(scan_start_times[scan_number], "%H:%M:%S")
        while True:
            curr_ccnc_time = dt.datetime.strptime(ccnc_dat[ccnc_index][0], "%H:%M:%S")
            if curr_ccnc_time < next_scan_start_time:
                ccnc_index += 1
                # if we reach out of ccnc data bound
                if ccnc_index >= len(ccnc_dat):
                    # stop scanning ccnc data
                    finish_scanning_ccnc_dat = True
                    break
            else:
                break
    return raw_ccnc_cts


# Get files in directory
directory = '/home/lilyheart/Dropbox/Classes/19.2.Chemics/TestData/O3 (150), VOC (150) TRIAL 6/Analysis'

# Mark the algo index and pref index
# algo_index = [0, 0, 0, 12, 12, 0, 0, 0, 0, 0, 0, 0, 0, 12, 12, 0, 0, 0, 0, 13, 13, 0, 12, 12, 0, 12, 0, 0, 0,
#               0, 0, 0, 12, 12, 12, 12, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 12, 12, 0, 0, 0, 0, 0, 0, 0, 0,
#               0, 0, 0, 0, 0, 0, 0, 0, 0, 12, 0]
# pref_index = [0, 0, 0, 13, 13, 0, 0, 0, 0, 0, 0, 0, 0, 13, 13, 0, 0, 0, 0, 14, 14, 0, 13, 13, 0, 13, 0, 0, 0,
#               0, 0, 0, 13, 13, 13, 13, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 13, 13, 0, 0, 0, 0, 0, 0, 0, 0,
#               0, 0, 0, 0, 0, 0, 0, 0, 0, 13, 0]

# Set filesnames for this dir
filenames = os.listdir(directory)
directory = os.path.abspath(directory)
for i in range(len(filenames)):
    filenames[i] = os.path.join(directory, filenames[i])

filenames.sort()

experiment_date, ccnc_data, smps_data = parse_files(filenames)
all_raw_smps_counts = get_smps_counts(smps_data, c2c=1.25)
all_raw_ccnc_counts = get_ccnc_counts(ccnc_data, smps_data)

all_pro1_smps_counts = np.asarray(all_raw_smps_counts).astype(float)
all_pro1_ccnc_counts = np.asarray(all_raw_ccnc_counts).astype(float)

debug = {"data": False, "peaks": False, "iter_details": False, "plot": False}
index = None

shift_algo.process_autoshift(all_pro1_smps_counts, all_pro1_ccnc_counts, index=index, debug=debug)
