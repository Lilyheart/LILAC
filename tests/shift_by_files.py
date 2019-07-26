"""
Run the shift algo by supplying a directory name
"""
import datetime as dt
import helper_functions as hf
import logging
import logging_config
import numpy as np
import os
import re
import shift_algo
from algorithm import auto_shift

# Set logger for this module
logging_config.configure_logger_env()
logger = logging.getLogger("controller")


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
    raw_smps_cts = [[] for k in range(len(scan_start_times))]

    start_line_index = 0
    end_line_index = len(smps_dat) - 1
    # Find where second data section begins
    for m in range(3, len(smps_dat)):
        # Find beginning of middle text section
        if re.search('[a-zA-Z]', smps_dat[m][0]):
            for k in range(m + 1, len(smps_dat)):
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
        for k in range(0, len(scan_start_times)):
            count = int(smps_dat[curr_line_index][k * 2 + 2])
            count_by_scans[k] += count
        if hf.are_floats_equal(curr_time, target_time) or curr_line_index == end_line_index:
            target_time += 1
            for k in range(0, len(scan_start_times)):
                # self.scans[j].add_to_raw_smps_counts(count_by_scans[j])
                raw_smps_cts[k].append(count_by_scans[k] * c2c)
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
    :rtype: list[list[float]]
    """
    scan_start_times = smps_dat[0]
    # noinspection PyUnusedLocal
    raw_ccnc_cts = [[] for k in range(len(scan_start_times))]
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
        for k in range(duration + duration // 4):  # RESEARCH not evenly div by 4 - what's this?
            curr_ccnc_index = ccnc_index + k
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


if __name__ == '__main__':
    # Get files in directory
    # directory = 'C:/Users/purpl/repos/TestData/O3 (150), VOC (150) TRIAL 6/Analysis'
    directory = 'C:/Users/purpl/repos/TestData/Penn State 2019/Caryophyllene (150), Ozone (200), dry/ANALYSIS'

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
    all_raw_smps_counts = get_smps_counts(smps_data, c2c=1.2)
    all_raw_ccnc_counts = get_ccnc_counts(ccnc_data, smps_data)
    all_raw_ccnc_counts = [[float(j) for j in i] for i in all_raw_ccnc_counts]

    all_pro1_smps_counts = np.asarray(all_raw_smps_counts)
    all_pro1_ccnc_counts = np.asarray(all_raw_ccnc_counts)

    scans = []
    for i in range(len(all_raw_ccnc_counts)):
        smps = np.asarray(all_pro1_smps_counts[i]).astype(float)
        ccnc = np.asarray(all_pro1_ccnc_counts[i]).astype(float)
        scans.append([smps, ccnc])

    scan_up_time = 0
    scan_down_time = 0

    for i in range(len(smps_data)):
        if ''.join(smps_data[i][0].split()).lower() == "scanuptime(s)":
            scan_up_time = int(smps_data[i][1])
            scan_down_time = int(smps_data[i + 1][1])  # this is the retrace time
            break

    debug = {"data": False, "peaks": False, "iter_details": False, "plot": False}
    scan_index = None

    result1 = shift_algo.process_autoshift(all_pro1_smps_counts, all_pro1_ccnc_counts, index=scan_index, debug=debug)

    result2 = []
    if scan_index is None:
        shift_factors = []
        for i in range(len(scans)):
            a_scan = scans[i]
            smps = a_scan[0]
            ccnc = a_scan[1]
            shift_factors.append(auto_shift.get_auto_shift(smps, ccnc, scan_up_time, 0)[0])
        median_shift = sorted(shift_factors)[(len(shift_factors) + 1) // 2]

        for i in range(len(scans)):
            a_scan = scans[i]
            smps = a_scan[0]
            ccnc = a_scan[1]
            shift_factor, err_msg = auto_shift.get_auto_shift(smps, ccnc, scan_up_time, median_shift)
            result2.append([shift_factor, err_msg])
            for index, value in enumerate(err_msg):
                if index == 0:
                    logger.warn("get_auto_shift error on scan: " + str(i))
                logger.warn("    (%d) %s" % (index, value))
    else:
        # noinspection PyTypeChecker
        smps = scans[scan_index][0]
        # noinspection PyTypeChecker
        ccnc = scans[scan_index][1]
        shift_factor, err_msg = auto_shift.get_auto_shift(smps, ccnc, scan_up_time, 0)
        result2.append([shift_factor, err_msg])
        for index, value in enumerate(err_msg):
            if index == 0:
                logger.warn("get_auto_shift error on scan: " + str(scan_index))
            logger.warn("    (%d) %s" % (index, value))

    for i in range(len(result2)):
        if scan_index is None:
            printstring = "Index: %2d" % i
        else:
            printstring = "Index: %2d" % scan_index
        if result1.iloc[i][0] == result2[i][0]:
            printstring += "  Match:    %3d" % result1.iloc[i][0]
        else:
            printstring += "  O: %3d N: %3d" % (result1.iloc[i][0], result2[i][0])
        print(printstring)
