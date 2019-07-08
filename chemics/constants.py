"""
Constants used throughout the program.
"""

#: Used in the steps to get the CCNC count
BIN_SIZES = [0.625, 0.875, 1.25, 1.75, 2.25, 2.75, 3.25, 3.75, 4.25, 4.75, 5.25, 5.75, 6.25, 6.75, 7.25,
             7.75, 8.25, 8.75, 9.25, 9.75]

# RESEARCH Use of this may go away when sigmoid calculation is reviewed
#: Very small number used to resolve zeros
EPSILON = 0.000001

#: # QUESTION What the background behind this constant?
NUM_OF_CHARGES_CORR = 8

#: Used during calculating the shift amount in a scan.  The total area between SMPS and CCNC data, when the SMPS data
# is greater, is multipled by this weight.  This value was determined empirically.
HIGH_SMPS_WEIGHT = 1

#: Used during calculating the shift amount in a scan.  The total area between SMPS and CCNC data, when the CCNC data
# is greater, is multipled by this weight.  This value was determined empirically.
HIGH_CCNC_WEIGHT = 2.2
