"""
The main entry point of the program
"""
# External Packages
import datetime
import logging
import os
import PySide.QtCore as Qc
import PySide.QtGui as Qg
import sys
import webbrowser

# Internal Packages
import controller
import custom.central_widget as c_central_widget
import custom.docker_widget as c_dock_widget
import custom.modal_dialogs as c_modal_dialogs
import graphs
import logging_config


##############
# Setup Code #
##############

# Determine if running in pyinstaller bundle or python environment
#   Debugger
#      If frozen, log to both black box and a log file
#      If running in nomal environment, only display in console
#   Test Environment
#      If frozen, do not show any testing features
#      If running in nomal environment, preset folders and allow exporting of data
if getattr(sys, 'frozen', False):  # we are running in a |PyInstaller| bundle
    logging_config.configure_logger_frz("Chemicslog-" + datetime.datetime.now().strftime("%Y-%m-%d") + ".log")
    isTest = False
else:  # we are running in a normal Python environment
    logging_config.configure_logger_env()
    isTest = True

logger = logging.getLogger("main")

########
# Main #
########


class MainView(Qg.QMainWindow):  # REVIEW Code Class
    """
    Initialzes the main window of the program.
    """

    def __init__(self, main_app):
        # Initalize the window
        Qg.QMainWindow.__init__(self)
        # Basic window settings
        self.setWindowTitle('Chemics')
        self.font = Qg.QFont("Calibri")
        main_app.setFont(self.font)
        # Create the controller that handles all of the functionalities of the program
        self.controller = controller.Controller(self)
        # create menu bar
        self.file_menu, self.action_menu, self.window_menu = self.create_menus()
        self.set_menu_bar_by_stage()
        # Create graph objects
        self.raw_conc_time_graph = graphs.ConcOverTimeRawDataGraph()
        self.smoothed_conc_time_graph = graphs.ConcOverTimeSmoothGraph()
        self.temp_graph = graphs.TemperatureGraph()
        self.ratio_dp_graph = graphs.RatioOverDiameterGraph()
        self.kappa_graph = graphs.KappaGraph()
        # create left dock widget for information related stuff
        [self.scaninfo_docker_widget, self.sigmoid_docker_widget,
         self.kappa_docker, self.kappa_docker_widget] = self.create_left_docker()
        # set options for left doc
        dock_options = Qg.QMainWindow.VerticalTabs | Qg.QMainWindow.AnimatedDocks | Qg.QMainWindow.ForceTabbedDocks
        self.setDockOptions(dock_options)
        # create central widget
        [self.stacked_central_widget, self.central_widget_alignscan,
         self.central_widget_kappa] = self.create_central_widget()
        # create progress bar
        self.progress_dialog = self.create_progress_bar()
        # showMaximized must be at end of init
        self.showMaximized()
        self.reset_view()
        if isTest:  # TEST
            self.open_files()

    ########
    # Menu #
    ########

    def create_menus(self):
        """
        Creates the menu bar for the main view

        :returns:
            - **file_menu** - Qg.QMenu object that allows the user to open and save files and projects.
            - **action_menu** - Qg.QMenu object that allows the user to preform actions on the data
            - **window_menu** -  Qg.QMenu object that allows the user to turn windows on and off
            - **help_menu** - Qg.QMenu object that allows the user to access settings and help information
        """
        # Add file menu
        file_menu = Qg.QMenu("&File")
        new_action = Qg.QAction('&New Project from Files...', self, shortcut="Ctrl+N", triggered=self.open_files)
        open_action = Qg.QAction('&Open Existing Project...', self, triggered=self.open_project)
        save_action = Qg.QAction('&Save Project', self, shortcut="Ctrl+S", triggered=self.save_project)
        save_as_action = Qg.QAction('Save Project &As', self, triggered=self.save_project_as)
        export_data_action = Qg.QAction('Export &Kappa Data', self, triggered=self.export_project_data)
        exit_action = Qg.QAction('&Exit', self, shortcut="Ctrl+E", triggered=self.exit_run)
        file_menu.addAction(new_action)
        file_menu.addSeparator()
        file_menu.addActions([open_action, save_action, save_as_action, export_data_action])
        file_menu.addSeparator()
        file_menu.addAction(exit_action)
        self.menuBar().addMenu(file_menu)
        # Add action menu
        action_menu = Qg.QMenu("&Actions")
        preview_all_action = Qg.QAction('&Preview all scans', self, triggered=self.preview_all_scans)
        auto_align_action = Qg.QAction('Auto &Shift', self, triggered=self.show_auto_align_dialog)
        correct_charges = Qg.QAction('Correct Charges &All Scans', self, triggered=self.correct_charges)
        correct_charges_one = Qg.QAction('Correct Charges &One Scan', self, triggered=self.correct_charges_one)
        auto_fit_action = Qg.QAction('Auto &Fit Sigmoid All Scans', self, triggered=self.show_auto_fit_sigmoid_dialog)
        auto_fit_one_action = Qg.QAction('Auto F&it Sigmoid One Scan', self, triggered=self.auto_fit_sigmoid_one)
        cal_kappa_action = Qg.QAction('&Calculate Kappa', self, triggered=self.show_kappa_params_dialog)
        action_menu.addAction(preview_all_action)
        action_menu.addSeparator()
        action_menu.addActions([auto_align_action, correct_charges, correct_charges_one,
                                auto_fit_action, auto_fit_one_action])
        action_menu.addSeparator()
        action_menu.addAction(cal_kappa_action)
        self.menuBar().addMenu(action_menu)
        # Add window menu
        window_menu = Qg.QMenu("&Windows")
        self.menuBar().addMenu(window_menu)
        # Add Help menu
        help_menu = Qg.QMenu("&Help")
        setting_action = Qg.QAction('&Settings', self, triggered=self.show_setting_dialog)
        # TODO issues/23 User Manual help menu item
        user_manual_action = Qg.QAction('&User Manual', self, triggered=self.open_user_manual)
        about_action = Qg.QAction('&About', self, triggered=self.open_about)
        # TODO issues/23 Feedback help menu item
        help_menu.addActions([setting_action, user_manual_action])
        help_menu.addSeparator()
        help_menu.addAction(about_action)
        self.menuBar().addMenu(help_menu)
        # Add Test menu
        test_menu = Qg.QMenu("&Test")
        if isTest:  # TEST
            export_scans = Qg.QAction('Export Scans', self, triggered=self.export_scans)
            test_menu.addAction(export_scans)
            self.menuBar().addMenu(test_menu)
        return file_menu, action_menu, window_menu

    def set_menu_bar_by_stage(self):
        """
        Enables and Disables file menu items based on the stage that the :class:`~controller.Controller` is in.
        """
        # reset to visible
        self.file_menu.setEnabled(True)
        self.action_menu.setEnabled(True)
        self.window_menu.setEnabled(True)
        for an_action in self.file_menu.actions():
            an_action.setEnabled(True)
        for an_action in self.action_menu.actions():
            an_action.setEnabled(True)
        for an_action in self.window_menu.actions():
            an_action.setEnabled(True)
        # disable by stage
        if self.controller.stage == "init":
            # file menu
            file_action_list = self.file_menu.actions()  # TODO - Find better way to reference
            file_action_list[3].setDisabled(True)  # Disable Save Project
            file_action_list[4].setDisabled(True)  # Disable Save Project As
            file_action_list[5].setDisabled(True)  # Disable Export Kappa Data
            # action menu
            self.action_menu.setDisabled(True)
            # window menu
            self.window_menu.setDisabled(True)
        elif self.controller.stage == "align":
            # file menu - none disabled
            # action menu
            action_list = self.action_menu.actions()  # TODO - Find better way to reference
            action_list[4].setDisabled(True)  # Disable Correct charges one scan
            action_list[5].setDisabled(True)  # Disable Autofit sigmoid
            action_list[8].setDisabled(True)  # Disable calculate Kappa
            # window menu - none disable
        elif self.controller.stage == "sigmoid":
            # file menu - none disabled
            # action menu - none disabled
            # window menu - none disable
            pass
        elif self.controller.stage == "kappa":
            # file menu - none disabled
            # action menu - none disabled
            # window menu - none disable
            pass
        # TODO Delete this once smoothing algo has been expanded

    ##############
    # MENU ITEMS #
    ##############

    # File menu items

    def open_files(self):
        """
        Opens data files and begins the scan alignment process
        """
        if isTest:  # TEST
            open_dir = "../../TestData/Penn State 2019/caryophellen (150), ozone (200), dry seeding/Analysis"
        else:
            open_dir = ""
        # noinspection PyCallByClass
        files = Qg.QFileDialog.getOpenFileNames(self, "Open files", open_dir, "Data files (*.csv *.txt)")[0]
        if files:
            # read in new files
            self.controller.start(files)
            self.setWindowTitle("Chemics: " + self.controller.get_project_name())

    def open_project(self):
        """
        Opens a previously saved project and load the information that was stored at the time.

        See :class:`~controller.Controller.save_project` in the Controller class.
        """
        if isTest:  # TEST
            open_dir = "../../TestData/Saved Chemics Files"
        else:
            open_dir = ""
        # noinspection PyCallByClass
        run_file = Qg.QFileDialog.getOpenFileName(self, "Open file", open_dir, "Project files (*.chemics)")[0]
        if run_file:
            # read in new files
            self.controller.load_project(run_file)
            self.setWindowTitle("Chemics: " + self.controller.get_project_name())

    def save_project(self):
        """
        Saves the current open project to the disk
        """
        self.controller.save_project()

    def save_project_as(self):
        """
        Allows the user to select a save name and saves the current open project to the disk
        """
        # Get file name
        file_name = self.controller.project_folder + "/"
        file_name += self.controller.get_project_name() + ".chemics"
        # noinspection PyCallByClass
        project_file = Qg.QFileDialog.getSaveFileName(self, "Save file", file_name, "Project files (*.chemics)")[0]
        if project_file:
            # append file extention if neccessary
            if not project_file.endswith(".chemics"):
                project_file += ".chemics"
            # Save files
            self.controller.set_save_name(project_file)
            self.controller.save_project()

    def export_project_data(self):
        """
        Exports the final kappa project data
        """
        # TODO issues/11
        file_name = self.controller.project_folder + "/kappa_"
        file_name += self.controller.get_project_name() + ".csv"
        # noinspection PyCallByClass
        export_file = Qg.QFileDialog.getSaveFileName(self, "Save file", file_name, "*.csv")[0]
        if export_file:
            # append file extention if neccessary
            if not export_file.endswith(".csv"):
                export_file += ".csv"
            # Save files
            self.controller.export_project_data(export_file)

    def closeEvent(self, event):
        """
        Overwrites base closeEvent function to execute the :class:`~main.MainView.exit_run` method.
        """
        self.exit_run()

    def exit_run(self):
        """
        Displays the dialog box asing if the user wishes to truly exit the program.  The
        QT app is quit if the user selects yes.  Otherwise, no action is taken.
        """
        if self.controller.data_files is None:
            app.quit()
        dialog = Qg.QMessageBox()
        dialog.setWindowTitle("Exit")
        dialog.setText("Do you really wish to exit the program")
        dialog.setIcon(Qg.QMessageBox.Question)
        yes_button = dialog.addButton("Exit", Qg.QMessageBox.AcceptRole)
        save_button = dialog.addButton("Save then exit", Qg.QMessageBox.AcceptRole)
        dialog.addButton("Cancel", Qg.QMessageBox.RejectRole)
        dialog.exec_()
        if dialog.clickedButton() == yes_button:
            app.quit()
        elif dialog.clickedButton() == save_button:
            self.save_project()
            app.quit()

    def export_scans(self):  # TEST
        """
        # REVIEW Documentation
        """
        if isTest:
            filename = os.path.basename(os.path.normpath(self.controller.project_folder)) + "-exported"
            self.controller.export_scans(filename)

    # Action menu items

    def preview_all_scans(self):
        """
        Cycles through the scan starting from zero and then returns to the scan on when triggered
        """
        # noinspection PyCallByClass
        timer, ok = Qg.QInputDialog.getDouble(self, "Time of each preview",
                                              "Enter the amount of pause time between each scan",
                                              value=0.5, minValue=0.1, maxValue=3, decimals=1)
        if timer and ok:
            self.controller.preview_scans(timer)

    def show_auto_align_dialog(self):
        """
        Shows the auto align dialog box.

        :return: The result of the dialog execution
        :rtype: int
        """
        if len(self.controller.scans) == 0:
            self.show_error_by_type("no_data")
            return
        message = Qg.QMessageBox()
        message.setWindowTitle("Attempt to calculate shift values")
        message.setIcon(Qg.QMessageBox.Question)
        message.setText("Are you sure you want to attempt to find shift values for all scans?")
        message.setInformativeText(
            "This will overwrite any existing values!")
        message.setStandardButtons(Qg.QMessageBox.Yes | Qg.QMessageBox.No)
        message.setDefaultButton(Qg.QMessageBox.No)
        ret = message.exec_()
        if ret == Qg.QMessageBox.Yes:
            self.controller.auto_align_scans()

    def correct_charges(self):
        """
        # REVIEW Documentation
        """
        # COMBAKL Sigmoid
        if len(self.controller.scans) == 0:
            self.show_error_by_type("no_data")
            return
        message = Qg.QMessageBox()
        message.setWindowTitle("Correct Charges All Scans")
        message.setIcon(Qg.QMessageBox.Question)
        message.setText("Are you sure you want to start correcting charges for all scans?")
        message.setInformativeText(
            "It is highly recommended that all scans are aligned before performing charge corrections!")
        message.setStandardButtons(Qg.QMessageBox.Yes | Qg.QMessageBox.No)
        message.setDefaultButton(Qg.QMessageBox.No)
        ret = message.exec_()
        if ret == Qg.QMessageBox.Yes:
            self.controller.correct_charges()
            self.show_auto_manual_fit_sigmoid_dialog()

    def correct_charges_one(self):
        """
        # REVIEW Documentation
        """
        # COMBAKL Sigmoid
        if len(self.controller.scans) == 0:
            self.show_error_by_type("no_data")
            return
        message = Qg.QMessageBox()
        message.setWindowTitle("Correct Charges One Scan")
        message.setIcon(Qg.QMessageBox.Question)
        message.setText("Please confirm that you wish to correct charges for this scan!")
        message.setStandardButtons(Qg.QMessageBox.Yes | Qg.QMessageBox.No)
        message.setDefaultButton(Qg.QMessageBox.No)
        ret = message.exec_()
        if ret == Qg.QMessageBox.Yes:
            curr_scan = self.controller.scans[self.controller.curr_scan_index]
            curr_scan.generate_processed_data()
            curr_scan.correct_charges()
            self.controller.switch_to_scan(self.controller.curr_scan_index)

    def show_auto_fit_sigmoid_dialog(self):
        """
        Shows the dialog box that asked the usef if they want to let the program fit the sigmoid line automatically.
        """
        message = Qg.QMessageBox()
        message.setWindowTitle("Sigmoid Fit")
        message.setText("Are you sure you want to let the program fit the sigmoid lines for you?")
        message.setIcon(Qg.QMessageBox.Question)
        message.setStandardButtons(Qg.QMessageBox.Yes | Qg.QMessageBox.No)
        message.setDefaultButton(Qg.QMessageBox.No)
        ret = message.exec_()
        if ret == Qg.QMessageBox.Yes:
            self.controller.auto_fit_sigmoids()

    def auto_fit_sigmoid_one(self):
        """
        Shows the dialog box that asked the usef if they want to let the program fit the sigmoid line automatically.
        """
        if len(self.controller.scans) == 0:
            self.show_error_by_type("no_data")
            return
        message = Qg.QMessageBox()
        message.setWindowTitle("Fit Sigmoid One Scan")
        message.setIcon(Qg.QMessageBox.Question)
        message.setText("Please confirm that you wish to reset the sigmoid settings and refit for this scan!")
        message.setStandardButtons(Qg.QMessageBox.Yes | Qg.QMessageBox.No)
        message.setDefaultButton(Qg.QMessageBox.No)
        ret = message.exec_()
        if ret == Qg.QMessageBox.Yes:
            curr_scan = self.controller.scans[self.controller.curr_scan_index]
            curr_scan.generate_processed_data()
            curr_scan.correct_charges()
            self.controller.auto_fit_one_sigmoid(self.controller.curr_scan_index)
            self.controller.switch_to_scan(self.controller.curr_scan_index)
            self.controller.stage = "kappa"
            self.action_menu.actions()[8].setDisabled(False)

    def show_kappa_params_dialog(self):
        """
        Shows the kappa parameters dialog box.
        """
        kappa_dialog = c_modal_dialogs.SelectParamsKappaDialog(self.controller)
        kappa_dialog.exec_()

    # Settings menu item

    def show_setting_dialog(self):
        """
        Shows the settings dialog box.
        """
        setting_dialog = c_modal_dialogs.SettingDialog(self)
        setting_dialog.exec_()

    def open_about(self):
        """
        Shows dialog box that displays current Chemics version.
        """
        # TODO issues/23 https://gitlab.bucknell.edu/nrr004/Chemics/issues/23
        # noinspection PyCallByClass
        Qg.QMessageBox.about(self, "About", "Chemics\n\nVersion 2.2.2")

    @staticmethod
    def open_user_manual():
        """
        Launches a webpage that shows the user manual as well as the code documentation
        """
        # TODO issues/8 https://gitlab.bucknell.edu/nrr004/Chemics/issues/8
        org_stdout = os.dup(1)
        org_stderr = os.dup(2)
        os.close(1)
        os.close(2)
        os.open(os.devnull, os.O_RDWR)
        try:
            webbrowser.open("https://lilyheart.github.io/chemics_documentation/")
        except Exception as e:
            logger.error(e, exc_info=True)
        finally:
            os.dup2(org_stdout, 1)
            os.dup2(org_stderr, 2)

    ##############################
    # Create Widgets and Dockers #
    ##############################

    def create_left_docker(self):
        """
        Creates the left docker screen and adds menu options to the Window menu bar section

        :returns:

            - **scaninfo_docker** - Qg.QDockWidget object that represents the Scan Information screen
            - **scan_docker_widget** - c_dock_widget.DockerScanInformation object that contains the lay out for the
              Scan Information screen
            - **sigmoid_docker** - Qg.QDockWidget object that represents the Sigmoid Parameters screen
            - **sigmoid_docker_widget** - c_dock_widget.DockerSigmoidWidget object that contains the lay out for the
              Sigmoid Parameters screen
            - **kappa_docker** - Qg.QDockWidget object that represents the Kappa Values screen
            - **kappa_docker_widget** - c_dock_widget.DockerKappaWidget object that contains the lay out for the Kappa
              Values screen
        """
        # create left docker
        scaninfo_docker = Qg.QDockWidget("Scan &Information", self)
        scan_docker_widget = c_dock_widget.DockerScanInformation(self.controller)
        scaninfo_docker.setWidget(scan_docker_widget)
        scaninfo_docker.setAllowedAreas(Qc.Qt.RightDockWidgetArea | Qc.Qt.LeftDockWidgetArea)
        scaninfo_docker.setFeatures(Qg.QDockWidget.DockWidgetMovable | Qg.QDockWidget.DockWidgetClosable)
        self.window_menu.addAction(scaninfo_docker.toggleViewAction())
        self.addDockWidget(Qc.Qt.LeftDockWidgetArea, scaninfo_docker)
        # create sigmoid docker
        sigmoid_docker = Qg.QDockWidget("Sigmoid &Parameters", self)
        sigmoid_docker_widget = c_dock_widget.DockerSigmoidWidget(self.controller)
        sigmoid_docker.setWidget(sigmoid_docker_widget)
        sigmoid_docker.setAllowedAreas(Qc.Qt.RightDockWidgetArea | Qc.Qt.LeftDockWidgetArea)
        sigmoid_docker.setFeatures(Qg.QDockWidget.DockWidgetMovable | Qg.QDockWidget.DockWidgetClosable)
        self.window_menu.addAction(sigmoid_docker.toggleViewAction())
        self.addDockWidget(Qc.Qt.LeftDockWidgetArea, sigmoid_docker)
        self.tabifyDockWidget(sigmoid_docker, scaninfo_docker)
        # create kappa docker
        kappa_docker = Qg.QDockWidget("&Kappa Values", self)
        kappa_docker_widget = c_dock_widget.DockerKappaWidget(self.controller, self.kappa_graph)
        kappa_docker.setWidget(kappa_docker_widget)
        kappa_docker.setAllowedAreas(Qc.Qt.RightDockWidgetArea | Qc.Qt.LeftDockWidgetArea)
        kappa_docker.setFeatures(Qg.QDockWidget.DockWidgetMovable | Qg.QDockWidget.DockWidgetClosable)
        self.window_menu.addAction(kappa_docker.toggleViewAction())
        self.addDockWidget(Qc.Qt.LeftDockWidgetArea, kappa_docker)
        show_window_action = Qg.QAction("&Show Alignment Graphs", self, triggered=self.switch_central_widget)
        show_window_action.setCheckable(True)
        self.window_menu.addAction(show_window_action)
        return [scan_docker_widget, sigmoid_docker_widget, kappa_docker,
                kappa_docker_widget]

    def create_central_widget(self):
        """
        Creates the central widget that appear in the main area.
        The central widget includes the widgets for the align scans and kappa sections.

        :returns:

            - **stacked_central_widget** - Qg.QStackedWidget object that represents where the center widgets appear
            - **central_widget_alignscan** - c_central_widget.CentralWidgetScans object that represents
              the four graphs that are displayed during the alignment phase
            - **central_widget_kappa** - c_central_widget.CentralWidgetKappa object that represents the kappa graph.

        """
        # create alignment central widget
        central_widget_alignscan = c_central_widget.CentralWidgetScans(self)
        central_widget_kappa = c_central_widget.CentralWidgetKappa(self)
        stacked_central_widget = Qg.QStackedWidget()
        stacked_central_widget.addWidget(central_widget_alignscan)
        stacked_central_widget.addWidget(central_widget_kappa)
        # lock out the menus that we will not use
        self.setCentralWidget(stacked_central_widget)
        # Lock down all actions in the action menu
        self.action_menu.setDisabled(True)
        return stacked_central_widget, central_widget_alignscan, central_widget_kappa

    def switch_central_widget(self):  # RESEARCH How code works after controller.start is added
        """
        Toggles graph display in middle of screen between Alighment Graphs and Kappa Graphs
        """
        # TODO issues/36  This is a strange way of switching
        new_index = self.stacked_central_widget.count() - self.stacked_central_widget.currentIndex() - 1
        self.stacked_central_widget.setCurrentIndex(new_index)

    ##################
    # Create Dialogs #
    ##################

    def create_progress_bar(self):
        """
        Creates a progress bar dialog object that can be used when neccessary

        :return: A process bar dialog object
        :rtype: Qg.QProgressDialog
        """
        progress_dialog = Qg.QProgressDialog("Starting..", "Cancel", 0, 100, self)
        progress_dialog.setWindowTitle("Progress...")
        progress_dialog.setWindowModality(Qc.Qt.WindowModal)
        progress_dialog.setAutoReset(True)
        progress_dialog.setAutoClose(True)
        return progress_dialog

    @Qc.Slot(str)
    def init_progress_bar(self, task_name):
        """
        Opens the progress bar dialog with desired name and tags a PySide.QtCore.Slot.

        :param str task_name: The label to show on the progress bar
        """
        self.progress_dialog.setLabelText(task_name)
        self.progress_dialog.setValue(0)
        self.progress_dialog.show()

    @Qc.Slot(int)
    def update_progress_bar(self, percentage):
        """
        Updates the progress bar and tags a PySide.QtCore.Slot.

        :param int percentage: The value to update the bar to.  This should be a number 0 to 100
        """
        self.progress_dialog.setValue(min(max(0, percentage), 100))

    @Qc.Slot()
    def close_progress_bar(self):
        """
        Closes the progress bar and tags a PySide.QtCore.Slot.
        """
        self.progress_dialog.reset()

    @staticmethod
    def show_error_message(err_type):
        """
        Shows an error message dialog box

        :param str err_type: The type of error
        """
        # TODO - update to match show info message
        (title, text, subtext) = (None, None, None)
        # Get text information for message box
        if err_type == "no_data":
            # noinspection PyUnusedLocal
            title = "Error!"
            # noinspection PyUnusedLocal
            text = "There is no scan data to perform this action!"
            subtext = "Please import scan data through File/New or import a project through File/Open first!"
        elif err_type == "old project file":
            title = "Old File"
            text = "This file was created with an older version and " \
                   "can only be opened with an older version of this application"
        else:
            title = "Error!"
            text = "There is was an error"
            pass
        warning_msbx = Qg.QMessageBox()
        warning_msbx.setIcon(Qg.QMessageBox.Warning)
        warning_msbx.setWindowTitle(title)
        warning_msbx.setText(text)
        warning_msbx.setInformativeText(subtext)
        warning_msbx.exec_()

    @staticmethod
    def show_information_message(title=None, text=None, subtext=None):
        """
        Shows an informational message dialog box

        :param str title: The title of message
        :param str text: The top text of message
        :param str subtext: The bottom text of message
        """
        warning = Qg.QMessageBox()
        warning.setIcon(Qg.QMessageBox.Information)
        warning.setWindowTitle(title)
        warning.setText(text)
        warning.setInformativeText(subtext)
        warning.exec_()

    def get_counts_to_conc_conv(self):
        """
        Display a dialog box to the user to obtain the Counts2ConcConv value
        """
        # DOCQUESTION English?
        # TODO issues/30  New Counts2ConcConv formula
        # noinspection PyCallByClass
        cc = Qg.QInputDialog.getDouble(self, "Counts to concentration conversion", "Counts to concentration conversion",
                                       value=1.2, decimals=2)
        if cc[1]:
            return float(cc[0])
        else:
            return None

    def show_auto_manual_fit_sigmoid_dialog(self):
        """
        Shows the Auto or Manual fit sigmoid dialog.  If the manual button is clicked, program performs no calcuations.
        If the Auto button is click, the :class:`~controller.Controller.auto_fit_sigmoid` from the Controller class is
        processed.
        """
        dialog = Qg.QMessageBox()
        dialog.setWindowTitle("Sigmoid Fit")
        dialog.setText("Select your preferred way to fit the sigmoid line to the data")
        dialog.setInformativeText("Do you want to manually fit the sigmoid lines, or let the program do it for you?")
        dialog.setIcon(Qg.QMessageBox.Question)
        dialog.addButton("Manual", Qg.QMessageBox.RejectRole)
        auto_button = dialog.addButton("Auto", Qg.QMessageBox.AcceptRole)
        dialog.exec_()
        if dialog.clickedButton() == auto_button:
            self.controller.auto_fit_sigmoids()

    def show_sigmoid_docker(self):
        """
        # REVIEW Documentation
        """
        # Remove all the dockers via the file menu
        if self.window_menu.actions()[0].isChecked():
            self.window_menu.actions()[0].trigger()
        if self.window_menu.actions()[1].isChecked():
            self.window_menu.actions()[1].trigger()
        if self.window_menu.actions()[2].isChecked():
            self.window_menu.actions()[2].trigger()
        # Enable the desired dockers
        self.window_menu.actions()[1].trigger()
        self.window_menu.actions()[0].trigger()

    ##################
    # Update Display #
    ##################

    def reset_view(self):
        """
        Utlizing the window_menu triggers, activates the scaninfo_docker and disables the sigmoid_docker
        and kappa_docker.  Sets the center widget to display the alignscans widget.
        """
        # TODO Find better way to reference
        # trigger windows in the event they havn't been triggered before
        self.window_menu.actions()[0].trigger()
        self.window_menu.actions()[1].trigger()
        self.window_menu.actions()[2].trigger()

        # Set only scaninfo as visible
        while not self.window_menu.actions()[0].isChecked():
            self.window_menu.actions()[0].trigger()  # check scaninfo_docker menu item
        while self.window_menu.actions()[1].isChecked():
            self.window_menu.actions()[1].trigger()  # uncheck sigmoid_docker
        while self.window_menu.actions()[2].isChecked():
            self.window_menu.actions()[2].trigger()  # uncheck kappa_docker
        self.stacked_central_widget.setCurrentWidget(self.central_widget_alignscan)

    def update_experiment_info(self):
        """
        Updates the experiment information by running the code in the
        :class:`~custom.docker_widget.DockerScanInformation.update_experiment_info` method of the
        :class:`~custom.docker_widget.DockerScanInformation` custom docker_widget.
        """
        self.scaninfo_docker_widget.update_experiment_info()
        self.sigmoid_docker_widget.update_experiment_info()

    def update_scan_info_and_graphs(self):
        """
        Updates the graphs, scan information docker widget and sigmoid docker widget
        """
        # Get the current scan's information
        a_scan = self.controller.scans[self.controller.curr_scan_index]
        # Update the graphs
        self.raw_conc_time_graph.update_graph(a_scan)
        self.smoothed_conc_time_graph.update_graph(a_scan)
        self.ratio_dp_graph.update_graph(a_scan)
        self.temp_graph.update_graph(a_scan)
        # Update the docker widgets
        self.scaninfo_docker_widget.update_scan_info()
        self.sigmoid_docker_widget.update_scan_info()

    def update_kappa_graph(self):
        """
        Updates the the kappa graph.
        """
        # COMBAKL Kappa
        self.kappa_docker_widget.update_kappa_graph()

    def switch_to_kappa_view(self):
        """
        # REVIEW Documentation
        """
        # COMBAKL Kappa
        if self.window_menu.actions()[0].isChecked():
            self.window_menu.actions()[0].trigger()
        if self.window_menu.actions()[1].isChecked():
            self.window_menu.actions()[1].trigger()
        self.stacked_central_widget.setCurrentWidget(self.central_widget_kappa)
        self.kappa_graph.update_all_kappa_points(self.controller.alpha_pinene_dict,
                                                 self.controller.valid_kappa_points)
        self.kappa_docker_widget.update_kappa_values()
        self.set_menu_bar_by_stage()

        if not self.window_menu.actions()[2].isChecked():
            self.window_menu.actions()[2].trigger()

    def set_font(self, font, size):
        """
        Sets the font and font size desired.

        :param PySide.QtGui.QFont font: The new font style.
        :param int size: The new font size
        """
        # noinspection PyUnresolvedReferences
        self.font = Qg.QFont(font.family(), size)
        app.setFont(self.font)


if __name__ == "__main__":
    # setup debugger
    logger.info("=================================================")
    logger.info("=================================================")
    logger.debug("Chemics started")

    app = Qg.QApplication(sys.argv)
    main_window = MainView(app)
    main_window.show()

    app.setWindowIcon(Qg.QIcon('icon.png'))
    main_window.setWindowIcon(Qg.QIcon('icon.png'))
    sys.exit(app.exec_())
