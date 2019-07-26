"""
Tests the automatically shifting algorithm which matches the SMPS and CCNC data
Version 2.0
"""
import numpy as np
import pandas as pd
import scipy.signal
import warnings


def process_autoshift(smps_counts, ccnc_counts, scan_up_time, index=None, debug=None):
    """
    Determines shift values of CCNC and SMPS files and prints the results to the console

    :param ndarray smps_counts:
    :param ndarray ccnc_counts:
    :param int scan_up_time:
    :param int|None index: The specific scan to look at
    :param dict|None debug: Dictioary of what things to print to console
    """
    # Initalize variables
    calculated_shifts = pd.DataFrame(columns=["index", "shift", "status"])
    if debug is None:
        debug = {"data": False, "peaks": False, "iter_details": False, "plot": False}
    if "data" not in debug:
        debug["data"] = False
    if "peaks" not in debug:
        debug["peaks"] = False
    if "iter_details" not in debug:
        debug["iter_details"] = False
    if "plot" not in debug:
        debug["plot"] = False

    # Pretest parameters
    if len(smps_counts) != len(ccnc_counts):
        print("Arrays are not the same length S: %d  C: %d" % (len(smps_counts), len(ccnc_counts)))
        quit()

    # Print debug information
    if debug["data"]:
        print("===SMPS===")
        print(smps_counts)
        print("===CCNC===")
        print(ccnc_counts)

    # print("\n======== Manual By Area between the curves ========\n")

    # Smooth the curves some
    # RESEARCH best way?
    all_pro3_ccnc_counts = []
    for i in range(len(smps_counts)):
        with warnings.catch_warnings():
            warnings.simplefilter(action="ignore", category=FutureWarning)
            all_pro3_ccnc_counts.append(scipy.signal.savgol_filter(ccnc_counts[i], 7, 2))

    all_pro3_smps_counts = []
    for i in range(len(smps_counts)):
        with warnings.catch_warnings():
            warnings.simplefilter(action="ignore", category=FutureWarning)
            all_pro3_smps_counts.append(scipy.signal.savgol_filter(smps_counts[i], 7, 2))

    def calculate_shift(curr_scan):
        """
        # REVIEW Documentation

        :param curr_scan:
        :type curr_scan:
        :return:
        :rtype:
        """

        # Get peak information
        # smps_peak_index, smps_peak_heights = scipy.signal.find_peaks(all_pro3_smps_counts[curr_scan],
        #                                                              height=0, distance=20)
        # smps_peak_heights = smps_peak_heights.get("peak_heights", "")
        # ccnc_peak_index, ccnc_peak_heights = scipy.signal.find_peaks(all_pro3_ccnc_counts[curr_scan],
        #                                                              height=0, distance=20)
        # ccnc_peak_heights = ccnc_peak_heights.get("peak_heights", "")

        smps_next_peak = np.argmax(all_pro3_smps_counts[scan_index][scan_up_time:]) + scan_up_time
        ccnc_next_peak = np.argmax(all_pro3_ccnc_counts[scan_index][scan_up_time:]) + scan_up_time

        if debug["peaks"]:
            print("===Peak Details===")
            print([smps_next_peak, all_pro3_smps_counts[scan_index][smps_next_peak]])
            print([ccnc_next_peak, all_pro3_ccnc_counts[scan_index][ccnc_next_peak]])

        # noinspection PyUnusedLocal
        return curr_scan, ccnc_next_peak - smps_next_peak, None

    # Calculate the shifts
    if index is not None:
        print("  Scanning #%d" % index)
        calculated_shifts = calculated_shifts.append(
            pd.DataFrame([calculate_shift(index)], columns=["index", "shift", "status"]))
    else:
        for scan_index in range(len(all_pro3_smps_counts)):
            calculated_shifts = calculated_shifts.append(
                pd.DataFrame([calculate_shift(scan_index)], columns=["index", "shift", "status"]))

    calculated_shifts = calculated_shifts.set_index("index")
    return calculated_shifts
