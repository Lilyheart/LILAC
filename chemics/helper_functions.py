"""
Functions and classes that are used by other parts of the application
"""
# External Packages
import csv
import numpy as np
import pickle
import scipy.signal
import sys
import types
import warnings  # TODO issues/49 Remove after fixing issue

# Internal Packages
import constants as const

################
# Parse Files  #
################


def process_csv_files(file_path):
    """
    Converts a list of csv files into a single python list.  Each data point is stored as a str.  Each row if items is
    stored as a list.  All the rows are stores a list.

    :param list[str] file_path:
    :return: The date from the first record in the first csv followed by the contents of the all the cvs files as a list
    :rtype: (str, list[list[str]])
    """
    if len(file_path) < 1:
        raise IOError("File not found")  # TODO issues/25 Error not handled well
    elif len(file_path) == 1:
        return process_a_csv(file_path[0])
    else:
        date = None
        csv_content = None
        # for each file name
        for i in file_path:
            # process the file
            csv_file_contents = process_a_csv(i)
            date = csv_file_contents[0]
            # DOCQUESTION safe to assume ALWAYS same date? Or should each file be checked for error reasons?
            if csv_content is None:  # if this is the first file being processed with data
                csv_content = csv_file_contents[1]
            else:
                csv_content.extend(csv_file_contents[1])
    return date, csv_content


def process_a_csv(file_path):
    """
    Converts a csv file into a python list.  Each data point is stored as a str.  Each row if items is stored as a list.
    All the rows are stores a list.

    :param str file_path:  The full path name to the csv file to process
    :return: The date from the first record in the first csv followed by the contents of the cvs file as a list
    :rtype: (str, list[list[str]])
    """
    # Open the file
    with open(file_path, 'r') as csvFile:
        # Create a reader for the file
        reader = csv.reader(csvFile, delimiter=',')
        # Convert to list for easier processing
        csv_content = list(reader)
        # Get the experiment_date
        date = csv_content[1][1]
        # Remove empty rows
        csv_content = filter(None, csv_content)
        # Remove the unnecessary processed_data - first four lines
        csv_content = csv_content[4:]  # TODO Magic Number - Make setting?  Look for Header row?
        # Process the csv
        for i in range(0, len(csv_content)):
            # Remove empty string in each row
            csv_content[i] = filter(None, csv_content[i])
        return date, csv_content


def process_tab_sep_files(file_path):
    """
    Converts a tab seperated value file into a python list.  Each data point is stored as a str.  Each row if items is
    stored as a list.  All the rows are stores a list.

    :param str file_path:  The full path name to the txt file to process
    :return: The contents of the text file as a list
    :rtype: list[list[str]]
    """
    # Open the file
    with open(file_path, 'r') as csv_file:
        # Create a reader for the file
        reader = csv.reader(csv_file, delimiter='\t')
        # convert to list for easier processing
        # Convert to list for easier processing
        txt_content = list(reader)
        # Find where the header ends  # TODO issues/47 Magic Start - Make setting?  Look for Header row?
        for i in range(len(txt_content)):
            # if ''.join(txt_content[i][0].split()).lower() == "sample#":  # TODO issues/4 Place to start
            if ''.join(txt_content[i][0].split()).lower() == "starttime":
                txt_content = txt_content[i:]
                break
        # TODO issues/4 Remove row index from sample# time row
        # Remove row index from start time row
        txt_content[0] = txt_content[0][1:]
        # Drop the row that only states "Diameter midpoint"
        txt_content = txt_content[0:1] + txt_content[2:]
        # Remove empty cells
        for i in range(0, len(txt_content)):
            txt_content[i] = filter(None, txt_content[i])
        return txt_content

########################
# Help Math Functions  #
########################


def are_floats_equal(a, b, err=0.01):
    """
    Compares two float to see if they are equal within an error value

    :param float a: First value to compare
    :param float b: Second value to compare
    :param err: Amount of allowable differences with a default of 0.01.
    :return: True if the absolute value of (a - b) is less than err, otherwise False
    :rtype: bool
    """
    return abs(a - b) < err


