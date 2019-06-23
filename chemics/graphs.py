"""
Initalizes and updates the graphs
"""
# External Packages
import math
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from StringIO import StringIO

# Internal Packages
import data.klines
import helper_functions as hf


class ConcOverTimeRawDataGraph(FigureCanvas):
    """
    Creates and updates the Raw SMPS and CCNC concentration over time graph.
    """
    def __init__(self):
        self.scan = None
        self.fig, self.ax = plt.subplots()
        super(self.__class__, self).__init__(self.fig)
        # set up the figure and axes
        self.ax.set_title("Raw SMPS and CCNC concentration over time")
        self.ax.set_xlabel("Scan time(s)")
        self.ax.set_ylabel("Concentration (1/cm3)")
        self.ax.legend()
        # set up empty data lines
        self.smps_points, = self.ax.plot([], [], label="Raw SMPS")
        self.ccnc_points, = self.ax.plot([], [], label="Raw CCNC")
        # plot graph
        plt.tight_layout()

    def update_graph(self, a_scan):
        """
        Updates the graph with the data in the scan provided.

        :param Scan a_scan: The scan object to update the graph with
        """
        # RESEARCH why are scans sent to graph.py but current scan from controller is pulled elsewhere?
        # Get data from the scan
        smps_counts = a_scan.raw_smps_counts
        ccnc_counts = a_scan.raw_ccnc_counts
        # Get the number of data points
        num_data_pts = max(len(smps_counts), len(ccnc_counts))
        # Make up for the lost data points
        smps_counts = hf.fill_zeros_to_end(smps_counts, num_data_pts)
        ccnc_counts = hf.fill_zeros_to_end(ccnc_counts, num_data_pts)
        smps_counts = smps_counts[:num_data_pts]
        ccnc_counts = ccnc_counts[:num_data_pts]
        # Set new data
        x_axis = np.arange(num_data_pts)
        self.smps_points.set_xdata(x_axis)
        self.smps_points.set_ydata(smps_counts)
        self.ccnc_points.set_xdata(x_axis)
        self.ccnc_points.set_ydata(ccnc_counts)
        self.ax.relim(visible_only=True)
        self.ax.autoscale_view(True, True, True)
        self.draw()
        self.flush_events()


class ConcOverTimeSmoothGraph(FigureCanvas):
    """
    Creates and updates the Smoothed SMPS and CCNC concentration over scan time graph.
    """
    def __init__(self):
        self.fig, self.ax = plt.subplots()
        super(self.__class__, self).__init__(self.fig)
        # set up the figure and axes
        self.ax.set_title("Smoothed SMPS and CCNC concentration over scan time")
        self.ax.set_xlabel("Scan time(s)")
        self.ax.set_ylabel("Concentration (1/cm3)")
        self.ax.legend()
        # set up empty data lines
        self.smps_points, = self.ax.plot([], [], label="SMPS")
        self.ccnc_points, = self.ax.plot([], [], label="CCNC")
        # plot graph
        plt.tight_layout()

    def update_graph(self, a_scan):
        """
        Updates the graph with the data in the scan provided.

        :param Scan a_scan: The scan object to update the graph with
        """
        # Get data from the scan
        smps_counts = a_scan.processed_smps_counts
        ccnc_counts = a_scan.processed_ccnc_counts
        # Get the number of data points
        num_data_pts = a_scan.duration
        # Make up for the lost data points
        smps_counts = hf.fill_zeros_to_end(smps_counts, num_data_pts)
        ccnc_counts = hf.fill_zeros_to_end(ccnc_counts, num_data_pts)
        smps_counts = smps_counts[:num_data_pts]
        ccnc_counts = ccnc_counts[:num_data_pts]
        # Smooth the CCNC data
        ccnc_counts = hf.smooth(ccnc_counts)
        # set new data
        x_axis = np.arange(num_data_pts)
        self.smps_points.set_xdata(x_axis)
        self.smps_points.set_ydata(smps_counts)
        self.ccnc_points.set_xdata(x_axis)
        self.ccnc_points.set_ydata(ccnc_counts)
        self.ax.relim(visible_only=True)
        self.ax.autoscale_view(True, True, True)
        self.draw()
        self.flush_events()


