import datetime as dt
import helper_functions as hf
import numpy as np
import os
import re
import scipy.signal
import warnings


def parse_files(f):
    ccnc_csv_files = []  # Should be hourly files  # TODO Add error handling
    smps_txt_files = []  # Should be one file  # TODO Add error handling
    # Acquire the smps and ccnc files from the input files
    for a_file in f:
        if a_file.lower().endswith('.csv'):
            ccnc_csv_files.append(a_file)
        elif a_file.lower().endswith('.txt'):
            smps_txt_files.append(a_file)
    # Stringify each item in the list
    ccnc_csv_files = [str(x) for x in ccnc_csv_files]
    smps_txt_files = [str(x) for x in smps_txt_files]
    # Turn smps to a str instead of a list - Assumes only one file
    smps_txt_files = smps_txt_files[0]
    exp_date, ccnc_dat = hf.process_csv_files(ccnc_csv_files)
    smps_dat = hf.process_tab_sep_files(smps_txt_files)
    return exp_date, ccnc_dat, smps_dat


def get_smps_counts(smps_dat, c2c):
    # Determine where data is in file
    scan_start_times = smps_dat[0]
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
    scan_start_times = smps_dat[0]
    raw_ccnc_cts = [[] for j in range(len(scan_start_times))]
    # Get the first position of CCNC count in the ccnc file
    curr_scan = 0
    curr_scan_start_time = dt.datetime.strptime(scan_start_times[curr_scan], "%H:%M:%S")
    # the index at which ccnc data is in sync with smps data
    ccnc_index = 0
    while True:
        curr_ccnc_time = dt.datetime.strptime(ccnc_dat[ccnc_index][0], "%H:%M:%S")
        if curr_ccnc_time > curr_scan_start_time:
            curr_scan += 1
            curr_scan_start_time = dt.datetime.strptime(scan_start_times[curr_scan], "%H:%M:%S")
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
            raw_ccnc_cts[curr_scan].append(ccnc_count)

        curr_scan += 1
        # if we run of out scans to compare with ccnc data, stop scanning ccnc data
        if curr_scan >= len(scan_start_times):
            break
        # find the next ccnc_index
        # we got to based on the start time, since the duration values are always off
        next_scan_start_time = dt.datetime.strptime(scan_start_times[curr_scan], "%H:%M:%S")
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


# Set filesnames for this dir
filenames = os.listdir(directory)
directory = os.path.abspath(directory)
for i in range(len(filenames)):
    filenames[i] = os.path.join(directory, filenames[i])

filenames.sort()

experiment_date, ccnc_data, smps_data = parse_files(filenames)
all_raw_smps_counts = get_smps_counts(smps_data, c2c=1.25)
all_raw_ccnc_counts = get_ccnc_counts(ccnc_data, smps_data)

print(all_raw_smps_counts)
print("======")
print(all_raw_ccnc_counts)

if len(all_raw_smps_counts) != len(all_raw_ccnc_counts):
    print("Arrays are not the same length S: %d  C: %d" % (len(all_raw_smps_counts), len(all_raw_ccnc_counts)))
    quit()

all_pro1_smps_counts = np.asarray(all_raw_smps_counts).astype(float)
all_pro1_ccnc_counts = np.asarray(all_raw_ccnc_counts).astype(float)

print("\n======== Manual By Area between the curves ========\n")

# Smooth the curves some
all_pro3_ccnc_counts = []
for i in range(len(all_pro1_smps_counts)):
    with warnings.catch_warnings():
        warnings.simplefilter(action="ignore", category=FutureWarning)
        all_pro3_ccnc_counts.append(scipy.signal.savgol_filter(all_pro1_ccnc_counts[i], 7, 2))

all_pro3_smps_counts = []
for i in range(len(all_pro1_smps_counts)):
    with warnings.catch_warnings():
        warnings.simplefilter(action="ignore", category=FutureWarning)
        all_pro3_smps_counts.append(scipy.signal.savgol_filter(all_pro1_smps_counts[i], 7, 2))

