"""
Tests the automatically shifting algorithm which matches the SMPS and CCNC data
Version 2.0
"""
import logging
import numpy as np

import constants as const
import helper_functions as hf

# Set logger for this module
logger = logging.getLogger("controller")


def get_auto_shift(smps_count, ccnc_count, scan_up_time, median_shift):
    """
    Determines shift values of CCNC and SMPS files and prints the results to the console

    # REVIEW Documentation - Add return information

    :param ndarray smps_count:
    :param ndarray ccnc_count:
    :param int scan_up_time:
    :param int median_shift:
    """
    if sum(smps_count) == 0 or sum(ccnc_count) == 0:
        return 0, ["No SMPS and/or CCNC data"]
    if len(smps_count) > len(ccnc_count):
        return 0, ["SMPS data longer than CCNC data"]
    # Initalize weight values
    high_smps_weight = const.HIGH_SMPS_WEIGHT
    high_ccnc_weight = const.HIGH_CCNC_WEIGHT
    error_messages = []

    # RESEARCH best way?
    smooth_smps_count = hf.smooth(smps_count, window_length=7, polyorder=2)

    smooth_ccnc_count = hf.smooth(ccnc_count, window_length=7, polyorder=2)

    smps_first_peak = np.argmax(smooth_smps_count[0:scan_up_time])
    smps_next_peak = np.argmax(smooth_smps_count[scan_up_time:]) + scan_up_time
    ccnc_first_peak = np.argmax(smooth_ccnc_count[median_shift:(median_shift + scan_up_time)]) + median_shift
    ccnc_next_peak = np.argmax(smooth_ccnc_count[(median_shift + scan_up_time):]) + scan_up_time + median_shift

    # Increase SMPS range to ensure enough values are captured.
    # RESEARCH magic numbers
    # shift the SMPS first peak back by whatever is larger, 3% of the SMPS data size or 3 scans
    smps_first_peak -= max(3, int(len(smooth_smps_count) * 0.03))
    # shift the SMPS next peak back by whatever is larger, 3% of the SMPS data size or 3 scans
    smps_next_peak += max(3, int(len(smooth_smps_count) * 0.03))

    # Get length of data based on peaks
    data_length = ccnc_next_peak - ccnc_first_peak
    max_iter = (smps_next_peak - smps_first_peak) - (ccnc_next_peak - ccnc_first_peak) + 1

    # If the length of smps data is close to the length of ccnc data, add a few more iterations
    # RESEARCH magic numbers
    smpsccnc_peak_len_diff = max(0,
                                 4 - abs((ccnc_next_peak - ccnc_first_peak) - (smps_next_peak - smps_first_peak)))
    max_iter += smpsccnc_peak_len_diff

    total_area = []
    # Repeat for the number of iterations or until the smps end index > smps_next_peak
    for iteration in range(max_iter):
        # Determine Ranges
        s_s = iteration + smps_first_peak - smpsccnc_peak_len_diff
        s_e = iteration + smps_first_peak + data_length - smpsccnc_peak_len_diff
        c_s = ccnc_first_peak
        c_e = ccnc_first_peak + data_length

        # get middle data for test [Loop needs to start before here]
        smps_middle_data = smooth_smps_count[s_s:s_e]
        ccnc_middle_data = smooth_ccnc_count[c_s:c_e]

        # Get area between the curves
        with np.errstate(all='raise'):
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
            except Exception as e:
                # Catch divide by zero errors
                error_message = "Shift issue on iteration " + str(iteration)
                error_message += " (" + str(e) + ")"
                if len(total_area) == 0:
                    total_area.append(999999999999)
                    error_message += " [set to 9's]"
                else:
                    total_area.append(total_area[-1])
                    error_message += " [set to prior value]"
                error_messages.append(error_message)

    if len(total_area) == 0:
        return 0, error_messages
    else:
        proposed_shift = ccnc_first_peak - smps_first_peak - np.argmin(total_area)
        return proposed_shift, error_messages