class TemperatureGraph(FigureCanvas):
    """
    Creates and updates the Temperature over scan time graph.
    """
    def __init__(self):
        self.fig, self.ax = plt.subplots()
        super(self.__class__, self).__init__(self.fig)
        # set up the figure and axes
        self.ax.set_title("Temperature over scan time")
        self.ax.set_xlabel("Scan time(s)")
        self.ax.set_ylabel("Temperature")
        self.ax.legend()
        # set up empty data lines
        self.t1_line, = self.ax.plot([0], [0], label="T1")
        self.t2_line, = self.ax.plot([0], [0], label="T2")
        self.t3_line, = self.ax.plot([0], [0], label="T3")
        # plot graph
        plt.tight_layout()

    def update_graph(self, a_scan):
        """
        Updates the graph with the data in the scan provided.

        :param Scan a_scan: The scan object to update the graph with
        """
        # Get data from the scan
        t1s = a_scan.processed_T1s
        t2s = a_scan.processed_T2s
        t3s = a_scan.processed_T3s
        # Get the number of data points
        num_data_pts = a_scan.duration
        # Make up for the lost data points
        t1s = hf.fill_zeros_to_end(t1s, num_data_pts)  # QUESTION I'm not liking how zeros are added to all these graphs
        t2s = hf.fill_zeros_to_end(t2s, num_data_pts)
        t3s = hf.fill_zeros_to_end(t3s, num_data_pts)
        # Find the limits of y-axis
        min_y = np.amin([t1s, t2s, t3s])
        max_y = np.amax([t1s, t2s, t3s])
        # Widen the range of data a bit
        min_y -= max_y / 10
        max_y += max_y / 10
        # Set the limits
        self.ax.axes.set_ylim([min_y, max_y])
        self.ax.axes.set_xlim([0, num_data_pts])
        # Set new data
        x_axis = np.arange(num_data_pts)
        self.t1_line.set_xdata(x_axis)
        self.t1_line.set_ydata(t1s)
        self.t2_line.set_xdata(x_axis)
        self.t2_line.set_ydata(t2s)
        self.t3_line.set_xdata(x_axis)
        self.t3_line.set_ydata(t3s)
        self.draw()
        self.flush_events()


class RatioOverDiameterGraph(FigureCanvas):
    """
    Creates and updates the CCNC/SMPS over Dry Diameter graph.
    """
    def __init__(self):
        self.fig, self.ax = plt.subplots()
        super(self.__class__, self).__init__(self.fig)
        # set up the figure and axes
        self.ax.set_title("CCNC/SMPS over Dry Diameter")
        self.ax.set_xlabel("Diameter (nm)")
        self.ax.set_ylabel("CCNC/SMPS")
        # set up empty data lines
        self.ccn_cn_ratio_points, = self.ax.plot([0], [0], 'o', label="CCNC/SMPS")
        self.ccn_cn_ratio_corrected_points, = self.ax.plot([0], [0], 'o', label="CCNC/SMPS corrected")
        self.normalized_conc, = self.ax.plot([0], [0], label="normalized conc (dNdlogDp)")
        self.sigmoid_lines = []
        self.ax.axhline(1, linestyle='dashed')
        self.ax.legend()
        # plot graph
        plt.tight_layout()

    def update_graph(self, a_scan):
        """
        Updates the graph with the data in the scan provided.

        :param Scan a_scan: The scan object to update the graph with
        """
        # Get data from the scan
        ccnc = a_scan.processed_ccnc_counts
        smps = a_scan.processed_smps_counts
        ave_smps_dp = a_scan.ave_smps_diameters
        normalized_concs = a_scan.processed_normalized_concs
        diameter_midpoints = a_scan.diameter_midpoints
        corrected_ccnc = a_scan.corrected_ccnc_counts
        corrected_smps = a_scan.corrected_smps_counts
        # QUESTION K comment: if there are less normalized concs data, then trim the other data list
        # Calculate the ratios
        ratio = []
        for i in range(len(smps)):
            ratio.append(hf.safe_div(ccnc[i], smps[i]))
        # QUESTION K comment: We only need data within 0 to 1.5.
        # QUESTION K comment: Anything beyond that should be errors, so we don't need to graph them
        # Set the limits of the vertical axis
        # QUESTION which is the minimum?  1.5 or 0.3 + max(ratio, normalized_concs)
        y_max = np.amin([1.5, max(np.amax(ratio), np.amax(normalized_concs)) + 0.3])
        self.ax.axes.set_ylim([0, y_max])
        # Set the limits of the horizontal axis QUESTION
        x_min = np.amin(ave_smps_dp)
        x_max = min(np.amax(ave_smps_dp), np.amax(diameter_midpoints))
        self.ax.axes.set_xlim([x_min, x_max])
        # Set new data
        self.ccn_cn_ratio_points.set_xdata(ave_smps_dp)
        self.ccn_cn_ratio_points.set_ydata(ratio)
        self.normalized_conc.set_xdata(diameter_midpoints)
        self.normalized_conc.set_ydata(normalized_concs)
        # If there are correct charges data
        if len(corrected_ccnc) > 0 and len(corrected_smps) > 0:
            ratio_corrected = []
            for i in range(len(smps)):
                ratio_corrected.append(hf.safe_div(corrected_ccnc[i], corrected_smps[i]))
            # add to graph as well
            self.ccn_cn_ratio_corrected_points.set_xdata(ave_smps_dp)
            self.ccn_cn_ratio_corrected_points.set_ydata(ratio_corrected)
        # Handle the sigmoid lines
        # -- Remove old lines
        for i in range(len(self.sigmoid_lines)):
            self.ax.lines.remove(self.sigmoid_lines[i])
        # -- Determine new lines
        sigmoid_y_vals = a_scan.sigmoid_y_vals
        self.sigmoid_lines = []
        for i in range(len(sigmoid_y_vals)):
            y_vals = sigmoid_y_vals[i]
            self.sigmoid_lines.append(self.ax.plot(ave_smps_dp, y_vals, label="Sigmoid Line #" + str(i + 1))[0])
        # Other graph details
        self.ax.legend()
        self.draw()
        self.flush_events()