# noinspection PyPep8
for i in range(len(all_pro3_smps_counts)):
    # if i != 11:
    #     continue
    # print("  Scanning #%d" % i)

    # Get peak information
    smps_peak_index, smps_peak_heights = scipy.signal.find_peaks(all_pro3_smps_counts[i], height=0, distance=20)
    smps_peak_heights = smps_peak_heights.get("peak_heights", "")
    ccnc_peak_index, ccnc_peak_heights = scipy.signal.find_peaks(all_pro3_ccnc_counts[i], height=0, distance=20)
    ccnc_peak_heights = ccnc_peak_heights.get("peak_heights", "")

    # print(smps_peak_index, smps_peak_heights)
    # print(ccnc_peak_index, ccnc_peak_heights)

    # Check there are at least two peaks in both datasets.
    if len(smps_peak_index) < 2 or len(ccnc_peak_index) < 2:
        print("  Not enough peak data in scan %d" % i)
        continue

    # determine peak indcies.
    if (len(smps_peak_index) - 1) > np.argmax(smps_peak_heights):
        smps_first_peak = smps_peak_index[np.argmax(smps_peak_heights)]
        smps_next_peak = smps_peak_index[np.argmax(smps_peak_heights) + 1]
    else:
        smps_first_peak = smps_peak_index[np.argmax(smps_peak_heights) - 1]
        smps_next_peak = smps_peak_index[np.argmax(smps_peak_heights)]

    if (len(ccnc_peak_index) - 1) > np.argmax(ccnc_peak_heights):
        ccnc_first_peak = ccnc_peak_index[np.argmax(ccnc_peak_heights)]
        ccnc_next_peak = ccnc_peak_index[np.argmax(ccnc_peak_heights) + 1]
    else:
        ccnc_first_peak = ccnc_peak_index[np.argmax(ccnc_peak_heights) - 1]
        ccnc_next_peak = ccnc_peak_index[np.argmax(ccnc_peak_heights)]

    # print("    %d: SMPS: %d %d   CCNC: %d %d" % (i, smps_first_peak, smps_next_peak, ccnc_first_peak, ccnc_next_peak))

    # Get length of data based on peaks
    data_length = ccnc_next_peak - ccnc_first_peak
    max_iter = ccnc_first_peak - smps_first_peak

    # If the length of smps data is close to the length of ccnc data, add a few more iterations
    smpsccnc_peak_len_diff = max(0, 5 - abs((ccnc_next_peak - ccnc_first_peak) - (smps_next_peak - smps_first_peak)))
    max_iter += smpsccnc_peak_len_diff

    # print("    Data Length: %d\n    Max iterations: %d" % (ccnc_mid_length, max_iter))

    # plt.plot(all_pro3_smps_counts[i])
    # plt.plot(all_pro3_ccnc_counts[i])
    # plt.show()

    total_area = []
    # Repeat for the number of iterations or until the smps end index > smps_next_peak
    for j in range(max_iter):
        # Determine Ranges
        s_s = j + smps_first_peak - smpsccnc_peak_len_diff
        s_e = j + smps_first_peak + data_length - smpsccnc_peak_len_diff
        c_s = ccnc_first_peak
        c_e = ccnc_first_peak + data_length

        # If shoved off the end, end calculations
        if s_e > smps_next_peak:
            break

        # get middle data for test [Loop needs to start before here]
        smps_middle_data = all_pro3_smps_counts[i][s_s:s_e]
        ccnc_middle_data = all_pro3_ccnc_counts[i][c_s:c_e]

        # plt.plot(smps_middle_data)
        # plt.plot(ccnc_middle_data)
        # plt.show()

        # Get area between the curves
        s_subt_c = smps_middle_data - ccnc_middle_data
        # -- Find where lines cross, if any
        data_crosses = np.sign(s_subt_c[:-1] * s_subt_c[1:])
        # -- Setup formulas for where
        np.seterr(all='warn')
        warnings.filterwarnings('error')
        try:
            x_isects = np.arange(0, (data_length - 1)) - (s_subt_c[:-1] / (s_subt_c[1:] - s_subt_c[:-1]))
            dx_isects = - np.ones(data_length - 1) / (s_subt_c[1:] - s_subt_c[:-1]) * s_subt_c[:-1]
            # -- Trapezoidal Rule
            areas_no_isects = (0.5 * abs(s_subt_c[:-1] + s_subt_c[1:]))
            areas_of_isects = (0.5 * dx_isects * abs(s_subt_c[:-1]))
            areas_of_isects += (0.5 * (np.ones(data_length - 1)) - dx_isects) * abs(s_subt_c[1:])
            total_area.append(np.sum(np.where(data_crosses > 0, areas_no_isects, areas_of_isects)))
        except RuntimeWarning as e:
            # Catch divide by zero errors
            if len(total_area) == 0:
                total_area.append(999999999999)
            else:
                total_area.append(total_area[-1])

    proposed_shift = 0
    if len(total_area) == 0:
        print("    %d: Proposed shift is unknown" % i)
    else:
        proposed_shift = max_iter - np.argmin(total_area)
        print("    %d: Proposed shift of %d" % (i, proposed_shift))
