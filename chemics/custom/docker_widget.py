"""
Creates the various widgets that display in the docker section of the display
"""
# External Packages
import datetime as dt
import PySide.QtCore as Qc
import PySide.QtGui as Qg

# Internal Packages
import custom.modal_dialogs as c_modal_dialogs
import custom.widget as c_widget


class DockerScanInformation(Qg.QFrame):
    """
    Creates the docker widget (docker = left pane) that displays the scan information.

    :param Controller controller: The controller for the current program
    """
    def __init__(self, controller):
        super(self.__class__, self).__init__()
        self.controller = controller
        # set up the layout
        form_layout = Qg.QFormLayout()
        self.setContentsMargins(-10, -10, 0, -10)
        form_layout.setContentsMargins(30, 20, 20, 0)
        self.setAutoFillBackground(True)
        palette = Qg.QPalette()
        palette.setColor(Qg.QPalette.Background, Qc.Qt.white)
        self.setPalette(palette)
        self.setFrameShape(Qg.QFrame.StyledPanel)
        self.setFrameShadow(Qg.QFrame.Plain)
        ########################################
        # Top Section - Experiment Information
        # -- add a title
        form_layout.addRow(c_widget.TitleHLine("Experiment Information"))
        # -- add date
        self.experiment_date = Qg.QLabel("-")
        self.experiment_date.setAlignment(Qc.Qt.AlignRight)
        form_layout.addRow("Date (m/d/y)", self.experiment_date)
        # -- add smps duration
        self.scan_duration = Qg.QLabel("-")  # TODO issues/5 Does not update when loading a project
        self.scan_duration.setAlignment(Qc.Qt.AlignRight)
        form_layout.addRow("Scan duration(s)", self.scan_duration)
        # -- add total numbe rof scan
        self.num_scan = Qg.QLabel("-")
        self.num_scan.setAlignment(Qc.Qt.AlignRight)
        form_layout.addRow("Number of scans", self.num_scan)
        # -- add Counts2ConcConv
        self.counts_2_conc_conv = Qg.QLabel("-")
        self.counts_2_conc_conv.setAlignment(Qc.Qt.AlignRight)
        form_layout.addRow("Counts2ConcConv", self.counts_2_conc_conv)  # DOCQUESTION Convert to complete sentence
        ########################################
        # Middle Section - Update Scan
        # -- add a title
        form_layout.addRow(c_widget.TitleHLine("Update Scan"))
        # -- add the scan selector
        self.scan_selector = c_widget.ArrowSpinBox(forward=True)
        self.scan_selector.set_callback(self.scan_index_changed)
        self.scan_selector.set_range(0, 0)
        form_layout.addRow("Scan number", self.scan_selector)
        # -- add the shift selector
        self.shift_selector = c_widget.ArrowSpinBox(forward=True)
        self.shift_selector.set_callback(self.shift_factor_changed)
        self.shift_selector.set_range(0, 0)
        form_layout.addRow("Shift (s)", self.shift_selector)
        # -- add the buttons
        # ---- add show data action
        self.show_data_button = Qg.QPushButton("Show Data")
        # noinspection PyUnresolvedReferences
        self.show_data_button.clicked.connect(self.show_data)  # RESEARCH connect unresolved ref
        # ---- add the enable/disable button
        self.enable_disable_button = Qg.QPushButton("Disable scan")
        # noinspection PyUnresolvedReferences
        self.enable_disable_button.clicked.connect(self.set_scan_enable_status)  # RESEARCH connect unresolved ref
        # form_layout.addRow(self.show_data_button, self.enable_disable_button)  # RESEARCH Put buttons on same line
        form_layout.addRow(self.enable_disable_button)
        form_layout.addRow(self.show_data_button)
        ########################################
        # Bottom Section - Scan Details
        # -- add a title
        form_layout.addRow(c_widget.TitleHLine("Scan Details"))
        # -- add the scan time
        self.scan_time = Qg.QLabel("-")
        self.scan_time.setAlignment(Qc.Qt.AlignRight)
        form_layout.addRow("Scan Time (h:m:s)", self.scan_time)
        # -- add the super saturation indicator
        self.super_saturation = Qg.QLabel("-")  # TODO issues/2 Update label when changing scans
        self.super_saturation.setAlignment(Qc.Qt.AlignRight)
        form_layout.addRow("Super Saturation (%)", self.super_saturation)
        # -- add the status of the scan
        self.scan_status = Qg.QLabel("-")
        self.scan_status.setAlignment(Qc.Qt.AlignRight)
        form_layout.addRow("Scan status", self.scan_status)
        # -- add the status of the scan
        form_layout.addRow("Additional Info", None)
        self.additional_information = Qg.QTextEdit("Welcome to Chemics!")
        self.additional_information.setReadOnly(True)
        self.additional_information.setAlignment(Qc.Qt.AlignLeft)
        form_layout.addRow(self.additional_information)
        # set the layout
        self.setLayout(form_layout)

    def update_scan_info(self):
        """
        Updates the scan detail section of the Scan Information widget
        """
        curr_scan = self.controller.scans[self.controller.curr_scan_index]
        # Update the Update Scan section
        self.scan_selector.set_value(self.controller.curr_scan_index)
        self.shift_selector.set_value(curr_scan.shift_factor)
        # Update the Scan Details section
        start_time = dt.date.strftime(curr_scan.start_time, "%H:%M:%S")
        end_time = dt.date.strftime(curr_scan.end_time, "%H:%M:%S")
        scan_time = start_time + " - " + end_time
        self.scan_time.setText(scan_time)
        # TODO issues/2 Update the Super Saturation
        self.super_saturation = curr_scan.processed_super_sats
        if curr_scan.is_valid():
            self.scan_status.setText("VALID")
            self.scan_status.setStyleSheet("QWidget { background-color:None}")
            self.additional_information.setText("The scan shows no problem.")
            self.enable_disable_button.setText("Disable scan")
        else:
            self.scan_status.setText("INVALID")
            self.scan_status.setStyleSheet("QWidget { color: white; background-color:red}")
            self.additional_information.setText(curr_scan.get_status_code_descript())
            self.enable_disable_button.setText("Enable scan")

    def update_experiment_info(self):
        """
        Updates the experiment information section of the Scan Information widget
        """
        # Get the number scans
        num_scan = len(self.controller.scans)
        # Update the values
        self.experiment_date.setText(self.controller.experiment_date)
        self.scan_duration.setText(str(self.controller.scan_duration))
        self.num_scan.setText(str(len(self.controller.scans)))
        self.counts_2_conc_conv.setText(str(self.controller.counts_to_conc_conv))
        # Set the Arrow Box ranges
        # DOCQUESTION Possible shift range correct?  [If dur=135, possible is -68-67]
        self.shift_selector.set_range(-self.controller.scans[0].duration // 2, self.controller.scans[0].duration // 2)
        self.scan_selector.set_range(0, num_scan - 1)  # TODO issues/5

    def scan_index_changed(self, new_scan_index):
        """
        Callback function set when a new scan is selected on the Scan Information docker widget.  It:

        - Sets the current scan index in the controller (:class:`~controller.Controller.set_scan_index`)
        - Switches to the new scan via the controller (:class:`~controller.Controller.switch_to_scan`)

        :param int new_scan_index: The new index to set in the the controller and view.
        """
        self.controller.set_scan_index(new_scan_index)  # RESEARCH shouldn't set index auto switch scan?  Why not?
        self.controller.switch_to_scan(new_scan_index)  # If so, this line is redundent

    def shift_factor_changed(self, new_shift_index):
        """
        Callback function set when the shift factor is changed on the Scan Information docker widget.  It:

        - Sets the shift factor on the scan (:class:`~scan.Scan.set_shift_factor`)
        - Reprocesses the data (:class:`~scan.Scan.generate_processed_data`)
        - Reloads the current scan into the display (:class:`~controller.Controller.switch_to_scan`)

        :param int new_shift_index: The new shift value to set in the controller
        """
        curr_scan = self.controller.scans[self.controller.curr_scan_index]
        curr_scan.set_shift_factor(new_shift_index)        # RESEARCH shouldn't set index auto update display?  Why not?
        curr_scan.generate_processed_data()                # If so, this may be redundent
        self.controller.switch_to_scan(self.controller.curr_scan_index)    # As well as this line

    def set_scan_enable_status(self):
        """
        Toggles the enabled status of a scan.  Updates the scan values and the scan information display.
        """
        # TODO issues/45 Update code when reworked scan status code
        if len(self.controller.scans) != 0:
            curr_scan = self.controller.scans[self.controller.curr_scan_index]
            # Scan is originally marked good
            if curr_scan.status == 1:
                curr_scan.status = 0
                curr_scan.set_status_code(9)
            else:
                curr_scan.status = 1
                curr_scan.set_status_code(0)
            if curr_scan.is_valid():
                self.scan_status.setText("VALID")
                self.scan_status.setStyleSheet("QWidget { background-color:None}")
                self.additional_information.setText(curr_scan.get_status_code_descript())
                self.enable_disable_button.setText("Disable this scan")
            else:
                self.scan_status.setText("INVALID")
                self.scan_status.setStyleSheet("QWidget { color: white; background-color:red}")
                self.additional_information.setText(curr_scan.get_status_code_descript())
                self.enable_disable_button.setText("Enable this scan")

    def show_data(self):
        """
        Shows the dialog box which displays the scan's data to the user
        (:class:`~custom.modal_dialogs.ScanDataDialog`)
        """
        if len(self.controller.scans) != 0:
            a_scan = self.controller.scans[self.controller.curr_scan_index]
            dialog = c_modal_dialogs.ScanDataDialog(a_scan)
            dialog.exec_()


class DockerSigmoidWidget(Qg.QFrame):
    """
    Creates the docker widget that appears on the left that shows scan information

    :param Controller controller: The Controller object that controls the program
    """
    def __init__(self, controller):
        # TODO issues/17 Add Scan information section
        # TODO issues/10 Add toggle to show or hide invalid scans
        super(self.__class__, self).__init__()
        self.controller = controller
        self.num_sigmoid_lines = 0
        self.dp_widgets = []
        self.curr_scan_index = self.controller.curr_scan_index
        # set up the layout
        form_layout = Qg.QFormLayout()
        self.setContentsMargins(-10, -10, 0, -10)
        form_layout.setContentsMargins(30, 20, 20, 0)
        self.setAutoFillBackground(True)
        palette = Qg.QPalette()
        palette.setColor(Qg.QPalette.Background, Qc.Qt.white)
        self.setPalette(palette)
        self.setFrameShape(Qg.QFrame.StyledPanel)
        self.setFrameShadow(Qg.QFrame.Plain)
        # Layout sigmoid parameters section
        # -- add the scan selector
        self.scan_selector = c_widget.ArrowSpinBox(forward=True)
        self.scan_selector.set_callback(self.scan_index_changed)
        form_layout.addRow("Scan number", self.scan_selector)
        # -- add the status of the scan
        self.scan_status = Qg.QLabel("-")
        self.scan_status.setAlignment(Qc.Qt.AlignRight)
        form_layout.addRow("Scan Status", self.scan_status)
        # -- add the params area
        self.sigmoid_line_spinbox = c_widget.ArrowSpinBox(forward=True)
        form_layout.addRow("Number of sigmoid lines", self.sigmoid_line_spinbox)
        self.sigmoid_line_spinbox.set_callback(self.num_sigmoids_changed)
        # -- Add the apply button
        button_boxes = Qg.QDialogButtonBox()
        self.apply_button = button_boxes.addButton("Apply", Qg.QDialogButtonBox.ApplyRole)
        self.apply_button.clicked.connect(self.apply_sigmoid_params)  # RESEARCH why no connect unresolved ref
        form_layout.addWidget(button_boxes)
        self.setLayout(form_layout)

    def num_sigmoids_changed(self, new_sigmoid_number):
        """
        Adds or removes Parameter Set widgets

        :param int new_sigmoid_number:  The new number of sigmoid lines
        """
        if new_sigmoid_number > self.num_sigmoid_lines:
            for i in range(new_sigmoid_number - self.num_sigmoid_lines):
                self.add_params_group_box()
        else:
            for i in range(self.num_sigmoid_lines - new_sigmoid_number):
                self.rem_params_group_box()

    def scan_index_changed(self, new_scan_index):
        """
        Callback function set when a new scan is selected on the Sigmoid docker widget.  It:

        - Sets the current scan index in the controller (:class:`~controller.Controller.set_scan_index`)
        - Switches to the new scan via the controller (:class:`~controller.Controller.switch_to_scan`)

        :param int new_scan_index: The scan index to display
        """
        self.controller.set_scan_index(new_scan_index)
        self.controller.switch_to_scan(new_scan_index)

    def update_scan_info(self):
        """
        Updates the Sigmoid Parameters widget.
        """
        # RESEARCH Find out why this method is being called twice every time a new scan is selected
        curr_scan = self.controller.scans[self.controller.curr_scan_index]
        num_scan = len(self.controller.scans)
        # Update the Sigmoid Parameters section
        self.scan_selector.set_range(0, num_scan - 1)
        self.scan_selector.set_value(self.controller.curr_scan_index)
        # Update the Scan status
        if curr_scan.is_valid():
            self.scan_status.setText("VALID")
            self.scan_status.setStyleSheet("QWidget { background-color:None}")
        else:
            self.scan_status.setText("INVALID")
            self.scan_status.setStyleSheet("QWidget { color: white; background-color:red}")
        # For all dp widgets on the screen, remove them
        for i in range(len(self.dp_widgets)):
            self.rem_params_group_box()
        # Set up for current scan's parameters
        self.num_sigmoid_lines = 0
        sigmoid_params = curr_scan.sigmoid_params
        dp_params = curr_scan.dps
        # For each set of sigmoid parameters, create a widget and increase num_of_sigmoid_lines by one
        for i in range(len(sigmoid_params)):
            a_sigmoid_param = sigmoid_params[i]
            a_dp_param = None
            # If dp parameters already exist, set with known values
            if i < len(dp_params):
                a_dp_param = dp_params[i]
            self.add_params_group_box(a_sigmoid_param, a_dp_param)

    def rem_params_group_box(self):
        """
        Reduces the number of Sigmoid Parameters by 1
        """
        # Reduce the number of sigmoid lines by one
        self.num_sigmoid_lines = max(self.num_sigmoid_lines - 1, 0)
        # Change the spinbox value
        self.sigmoid_line_spinbox.set_value(self.num_sigmoid_lines)
        # If there are still dp_widgets
        if len(self.dp_widgets) > 0:
            # RESEARCH This is too hardcoded to be flexible
            to_del = self.layout().takeAt(len(self.dp_widgets)+6)
            del self.dp_widgets[-1]
            to_del.widget().deleteLater()

    def add_params_group_box(self, sigmoid_params=None, dp_params=None):
        """
        Adds a sigmoid parameter set box which allows the user to adjust the sidmoid parameters lines and
        view the Dp50 values.

        :param list[int] sigmoid_params: A list containing the four interger values needed for the sigmoid parameters.

                                         - begin_rise_dp
                                         - end_rise_dp
                                         - begin_asymp_dp
                                         - end_asymp_dp)
        :param list[int] dp_params: A list containing the three interger values needed for the sigmoid parameters.

                                    - Dp50
                                    - Dp50_wet
                                    - Dp50+20 wet
        """
        # Set variable values
        if sigmoid_params is None:
            sigmoid_params = [0, 0, 0, 0]
        if dp_params is None:
            dp_params = [0, 0, 0]
        self.num_sigmoid_lines += 1
        maximum = max(self.controller.scans[self.curr_scan_index].ave_smps_diameters)  # QUESTION What should it be?
        # Update existing widgets
        self.sigmoid_line_spinbox.set_value(self.num_sigmoid_lines)
        # Create new sigmoid parameters widgets
        params_group_box = Qg.QGroupBox("Parameter Set #" + str(self.num_sigmoid_lines))
        begin_rise_dp = c_widget.LabeledDoubleSpinbox("begin rise dp")  # QUESTION Better label wording
        begin_rise_dp.set_maximum(maximum)
        begin_rise_dp.set_value(sigmoid_params[0])
        end_rise_dp = c_widget.LabeledDoubleSpinbox("end rise dp")  # QUESTION Better label wording
        end_rise_dp.set_maximum(maximum)
        end_rise_dp.set_value(sigmoid_params[1])
        begin_asymp_dp = c_widget.LabeledDoubleSpinbox("begin asymp dp")  # QUESTION Better label wording
        begin_asymp_dp.set_maximum(maximum)
        begin_asymp_dp.set_value(sigmoid_params[2])
        end_asymp_dp = c_widget.LabeledDoubleSpinbox("end asymp dp")  # QUESTION Better label wording
        end_asymp_dp.set_value(sigmoid_params[3])
        end_asymp_dp.set_maximum(maximum)
        v_layout = Qg.QVBoxLayout()
        v_layout.addWidget(begin_rise_dp)
        v_layout.addWidget(end_rise_dp)
        v_layout.addWidget(begin_asymp_dp)
        v_layout.addWidget(end_asymp_dp)
        # Create the DP50 parameters widgets
        h_layout = Qg.QHBoxLayout()
        dp_group_box = Qg.QGroupBox("Dp50 parameters")
        # -- dp50
        dp_50_label = Qg.QLabel("Dp50")
        dp_50_box = Qg.QLineEdit(str(dp_params[0]))
        dp_50_box.setReadOnly(True)
        another_v_layout = Qg.QVBoxLayout()
        another_v_layout.addWidget(dp_50_label)
        another_v_layout.addWidget(dp_50_box)
        h_layout.addLayout(another_v_layout)
        # TODO issues/16 Remove extra DP values
        # -- dp50 wet
        dp_50_wet_label = Qg.QLabel("Dp50_wet")
        dp_50_wet_box = Qg.QLineEdit(str(dp_params[1]))
        dp_50_wet_box.setReadOnly(True)
        another_v_layout = Qg.QVBoxLayout()
        another_v_layout.addWidget(dp_50_wet_label)
        another_v_layout.addWidget(dp_50_wet_box)
        h_layout.addLayout(another_v_layout)
        # -- dp50+20 wet
        dp_50_20_label = Qg.QLabel("Dp50+20 wet")
        dp_50_20_box = Qg.QLineEdit(str(dp_params[2]))
        dp_50_20_box.setReadOnly(True)
        another_v_layout = Qg.QVBoxLayout()
        another_v_layout.addWidget(dp_50_20_label)
        another_v_layout.addWidget(dp_50_20_box)
        h_layout.addLayout(another_v_layout)
        # Add various widgets to display
        dp_group_box.setLayout(h_layout)
        v_layout.addWidget(dp_group_box)
        params_group_box.setLayout(v_layout)
        self.dp_widgets.append([begin_rise_dp, end_rise_dp, begin_asymp_dp, end_asymp_dp])
        # RESEARCH Hard code-y values again for first parameter
        self.layout().insertRow(len(self.dp_widgets)+2, params_group_box)

    def apply_sigmoid_params(self):
        """
        Applies the sigmoid parameters and fits the new sigmoid line.
        """
        param_list = []

        for a_param_set in self.dp_widgets:
            begin_rise = a_param_set[0].content_box.value()
            end_rise = a_param_set[1].content_box.value()
            begin_asymp = a_param_set[2].content_box.value()
            end_asymp = a_param_set[3].content_box.value()
            param_list.append([begin_rise, end_rise, begin_asymp, end_asymp])
        # set the sigmoid parameters and fit new sigmoid lines
        self.controller.scans[self.controller.curr_scan_index].set_sigmoid_params(param_list)
        self.controller.switch_to_scan(self.controller.curr_scan_index)


class DockerKappaWidget(Qg.QFrame):
    """
    # REVIEW Documentation

    :param controller:
    :type controller:
    :param kappa_graph:
    :type kappa_graph:
    """
    def __init__(self, controller, kappa_graph):
        # COMBAKL Kappa
        super(self.__class__, self).__init__()
        self.controller = controller
        self.kappa_graph = kappa_graph
        # set up the layout
        v_layout = Qg.QVBoxLayout()
        self.setContentsMargins(-10, -10, 0, -10)
        v_layout.setContentsMargins(30, 20, 20, 0)
        self.setAutoFillBackground(True)
        palette = Qg.QPalette()
        palette.setColor(Qg.QPalette.Background, Qc.Qt.white)
        self.setPalette(palette)
        self.setFrameShape(Qg.QFrame.StyledPanel)
        self.setFrameShadow(Qg.QFrame.Plain)
        # Layout kappa values section
        # -- groupbox to control showing k lines
        show_k_lines_groupbox = Qg.QGroupBox("Kappa lines")
        self.show_all_lines_radio_button = Qg.QRadioButton("Show all lines")
        # noinspection PyUnresolvedReferences
        self.show_all_lines_radio_button.clicked.connect(self.show_all_k_lines)  # RESEARCH connect unresolved ref
        self.show_tight_lines_radio_button = Qg.QRadioButton("Show tight lines")
        # noinspection PyUnresolvedReferences
        self.show_tight_lines_radio_button.clicked.connect(self.show_tight_k_lines)  # RESEARCH connect unresolved ref
        self.show_all_lines_radio_button.setChecked(True)
        h_layout = Qg.QHBoxLayout()
        h_layout.addWidget(self.show_all_lines_radio_button)
        h_layout.addWidget(self.show_tight_lines_radio_button)
        show_k_lines_groupbox.setLayout(h_layout)
        v_layout.addWidget(show_k_lines_groupbox)
        # -- groupbox to control showing k points
        show_k_points_groupbox = Qg.QGroupBox("Kappa values")
        self.show_all_points_radio_button = Qg.QRadioButton("Show all Ks")
        # noinspection PyUnresolvedReferences
        self.show_all_points_radio_button.clicked.connect(self.show_all_k_points)  # RESEARCH connect unresolved ref
        self.show_ave_points_radio_button = Qg.QRadioButton("Show averge Ks")
        # noinspection PyUnresolvedReferences
        self.show_ave_points_radio_button.clicked.connect(self.show_ave_k_points)  # RESEARCH connect unresolved ref
        self.show_all_points_radio_button.setChecked(True)
        h_layout = Qg.QHBoxLayout()
        h_layout.addWidget(self.show_all_points_radio_button)
        h_layout.addWidget(self.show_ave_points_radio_button)
        show_k_points_groupbox.setLayout(h_layout)
        v_layout.addWidget(show_k_points_groupbox)
        # -- Show kappa data table
        self.kappa_data_table = c_widget.KappaTableWidget(self)
        v_layout.addWidget(self.kappa_data_table)
        self.setLayout(v_layout)

    def show_all_k_lines(self):
        """
        # REVIEW Documentation
        """
        # COMBAKL Kappa
        self.kappa_graph.update_all_klines()

    def show_tight_k_lines(self):
        """
        # REVIEW Documentation
        """
        # COMBAKL Kappa
        self.kappa_graph.update_tight_klines(self.controller.alpha_pinene_dict)

    def show_all_k_points(self):
        """
        # REVIEW Documentation
        """
        # COMBAKL Kappa
        self.kappa_graph.update_all_kappa_points(self.controller.alpha_pinene_dict,
                                                 self.controller.valid_kappa_points)

    def show_ave_k_points(self):
        """
        # REVIEW Documentation
        """
        # COMBAKL Kappa
        self.kappa_graph.update_average_kappa_points(self.controller.alpha_pinene_dict)

    def update_kappa_graph(self):
        """
        # REVIEW Documentation
        """
        # COMBAKL Kappa
        if self.show_all_points_radio_button.isChecked():
            self.show_all_k_points()
        else:
            self.show_ave_k_points()

    def toggle_k_points(self, ss, dp, state):
        """
        # REVIEW Documentation

        :param ss:
        :type ss:
        :param dp:
        :type dp:
        :param state:
        :type state:
        """
        # COMBAKL Kappa
        ss = float(ss)
        dp = float(dp)
        self.controller.set_kappa_point_state(ss, dp, state)
        self.kappa_data_table.set_status(ss, dp, self.controller.valid_kappa_points[(dp, ss)])

    def update_kappa_values(self):
        """
        # REVIEW Documentation
        """
        # COMBAKL Kappa
        for a_key in self.controller.kappa_calculate_dict.keys():
            a_scan = self.controller.kappa_calculate_dict[a_key]
            for aSS in a_scan:
                ss = a_key
                dp_50 = aSS[0]
                app_k = aSS[1]
                self.kappa_data_table.add_row(ss, dp_50, app_k, self.controller.valid_kappa_points[(dp_50, ss)])
