"""
Functions and classes that are used by other parts of the application
"""
# External Packages
import csv
import logging
import numpy as np
import scipy.signal
import warnings  # TODO issues/49 Remove after fixing issue

# Internal Packages
import constants as const

# Set logger for this module
logger = logging.getLogger("helper_functions")

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
    file_path.sort()
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
    with open(file_path) as csvFile:
        # Create a reader for the file
        reader = csv.reader(csvFile, delimiter=',')
        # Convert to list for easier processing
        csv_content = list(reader)
        # Get the experiment_date
        date = csv_content[1][1]
        # Remove empty rows
        csv_content = [_f for _f in csv_content if _f]
        # Remove the unnecessary processed_data - first four lines
        csv_content = csv_content[4:]  # TODO Magic Number - Make setting?  Look for Header row?
        # Process the csv
        for i in range(0, len(csv_content)):
            # Remove empty string in each row
            csv_content[i] = [_f for _f in csv_content[i] if _f]
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
    with open(file_path, encoding="ISO-8859-1") as csv_file:
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
            txt_content[i] = [_f for _f in txt_content[i] if _f]
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


def smooth(a_list, window_length, polyorder):
    """
    Takes a list and smooths it using a Savitzky-Golay filter.  If an error occurs, the original list is returned.

    Filter settings are:

    - The length of the filter window: 5
    - The order of the polynomial used to fit the samples: 2

    :param ndarray|list[float] a_list: The list to smooth
    :param int window_length: The length of the filter window (i.e. the number of coefficients).
                              `window_length` must be a positive odd integer. If `mode` is 'interp',
                              `window_length` must be less than or equal to the size of `x`.
    :param int polyorder: The order of the polynomial used to fit the samples.
                          `polyorder` must be less than `window_length`.
    :return: The smoothed list if it could be smoothed
    :rtype: ndarray
    """
    # TODO issues/48 if a_list is short than 5, there will be an error - Put in tests for all the restrictions above
    try:
        with warnings.catch_warnings():
            warnings.simplefilter(action="ignore", category=FutureWarning)
            a_list = scipy.signal.savgol_filter(a_list,  window_length, polyorder)
        # TODO issues/49 FutureWarning: Using a non-tuple sequence for multidimensional indexing is deprecated;
        # use `arr[tuple(seq)]` instead of `arr[seq]`. In the future this will be interpreted as an array
        # index, `arr[np.array(seq)]`, which will result either in an error or a different result.  = a[a_slice]
    except Exception as e:
        logger.error(e, exc_info=True)
        pass
    return a_list


################
# Code Helpers #
################


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

# Breaking backwards compatibility until the new workflow arrives
# class CustomUnpickler(object, pickle.Unpickler):
#     """
#     Extends the pickle package.  Creates a custom unpickler.  This is neccessary for backporting to prior versions of
#     chemics.
#
#     :param filename: The file like object that the pickler will be unpickling
#     """
#     def __init__(self, filename):
#         # noinspection PyTypeChecker
#         pickle.Unpickler.__init__(self, filename)
#
#     def find_class(self, module, name):
#         """
#         Updates the module name to the new package structure for backwards compatibility.
#
#         :param str module: The original module name
#         :param str name: The class or next level neecessary to return to the super class.
#         """
#         if module == 'Scan':
#             module = 'scan'
#         return super(CustomUnpickler, self).find_class(module, name)
#
#     def _instantiate(self, klass, k):
#         """
#         Extends the pickle package's _instantiate method to account for the new variable in scan.
#
#         :param Class klass: The class to instantiate
#         :param int k:
#         """
#         value = None
#         args = tuple(self.stack[k+1:])
#         del self.stack[k:]
#         instantiated = 0
#         if (not args and
#                 isinstance(type(klass), types.ClassType) and
#                 not hasattr(klass, "__getinitargs__")):
#             try:
#                 value = _EmptyClass()
#                 value.__class__ = klass
#                 instantiated = 1
#             except RuntimeError:
#                 # In restricted execution, assignment to inst.__class__ is
#                 # prohibited
#                 pass
#         if not instantiated:
#             try:
#                 value = klass(0, *args)
#             except TypeError as err:
#                 raise TypeError("in constructor for %s: %s" % (klass.__name__, str(err)), sys.exc_info()[2])
#         self.append(value)
#
#
# # noinspection PyClassHasNoInit,PyClassicStyleClass
# class _EmptyClass:
#     """
#     Helper class for load_inst/load_obj of CustomUnpickler
#     """
#     pass
