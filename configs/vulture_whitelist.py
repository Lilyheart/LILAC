"""
Whitelist for vulture package which checks for unused code

Use on the command line with `vulture chemics/ tests/vulture_whitelist.py`
"""

# noinspection PyStatementEffect
import algorithm
import export_data
import graphs
import helper_functions
import main
import scan


# noinspection PyStatementEffect,PyUnresolvedReferences
algorithm.sigmoid_fit.pcov  # Returns from curve_fit but is unneeded.


# noinspection PyStatementEffect,PyUnresolvedReferences
export_data.path_dir  # Part of os.walk but is unneeded.
# noinspection PyStatementEffect,PyUnresolvedReferences
export_data.m_value  # Part of `in class_methods` but is unneded


# noinspection PyStatementEffect,PyUnresolvedReferences
graphs.xy  # False positive - Is actually setting value on graph


# noinspection PyStatementEffect,PyUnresolvedReferences,PyProtectedMember
helper_functions.CustomUnpickler._instantiate  # False positive - Used for unpickling projects


# noinspection PyStatementEffect
main.MainView.closeEvent  # False postive - Is actually overloading when the close button in the app is pressed
# noinspection PyStatementEffect
main.MainView.show_error_message  # Currently unused function


# noinspection PyStatementEffect,PyUnresolvedReferences
scan.version  # False positive - Used for unpickling projects
# noinspection PyStatementEffect,PyUnresolvedReferences
scan.index  # RESEARCH - Actually Unused?
# noinspection PyStatementEffect,PyUnresolvedReferences
scan.scan_up_time  # RESEARCH - Actually Unused?
# noinspection PyStatementEffect,PyUnresolvedReferences
scan.scan_down_time  # RESEARCH - Actually Unused?
# noinspection PyStatementEffect,PyUnresolvedReferences
scan.processed_ave_ccnc_sizes  # RESEARCH - Actually Unused?
# noinspection PyStatementEffect,PyUnresolvedReferences
scan.sigmoid_y_vals  # RESEARCH - Actually Unused?
