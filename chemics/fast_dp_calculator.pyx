"""
The fast_dp_calculator is written in cython to speed up the execution speed.
"""
import numpy as np
import scipy.constants
from numpy.lib import scimath
from libc.math cimport exp
cimport numpy as np
DTYPE = np.float64
ctypedef np.float64_t DTYPE_t

# QUESTION Confirm Correct
# The fast_dp_calculator is written in cython to speed up the execution speed.

# <editor-fold desc="find_dp">
def find_dp(long double dp, double lambda_air, int n):
    """
    # REVIEW Documentation

    :param long double dp: # REVIEW Documentation
    :param double lambda_air: # REVIEW Documentation
    :param int n: # REVIEW Documentation
    :return: # REVIEW Documentation
    :rtype: double
    """
    # QUESTION Background on this calculation?
    cdef long double dp_old = dp * 1 * n
    cdef long double c
    cdef long double dp_new
    cdef int i
    cdef double t
    for i in range(1000):
        t =  exp(-1.1 * dp_old / 2 / lambda_air)
        c =  1 + 2 * lambda_air / dp_old * (1.257 + 0.4 * t)
        dp_new = dp * c * n
        if abs(dp_new - dp_old) / dp_old < 0.000001:
            break
        else:
            dp_old = dp_new
    return dp_new
# </editor-fold>


# <editor-fold desc="calculate_fraction">
def calculate_fraction(np.ndarray a_list, int charge_number, np.ndarray coef_list=None):
    """
    # REVIEW Documentation

    :param ndarray a_list: # REVIEW Documentation
    :param int charge_number: # REVIEW Documentation
    :param ndarray coef_list: # REVIEW Documentation
    :return: # REVIEW Documentation
    :rtype: ndarray
    """
    # QUESTION Background on this calculation?
    new_list = []
    cdef double epsilon = 0.0000001
    cdef double e = scipy.constants.e
    cdef double e0 = scipy.constants.epsilon_0
    cdef double k = scipy.constants.k
    cdef double t = scipy.constants.zero_Celsius + 25
    cdef double z = 0.875
    cdef double p = 1013
    cdef double nair = 0.000001458 * t ** 1.5 / (t + 110.4)
    cdef double lambda_air = 2 * nair / 100 / p / (8 * 28.84 / scipy.constants.pi / 8.314 / t) ** 0.5 * 1000 ** 0.5

    if charge_number <= 2:
        for i in range(len(a_list)):
            l = scimath.log10(a_list[i])
            chare_sum = 0
            for j in range(len(coef_list)):
                chare_sum += coef_list[j] * l ** j
            new_list.append(10 ** chare_sum)
    else:
        for i in a_list:
            # divide the equation for easier processing
            f1 = e / scimath.sqrt(4 * scipy.constants.pi ** 2 * e0 * i * pow(10,-9) * k * t)
            f2 = -((charge_number - (2 * scipy.constants.pi * e0 * i * pow(10,-9) * k * t / e ** 2) * scimath.log(z)) ** 2)
            f3 = (4 * scipy.constants.pi * e0 * i * pow(10,-9) * k * t / e ** 2)
            value = f1 * exp(f2 / f3)
            new_list.append(value)
    return np.asarray(new_list)
# </editor-fold>


