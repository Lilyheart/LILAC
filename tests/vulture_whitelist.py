"""
Whitelist for vulture package which checks for unused code

Use on the command line with `vulture chemics/ tests/vulture_whitelist.py`
"""

# noinspection PyStatementEffect
import export_data
import graphs
import helper_functions
import main
import scan

# noinspection PyStatementEffect,PyUnresolvedReferences
export_data.path_dir
# noinspection PyStatementEffect,PyUnresolvedReferences
export_data.m_value

# noinspection PyStatementEffect,PyUnresolvedReferences
graphs.xy

# noinspection PyStatementEffect,PyProtectedMember,PyUnresolvedReferences
helper_functions._instantiate

# noinspection PyStatementEffect
main.MainView.closeEvent
# noinspection PyStatementEffect
main.MainView.submit_feedback
# noinspection PyStatementEffect
main.MainView.show_error_message

# noinspection PyStatementEffect,PyUnresolvedReferences
scan.index_in_ccnc_data
# noinspection PyStatementEffect,PyUnresolvedReferences
scan.ref_index_smps
# noinspection PyStatementEffect,PyUnresolvedReferences
scan.ref_index_ccnc
