"""
This class creates a scan object stores the data from a single scan.
"""
# External Packages
import numpy as np
import scipy.optimize as opt
import scipy.stats

# Internal Packages
import constants as const
import fast_dp_calculator as fast_dp_calculator
import helper_functions as hf


class Scan(object):
    """
    This class creates a scan object stores the data from a single scan.

        The following variables are stored:  # RESEARCH Confirm variable descriptions

        - **status**: status of the scan
        - **status_code**: The reason why the scan is not good
        - **counts_to_conc**: the flow rate
        - **index**: the scan #
        - **index_in_ccnc_data**:  the position of the scan in ccnc data
        - **start_time**: what time the scan starts. Format is hh:mm:ss
        - **end_time**: what time the scan ends. Format is hh:mm:ss
        - **duration**: duration of the scan
        - **scan_up_time**: up and down scan time. Very useful to align the data
        - **scan_down_time**:
        - **raw_super_sats**: the list of super saturation rate.
        - **raw_T1s**: T1 Read
        - **raw_T2s**: T2 Read
        - **raw_T3s**: T3 Read
        - **raw_smps_counts**: SMPS and CCNC counts. SMPS count is calculated from smps file and ccnc count is
          calculated from ccnc file
        - **raw_ccnc_counts**:
        - **raw_ave_ccnc_sizes**: calculated average size of ccnc particles from ccnc file
        - **raw_normalized_concs**: normalized concentration. Also called dN/dlogDp.
        - **diameter_midpoints**: diameter midpoints.
        - **ave_smps_diameters**: ave diameter from smps file
        - **ref_index_smps**: Used to align smps and ccnc data. The reference point of smps and ccnc data.
          Normally, this is the local minimum between the peaks
        - **ref_index_ccnc**: Used to align smps and ccnc data. The reference point of smps and ccnc data.
          Normally, this is the local minimum between the peaks
        - **shift_factor**:
        - **processed_smps_counts**:  Processed data. Since we only need a portion of the raw data and work with it,
          we don't use all the raw data.  Furthermore, we need to perform certain processing techniques on the data
        - **processed_ccnc_counts**:
          we don't use all the raw data.  Furthermore, we need to perform certain processing techniques on the data
        - **processed_T1s**:
        - **processed_T2s**:
        - **processed_T3s**:
        - **processed_super_sats**:
        - **true_super_sat**:
        - **processed_ave_ccnc_sizes**:
        - **processed_normalized_concs**:
        - **corrected_smps_counts**: smps and ccnc data after we correct for the charges
        - **corrected_ccnc_counts**:
        - **sigmoid_params**: necessary parameters for sigmoid fit.  the main reason we need this is because we have to
          handle fitting in two sigmoid lines [begin rise. end rise, begin asymp, end asymp]
        - **functions_params**: b,d and c
        - **dps**: dps of interest: dp50, dp50wet, dp50+20
        - **sigmoid_y_vals**: sigmoid line y values
        - **asym_limits**:  the asym limits to fit sigmoid lines and predict params for sigmoid line.
          the reason we need a class variable for this is because we use them for two different functions.

    :param int index: The scan number from the SMPS file.  # TODO issues/4 [Current is sequential #s from zero]

    """

    def __init__(self, index):
        # TODO issues/45 combine status and code into one
        # QUESTION / RESEARCH duration = scan_up_time + scan_down_time; end time is start_time+duration. All neccessary?
        self.status = 1
        self.status_code = 0
        self.counts_to_conc = 0.0
        self.index = index
        self.index_in_ccnc_data = 0
        self.start_time = None
        self.end_time = None
        self.duration = 0
        self.scan_up_time = 0
        self.scan_down_time = 0
        self.raw_super_sats = []
        self.raw_T1s = []
        self.raw_T2s = []
        self.raw_T3s = []
        self.raw_smps_counts = []
        self.raw_ccnc_counts = []
        self.raw_ave_ccnc_sizes = []
        self.raw_normalized_concs = []
        self.diameter_midpoints = []
        self.ave_smps_diameters = []
        self.ref_index_smps = 0
        self.ref_index_ccnc = 0
        self.shift_factor = 0
        self.processed_smps_counts = []
        self.processed_ccnc_counts = []
        self.processed_T1s = []
        self.processed_T2s = []
        self.processed_T3s = []
        self.processed_super_sats = []
        self.true_super_sat = 0
        self.processed_ave_ccnc_sizes = []
        self.processed_normalized_concs = []
        self.corrected_smps_counts = []
        self.corrected_ccnc_counts = []
        self.sigmoid_params = []
        self.functions_params = []
        self.dps = []
        self.sigmoid_y_vals = []
        self.asym_limits = [0.75, 1.5]  # RESEARCH Magic number

    def __repr__(self):
        """
        Returns a string representation of variables stored in the the scan.  The format is: `var_name;var_value`.
        Nonprimative variables are stored as  `var_name;type(var_value)`

        :return: The scan as a string.
        :rtype: str
        """
        items = ("%s;%r" % (k, v) for k, v in self.__dict__.items())
        return "%s" % "\n".join(items)

    ###############
    # Get Values  #
    ###############

    def is_valid(self):
        """
        Retuns if the scan is valid or not.

        :return: True if status == 1, otherwise False
        :rtype: bool
        """
        return self.status == 1  # TODO issues/45 affected by proposed status code change

    def compare_smps(self, another_scan):
        # noinspection PyPep8
        """
        Compares a scan to another scan by using the correlation coefficient and also Kolmogorov-Smirnov statistic
        on the smps counts to determine if the scan have the same distribution.

        - `Pearsons Correlation Coefficient <https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.pearsonr.html/>`_
        - `Kolmogorov-Smirnov statistic on 2 samples <https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.ks_2samp.html/>`_

        :param Scan another_scan: a scan object to compare to this one
        :return: Returns true if the correlation coefficient is less that 0.05 **and** the Kolmogorov-Smirnov
                 statistic is greater than 0.05
        :rtype: bool
        """
        # Compare two scans using correlation coefficient
        corr_coef_p = scipy.stats.pearsonr(self.raw_smps_counts, another_scan.raw_smps_counts)[1]
        # Compare two scans using Kolmogorov-Smirnov statistic
        ks_stat_p = scipy.stats.ks_2samp(self.raw_smps_counts, another_scan.raw_smps_counts)[1]
        # Set the value
        if corr_coef_p < 0.05 < ks_stat_p:
            return True
        else:
            return False

    def get_status_code_descript(self):
        """
        Returns a string value explaining the status code of the current scan

        :return: The status code of the current scan.
        :rtype: str
        """
        if self.status_code == 0:  # RESEARCH 0 Status Code
            return "The scan shows no problem."
        elif self.status_code == 1:  # RESEARCH 1 Status Code
            return "There is no equivalent ccnc data for this scan. This is likely because ccnc data start at a later" \
                   "time than smps scan, or it ends before the smps scan."
        elif self.status_code == 2:  # RESEARCH 2 Status Code
            return "The length of SMPS for this scan does not agree with the indicated scan duration of the experiment."
        elif self.status_code == 3:  # RESEARCH 3 Status Code
            return "The distribution of SMPS and CCNC data has a low correlation with those of the next few scans."
        elif self.status_code == 4:  # RESEARCH 4 Status Code
            return "The program can not locate the reference point for SMPS data."
        elif self.status_code == 5:  # RESEARCH 5 Status Code
            return "The program can not locate the reference point for CCNC data."
        elif self.status_code == 6:  # RESEARCH 6 Status Code
            return "The scan do not have enough CCNC or SMPS data. Most likely because we shift the data too much"
        elif self.status_code == 7:  # RESEARCH 7 Status Code
            return "The super saturation rate or temperature do not remain constant throughout the scan!"
        elif self.status_code == 8:  # RESEARCH 8 Status Code
            return "The temperature do not remain constant enough throughout the scan!"
        elif self.status_code == 9:  # RESEARCH 9 Status Code
            return "The Scan is manually disabled by the user!"
            # QUESTION Where does the following play in?  Was commented out.  Looked like combined with 7? Split?
            # return "The super saturation rate does not remain constant throughout the scan duration."

    ###############
    # Set Values  #
    ###############

    def set_start_time(self, start_time):
        """
        Sets the start_time value in the scan object.

        :param datetime.datetime start_time:  The time the scan started.  From the smps file.
        """
        self.start_time = start_time

    def set_end_time(self, end_time):
        """
        Sets the end_time value in the scan object.

        :param datetime.datetime end_time: The end time of the scan.  Typically the start time plus the duration.
        """
        self.end_time = end_time

    def set_up_time(self, up_time):
        """
        Sets the scan_up_time value in the scan object.

        :param int up_time:  The scan up time from the smps file.
        """
        self.scan_up_time = up_time

    def set_down_time(self, down_time):
        """
        Sets the scan_down_time value in the scan object.

        :param int down_time:  The scan down time from the retrace time in the smps file.
        """
        self.scan_down_time = down_time

    def set_duration(self, duration):
        """
        Sets the duration value in the scan object.

        :param int duration:  The duration of the scan. Typically this is scan_up_time + scan_down_time.
        """
        self.duration = duration

    def set_counts_2_conc(self, new_value):
        """
        Sets the counts_to_conc value in the scan object.

        :param float new_value: The counts_to_conc value
        """
        self.counts_to_conc = new_value

    def add_to_diameter_midpoints(self, new_data):
        """
        Adds the new_data value to the diameter_midpoints list in the scan object.

        :param str|int|float new_data: The diameter_midpoints to add to the list
        """
        self.diameter_midpoints.append(float(new_data))

    def add_to_raw_normalized_concs(self, new_data):
        """
        Adds the new_data value to the raw_normalized_concs list in the scan object.

        :param str|int|float new_data: The raw_normalized_concs to add to the list
        """
        self.raw_normalized_concs.append(float(new_data))

    def add_to_raw_smps_counts(self, new_data):
        """
        Multiplies the new_data by counts_to_conc and adds the result to the raw_smps_counts list in the scan object.

        :param int new_data: The raw_smps_counts to add to the list
        """
        self.raw_smps_counts.append(int(new_data) * self.counts_to_conc)

    def add_to_ave_smps_diameters(self, new_data):
        """
        Adds the new_data value to the ave_smps_diameters list in the scan object.

        :param float new_data: The ave_smps_diameters to add to the list
        """
        self.ave_smps_diameters.append(new_data)

    def add_to_raw_t1s_t2s_t3s(self, t1, t2, t3):
        """
        Adds the three temperaturs values to the t1, t2 and t3 lists in the scan object.

        :param str|int|float t1: The raw t1 value.
        :param str|int|float t2: The raw t1 value.
        :param str|int|float t3: The raw t1 value.
        """
        self.raw_T1s.append(float(t1))
        self.raw_T2s.append(float(t2))
        self.raw_T3s.append(float(t3))

    def set_index_in_ccnc_data(self, index):
        """
        Sets the index_in_ccnc_data value in the scan object.

        :param int index: The position of the scan in ccnc data
        """
        self.index_in_ccnc_data = index

    def set_status(self, status):
        """
        Sets the status value in the scan object.

        :param int status: The updated status
        """
        self.status = status

    def set_status_code(self, code):
        """
        Sets the status_code value in the scan object.

        :param int code: The updated status code
        """
        self.status_code = code

    def add_to_raw_super_sats(self, ss):
        """
        Adds the new_data value to the raw_super_sats list in the scan object.

        :param str|int|float ss: The raw super saturation value to add to the list
        """
        self.raw_super_sats.append(float(ss))

    def add_to_raw_ccnc_counts(self, new_data):
        """
        Adds the new_data value to the raw_ccnc_counts list in the scan object.

        :param str|int|float new_data: The raw_ccnc_count to add to the list
        """
        self.raw_ccnc_counts.append(float(new_data))

    def add_to_raw_ave_ccnc_sizes(self, new_data):
        """
        Adds the new_data value to the raw_ave_ccnc_sizes list in the scan object.

        :param  str|int|float new_data: The ave_ccnc_size to add to the list
        :type new_data:
        """
        self.raw_ave_ccnc_sizes.append(float(new_data))

    def set_shift_factor(self, factor):
        """
        If the factor is lless then that length of number of CCNC raw data points, it sets the shift factor to the
        value provided.  Otherwise it sets the shift factor to zero.

        :param int factor: The number of data points to shift data so that the SMPS data and the CCNC data align.
        """
        if factor < len(self.raw_ccnc_counts):
            self.shift_factor = factor
        else:
            self.shift_factor = 0  # RESEARCH Does a 0 make sense?

    def set_sigmoid_params(self, params):
        """
        # REVIEW Documentation

        :param params: # REVIEW Documentation
        :type params: # REVIEW Documentation
        """
        # COMBAKL Sigmoid
        self.sigmoid_params = params
        self.fit_sigmoids()

    #######################
    # Validation Methods  #
    #######################

    def pre_align_self_test(self):
        """
        Compares the length of the smps data and if it's not in the same as the duration, invalidates the scan
        """
        if len(self.raw_smps_counts) != self.duration:
            self.status = 0
            self.set_status_code(2)  # RESEARCH 2 Status Code
            # QUESTION K: more work over here. Can always improve
            # QUESTION K: perform Hartigan's dip test to test for bimodality

    def post_align_self_test(self):
        """
        Checks for invalid scans.  Currently tests for:

        - Error in super saturation
        - Standard devations in the three tempuratures greater than 1
        - Checks for uniform values in temperatures by comparing the first value to all the values

        """
        # QUESTION K: more work over here. Can always improve this one
        # Check for error in super saturation
        for i in range(len(self.processed_super_sats)):
            if not hf.are_floats_equal(self.true_super_sat, self.processed_super_sats[i]):
                self.true_super_sat = None
                self.set_status(0)
                self.set_status_code(7)  # RESEARCH 7 Status Code
                break
        # check for standard deviation on tempuratures
        if np.std(self.processed_T1s) > 1 or np.std(self.processed_T2s) > 1 or np.std(self.processed_T3s) > 1:
            self.set_status(0)
            self.set_status_code(7)  # RESEARCH 7 Status Code
        # check for uniform values
        for i in range(len(self.processed_T1s)):
            # check for temperature 1
            if not hf.are_floats_equal(self.processed_T1s[0], self.processed_T1s[i], 1):
                self.set_status(0)
                self.set_status_code(7)  # RESEARCH 7 Status Code
            # check for temperature 2
            if not hf.are_floats_equal(self.processed_T2s[0], self.processed_T2s[i], 1):
                self.set_status(0)
                self.set_status_code(7)  # RESEARCH 7 Status Code
            # check for temperature 3
            if not hf.are_floats_equal(self.processed_T2s[0], self.processed_T2s[i], 1):
                self.set_status(0)
                self.set_status_code(7)  # RESEARCH 7 Status Code

    #############################
    # Data Transformation Code  #
    #############################

    def do_basic_trans(self):
        """
        Convert lists to numpy arrays.
        """
        # RESEARCH K comment "got to generate processed_smps_counts early"
        self.raw_T1s = np.asarray(self.raw_T1s)
        self.raw_T2s = np.asarray(self.raw_T2s)
        self.raw_T3s = np.asarray(self.raw_T3s)
        self.raw_smps_counts = np.asarray(self.raw_smps_counts, dtype=np.float64)
        self.raw_ccnc_counts = np.asarray(self.raw_ccnc_counts, dtype=np.float64)
        self.raw_normalized_concs = np.asarray(self.raw_normalized_concs)
        self.diameter_midpoints = np.asarray(self.diameter_midpoints)
        self.raw_ave_ccnc_sizes = np.asarray(self.raw_ave_ccnc_sizes)
        self.raw_super_sats = np.asarray(self.raw_super_sats)
        self.ave_smps_diameters = np.asarray(self.ave_smps_diameters)

    def generate_processed_data(self):  # RESEARCH should this be called apply shift?
        """
        Processing SMPS is straightforward.

        Processing CCNC is based on the shift factor.

        - If there is a negative shift factor, insert zeros before the CCNC data.
        - If there is a positive shift factor, drop the beginning rows by the shift factor.
        - If there is not enough data, then zeros are added to the end.
        - Processed data is then truncated to match the length of duration.

        Finally the :class:`~scan.Scan.post_align_self_test` is processed to verify validity of scan.

        Original data is stored seperately to ensure no data loss when shifting.
        """
        # Copy the raw SMPS data to ensure no data loss
        self.processed_smps_counts = self.raw_smps_counts
        # Process the dndlogdp list  # QUESTION naming again
        self.processed_normalized_concs = hf.normalize_dndlogdp_list(self.raw_normalized_concs)
        # Copy raw CCNC values to local variables
        ccnc_counts = self.raw_ccnc_counts
        t1s = self.raw_T1s
        t2s = self.raw_T2s
        t3s = self.raw_T3s
        super_sats = self.raw_super_sats
        ave_ccnc_sizes = self.raw_ave_ccnc_sizes
        # Update for shift factors
        # -- if shift factor is positive
        if self.shift_factor >= 0:
            # if not enough ccnc counts to even shift, the scan is invalid
            if len(ccnc_counts) < self.shift_factor:  # RESEARCH This would never happen as self.shift when set, checks
                self.set_status(0)
                self.set_status_code(6)  # RESEARCH 6 Status Code
            # Shift the data based on the shift factor
            ccnc_counts = ccnc_counts[self.shift_factor:]
            t1s = t1s[self.shift_factor:]
            t2s = t2s[self.shift_factor:]
            t3s = t3s[self.shift_factor:]
            super_sats = super_sats[self.shift_factor:]
            ave_ccnc_sizes = ave_ccnc_sizes[self.shift_factor:]
        else:  # -- if shift factor is negative  # QUESTION anything needed of factor == 0?
            # populate ccnc counts with 0s in the fronts
            ccnc_counts = hf.fill_zeros_to_begin(ccnc_counts, abs(self.shift_factor))
            t1s = hf.fill_zeros_to_begin(t1s, abs(self.shift_factor))
            t2s = hf.fill_zeros_to_begin(t2s, abs(self.shift_factor))
            t3s = hf.fill_zeros_to_begin(t3s, abs(self.shift_factor))
            super_sats = hf.fill_zeros_to_begin(super_sats, abs(self.shift_factor))
            ave_ccnc_sizes = hf.fill_zeros_to_begin(ave_ccnc_sizes, abs(self.shift_factor))
        # If we still don't have enough data, populate with 0s  # QUESTION Define "enough"
        ccnc_counts = hf.fill_zeros_to_end(ccnc_counts, self.duration)
        t1s = hf.fill_zeros_to_end(t1s, self.duration)
        t2s = hf.fill_zeros_to_end(t2s, self.duration)
        t3s = hf.fill_zeros_to_end(t3s, self.duration)
        super_sats = hf.fill_zeros_to_end(super_sats, self.duration)
        ave_ccnc_sizes = hf.fill_zeros_to_end(ave_ccnc_sizes, self.duration)
        # Update the objects values with the local calculations truncating to the length of duration
        self.processed_ccnc_counts = ccnc_counts[:self.duration]
        self.processed_T1s = t1s[:self.duration]
        self.processed_T2s = t2s[:self.duration]
        self.processed_T3s = t3s[:self.duration]
        self.processed_super_sats = super_sats[:self.duration]
        self.processed_ave_ccnc_sizes = ave_ccnc_sizes[:self.duration]
        # QUESTION Why is this value?
        self.true_super_sat = self.processed_super_sats[0]
        # Perform self test
        self.post_align_self_test()

    def align_smps_ccnc_data(self, base_shift_factor):
        """
        Assumes the shift factor is positive.  The base shift factor is used as a reference.  The shift factors
        of the two scans should be within 1 index of each other.

        :param int base_shift_factor: The potential shift factor from the auto alignment process.
        :return: The desired shift_factor
        :rtype: int
        """
        # TODO issues/27 is this where the new auto align code should go?
        # QUESTION why do we assume it's always postive? Is that safe?
        # QUESTION why do we assume it's always 1 index apart?  Does my code fix this?
        # Set the base shift factor of the scan with new factor
        self.shift_factor = base_shift_factor
        # Pull the raw counts
        ccnc_counts = self.raw_ccnc_counts
        smps_counts = self.raw_smps_counts
        # if we have an invalid scan, then do nothing.
        if not self.is_valid():
            return base_shift_factor
        # Normalize ccnc counts if there are more than three counts  # QUESTION why 3?
        if len(self.raw_ccnc_counts) > 3:
            ccnc_counts = hf.smooth(ccnc_counts)
        # Find the ref index in the SMPS data. This is almost always accurate.
        self.ref_index_smps = hf.find_ref_index_smps(smps_counts, self.scan_up_time)
        if self.ref_index_smps is None:
            self.status = 0
            self.set_status_code(4)  # RESEARCH 4 Status Code
            return base_shift_factor
        # try to find the ref index in ccnc data. Very difficult
        self.ref_index_ccnc = hf.find_ref_index_ccnc(ccnc_counts, self.ref_index_smps + base_shift_factor)
        # if we did not manage to find and point that fits our target
        if self.ref_index_ccnc is None:
            self.status = 0
            self.set_status_code(5)  # RESEARCH 5 Status Code
            return base_shift_factor
        else:
            self.shift_factor = self.ref_index_ccnc - self.ref_index_smps
        return self.shift_factor

    def correct_charges(self):
        """
        Corrects the charges for the scan by resolving zeros to small values and correcting the charges via
        :class:`~fast_dp_calculator`
        """
        # scan is not usable, do nothing
        if not self.is_valid():
            return -1
        # Initiate some necessary variables
        ccnc = self.processed_ccnc_counts
        smps = self.processed_smps_counts
        ave_smps_dp = self.ave_smps_diameters
        # Basic Processing
        ccnc = hf.resolve_zeros(ccnc)
        smps = hf.resolve_zeros(smps)
        ccnc = hf.resolve_small_ccnc_vals(ccnc)
        # Make copies of the lists
        prev_ccnc = np.copy(ccnc)
        prev_smps = np.copy(smps)
        corrected_ccnc = np.copy(ccnc)
        corrected_smps = np.copy(smps)
        # Correct the charges
        for i in range(const.NUM_OF_CHARGES_CORR):
            ave_smps_dp, smps, ccnc, corrected_smps, corrected_ccnc, prev_smps, prev_ccnc = \
                fast_dp_calculator.correct_charges(
                    ave_smps_dp, smps, ccnc, corrected_smps, corrected_ccnc, prev_smps, prev_ccnc)
        # Save the smps and ccnc data after charge correction to new variables
        self.corrected_smps_counts = corrected_smps
        self.corrected_ccnc_counts = corrected_ccnc

    def cal_params_for_sigmoid_fit(self):
        """
        # REVIEW Documentation
        """
        # COMBAKL Sigmoid
        while True:
            # noinspection PyBroadException
            try:
                self.cal_params_for_sigmoid_fit_single_loop()
                break
            except Exception:  # RESEARCH error logging to determine what causes
                # widen the gap between the limits so that we can cover a larger area
                self.asym_limits = [self.asym_limits[0] - 0.1, self.asym_limits[1] + 0.1]

    def cal_params_for_sigmoid_fit_single_loop(self):
        """
        # REVIEW Documentation
        """
        # COMBAKL Sigmoid
        if not self.is_valid():
            return
        # Create clean lists
        self.sigmoid_params = []
        self.functions_params = []
        self.dps = []
        self.sigmoid_y_vals = []
        # Obtain an approximate ratio
        ratio_corrected = self.helper_get_ratio_corrected_smooth()
        # next, find min_dp by finding first point where all points before it are less than 0.1, with an error of 5%
        begin_rise = 0
        # Get the bottom inflation point. Great!
        for i in range(len(ratio_corrected) - 1, 1, -1):
            value = ratio_corrected[i]
            pre_values = ratio_corrected[:i]
            pre_percent = hf.cal_percentage_less(pre_values, value, 0.05)
            if value < 0.15 and pre_percent > 0.80:
                begin_rise = self.ave_smps_diameters[i]
                break
        # Get the top inflation point
        # -- get the top 10% of the data
        high_index_list = []
        for i in range(len(ratio_corrected)):
            if self.asym_limits[0] <= ratio_corrected[i] <= self.asym_limits[1]:
                high_index_list.append(i)
        high_list = ratio_corrected[high_index_list]
        high_index_list = hf.outliers_iqr(high_list, high_index_list)
        # if the return is an error/meaning we can't detect any outliers  # TODO issues/40 Better error handling
        # then we simply get the highest possible value from the array
        if high_index_list == -1:
            high_index_list = np.argmax(ratio_corrected)
        high_index_list = np.sort(high_index_list)
        # next, remove outliers
        top_inflation_index = high_index_list[0]
        last_dp_index = high_index_list[-1]
        # now, chose the last dp so that the std of the remaining data is within 0.1
        while True:
            if len(high_index_list) <= 2:
                break
            last_dp_index = high_index_list[-1]
            interested_list = ratio_corrected[top_inflation_index:last_dp_index]
            std = np.std(interested_list)
            if std <= (self.asym_limits[1] - self.asym_limits[0]) / 2:
                break
            else:
                high_index_list = high_index_list[:-1]
        end_rise = self.ave_smps_diameters[top_inflation_index]
        end_asymp = self.ave_smps_diameters[last_dp_index]
        self.sigmoid_params.append([begin_rise, end_rise, end_rise, end_asymp])

    def helper_get_ratio_corrected_smooth(self):
        """
        # REVIEW Documentation

        :return: # REVIEW Documentation
        :rtype: # REVIEW Documentation
        """
        # COMBAKL Sigmoid
        ratio_corrected = []
        ccnc = self.corrected_ccnc_counts
        smps = self.corrected_smps_counts
        # Smooth the corrections
        ccnc = hf.heavy_smooth(ccnc)
        smps = hf.heavy_smooth(smps)
        is_the_beginning = True
        # Take care of the case where there can be unreasonable ccnc data at the beginning
        for i in range(len(self.corrected_smps_counts)):
            if smps[i] > max(smps) // 20:
                is_the_beginning = False
            if is_the_beginning:
                ratio_corrected.append(0)
            else:
                ratio_corrected.append(hf.safe_div(ccnc[i], smps[i]))
        ratio_corrected = ratio_corrected[:len(self.ave_smps_diameters)]
        # Smooth the data
        ratio_corrected = hf.heavy_smooth(ratio_corrected)
        # Remove huge data points
        for i in range(len(ratio_corrected)):
            if ratio_corrected[i] > self.asym_limits[1]:
                if i > 0:
                    ratio_corrected[i] = ratio_corrected[i - 1]
                else:
                    ratio_corrected[i] = 0
        return ratio_corrected

    def fit_sigmoids(self):
        """
        # REVIEW Documentation
        """
        # COMBAKL Sigmoid
        if not self.is_valid():
            return
        self.functions_params = []
        self.sigmoid_y_vals = []
        self.dps = []
        for i in range(len(self.sigmoid_params)):
            self.fit_one_sigmoid(i)

    def fit_one_sigmoid(self, params_set_index):
        """
        # REVIEW Documentation

        :param params_set_index: # REVIEW Documentation
        :type params_set_index: # REVIEW Documentation
        """
        # COMBAKL Sigmoid
        begin_rise = self.sigmoid_params[params_set_index][0]
        end_rise = self.sigmoid_params[params_set_index][1]
        begin_asymp = self.sigmoid_params[params_set_index][2]
        end_asymp = self.sigmoid_params[params_set_index][3]
        ratio_corrected = hf.safe_div_array(self.corrected_ccnc_counts, self.corrected_smps_counts)
        # smooth the hell out of the data
        ratio_corrected = hf.heavy_smooth(ratio_corrected)
        # get b
        ave_list = []
        for i in range(len(self.ave_smps_diameters)):
            if begin_asymp < self.ave_smps_diameters[i] < end_asymp and self.asym_limits[0] < ratio_corrected[i] < \
                    self.asym_limits[1]:
                ave_list.append(ratio_corrected[i])
        b = hf.get_ave_none_zero(ave_list)
        if not self.asym_limits[0] <= b <= self.asym_limits[1]:
            b = 1

        def fn(x, dd, cc):
            """
            # REVIEW Documentation the function for which we will fit the sigmoid line for
            # RESEARCH Better variable names and function name

            :param x:
            :type x:
            :param dd:
            :type dd:
            :param cc:
            :type cc:
            :return:
            :rtype:
            """
            # COMBAKL Sigmoid
            return b / (1 + (x / dd) ** cc)

        x_list = []
        y_list = []
        # get all data points on the rise
        for i in range(len(self.ave_smps_diameters)):
            if begin_rise < self.ave_smps_diameters[i] < end_rise:
                x_list.append(self.ave_smps_diameters[i])
                y_list.append(ratio_corrected[i])
        # get all data points on the asymp
        for i in range(len(self.ave_smps_diameters)):
            if begin_asymp < self.ave_smps_diameters[i] < end_asymp:
                x_list.append(self.ave_smps_diameters[i])
                y_list.append(ratio_corrected[i])
        x_list = np.asarray(x_list)
        y_list = np.asarray(y_list)
        # noinspection PyBroadException
        try:
            # RESEARCH OptimizeWarning: Covariance of the parameters could not be estimated category=OptimizeWarning)
            result = opt.curve_fit(fn, x_list, y_list, bounds=([begin_rise, -200], [end_asymp + 1, -1]), method="trf")
            d = result[0][0]
            c = result[0][1]
        except Exception:  # RESEARCH error logging to determine what causes
            d = 60
            c = -2
        self.functions_params.append([b, d, c])
        dp_50 = d
        dp_50_wet = 0
        dp_50_20_wet = 0
        # find dp50 and dp50 wet
        for i in range(1, len(self.ave_smps_diameters)):
            if self.ave_smps_diameters[i] > d:
                dp_50_wet = self.processed_ave_ccnc_sizes[i - 1]
                break
        # find dp50 +20 (wet)
        for i in range(1, len(self.ave_smps_diameters)):
            if self.ave_smps_diameters[i] > d + 20:
                dp_50_20_wet = self.processed_ave_ccnc_sizes[i - 1]
                break
        sigmoid_points = [0]
        for i in range(1, len(self.ave_smps_diameters)):
            if begin_rise <= self.ave_smps_diameters[i] <= end_asymp:
                sigmoid_points.append(fn(self.ave_smps_diameters[i], d, c))
            else:
                sigmoid_points.append(sigmoid_points[i - 1])
        self.sigmoid_y_vals.append(sigmoid_points)
        dp_50 = round(dp_50, 3)
        dp_50_wet = round(dp_50_wet, 3)
        dp_50_20_wet = round(dp_50_20_wet, 3)
        self.dps.append([dp_50, dp_50_wet, dp_50_20_wet])