def safe_div(x, y):
    """
    Divides to values and returns a value safely.

    :param int|float x: The numerator
    :param int|float y: The denominator
    :return: if the denominator is zero, returns 0, otherwise returns x / y
    :rtype: int|float
    """
    return 0 if y == 0 else x / y


def safe_div_array(l1, l2):
    """
    Divides the values in two arrays. # REVIEW Documentation

    :param list[float] l1: The list containing the numerators.
    :param list[float] l2: The list containing the denominators.
    :return:
    :rtype: list[float]
    """
    length = min(len(l1), len(l2))
    result_list = []
    for i in range(length):
        result_list.append(safe_div(l1[i], l2[i]))
    return result_list


def normalize_dndlogdp_list(a_list):  # DOCQUESTION naming again
    """
    Normalize the data is a_list by finding the max value of the values in the list while ignoring the first 5 values.
    The assumption is that the first few data points are probably not quite right so normalization is only based
    on the max of later points.

    :param list[float] a_list: A list of values to normalize
    :return: The normalized list
    :rtype: list[float]
    """
    max_value = max(a_list[5:])  # DOCQUESTION Magic Number, can this be something else?
    if max_value == 0:  # DOCQUESTION Are they always postive?
        return a_list
    for x in range(len(a_list)):  # QUESTION BK: Is there any dis/advantagous to manually done?
        if a_list[x]:
            a_list[x] /= max_value
    return np.asarray(a_list)


def cal_percentage_less(a_list, value, min_diff):
    """
    # REVIEW Documentation
    # RESEARCH Better Function name

    :param a_list:
    :type a_list:
    :param value:
    :type value:
    :param min_diff:
    :type min_diff:
    :return:
    :rtype:
    """
    # COMBAKL Sigmoid
    count = 0
    for a_val in a_list:
        if value > a_val or abs(value - a_val) < min_diff:
            count += 1
    return safe_div(count, len(a_list))


def get_ave_none_zero(a_list):
    """
    # REVIEW Documentation

    :param list[float] a_list:
    :return:
    :rtype: float
    """
    # COMBAKL Sigmoid
    sum_val = 0
    count = 0
    for i in a_list:
        if i != 0:
            sum_val += i
            count += 1
    if count != 0:
        return sum_val / count
    else:
        return 0


############################
# Data Transformation Code #
############################


def fill_zeros_to_begin(a_list, fill_amount):
    """
    Appends zero to the beginning of a list.

    :param list a_list: The list to add zeros in front of
    :param int fill_amount: The number of zeros to add
    :return: The new list with zeros added to the front.
    :rtype: list
    """
    # Create array of zeros the length to append to the beginning of the list
    filler_array = np.asarray([0] * fill_amount)
    # append the filler array to the beginning of the list to return
    a_list = np.append(filler_array, a_list)
    return np.asarray(a_list)


def fill_zeros_to_end(a_list, length_to_fill):  # RESEARCH Better Code Name
    """
    Appends zero to the end of a list to make the list the desired length.

    :param list a_list: The list to add zeros to the end of
    :param int length_to_fill: The length the list should be.
    :return: The new list with zeros added to the back.
    :rtype: list
    """
    # If the list is too short,
    if len(a_list) < length_to_fill:
        # Create array of zeros the length needed to increases the list to the needed size
        filler_array = np.asarray([0] * (length_to_fill - len(a_list)))
        # append the filler array to the end of the list to return
        a_list = np.append(a_list, filler_array)
    return np.asarray(a_list)


def resolve_zeros(a_list):
    """
    Change all zeros in the list to a very small number (:class:`~constants.EPSILON`)

    :param list[float] a_list: the input list with zeros
    :return: a new list with all zeros replaced with :class:`~constants.EPSILON`
    :rtype: list[float]
    """
    for i in range(len(a_list)):
        if a_list[i] == 0:
            a_list[i] = const.EPSILON
    return a_list


