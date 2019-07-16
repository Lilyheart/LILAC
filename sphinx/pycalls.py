"""
Creates visalization of the call graph
"""
from pycallgraph import PyCallGraph
from pycallgraph.output import GraphvizOutput
import PySide.QtGui as Qg
import sys

import main

# Setup
graphviz = GraphvizOutput()
count = 1

# Initalize Chemics
# filename = "callgraphs/" + str(count) + "init.png"
# filename = "source/callgraphs/test.png"
filename = "source/callgraphs/" + str(count) + "-init.png"
graphviz.output_file = filename
count += 1
with PyCallGraph(output=graphviz):
    app = Qg.QApplication(sys.argv)
    main_window = main.MainView(app)

# Open File
filename = "source/callgraphs/" + str(count) + "-open.png"
graphviz.output_file = filename
count += 1
with PyCallGraph(output=graphviz):
    main_window.open_files()

