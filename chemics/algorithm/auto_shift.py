"""
Tests the automatically shifting algorithm which matches the SMPS and CCNC data
Version 2.0
"""
import logging
import numpy as np
import scipy.signal
import warnings

import constants as const
import helper_functions as hf

# Set logger for this module
logger = logging.getLogger("controller")


def get_auto_shift(smps_count, ccnc_count):
    """
    Determines shift values of CCNC and SMPS files and prints the results to the console

    # REVIEW Documentation

    :param ndarray smps_count:
    :param ndarray ccnc_count:
    """
    # Initalize weight values
    high_smps_weight = const.HIGH_SMPS_WEIGHT
    high_ccnc_weight = const.HIGH_CCNC_WEIGHT

    # RESEARCH best way?
    smooth_smps_count = hf.smooth(smps_count, window_length=7, polyorder=2)

    smooth_ccnc_count = hf.smooth(ccnc_count, window_length=7, polyorder=2)

    # Get peak information
    # RESEARCH better peak method?
    smps_peak_index, smps_peak_heights = scipy.signal.find_peaks(smooth_smps_count,
                                                                 height=0, distance=20)
    smps_peak_heights = smps_peak_heights.get("peak_heights", "")
    ccnc_peak_index, ccnc_peak_heights = scipy.signal.find_peaks(smooth_ccnc_count,
                                                                 height=0, distance=20)
    ccnc_peak_heights = ccnc_peak_heights.get("peak_heights", "")

    # Check there are at least two peaks in both datasets.
    if len(smps_peak_index) < 2 or len(ccnc_peak_index) < 2:
        return 0

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
        except RuntimeWarning as e:
            # Catch divide by zero errors
            if len(total_area) == 0:
                total_area.append(999999999999)
            else:
                logger.error(e, exc_info=True)
                total_area.append(total_area[-1])

    if len(total_area) == 0:
        return 0
    else:
        proposed_shift = ccnc_first_peak - smps_first_peak - np.argmin(total_area)
        return proposed_shift
