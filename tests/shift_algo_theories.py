"""
Original ideas for the auto shifting
"""
import csv
# import matplotlib.pyplot as plt
import numpy as np
import scipy.fftpack
# import scipy.optimize
import scipy.signal
import warnings

# Load csv
with open("testdata/2raw_smps.csv") as csvFile:
    # Create a reader for the file
    reader = csv.reader(csvFile, delimiter=',')
    # Convert to list for easier processing
    all_raw_smps_counts = np.asarray(list(reader))

with open("testdata/2raw_ccnc.csv") as csvFile:
    # Create a reader for the file
    reader = csv.reader(csvFile, delimiter=',')
    # Convert to list for easier processing
    all_raw_ccnc_counts = np.asarray(list(reader))

if len(all_raw_ccnc_counts) != len(all_raw_ccnc_counts):
    print("Arrays are not the same length")
    quit()

all_smps_counts = all_raw_smps_counts.astype(float)
all_ccnc_counts = all_raw_ccnc_counts.astype(float)

all_pro2_ccnc_counts = []
for i in range(len(all_smps_counts)):
    with warnings.catch_warnings():
        warnings.simplefilter(action="ignore", category=FutureWarning)
        all_pro2_ccnc_counts.append(scipy.signal.savgol_filter(all_ccnc_counts[i], 5, 2))

test_index = 12
goal_value = 21

# pad_end = len(all_pro2_ccnc_counts[test_index]) - len(all_smps_counts[test_index])
# print(all_pro2_ccnc_counts[test_index].shape[0])
# print(np.pad(all_smps_counts[i], (0, pad_end), 'constant', constant_values=0)).shape[0])

print("\n======== Testing scipy.signal.correlate on index %d (Need %d) ========\n" % (test_index, goal_value))

with warnings.catch_warnings():
    warnings.simplefilter(action="ignore", category=FutureWarning)
    s2c_sscor = np.argmax(scipy.signal.correlate(all_smps_counts[test_index], all_pro2_ccnc_counts[test_index]))
    c2s_sscor = np.argmax(scipy.signal.correlate(all_pro2_ccnc_counts[test_index], all_smps_counts[test_index]))

# noinspection PyStringFormat
print("   scipy.signal.correlate test smps -> ccnc %d (off by %d)" % (s2c_sscor, goal_value-s2c_sscor))
# noinspection PyStringFormat
print("   scipy.signal.correlate test ccnc -> smps %d (off by %d)" % (c2s_sscor, goal_value-c2s_sscor))


print("\n======== Testing fftpack on index %d (Need %d) ========\n" % (test_index, goal_value))

pad_end = len(all_pro2_ccnc_counts[test_index]) - len(all_smps_counts[test_index])
s_fft = scipy.fftpack.fft(np.pad(all_smps_counts[test_index], (0, pad_end), 'constant', constant_values=0))
c_fft = scipy.fftpack.fft(all_pro2_ccnc_counts[test_index])
s_fft_r = -s_fft.conjugate()
c_fft_r = -c_fft.conjugate()

s2c_ssfft = np.argmax(np.abs(scipy.fftpack.ifft(s_fft_r*c_fft)))
c2s_ssfft = np.argmax(np.abs(scipy.fftpack.ifft(s_fft*c_fft_r)))

# noinspection PyStringFormat
print("   scipy.fftpack.fft test smps -> ccnc %d (off by %d)" % (s2c_ssfft, goal_value-s2c_ssfft))
# noinspection PyStringFormat
print("   scipy.fftpack.fft test ccnc -> smps %d (off by %d)" % (c2s_ssfft, goal_value-c2s_ssfft))


print("\n======== Manual ========\n")

# Smooth the curves some
# -- Totally random values picked here - further RESEARCH needed if going down this path.
all_smoothed_ccnc_counts = []
for i in range(len(all_smps_counts)):
    with warnings.catch_warnings():
        warnings.simplefilter(action="ignore", category=FutureWarning)
        all_smoothed_ccnc_counts.append(scipy.signal.savgol_filter(all_ccnc_counts[i], 7, 2))

all_smoothed_smps_counts = []
for i in range(len(all_smps_counts)):
    with warnings.catch_warnings():
        warnings.simplefilter(action="ignore", category=FutureWarning)
        all_smoothed_smps_counts.append(scipy.signal.savgol_filter(all_smps_counts[i], 7, 2))

