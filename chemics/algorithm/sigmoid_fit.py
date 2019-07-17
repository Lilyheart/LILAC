"""
# REVIEW Documentation
"""
import numpy as np
import pandas as pd
import scipy.optimize
import scipy.signal
import sys

import constants as const
import helper_functions as hf


def find_derv_peaks(a_scan):
    """
    Creates or recreated a dataframe in the scan which contains just cleaned data.  The resulting dataframe is
    stored in the scan.

    Determines the locations of the peaks and their widths of the derivative of the ratio curve.

    Dataframe contains ["ave_smps_diameters", "log_ave_smps_diameters", "corrected_ccnc_counts",
     "corrected_smps_counts", "corr_cs_ratio"]

    :param Scan a_scan:
    """
    # TODO issues/64  Probably unneccessary after Dataframe switchover
    df = pd.DataFrame({"ave_smps_diameters": a_scan.ave_smps_diameters,
                       "log_ave_smps_diameters": np.log(a_scan.ave_smps_diameters),
                       "corrected_ccnc_counts": a_scan.corrected_ccnc_counts,
                       "corrected_smps_counts": a_scan.corrected_smps_counts,
                       "corr_cs_ratio":
                           np.array(a_scan.corrected_ccnc_counts) / np.array(a_scan.corrected_smps_counts)})

    # Eliminate ave_smps_diameters data that exceeds diameter range
    sel = (df.ave_smps_diameters >= const.SIGMOID_MIN_DIAMETER) & (df.ave_smps_diameters <= const.SIGMOID_MAX_DIAMETER)
    df = df.loc[sel].copy()

    # Resolve the true zero readings
    sel = (df.corrected_ccnc_counts < const.SIGMOID_ZERO_COUNT_THRESH) | \
          (df.corrected_smps_counts < const.SIGMOID_ZERO_COUNT_THRESH)
    df.loc[sel, "corr_cs_ratio"] = 0.0

    # Eliminate points outside of valid range
    sel = (df.corr_cs_ratio >= const.SIGMOID_MIN_VALID_RATIO) & (df.corr_cs_ratio <= const.SIGMOID_MAX_VALID_RATIO)
    df = df.loc[sel, :].copy().reset_index(drop=True)

    # Now, let's throw away any points that lie between zero ratios values. We will define a helper function
    # that takes a Series and a starting index. If the value strictly positive, then count how many values
    # after that are also positive. Do the same for negative.
    def get_run_length(vec, start_i):
        """ Simple helper function to count the run length of values starting at start_i"""
        if start_i >= vec.shape[0]:
            return 0

        is_positive = False
        if vec[start_i] > 0.0:
            is_positive = True

        # noinspection PyShadowingNames
        i = start_i + 1
        while i < vec.shape[0]:
            if is_positive and vec[i] > 0.0 or not is_positive and vec[i] <= 0:
                i += 1
            else:
                break
        return i - start_i

    # Gather the run length encoding for the runs...
    rle = []
    index = 0
    while index < df.shape[0]:
        val = df.corr_cs_ratio[index]
        rl = get_run_length(df.corr_cs_ratio, index)
        rle.append({"val": val, "index": index, "rl": rl})
        index += rl

    # Use the rle to eliminate bumps surrounded by zeros
    count = 0
    if len(rle) >= 3:
        start_index = 0

        # Special check for the first case being a noisy value
        if rle[0]["val"] > 0.0 >= rle[1]["val"] and rle[0]["rl"] <= rle[1]["rl"]:
            df.loc[rle[0]["index"]:(rle[0]["index"] + rle[0]["rl"]), "corr_cs_ratio"] = 0.0
            start_index = 1
            count += 1

        for index in range(start_index, len(rle) - 2):
            if rle[index]["val"] <= 0.0 < rle[index + 1]["val"] and rle[index + 2]["val"] <= 0.0 and \
                    rle[index]["rl"] >= rle[index + 1]["rl"] and rle[index + 2]["rl"] >= rle[index + 1]["rl"] and \
                    rle[index + 1]["rl"] <= 2:
                df.loc[rle[index + 1]["index"]:(rle[index + 1]["index"] + rle[index + 1]["rl"]), "corr_cs_ratio"] = 0.0
                count += 1

    del index, count, rle

    # Compute delta
    x = hf.smooth(df.corr_cs_ratio, window_length=5, polyorder=1)
    delta_corr_cs_ratio = np.subtract(x[1:], x[:-1])
    delta_logd = np.subtract(df.log_ave_smps_diameters[1:], df.log_ave_smps_diameters[:-1])
    delta = np.divide(delta_corr_cs_ratio, delta_logd)
    delta = hf.smooth(delta, window_length=15, polyorder=2)

    # Identify peaks in derivative
    pk_indices, pk_params = scipy.signal.find_peaks(delta,
                                                    height=0,
                                                    prominence=const.SIGMOID_MIN_PEAK_PROMINENCE,
                                                    width=const.SIGMOID_MIN_PEAK_WIDTH)
    left_indices = pk_params["left_bases"]
    right_indices = pk_params["right_bases"]
    left_width = np.subtract(pk_indices, left_indices)
    right_width = np.subtract(right_indices, pk_indices)

    if len(pk_indices) == 1:

        # Correct the parameters of the curve
        w = (left_width[0] + right_width[0]) // 2
        left_indices[0] = pk_indices[0] - w
        if left_indices[0] < 0:
            left_indices[0] = 0
        right_indices[0] = pk_indices[0] + w
        if right_indices[0] >= df.shape[0]:
            right_indices[0] = df.shape[0] - 1

        sel = [pd.np.r_[left_indices[0]:right_indices[0]]]

    elif len(pk_indices) >= 2:
        # Let's correct some values... even if we have > 2 peaks, just deal with the first two

        # Set a new variable representing the middle of the peaks
        # peak_split_index = int(np.mean([right_indices[0],left_indices[1]]))
        # peak_split_index = int(np.mean(pk_indices))
        peak_split_index = ((pk_indices[1:] + pk_indices[0:-1]) / 2).astype(np.int)

        # correct the left index of the second peak to be the middle of the peaks
        left_indices[1:] = peak_split_index + 1

        # Update the right most index to the max of all right-most indices
        right_indices[-1] = np.max(right_indices)

        # Finally, reset the right of the first peak
        right_indices[0:-1] = peak_split_index - 1

        left_width = pk_indices - left_indices
        right_width = right_indices - pk_indices
        # noinspection PyUnusedLocal
        base = [pd.np.r_[(left_indices[0]):(left_indices[0] + left_width[0])] for i in range(len(pk_indices))]
        rise = [pd.np.r_[(pk_indices[i] - left_width[i] // 2):(pk_indices[i] + right_width[i] // 2)] for i in
                range(len(pk_indices))]
        # noinspection PyUnusedLocal
        asymptote = [pd.np.r_[(pk_indices[-1] + right_width[-1] // 2):(right_indices[-1])] for i in
                     range(len(pk_indices))]
        sel = [np.unique(np.concatenate((base[i], rise[i], asymptote[i]))) for i in range(len(pk_indices))]
    else:
        raise NotImplementedError("Unable to handle the number of peaks: reported = {}".format(len(pk_indices)))

    a_scan.sig_df = df
    a_scan.sig_peaks_indices = pk_indices
    a_scan.sig_selection = sel


def logistic_fit_func(xx, x_0, curve_max, k, y_0):
    """
    # REVIEW Documentation

    :param xx:
    :type xx:
    :param x_0:
    :type x_0:
    :param curve_max:
    :type curve_max:
    :param k:
    :type k:
    :param y_0:
    :type y_0:
    :return:
    :rtype:
    """
    with np.errstate(all='raise'):
        try:
            eulers = -k * (xx - x_0)
            if isinstance(xx, pd.Series):
                for i, v in eulers.items():
                    eulers[i] = min(np.log(sys.float_info.max), v)
                    eulers[i] = max(np.log(sys.float_info.min), eulers[i])
            else:
                eulers = min(np.log(sys.float_info.max), eulers)
                eulers = max(np.log(sys.float_info.min), eulers)
            return curve_max / (1.0 + np.exp(eulers)) + y_0
        except Exception as ee:
            if isinstance(xx, pd.Series):
                raise RuntimeWarning("logistic_fit_func series: Unhandled RuntimeWarning with "
                                     "(-%.4f * (xx - %.4f) (%s)" % (k, x_0, str(ee)))
            else:
                if str(ee).startswith("overflow encountered in exp"):
                    raise OverflowError("logistic_fit_func: exp overflow with (-%.4f * (%.4f - %.4f))" % (k, xx, x_0))
                if str(ee).startswith("underflow encountered in exp"):
                    raise OverflowError("logistic_fit_func: exp underflow with (-%.4f * (%.4f - %.4f))" % (k, xx, x_0))
                if str(ee).startswith("underflow encountered in double_scalars"):
                    return 0
                raise RuntimeWarning("logistic_fit_func: Unhandled "
                                     "RuntimeWarning with (%.4f / (1.0 + np.exp(-%.4f * (%.4f - %.4f))) + %.4f) (%s)"
                                     % (curve_max, k, xx, x_0, y_0, str(ee)))  # RESEARCH return 0?


def get_all_fit_parameters(a_scan):
    """
    # REVIEW Documentation

    :param Scan a_scan:
    :return:
    :rtype:
    """
    df = a_scan.sig_df.copy()
    sel = a_scan.sig_selection
    pk_indices = a_scan.sig_peaks_indices

    popt_arr = []

    for peak_num in range(len(pk_indices)):

        x_corr_cs_ratio = df.iloc[sel[peak_num]]["log_ave_smps_diameters"]
        y_corr_cs_ratio = df.iloc[sel[peak_num]]["corr_cs_ratio"]
        init_params = [df.log_ave_smps_diameters[pk_indices[peak_num]], 1.0, 0.5, 0]
        bounds = ([x_corr_cs_ratio.iloc[0], -np.inf, -np.inf, 0],
                  [x_corr_cs_ratio.iloc[-1], np.inf, np.inf, np.inf])

        try:
            # noinspection PyTypeChecker
            popt, pcov = scipy.optimize.curve_fit(logistic_fit_func,
                                                  xdata=x_corr_cs_ratio,
                                                  ydata=y_corr_cs_ratio,
                                                  p0=init_params,
                                                  bounds=bounds)
            popt_arr.append(np.round(popt, 4))
        except OverflowError as e:
            raise OverflowError("optimize.curve_fit: " + str(e))
        except RuntimeWarning as e:
            raise RuntimeWarning("optimize.curve_fit: " + str(e))
        except RuntimeError as e:
            raise RuntimeError("optimize.curve_fit: " + str(e))
        except FloatingPointError as e:
            raise OverflowError("optimize.curve_fit: " + str(e))

    a_scan.sigmoid_params = popt_arr


def get_all_fit_curves(a_scan):
    """

    :param Scan a_scan:
    """
    df = a_scan.sig_df.copy()
    # Round popt as sigmoid parameters screen will truncate at 4 decimal places
    # This will ensure identical Dp50 calculations
    popt = np.round(a_scan.sigmoid_params, 4)

    dp50s = []
    sigmoid_curve_x = []
    sigmoid_curve_y = []

    def sigmoid_at_val(y, x_0, curve_max, k, y_0):
        """
        # REVIEW Documentation
        :param y:
        :type y:
        :param x_0:
        :type x_0:
        :param curve_max:
        :type curve_max:
        :param k:
        :type k:
        :param y_0:
        :type y_0:
        :return:
        :rtype:
        """
        return -(np.log(curve_max / (y - y_0)) - 1) / k + x_0

    for peak_num in range(len(popt)):

        try:
            df.loc[:, "fitted"] = [logistic_fit_func(x, *popt[peak_num]) for x in df.log_ave_smps_diameters]
            dm_x = list(range(int(const.SIGMOID_MIN_DIAMETER), int(const.SIGMOID_MAX_DIAMETER)))
            dm_y = [logistic_fit_func(np.log(x), *popt[peak_num]) for x in dm_x]
        except OverflowError as e:
            raise OverflowError(e)
        except RuntimeWarning as e:
            raise RuntimeWarning(e)

        dp50 = np.exp(sigmoid_at_val(0.5, *popt[peak_num]))
        # Round dp50 as sigmoid parameters screen will truncate at 1 decimal places
        # This will ensure identical Dp50 calculations
        dp50s.append(round(dp50, 1))
        sigmoid_curve_x.append(dm_x)
        sigmoid_curve_y.append(dm_y)

    a_scan.sig_df = df
    a_scan.dp50 = dp50s
    a_scan.sigmoid_curve_x = sigmoid_curve_x
    a_scan.sigmoid_curve_y = sigmoid_curve_y


def get_sigmoid_info(a_scan):
    """
    # REVIEW Documentation

    :param Scan a_scan:
    :return:
    :rtype:
    """

    # Clean the datascan which also created the required dataframe
    try:
        find_derv_peaks(a_scan)
        get_all_fit_parameters(a_scan)
        get_all_fit_curves(a_scan)
    except NotImplementedError as e:
        raise NotImplementedError(e)
    except OverflowError as e:
        raise OverflowError(e)
    except RuntimeWarning as e:
        raise RuntimeWarning(e)
