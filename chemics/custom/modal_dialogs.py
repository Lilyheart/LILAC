"""
Creates the various dialog boxes.
"""
# External Packages
from copy import deepcopy
import datetime as dt
import PySide.QtCore as Qc
import PySide.QtGui as Qg
# Internal Packages
import custom.widget as c_widget
import graphs


class SetBaseShiftDialog(Qg.QDialog):
    """
    Creates the dialog allowing the user to select what shift factor they wish to have automatically applied to the
    entire dataset.

    :param Controller controller: The controller object that controls the program
    """
    # TODO issues/27
    def __init__(self, controller):
        super(self.__class__, self).__init__()
        # The master layout
        form_layout = Qg.QFormLayout()
        self.scans = controller.scans
        self.controller = controller
        self.setWindowTitle("Choose a shift factor")
        self.curr_shift_factor = 0
        # Set up the groupbox which contains the graph of the scan
        # -- Start at the first valid scan
        self.curr_scan_index = 0
        while not self.scans[self.curr_scan_index].is_valid():
            self.curr_scan_index += 1
        # Set up the  graphs and add to the layout
        self.shift_graph = graphs.ConcOverTimeSmoothGraph()
        h_layout = Qg.QHBoxLayout()
        h_layout.addWidget(self.shift_graph)
        # Set up the graph box
        graph_group_box = Qg.QGroupBox()
        graph_group_box.setLayout(h_layout)
        form_layout.addRow(graph_group_box)
        # Create scan object that will have deepcopy scan placed in it in scan_index_changed
        self.a_good_scan = None
        # Set up the controls and populate the graph
        self.scan_control_box = c_widget.ArrowSpinBox(forward=True)
        self.scan_control_box.set_callback(self.scan_index_changed)
        self.scan_control_box.set_range(0, len(self.scans) - 1)
        self.scan_control_box.set_value(self.curr_scan_index)  # populates the graph
        form_layout.addRow("Select scan number", self.scan_control_box)
        # The area to control shifting
        self.shift_control_box = c_widget.ArrowSpinBox(forward=True)
        self.shift_control_box.set_callback(self.shift_factor_changed)
        self.shift_control_box.set_range(-self.scans[0].duration // 2, self.scans[0].duration // 2)
        self.shift_control_box.set_value(0)
        form_layout.addRow("Select shift factor (s)", self.shift_control_box)
        # the final accept button
        button_boxes = Qg.QDialogButtonBox()
        next_button = Qg.QPushButton(self.tr("&Apply"))
        next_button.setDefault(False)
        next_button.setAutoDefault(False)
        # noinspection PyUnresolvedReferences
        next_button.clicked.connect(self.apply)  # RESEARCH connect unresolved ref
        button_boxes.addButton(next_button, Qg.QDialogButtonBox.ApplyRole)
        form_layout.addWidget(button_boxes)
        self.setLayout(form_layout)

    @Qc.Slot(int)
    def scan_index_changed(self, new_scan_index):
        """
        Udpates the dialog when a new scan is selected and tags a PySide.QtCore.Slot.

        :param int new_scan_index: The index of the new scan to show
        """
        self.curr_scan_index = new_scan_index
        self.process_a_scan()

    def process_a_scan(self):
        """
        Creates a deepcopy of the selected scan and sets that copy's shift factor to the current shift factor
        """
        # Deep copy into new scan object to ensure original data isn't changed
        self.a_good_scan = deepcopy(self.scans[self.curr_scan_index])
        self.shift_factor_changed(self.curr_shift_factor)

    @Qc.Slot(int)
    def shift_factor_changed(self, new_factor):
        """
        Updates the dialog when a new shift factor is selected and tags a PySide.QtCore.Slot.

        :param int new_factor: The new shift factor
        """
        self.curr_shift_factor = new_factor
        # update shift factor in good scan
        self.a_good_scan.set_shift_factor(self.curr_shift_factor)
        # Generate_processed_data shifts the data based on the new shift factor
        self.a_good_scan.generate_processed_data()
        # Update the graph based on new shift factor
        self.shift_graph.update_graph(self.a_good_scan)

    def apply(self):
        """
        Accepts the dialog box and prompts the user to confirm they want the program to automatically align the data.
        If the user confirms, all the scans are adjusted with the new shift factor.  Otherwise nothing is shifted and
        the user can start a manual align process.

        On confirm, the following methods are run.

             * Update the base shift factor in the controller (:class:`~controller.Controller.set_base_shift_factor`)
             * Regenerate the scan data after shifting the data (:class:`~controller.Controller.align_smps_ccnc_data`)
        """
        self.accept()
        # New dialog box
        dialog = Qg.QMessageBox()
        dialog.setWindowTitle("Confirm Auto Alignment")
        dialog.setText("Are you sure you want to let the program to automatically align the data?")
        dialog.setIcon(Qg.QMessageBox.Question)
        dialog.addButton("Cancel", Qg.QMessageBox.RejectRole)
        confirm_button = dialog.addButton("Confirm", Qg.QMessageBox.AcceptRole)
        dialog.exec_()
        # If the user confirm.
        if dialog.clickedButton() == confirm_button:
            # set the base shift factor
            self.controller.set_base_shift_factor(self.curr_shift_factor)
            # align the SMPS And CCNC data
            self.controller.align_smps_ccnc_data()


class ScanDataDialog(Qg.QDialog):
    """
    Shows the scan's detailed data to the user

    :param Scan scan: The scan to show the data for.
    """
    # TODO issues/35
    def __init__(self, scan):
        super(self.__class__, self).__init__()
        # initiate the layout
        form_layout = Qg.QFormLayout()
        # scan status
        self.additional_information = Qg.QTextEdit("-")
        self.additional_information.setReadOnly(True)
        self.additional_information.setMaximumHeight(100)
        if scan.is_valid():
            self.scan_status = Qg.QLabel("VALID")
            self.scan_status.setStyleSheet("QWidget { background-color:None}")
            self.additional_information.setText("The scan shows no problem.")
        else:
            self.scan_status = Qg.QLabel("INVALID")
            self.scan_status.setStyleSheet("QWidget { color: white; background-color:red}")
            self.additional_information.setText(scan.get_status_code_descript())
        form_layout.addRow("Scan status", self.scan_status)
        form_layout.addRow("Status Info", self.additional_information)
        # Scan times and Duration
        h_layout = Qg.QHBoxLayout()
        time_group_box = Qg.QGroupBox()
        # -- Start time
        h_layout.addWidget(Qg.QLabel("Start time"))
        start_time = dt.datetime.strftime(scan.start_time, "%H:%M:%S")
        start_time_box = Qg.QLineEdit(start_time)
        start_time_box.setReadOnly(True)
        h_layout.addWidget(start_time_box)
        # -- End time
        h_layout.addWidget(Qg.QLabel("End Time"))
        end_time = dt.date.strftime(scan.end_time, "%H:%M:%S")
        end_time_box = Qg.QLineEdit(end_time)
        end_time_box.setReadOnly(True)
        h_layout.addWidget(end_time_box)
        # -- Duration
        h_layout.addWidget(Qg.QLabel("Duration"))
        duration = str(scan.duration)
        duration_box = Qg.QLineEdit(duration)
        duration_box.setReadOnly(True)
        h_layout.addWidget(duration_box)
        # Add widgets
        time_group_box.setLayout(h_layout)
        form_layout.addRow("Times and duration", time_group_box)
        self.setLayout(form_layout)


class SettingDialog(Qg.QDialog):
    """
    Allows the user to change the program's seetings.

    :param MainView main_view: The main view of the program.
    """
    # TODO issues/46
    def __init__(self, main_view):
        super(self.__class__, self).__init__()
        self.main_view = main_view
        form_layout = Qg.QFormLayout()
        ######################
        # Fonts
        h_layout = Qg.QHBoxLayout()
        self.font_selector = Qg.QFontComboBox()
        self.font_selector.setCurrentFont(Qg.QFont("Calibri"))
        # noinspection PyUnresolvedReferences
        self.font_selector.currentFontChanged.connect(self.font_changed)   # RESEARCH connect unresolved ref
        h_layout.addWidget(self.font_selector)
        self.size_selector = Qg.QSpinBox()
        self.size_selector.setValue(12)
        # noinspection PyUnresolvedReferences
        self.size_selector.valueChanged.connect(self.font_size_changed)  # RESEARCH connect unresolved ref
        h_layout.addWidget(self.size_selector)
        form_layout.addRow("Fonts", h_layout)
        ######################
        button_boxes = Qg.QDialogButtonBox()
        apply_button = button_boxes.addButton("Ok", Qg.QDialogButtonBox.AcceptRole)
        apply_button.clicked.connect(self.accept)
        form_layout.addWidget(button_boxes)
        self.setLayout(form_layout)

    def font_changed(self, font):
        """
        Updates the font style used throughout the program.  Does not include font used on charts.

        :param PySide.QtGui.QFont font: The new font style.
        """
        # RESEARCH Can it include the charts?
        self.main_view.set_font(font, self.size_selector.value())

    def font_size_changed(self, size):
        """
        Updates the font size used throughout the program.  Does not include font size used on charts.

        :param int size: The new font size
        """
        # RESEARCH Can it include the charts?
        self.main_view.set_font(self.font_selector.currentFont(), size)


class SelectParamsKappaDialog(Qg.QDialog):
    """
    # REVIEW Documentation

    :param controller:
    :type controller:
    """
    def __init__(self, controller):
        # COMBAKL Kappa
        super(self.__class__, self).__init__()
        self.controller = controller
        self.setWindowTitle("Select parameters for kappa calculation!")
        self.sigma_spinbox = Qg.QDoubleSpinBox()
        self.sigma_spinbox.setValue(self.controller.sigma)
        self.sigma_spinbox.setButtonSymbols(Qg.QAbstractSpinBox.NoButtons)
        self.temp_spinbox = Qg.QDoubleSpinBox()
        self.temp_spinbox.setValue(self.controller.temp)
        self.temp_spinbox.setButtonSymbols(Qg.QAbstractSpinBox.NoButtons)
        self.dd_1_spinbox = Qg.QDoubleSpinBox()
        self.dd_1_spinbox.setValue(self.controller.dd_1)
        self.dd_1_spinbox.setButtonSymbols(Qg.QAbstractSpinBox.NoButtons)
        self.dd_2_spinbox = Qg.QDoubleSpinBox()
        self.dd_2_spinbox.setValue(self.controller.dd_2)
        self.dd_2_spinbox.setButtonSymbols(Qg.QAbstractSpinBox.NoButtons)
        self.i_kappa_1_spinbox = Qg.QDoubleSpinBox()
        self.i_kappa_1_spinbox.setValue(self.controller.i_kappa_1)
        self.i_kappa_1_spinbox.setButtonSymbols(Qg.QAbstractSpinBox.NoButtons)
        self.i_kappa_2_spinbox = Qg.QDoubleSpinBox()
        self.i_kappa_2_spinbox.setValue(self.controller.i_kappa_2)
        self.i_kappa_2_spinbox.setButtonSymbols(Qg.QAbstractSpinBox.NoButtons)
        self.solubility_spinbox = Qg.QDoubleSpinBox()
        self.solubility_spinbox.setValue(self.controller.solubility)
        self.solubility_spinbox.setButtonSymbols(Qg.QAbstractSpinBox.NoButtons)
        form_layout = Qg.QFormLayout()
        form_layout.addRow(self.tr("&Sigma"), self.sigma_spinbox)
        form_layout.addRow(self.tr("&Temperature"), self.temp_spinbox)
        form_layout.addRow(self.tr("&dry diameter(1)"), self.dd_1_spinbox)
        form_layout.addRow(self.tr("&iKappa(1)"), self.i_kappa_1_spinbox)
        form_layout.addRow(self.tr("&dry diameter(2)"), self.dd_2_spinbox)
        form_layout.addRow(self.tr("&iKappa(2)"), self.i_kappa_2_spinbox)
        form_layout.addRow(self.tr("&solubility"), self.solubility_spinbox)
        button_boxes = Qg.QDialogButtonBox()
        apply_button = button_boxes.addButton("Apply", Qg.QDialogButtonBox.ApplyRole)
        apply_button.clicked.connect(self.apply)
        form_layout.addWidget(button_boxes)
        self.setLayout(form_layout)

    def apply(self):
        """
        # REVIEW Documentation
        """
        # COMBAKL Kappa
        # transfer all of the values to the controller
        self.controller.set_sigma(self.sigma_spinbox.value())
        self.controller.set_temp(self.temp_spinbox.value())
        self.controller.set_dd_1(self.dd_1_spinbox.value())
        self.controller.set_dd_2(self.dd_2_spinbox.value())
        self.controller.set_i_kappa_1(self.i_kappa_1_spinbox.value())
        self.controller.set_i_kappa_2(self.i_kappa_2_spinbox.value())
        self.controller.set_solubility(self.solubility_spinbox.value())
        self.accept()
        self.controller.cal_kappa()