def resolve_small_ccnc_vals(ccnc_vals):
    """
    If there are less than 4 CCNC values, remove the values and change them to a very small number
    (:class:`~constants.EPSILON`)

    :param list[list[float]|float] ccnc_vals: The processed_ccnc_counts
    :return: The updated processed_ccnc_counts
    :rtype: list[list[float]|float]
    """
    for i in range(len(ccnc_vals)):
        if ccnc_vals[i] < 4:
            ccnc_vals[i] = const.EPSILON  # RESEARCH Inner level will no longer be a list?
    return ccnc_vals


def smooth(a_list):
    """
    Takes a list and smooths it using a Savitzky-Golay filter.  If an error occurs, the original list is returned.

    Filter settings are:

    - The length of the filter window: 5
    - The order of the polynomial used to fit the samples: 2

    :param list[float] a_list: The list to smooth
    :return: The smoothed list if it could be smoothed
    :rtype: list[float]
    """
    # TODO issues/48 if a_list is short than 5, there will be an error
    # noinspection PyBroadException
    try:
        with warnings.catch_warnings():
            warnings.simplefilter(action="ignore", category=FutureWarning)
            a_list = scipy.signal.savgol_filter(a_list,  5, 2)
        # TODO issues/49 FutureWarning: Using a non-tuple sequence for multidimensional indexing is deprecated;
        # use `arr[tuple(seq)]` instead of `arr[seq]`. In the future this will be interpreted as an array
        # index, `arr[np.array(seq)]`, which will result either in an error or a different result.  = a[a_slice]
    except Exception:  # TODO issues/40 error logging to determine what causes
        pass
    return a_list


def heavy_smooth(a_list):
    """
    Takes a list and smooths it using a Savitzky-Golay filter.  If an error occurs, the original list is returned.

    Filter settings are:

    - The length of the filter window: 15
    - The order of the polynomial used to fit the samples: 2

    :param list[float] a_list: The list to smooth
    :return: The smoothed list if it could be smoothed
    :rtype: list[float]
    """
    # TODO issues/48 if a_list is short than 15, there will be an error
    # noinspection PyBroadException
    try:
        # TODO issues/49
        with warnings.catch_warnings():
            warnings.simplefilter(action="ignore", category=FutureWarning)
            a_list = scipy.signal.savgol_filter(a_list, 15, 2)
    except Exception:  # TODO issues/40 error logging to determine what causes
        pass
    return a_list


################
# Code Helpers #
################


def find_ref_index_smps(smps_data, up_time):
    """
    Finds the reference point in the SMPS data.

    Assumptions:

    - First peak of SMPS data is between index 0 and index `scan.up_time`.
    - Second peak of SMPS data is between index `scan.up_time` and the end

    :param list[float] smps_data: The SMPS data list
    :param int up_time: The uptime of the scan
    :return: The reference point if it can find the minimum, otherwise returns `None`
    :rtype: None|int
    """
    # Seperate the list which contains left peak and right peak
    left_list = smps_data[0:up_time]
    right_list = smps_data[up_time:]
    # find the left peak and right peak
    left_max_index = np.argmax(left_list)
    right_max_index = up_time + np.argmax(right_list)
    # get the data between the peaks
    middle_list = smps_data[left_max_index:right_max_index]
    # then perform agressive smoothing
    middle_list = scipy.signal.savgol_filter(middle_list, 11, 2)  # RESEARCH Should all the smooths go into a function?
    # find the min between the two peaks, which is exactly what we need  # DOCQUESTION See Spreadsheet for test scan 10
    potential_mins = scipy.signal.argrelmin(middle_list, order=4)
    if len(potential_mins[0]) == 0:
        return None
    ref_index = left_max_index + potential_mins[0][0]
    # The reference point should be within a reasonable range of the up_time  # DOCQUESTION Valid?
    if abs(up_time - ref_index) > len(smps_data) / 20:
        return None
    else:
        return ref_index