# <editor-fold desc="correct_charges">
def correct_charges(np.ndarray[DTYPE_t] particle_diameter_list, np.ndarray[DTYPE_t] cn_list,
                    np.ndarray[DTYPE_t] ccn_list, np.ndarray[DTYPE_t] cn_fixed_list, np.ndarray[DTYPE_t] ccn_fixed_list,
                    np.ndarray[DTYPE_t] g_cn_list, np.ndarray[DTYPE_t] g_ccn_list):
    """
    # REVIEW Documentation

    :param list[float] particle_diameter_list: The average smps dp.  The ave_smps_dp variable from the :class:`~scan.Scan` class object.
    :param list[float] cn_list: The smps variable from the :class:`~scan.Scan` class object.
    :param list[float] ccn_list: The ccnc variable from the :class:`~scan.Scan` class object.
    :param list[float] cn_fixed_list: The corrected_smps variable from the :class:`~scan.Scan` class object.
    :param list[float] ccn_fixed_list: The corrected_ccnc variable from the :class:`~scan.Scan` class object.
    :param list[float] g_cn_list: The prev_smps variable from the :class:`~scan.Scan` class object.
    :param list[float] g_ccn_list: The prev_ccnc variable from the :class:`~scan.Scan` class object.
    :return: Updated versions of all the lists send to the method in the same order
             (particle_diameter_list, cn_list, ccn_list, cn_fixed_list, ccn_fixed_list, g_cn_list, g_ccn_list).
    :rtype: (list[float], list[float], list[float], list[float], list[float], list[float], list[float])
    """
    # QUESTION Background on this calculation?
    cdef double asymp = 99999
    cdef double epsilon = 0.0000000001
    cdef double e = scipy.constants.e
    cdef double e0 = scipy.constants.epsilon_0
    cdef double k = scipy.constants.k
    cdef double t = scipy.constants.zero_Celsius + 25
    cdef double z = 0.875
    cdef double p = 1013
    cdef double nair = 0.000001458 * pow(t,1.5) / (t + 110.4)
    cdef double lambda_air = 2 * nair / 100 / p / pow((8 * 28.84 / scipy.constants.pi / 8.314 / t),0.5) * pow(1000,0.5)
    coeficient_list = [[-0.0003, -0.1014, 0.3073, -0.3372, 0.1023, -0.0105],
                      [-2.3484, 0.6044, 0.48, 0.0013, -0.1553, 0.032],
                      [-44.4756, 79.3772, -62.89, 26.4492, -5.748, 0.5049]]
    cdef int i
    cdef int j
    cdef int n
    cdef double max_upper_bin_bound
    cdef double move_doublet_counts
    cdef double move_triplet_counts
    cdef double lower_bin_bound
    cdef double upper_bin_bound
    cdef np.ndarray[DTYPE_t] frac1_list = calculate_fraction(particle_diameter_list, 1, np.asarray(coeficient_list[1]))
    cdef np.ndarray[DTYPE_t] frac2_list = calculate_fraction(particle_diameter_list, 2, np.asarray(coeficient_list[2]))
    cdef np.ndarray[DTYPE_t] frac3_list = calculate_fraction(particle_diameter_list, 3)
    charge_list = []

    for i in particle_diameter_list:
        ad_list = [0]
        for k in range(1, 4):
            c = i * pow(10,-9)
            c = 1 + 2 * lambda_air / c * (1.257 + 0.4 * exp(-1.1 * c / 2 / lambda_air))

            dp = pow(10,9) * find_dp(i * pow(10,-9) / c, lambda_air, k)
            ad_list.append(dp)
        charge_list.append(ad_list)
    # second part of correct charges
    cn_fixed_list = np.copy(cn_list)
    ccn_fixed_list = np.copy(ccn_list)
    max_upper_bin_bound = (particle_diameter_list[-1] + particle_diameter_list[-2]) / 2
    len_dp_list = len(particle_diameter_list)
    for i in range(len_dp_list):
        n = len_dp_list - i - 1
        move_doublet_counts = frac2_list[n] / (frac1_list[n] + frac2_list[n] + frac3_list[n]) * cn_list[n]
        move_triplet_counts = frac3_list[n] / (frac1_list[n] + frac2_list[n] + frac3_list[n]) * cn_list[n]
        cn_fixed_list[n] = cn_fixed_list[n] - move_doublet_counts - move_triplet_counts
        ccn_fixed_list[n] = ccn_fixed_list[n] - move_doublet_counts - move_triplet_counts
        if charge_list[n][2] <= max_upper_bin_bound:
            j = len_dp_list - 2
            while True:
                upper_bin_bound = (particle_diameter_list[j] + particle_diameter_list[j + 1]) / 2
                lower_bin_bound = (particle_diameter_list[j] + particle_diameter_list[j - 1]) / 2
                if upper_bin_bound > charge_list[n][2] >= lower_bin_bound:
                    cn_fixed_list[j] = cn_fixed_list[j] + move_doublet_counts
                    if charge_list[n][2] < asymp:
                        if g_ccn_list[j] > epsilon:
                            ccn_fixed_list[j] = ccn_fixed_list[j] + move_doublet_counts * \
                                                                              g_ccn_list[j] / \
                                                                              g_cn_list[j]
                    else:
                        ccn_fixed_list[j] = ccn_fixed_list[j] + move_doublet_counts
                    break
                j -= 1

        if charge_list[n][3] < max_upper_bin_bound:
            j = len_dp_list - 2
            while True:
                upper_bin_bound = (particle_diameter_list[j] + particle_diameter_list[j + 1]) / 2
                lower_bin_bound = (particle_diameter_list[j] + particle_diameter_list[j - 1]) / 2
                if upper_bin_bound > charge_list[n][3] >= lower_bin_bound:
                    cn_fixed_list[j] = cn_fixed_list[j] + move_triplet_counts
                    if charge_list[n][3] < asymp:
                        ccn_fixed_list[j] = ccn_fixed_list[j] + move_triplet_counts * ccn_list[j] / cn_list[j]
                    else:
                        ccn_fixed_list[j] = ccn_fixed_list[j] + move_triplet_counts
                    break
                j -= 1
    for i in range(len(ccn_fixed_list)):
        if ccn_fixed_list[i] / cn_fixed_list[i] < -0.01:
            ccn_fixed_list[i] = 0

    g_ccn_list = np.copy(ccn_fixed_list)
    g_cn_list = np.copy(cn_fixed_list)
    return particle_diameter_list,cn_list,ccn_list,cn_fixed_list,ccn_fixed_list,g_cn_list,g_ccn_list
# </editor-fold>
