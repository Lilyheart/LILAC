"""
Tests the automatically shifting algorithm which matches the SMPS and CCNC data
Version 2.0
"""
import numpy as np
import pandas as pd
import scipy.signal
import warnings


def process_autoshift(smps_counts, ccnc_counts, scan_up_time, index=None, debug=None, weights=None):
    """
    Determines shift values of CCNC and SMPS files and prints the results to the console

    :param ndarray smps_counts:
    :param ndarray ccnc_counts:
    :param int|None index: The specific scan to look at
    :param dict|None debug: Dictioary of what things to print to console
    :param list[float]|None weights:
    """
    # Initalize variables
    calculated_shifts = pd.DataFrame(columns=["index", "shift", "status"])
    if weights is None:
        high_smps_weight = 1
        high_ccnc_weight = 2.2
    else:
        if len(weights) == 2:
            high_smps_weight = weights[0]
            high_ccnc_weight = weights[1]
        else:
            raise ValueError("weights should have length of 2 but was instead %d" % len(weights))
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

        smps_first_peak = np.argmax(all_pro3_smps_counts[scan_index][0:scan_up_time])
        smps_next_peak = np.argmax(all_pro3_smps_counts[scan_index][scan_up_time:]) + scan_up_time
        ccnc_first_peak = np.argmax(all_pro3_ccnc_counts[scan_index][0:scan_up_time])
        ccnc_next_peak = np.argmax(all_pro3_ccnc_counts[scan_index][scan_up_time:]) + scan_up_time

        if debug["peaks"]:
            print("===Peak Details===")
            print([smps_first_peak, smps_next_peak],
                  [all_pro3_smps_counts[scan_index][smps_first_peak],
                   all_pro3_smps_counts[scan_index][smps_next_peak]])
            print([ccnc_first_peak, ccnc_next_peak],
                  [all_pro3_ccnc_counts[scan_index][ccnc_first_peak],
                   all_pro3_ccnc_counts[scan_index][ccnc_next_peak]])

        # shift the SMPS first peak back by whatever is larger, 3% of the SMPS data size or 3 scans
        smps_first_peak -= max(3, int(len(all_pro3_smps_counts[curr_scan]) * 0.03))
        # shift the SMPS next peak back by whatever is larger, 3% of the SMPS data size or 3 scans
        smps_next_peak += max(3, int(len(all_pro3_smps_counts[curr_scan]) * 0.03))

        # Get length of data based on peaks
        data_length = ccnc_next_peak - ccnc_first_peak
        max_iter = (smps_next_peak - smps_first_peak) - (ccnc_next_peak - ccnc_first_peak) + 1

        if debug["peaks"]:
            smpsprint = "SMPS: "+str(smps_first_peak)+" "+str(smps_next_peak)
            smpsprint += " ("+str(smps_next_peak-smps_first_peak)+")"
            ccncprint = "CCNC: "+str(ccnc_first_peak)+" "+str(ccnc_next_peak)
            ccncprint += " ("+str(ccnc_next_peak-ccnc_first_peak)+")"
            print("    %d: %s   %s (Max: %d)" %
                  (curr_scan, smpsprint, ccncprint, max_iter))

        # If the length of smps data is close to the length of ccnc data, add a few more iterations
        smpsccnc_peak_len_diff = max(0,
                                     4 - abs((ccnc_next_peak - ccnc_first_peak) - (smps_next_peak - smps_first_peak)))
        max_iter += smpsccnc_peak_len_diff

        if debug["iter_details"]:
            print("    Data Length: %d\n    Max iterations: %d" % (data_length, max_iter))

        if debug["peaks"] and index is not None:
            print("===SMPS===")
            print(all_pro3_smps_counts[curr_scan][smps_first_peak:smps_next_peak])
            print("===CCNC===")
            print(all_pro3_ccnc_counts[curr_scan][ccnc_first_peak:ccnc_next_peak])

        if debug["plot"] and index is not None:
            import matplotlib.pyplot as plt
            plt.plot(all_pro3_smps_counts[curr_scan])
            plt.plot(all_pro3_ccnc_counts[curr_scan])
            plt.show()

        total_area = []
        # Repeat for the number of iterations or until the smps end index > smps_next_peak
        for iteration in range(max_iter):
            # Determine Ranges
            s_s = iteration + smps_first_peak - smpsccnc_peak_len_diff
            s_e = iteration + smps_first_peak + data_length - smpsccnc_peak_len_diff
            c_s = ccnc_first_peak
            c_e = ccnc_first_peak + data_length

            # get middle data for test [Loop needs to start before here]
            smps_middle_data = all_pro3_smps_counts[curr_scan][s_s:s_e]
            ccnc_middle_data = all_pro3_ccnc_counts[curr_scan][c_s:c_e]

            if debug["plot"] and index is not None:
                import matplotlib.pyplot as plt
                plt.plot(smps_middle_data)
                plt.plot(ccnc_middle_data)
                plt.show()

            # Get area between the curves
            np.seterr(all='warn')
            warnings.filterwarnings('error')
            try:
                # -- Set weights
                smps_weight = np.where(smps_middle_data[:-1] > ccnc_middle_data[:-1], high_smps_weight, 1)
                ccnc_weight = np.where(ccnc_middle_data[:-1] > smps_middle_data[:-1], high_ccnc_weight, 1)
                # -- create array to represent x axis
                x = np.arange(len(smps_middle_data))
                # -- create array of differences
                s_subt_c = smps_middle_data - ccnc_middle_data
                # -- Find if the lines cross
                data_crosses = np.sign(s_subt_c[:-1] * s_subt_c[1:])
                # -- Slopes and individual intersects
                smps_slope = smps_middle_data[1:] - smps_middle_data[:-1]
                ccnc_slope = ccnc_middle_data[1:] - ccnc_middle_data[:-1]
                smps_y_isects = smps_middle_data[:-1] - (smps_slope * x[:-1])
                ccnc_y_isects = ccnc_middle_data[:-1] - (ccnc_slope * x[:-1])
                # -- Find the x coordinate where the lines cross (the decimal places only)
                x_line_isects = (ccnc_y_isects - smps_y_isects) / (smps_slope - ccnc_slope)
                x_line_isects = np.where(data_crosses > 0, 0., x_line_isects)
                x_line_isects = np.where(data_crosses > 0, 0., x_line_isects - x[:-1])
                # -- Areas via trapezoidal rule
                areas_no_isects = 0.5 * abs(s_subt_c[:-1] + s_subt_c[1:]) * ccnc_weight * smps_weight
                areas_of_isects_l = 0.5 * abs(s_subt_c[:-1]) * x_line_isects * ccnc_weight * smps_weight
                areas_of_isects_r = 0.5 * abs(s_subt_c[1:]) * (1 - x_line_isects) * ccnc_weight * smps_weight
                areas_of_isects = areas_of_isects_l + areas_of_isects_r
                total_area.append(np.sum(np.where(data_crosses > 0, areas_no_isects, areas_of_isects)))
            except RuntimeWarning:
                # Catch divide by zero errors
                if len(total_area) == 0:
                    total_area.append(999999999999)
                else:
                    total_area.append(total_area[-1])

        # noinspection PyUnusedLocal
        proposed_shift = 0
        if len(total_area) == 0:
            if max_iter <= 0:
                return curr_scan, 0, "Too much SMPS data/Not enough CCNC, unknown"
            else:
                return curr_scan, 0, "Proposed shift, unknown"
        else:
            proposed_shift = ccnc_first_peak - smps_first_peak - np.argmin(total_area)
            if proposed_shift < 0:
                return curr_scan, 0, "Proposed shift, unknown"
            else:
                return curr_scan, proposed_shift, None
    # END OF calculate_shift function

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