def find_ref_index_ccnc(ccnc_list, potential_loc):
    """
    Finds the reference point in the CCNC data.

    Assumptions:

    - The two reference values must be quite close to each other.
    - Find absolute max
    - The potential location is the sum of the smps local minimum and the base shift factor calculated from other

    :param list[float] ccnc_list: The CCNC data list
    :param int potential_loc:  The potential reference index of the SMPS data
    :return: An updated potential reference index of the SMPS data
    :rtype: int
    """
    ccnc_list = smooth(ccnc_list)  # DOCQUESTION Smoothing an already smoothed list?
    # The the point at the potential location and the point before it.
    first_point = ccnc_list[potential_loc - 1]
    second_point = ccnc_list[potential_loc]
    # Determine slope at that point
    slope = second_point - first_point
    if slope > max(ccnc_list) / 20:  # DOCQUESTION Valid?
        return potential_loc - 1
    else:
        return potential_loc
    pass


def get_correct_num(a_list, number, bigger=True):
    """
    # REVIEW Documentation

    :param a_list:
    :type a_list:
    :param number:
    :type number:
    :param bigger:
    :type bigger:
    :return:
    :rtype:
    """
    # Get a number approximately around number
    # Assuming the a_list is sorted in descending order
    # :param bigger: if bigger, return the minimum number bigger than number, otherwise
    #                 return the maximum number smaller than number
    # :param a_list: the list
    # :param number: the number
    # :return: the correct number
    # COMBAKL Kappa
    num = a_list[0]
    for i in range(1, len(a_list)):
        if a_list[i] < number:
            if bigger:
                return num, i - 1
            else:
                return a_list[i], i
        else:
            num = a_list[i]
    return a_list[-1], len(a_list) - 1


def outliers_iqr(value_array, index_array):
    """
    Determines the outliers of an array.  If none, returns -1
    # REVIEW Documentation

    :param list[float] value_array: # REVIEW Documentation
    :param list[float] index_array: # REVIEW Documentation
    :return: returns a list of outliers if they exist, otherwise it returns -1
    :rtype: list[float]|int
    """
    # COMBAKL Sigmoid
    # RESEARCH better return or use Exception handling etc
    # noinspection PyBroadException
    try:
        quartile_1, quartile_3 = np.percentile(value_array, [25, 75])
        iqr = quartile_3 - quartile_1
        lower_bound = quartile_1 - (iqr * 1.25)
        upper_bound = quartile_3 + (iqr * 1.25)
        indexes = []
        for i in range(len(value_array)):
            if lower_bound <= value_array[i] <= upper_bound:
                indexes.append(index_array[i])
        return indexes
    except Exception:  # TODO issues/40 error logging to determine what causes
        return -1


class CustomUnpickler(object, pickle.Unpickler):
    """
    Extends the pickle package.  Creates a custom unpickler.  This is neccessary for backporting to prior versions of
    chemics.

    :param filename: The file like object that the pickler will be unpickling
    """
    def __init__(self, filename):
        # noinspection PyTypeChecker
        pickle.Unpickler.__init__(self, filename)

    def find_class(self, module, name):
        """
        Updates the module name to the new package structure for backwards compatibility.

        :param str module: The original module name
        :param str name: The class or next level neecessary to return to the super class.
        """
        if module == 'Scan':
            module = 'scan'
        return super(CustomUnpickler, self).find_class(module, name)

    def _instantiate(self, klass, k):
        """
        Extends the pickle package's _instantiate method to account for the new variable in scan.

        :param Class klass: The class to instantiate
        :param int k:
        """
        value = None
        args = tuple(self.stack[k+1:])
        del self.stack[k:]
        instantiated = 0
        if (not args and
                isinstance(type(klass), types.ClassType) and
                not hasattr(klass, "__getinitargs__")):
            try:
                value = _EmptyClass()
                value.__class__ = klass
                instantiated = 1
            except RuntimeError:
                # In restricted execution, assignment to inst.__class__ is
                # prohibited
                pass
        if not instantiated:
            try:
                value = klass(0, *args)
            except TypeError, err:
                raise TypeError("in constructor for %s: %s" % (klass.__name__, str(err)), sys.exc_info()[2])
        self.append(value)


# noinspection PyClassHasNoInit,PyClassicStyleClass
class _EmptyClass:
    """
    Helper class for load_inst/load_obj of CustomUnpickler
    """
    pass