# noinspection PyPep8
for i in range(0, len(all_smoothed_smps_counts)):

    # Get peak information
    smps_peak_index, smps_peak_heights = scipy.signal.find_peaks(all_smoothed_smps_counts[i], height=0, distance=20)
    ccnc_peak_index, ccnc_peak_heights = scipy.signal.find_peaks(all_smoothed_ccnc_counts[i], height=0, distance=20)

    print("smps_peak_index: " + str(smps_peak_index))
    print("smps_peak_heights: " + str(smps_peak_heights))
    print("ccnc_peak_index: " + str(ccnc_peak_index))
    print("ccnc_peak_heights: " + str(ccnc_peak_heights))

    smps_peak_heights = smps_peak_heights.get("peak_heights", "")
    ccnc_peak_heights = ccnc_peak_heights.get("peak_heights", "")

    # Check there are at least two peaks in both datasets.
    if len(smps_peak_index) < 2 or len(ccnc_peak_index) < 2:
        print("  Not enough peak data in scan %d" % i)
        continue

    # determine peak indices
    # -- In theory there should be one peak after the max peak, but in case of some more unusual
    # -- ccnc data, back up an index when neccessary
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

    print("SMPS: %d-%d   CCNC: %d-%d" % (smps_first_peak, smps_next_peak, ccnc_first_peak, ccnc_next_peak))

    # Get length of data based on peaks
    ccnc_mid_length = ccnc_next_peak - ccnc_first_peak

    # The ultimate maximum number of iterations for find the minimized value would be perfectly aligning
    # -- the ccnc peak under the smps peak.  Generally a significate less number of iterations are run
    max_iter = ccnc_first_peak - smps_first_peak

    # If the length of smps data is close to the length of ccnc data, add a few more iterations
    # -- Minimum 5 iterations [Another Arbitrary Magic Number  # RESEARCH]
    smpsccnc_peak_len_diff = max(0, 5 - abs((ccnc_next_peak - ccnc_first_peak) - (smps_next_peak - smps_first_peak)))
    max_iter += smpsccnc_peak_len_diff

    #: List[float] which stores the area between the curves over the shifting iterations
    total_area = []
    # Repeat for the number of iterations or until the smps end index > smps_next_peak
    # -- When this happens we would end up pulling and fitting data past the second peak.
    for j in range(max_iter):
        # Determine Ranges
        # -- Generally the CCNC peak to peak distance is smaller.
        # -- Compare the number of points in the SMPS and CCNC data sets equal to the the CCNC peak to peak distance.
        # -- Start with a shift that would put the CCNC peak under the SMPS peak [This is an over correction]
        # -- -- Get the full set of CCNC peak to peak data points
        # -- -- Get only the SMPS points that would correlate to the CCNC data points for this shift iteration
        # -- -- This means the same CCNC data is used every iteration but the SMPS data shifts up the line each time
        # -- --     until the end SMPS point is the same as the peak after the max peak.
        smps_frst_index = j + smps_first_peak - smpsccnc_peak_len_diff
        smps_last_index = j + smps_first_peak + ccnc_mid_length - smpsccnc_peak_len_diff
        ccnc_frst_index = ccnc_first_peak
        ccnc_last_index = ccnc_first_peak + ccnc_mid_length

        # When the SMPS data pulls past the next peak, stop iterating on this scan.
        if smps_last_index > smps_next_peak:
            break

        # Get middle data for comparison
        smps_middle_data = all_smoothed_smps_counts[test_index][smps_frst_index:smps_last_index]
        ccnc_middle_data = all_smoothed_ccnc_counts[test_index][ccnc_frst_index:ccnc_last_index]

        # plt.plot(smps_middle_data)
        # plt.plot(ccnc_middle_data)
        # plt.show()

        # Get area between the curves
        s_subt_c = smps_middle_data - ccnc_middle_data
        # -- Find where lines cross, if any
        data_crosses = np.sign(s_subt_c[:-1] * s_subt_c[1:])
        # -- Setup formulas for where
        x_isects = np.arange(0, (ccnc_mid_length - 1)) - (s_subt_c[:-1] / (s_subt_c[1:] - s_subt_c[:-1]))
        dx_isects = - np.ones(ccnc_mid_length - 1) / (s_subt_c[1:] - s_subt_c[:-1]) * s_subt_c[:-1]
        # -- Area using Trapezoidal Rule
        areas_no_isects = (0.5 * abs(s_subt_c[:-1] + s_subt_c[1:]))
        areas_of_isects = (0.5 * dx_isects * abs(s_subt_c[:-1]))
        areas_of_isects += (0.5 * (np.ones(ccnc_mid_length - 1)) - dx_isects) * abs(s_subt_c[1:])
        # -- Calculate the areas of all the points, sum them and add them to the total area list for this scan
        total_area.append(np.sum(np.where(data_crosses > 0, areas_no_isects, areas_of_isects)))

    # After completing all the iterations, find the shift that minimized the area between the curves.
    proposed_shift = 0
    if len(total_area) == 0:
        print("    %d: Proposed shift is unknown" % i)
    else:
        proposed_shift = max_iter - np.argmin(total_area)
        print("    %d: Proposed shift of %d" % (i, proposed_shift))
