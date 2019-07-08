"""
Run the shift algo by supplying an smps and ccnc csv file names
"""
import csv
import numpy as np
import shift_algo

smps_file = "../chemics/output_smps.csv"
ccnc_file = "../chemics/output_ccnc.csv"

with open(smps_file, 'r') as csvFile:
    # Create a reader for the file
    reader = csv.reader(csvFile, delimiter=',')
    # Convert to list for easier processing
    all_raw_smps_counts = np.asarray(list(reader))

with open(ccnc_file, 'r') as csvFile:
    # Create a reader for the file
    reader = csv.reader(csvFile, delimiter=',')
    # Convert to list for easier processing
    all_raw_ccnc_counts = np.asarray(list(reader))

all_pro1_smps = np.asarray(all_raw_smps_counts).astype(float)
all_pro1_ccnc = np.asarray(all_raw_ccnc_counts).astype(float)

debug = {"data": False, "peaks": False, "iter_details": False, "plot": False}
index = None

weights = [1, 2.2]

shifts = shift_algo.process_autoshift(all_pro1_smps, all_pro1_ccnc, weights=weights, index=index, debug=debug)

print(shifts.to_string())

# O3 (150), VOC (150) TRIAL 6
# pref_index = [0, 0, 0, 13, 13, 0, 0, 13, 13, 13, 0, 0, 0, 0, 13, 0, 13, 0, 13, 14, 14, 0, 13, 13, 0, 13, 0, 0, 13, 13,
#               13, 0, 13, 13, 13, 13, 12, 0, 0, 13, 13, 13, 0, 0, 12, 12, 12, 0, 0, 13, 13, 13, 13, 0, 12, 12, 12, 12,
#               0, 0, 13, 13, 13, 0, 0, 0, 0, 0, 13, 0]

# # Amm Sulf (0.1gL) Kappa Test
# pref_index = [25, 21, 21, 21, 0, 0, 23, 23, 23, 23, 0, 21, 21, 21, 21, 0, 0, 23, 23, 23, 0, 0, 21, 21, 21, 21, 0, 0,
#               23, 23, 23, 0, 21, 21, 21, 21, 0, 0, 23, 23, 23, 23, 0, 21, 21, 21, 21, 0, 0, 23, 22, 22, 0, 0, 21]
#
# overall_best_score = 92.11
# overall_best_scores = []
#
# start_weight = .1
# offset = 4  # 0 1 2 3 4
# weights = [start_weight + offset, start_weight]
# loop_range = range(len(pref_index))
#
# while weights[0] <= 1 + offset:
#     weights[1] = start_weight
#     curr_best_score = 0
#
#     while weights[1] <= 5:
#         shifts = shift_algo.process_autoshift(all_pro1_smps, all_pro1_ccnc, weights=weights, index=index, debug=debug)
#
#         correct = 0.0
#         total = 0.0
#         for i in loop_range:
#             if pref_index[i] == 0:
#                 continue
#             total += 1
#             if shifts.iloc[i]["shift"] == pref_index[i]:
#                 correct += 1
#
#         score = round((correct / total) * 100, 2)
#
#         # Set best scores
#         if score > overall_best_score:
#             overall_best_score = score
#             overall_best_scores = [weights[:]]
#         elif score == overall_best_score:
#             overall_best_scores += [weights[:]]
#
#         # test for skipping value
#         if curr_best_score == 0:
#             curr_best_score = score
#         if score > curr_best_score:
#             curr_best_score = score
#         elif score < (curr_best_score * .75):
#             print("Stopping current run")
#             break
#
#         print("Weights %.1f-%.1f have %.2f%% correct" % (weights[0], weights[1], score))
#         weights[1] = round(weights[1] + .1, 1)
#
#     print("Best Score: %.2f" % overall_best_score)
#     print(overall_best_scores)
#
#     weights[0] = round(weights[0] + .1, 1)
#
# print("Overall Best Score: %.2f" % overall_best_score)
# print(overall_best_scores)