class KappaGraph(FigureCanvas):
    """
    # REVIEW Documentation
    """
    def __init__(self):
        self.fig, self.ax = plt.subplots()
        super(self.__class__, self).__init__(self.fig)
        # set up the figure and axes
        # self.ax.set_title("")  # TODO
        self.ax.set_xlabel("Dry diameter(nm)")
        self.ax.set_ylabel("Super Saturation(%)")
        self.ax.legend()
        # set up klines  # TODO See if csv file is an issue for standalone exe
        self.klines_data = pd.read_csv(StringIO(data.klines.csv_codes), header=1)
        self.header = self.klines_data.columns
        self.klines_diameters = self.klines_data[self.header[1]]
        # set up empty data lines
        self.valid_kappa_points, = self.ax.plot([], [], "o", label="Valid K-points")
        self.invalid_kappa_points, = self.ax.plot([], [], "x", label="Invalid K-points")
        self.average_kappa_points, = self.ax.plot([], [], "o", label="Average K-points")
        self.klines = []
        # COMBAKL Kappa
        self.update_all_klines()
        # plot graph
        # plt.tight_layout()

    def update_tight_klines(self, alpha_pinene_dict):
        """
        # REVIEW Documentation

        :param alpha_pinene_dict:
        :type alpha_pinene_dict:
        """
        # COMBAKL Kappa
        kappa_list = []
        std_kappa_list = []
        # get a list of kappa values and std
        for a_key in alpha_pinene_dict:
            kappa_list.append(alpha_pinene_dict[a_key][2])
            std_kappa_list.append(alpha_pinene_dict[a_key][3])
        max_kappa = max(kappa_list) + max(std_kappa_list)
        min_kappa = min(kappa_list) - max(std_kappa_list)
        # now, find the position of the start column and end column that correspond to the max and
        # min kappa
        i = 2
        kappa = 1
        step = 0.1
        while True:
            if max_kappa > kappa:
                kline_start_column = max(2, i - 3)
                break
            i += 1
            kappa -= step
            if kappa == step:
                step /= 10
            if i >= len(self.header):
                kline_start_column = len(self.header)
                break
        i = 2
        kappa = 1
        step = 0.1
        while True:
            if min_kappa > kappa:
                kline_end_column = min(i + 3, len(self.header))
                break
            i += 1
            kappa -= step
            if kappa == step:
                step /= 10
            if i >= len(self.header):
                kline_end_column = len(self.header)
                break
        self.graph_klines(kline_start_column, kline_end_column)

    def update_all_klines(self):
        """
        # REVIEW Documentation
        """
        # COMBAKL Kappa
        kline_start_column = 2
        kline_end_column = len(self.header)
        self.graph_klines(kline_start_column, kline_end_column)

    def graph_klines(self, kline_start_column, kline_end_column):
        """
        # REVIEW Documentation

        :param kline_start_column:
        :type kline_start_column:
        :param kline_end_column:
        :type kline_end_column:
        """
        # COMBAKL Kappa
        # clean up previous lines
        for i in range(len(self.klines)):
            self.ax.lines.remove(self.klines[i])
        self.klines = []
        for i in range(kline_start_column, kline_end_column):
            y = self.klines_data[self.header[i]]
            self.klines.append(self.ax.loglog(self.klines_diameters, y, label=str(self.header[i]), linewidth=1)[0])
        self.ax.legend()
        self.draw_idle()
        self.flush_events()

    def update_all_kappa_points(self, alpha_pinene_dict, is_valid_kappa_points):
        """
        # REVIEW Documentation

        :param alpha_pinene_dict:
        :type alpha_pinene_dict:
        :param is_valid_kappa_points:
        :type is_valid_kappa_points:
        """
        # COMBAKL Kappa
        x_valid_ks = []
        y_valid_ks = []
        x_invalid_ks = []
        y_invalid_ks = []
        # print valid_kappa_points
        for a_key in alpha_pinene_dict.keys():
            for i in alpha_pinene_dict[a_key][-1]:
                if is_valid_kappa_points[i, a_key]:
                    x_valid_ks.append(i)
                    y_valid_ks.append(a_key)
                else:
                    x_invalid_ks.append(i)
                    y_invalid_ks.append(a_key)
        # update the valid points
        self.valid_kappa_points.set_xdata(x_valid_ks)
        self.valid_kappa_points.set_ydata(y_valid_ks)
        # update the invalid points
        self.invalid_kappa_points.set_xdata(x_invalid_ks)
        self.invalid_kappa_points.set_ydata(y_invalid_ks)
        # remove the average lines
        self.average_kappa_points.set_xdata([])
        self.average_kappa_points.set_ydata([])
        self.ax.set_title("Activation Diameter for all Kappa points and Lines of Constant Kappa (K)")
        self.ax.legend()
        self.draw()
        self.flush_events()

    def update_average_kappa_points(self, alpha_pinene_dict):
        """
        # REVIEW Documentation

        :param alpha_pinene_dict:
        :type alpha_pinene_dict:
        """
        # COMBAKL Kappa
        x_valid_ks = []
        y_valid_ks = []
        for a_key in alpha_pinene_dict.keys():
            if not math.isnan(alpha_pinene_dict[a_key][0]):
                x_valid_ks.append(alpha_pinene_dict[a_key][0])
                y_valid_ks.append(a_key)
        # update the average lines
        self.average_kappa_points.set_xdata(x_valid_ks)
        self.average_kappa_points.set_ydata(y_valid_ks)
        # remove other lines
        self.valid_kappa_points.set_xdata([])
        self.valid_kappa_points.set_ydata([])
        self.invalid_kappa_points.set_xdata([])
        self.invalid_kappa_points.set_ydata([])
        self.ax.set_title("Activation Diameter for average Kappa points and Lines of Constant Kappa (K)")
        self.ax.legend()
        self.draw()
        self.flush_events()


