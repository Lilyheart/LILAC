import datetime
import numpy as np
from numpy import array
import pandas as pd
from scipy.signal import find_peaks
from scipy.signal import savgol_filter

# import constants as const

const_SIGMOID_MIN_DIAMETER = 9.0
const_SIGMOID_MAX_DIAMETER = 200.0
const_SIGMOID_ZERO_COUNT_THRESH = 0.01
const_SIGMOID_MIN_VALID_RATIO = 0.0
const_SIGMOID_MAX_VALID_RATIO = 1.2
const_SIGMOID_MIN_PEAK_PROMINENCE = 0.75
const_SIGMOID_MIN_PEAK_WIDTH = 4
status_code = ""
corrected_smps_counts = ""
corrected_ccnc_counts = ""
ave_smps_diameters = ""


def get_sigmoid_info(corrected_smps_counts, corrected_ccnc_counts, ave_smps_diameters):
    """
    # REVIEW Documentation

    :param corrected_smps_counts:
    :type corrected_smps_counts:
    :param corrected_ccnc_counts:
    :type corrected_ccnc_counts:
    :param ave_smps_diameters:
    :type ave_smps_diameters:
    :return:
    :rtype:
    """
    # TODO Change names
    df = pd.DataFrame({"diameter": ave_smps_diameters,
                       "log_diameter": np.log(ave_smps_diameters),
                       "CCNC": corrected_ccnc_counts,
                       "SMPS": corrected_smps_counts,
                       "raw": np.array(corrected_ccnc_counts) / np.array(corrected_smps_counts)})

    # Eliminate diameter data that exceeds diameter range
    sel = (df.diameter >= const_SIGMOID_MIN_DIAMETER) & (df.diameter <= const_SIGMOID_MAX_DIAMETER)
    df = df.loc[sel]

    # Resolve the true zero readings
    sel = (df.CCNC < const_SIGMOID_ZERO_COUNT_THRESH) | (df.SMPS < const_SIGMOID_ZERO_COUNT_THRESH)
    df.loc[sel, "raw"] = 0.0

    # Eliminate points outside of valid range
    sel = (df.raw >= const_SIGMOID_MIN_VALID_RATIO) & (df.raw <= const_SIGMOID_MAX_VALID_RATIO)
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
        val = df.raw[index]
        rl = get_run_length(df.raw, index)
        rle.append({"val": val, "index": index, "rl": rl})
        index += rl

    # Use the rle to eliminate bumps surrounded by zeros
    count = 0
    if len(rle) >= 3:
        start_index = 0

        # Special check for the first case being a noisy value
        if rle[0]["val"] > 0.0 >= rle[1]["val"] and rle[0]["rl"] <= rle[1]["rl"]:
            df.loc[rle[0]["index"]:(rle[0]["index"] + rle[0]["rl"]), "raw"] = 0.0
            print("Fixed start number")
            start_index = 1
            count += 1

        for index in range(start_index, len(rle) - 2):
            if rle[index]["val"] <= 0.0 < rle[index + 1]["val"] and rle[index + 2]["val"] <= 0.0 and \
                    rle[index]["rl"] >= rle[index + 1]["rl"] and rle[index + 2]["rl"] >= rle[index + 1]["rl"] and \
                    rle[index + 1]["rl"] <= 2:
                df.loc[rle[index + 1]["index"]:(rle[index + 1]["index"] + rle[index + 1]["rl"]), "raw"] = 0.0
                count += 1

    del index, count, rle

    # Compute delta
    x = savgol_filter(df.raw, window_length=5, polyorder=1)
    delta_raw = np.subtract(x[1:], x[0:-1])
    delta_logd = np.subtract(df.log_diameter[1:], df.log_diameter[0:-1])
    delta = np.divide(delta_raw, delta_logd)
    delta = savgol_filter(delta, window_length=15, polyorder=2, delta=1)

    # Identify peaks in derivative
    pk_indices, pk_params = find_peaks(delta,
                                       height=0,
                                       prominence=const_SIGMOID_MIN_PEAK_PROMINENCE,
                                       width=const_SIGMOID_MIN_PEAK_WIDTH)
    left_indices = pk_params["left_bases"]
    right_indices = pk_params["right_bases"]

    # print("YOU HAVE {} PEAK(S)".format(len(pk_indices)))

    if len(pk_indices) == 1:
        sel = [pd.np.r_[left_indices[0]:right_indices[0]]]

    elif len(pk_indices) == 2:
        # Let's correct some values...

        # Set a new variable representing the middle of the peaks
        # peak_split_index = int(np.mean([right_indices[0],left_indices[1]]))
        peak_split_index = int(np.mean(pk_indices))

        # correct the left index of the second peak to be the middle of the peaks
        left_indices[1] = peak_split_index + 1

        # Update the right most index to the max of both right-most indices
        right_indices[1] = np.max(right_indices)

        # Finally, reset the right of the first peak
        right_indices[0] = peak_split_index - 1

        left_width = pk_indices - left_indices
        right_width = right_indices - pk_indices

        sel = [pd.np.r_[(left_indices[0]):(pk_indices[0] + right_width[0] // 2),
               (pk_indices[1] + 3):(right_indices[1])],
               pd.np.r_[(left_indices[0]):(left_indices[0] + left_width[0]),
               (pk_indices[1] - left_width[1] // 2):(right_indices[1])]]
    else:
        raise NotImplementedError("Unable to handle the number of peaks: reported = {}".format(len(pk_indices)))

    # RESEARCH Double Sigmoid
    peak_num = 0

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
                result = curve_max / (1.0 + np.exp(-k * (xx - x_0))) + y_0
                return result
            except Exception as eee:
                if isinstance(xx, pd.Series):
                    raise RuntimeWarning("logistic_fit_func series: Unhandled RuntimeWarning (%s)" % str(eee))
                else:
                    if str(eee).startswith("overflow encountered in exp"):
                        raise OverflowError(
                            "logistic_fit_func: exp overflow with (-%.4f * (%.4f - %.4f))" % (k, xx, x_0))
                    if str(eee).startswith("underflow encountered in exp"):
                        raise OverflowError(
                            "logistic_fit_func: exp underflow with (-%.4f * (%.4f - %.4f))" % (k, xx, x_0))
                    if str(eee).startswith("underflow encountered in double_scalars"):
                        return 0
                    raise RuntimeWarning("logistic_fit_func: Unhandled "
                                         "RuntimeWarning w/ (%.4f / (1.0 + np.exp(-%.4f * (%.4f - %.4f))) + %.4f) (%s)"
                                         % (curve_max, k, xx, x_0, y_0, str(eee)))  # RESEARCH return 0?

    x_raw = df.iloc[sel[peak_num]]["log_diameter"]
    y_raw = df.iloc[sel[peak_num]]["raw"]
    init_params = [df.log_diameter[pk_indices[peak_num]], 1.0, 0.5, 0]
    bounds = ([x_raw.iloc[0], -np.inf, -np.inf, 0],
              [x_raw.iloc[-1], np.inf, np.inf, np.inf])

    # RESEARCH - STUDY THESE INIT PARAMS AND THEIR BOUNDS! WE CAN EASILY DO THE TWO PEAK BY SETTING THESE!
    import scipy.optimize

    with np.errstate(all='raise'):
        try:
            # noinspection PyTypeChecker
            popt, pcov = scipy.optimize.curve_fit(logistic_fit_func,
                                                  xdata=x_raw,
                                                  ydata=y_raw,
                                                  p0=init_params,
                                                  bounds=bounds)
        except OverflowError as ee:
            raise OverflowError("optimize.curve_fit: " + str(ee))
        except RuntimeWarning as ee:
            raise RuntimeWarning("optimize.curve_fit: " + str(ee))
        except RuntimeError as ee:
            raise RuntimeError("optimize.curve_fit: " + str(ee))
        except FloatingPointError as ee:
            raise OverflowError("optimize.curve_fit: " + str(ee))

    try:
        df.loc[:, "fitted"] = [logistic_fit_func(x, *popt) for x in df.log_diameter]
        dm_x = list(range(int(const_SIGMOID_MIN_DIAMETER), int(const_SIGMOID_MAX_DIAMETER)))
        dm_y = [logistic_fit_func(np.log(x), *popt) for x in dm_x]
    except OverflowError as e:
        raise OverflowError(e)
    except RuntimeWarning as e:
        raise RuntimeWarning(e)
    except RuntimeError as e:
        raise RuntimeError(e)

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

    dp_50 = np.exp(sigmoid_at_val(0.5, *popt))
    # print("dp50 = {:.2f}".format(dp_50))

    return dm_x, dm_y, dp_50, pk_indices.shape[0]

import os
os.chdir("/home/lilyheart/Dropbox/Classes/19.2.Chemics")
# os.chdir("C:\Users\purpl\Dropbox\Classes\\19.2.Chemics")
print(os.getcwd())

pd.set_option('display.float_format', lambda x: '%.5f' % x)

xls = pd.ExcelFile("O3 (150), VOC (150), TRIAL 11 at 500 cc amd 4 SS-exported.xls")
sheets = xls.sheet_names
print(len(sheets))
print(sheets)

for sheet in sheets:
    xls_sheet = pd.read_excel(xls, sheet_name=sheet)
    for index, row in xls_sheet.iterrows():
        exec (str(row[0]) + " = " + str(row[1]))

    if status_code == 0:
        # print("=============== %s ===============" % sheet)
        try:
            get_sigmoid_info(corrected_smps_counts, corrected_ccnc_counts, ave_smps_diameters)
        except NotImplementedError as e:
            print("%s - NotImplementedError: %s" % (sheet, str(e)))
        except OverflowError as e:
            print("%s - OverflowError: %s" % (sheet, str(e)))
        except RuntimeWarning as e:
            print("%s - RuntimeWarning Error: %s" % (sheet, str(e)))
        except RuntimeError as e:
            print("%s - RuntimeError Error: %s" % (sheet, str(e)))

    # else:
    #     print("Invalid Scan")