class SelectSmoothingAlgorithmGraph(FigureCanvas):  # RESEARCH How is this diff than above code?
    """
    Creates and updates the Raw SMPS and CCNC concentration over time graph.
    """
    def __init__(self):
        self.fig, self.ax = plt.subplots()
        super(self.__class__, self).__init__(self.fig)
        # set up the figure and axes
        self.ax.set_title("Raw SMPS and CCNC concentration over time")
        self.ax.set_xlabel("Scan time(s)")
        self.ax.set_ylabel("Concentration (1/cm3)")
        self.ax.legend()
        # set up empty data lines
        self.smps_points, = self.ax.plot([], [], label="Raw SMPS", alpha=0.2)
        self.ccnc_points, = self.ax.plot([], [], label="Raw CCNC")

    def update_graph(self, a_scan, smooth_ccnc=False):
        """
        Updates the graph with the data in the scan provided.

        :param Scan a_scan: The scan object to update the graph with
        :param bool smooth_ccnc: If the graph should smooth or not.  Default is `False`
        """
        # Get data from the scan
        smps_counts = a_scan.raw_smps_counts
        ccnc_counts = a_scan.raw_ccnc_counts
        # Get the number of data points
        num_data_pts = max(len(smps_counts), len(ccnc_counts))
        # make up for the lost data points
        smps_counts = hf.fill_zeros_to_end(smps_counts, num_data_pts)
        ccnc_counts = hf.fill_zeros_to_end(ccnc_counts, num_data_pts)
        smps_counts = smps_counts[:num_data_pts]
        ccnc_counts = ccnc_counts[:num_data_pts]
        # Smooth the CCNC data
        if smooth_ccnc:
            ccnc_counts = hf.smooth(ccnc_counts)
        # set new data
        x_axis = np.arange(num_data_pts)
        self.smps_points.set_xdata(x_axis)
        self.smps_points.set_ydata(smps_counts)
        self.ccnc_points.set_xdata(x_axis)
        self.ccnc_points.set_ydata(ccnc_counts)
        self.ax.relim(visible_only=True)
        self.ax.autoscale_view(True, True, True)
        self.draw()
        self.flush_events()
