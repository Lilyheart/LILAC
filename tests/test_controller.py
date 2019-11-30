"""
# REVIEW Documentation
"""
from unittest import TestCase
import controller


class MainView(object):
    def __init__(self):
        pass


class TestController(TestCase):
    def setUp(self):
        self.control = controller.Controller(MainView())


class TestInit(TestController):
    def test_scans(self):
        self.assertEqual(self.control.scans, [])

    def test_counts_to_conc_conv(self):
        self.assertEqual(self.control.counts_to_conc_conv, 0)

    def test_cpc_sample_flow(self):
        self.assertEqual(self.control.cpc_sample_flow, 0.05)

    def test_data_files(self):
        self.assertEqual(self.control.data_files, None)

    def test_ccnc_data(self):
        self.assertEqual(self.control.ccnc_data, None)

    def test_smps_data(self):
        self.assertEqual(self.control.smps_data, None)

    def experiment_date(self):
        self.assertEqual(self.control.experiment_date, None)

    def smooth_method(self):
        self.assertEqual(self.control.smooth_method, "Savitzky-Golay filter")

    def base_shift_factor(self):
        self.assertEqual(self.control.base_shift_factor, 0)

    def test_curr_scan_index(self):
        self.assertEqual(self.control.curr_scan_index, 0)

    def test_b_limits(self):
        self.assertEqual(self.control.b_limits, [0.5, 1.5])

    def test_asym_limits(self):
        self.assertEqual(self.control.asym_limits, [0.75, 1.5])

    def test_stage(self):
        self.assertEqual(self.control.stage, "init")

    def test_save_name(self):
        self.assertEqual(self.control.save_name, None)

    def test_kappa_calculate_dict(self):
        self.assertEqual(self.control.kappa_calculate_dict, {})

    def test_alpha_pinene_dict(self):
        self.assertEqual(self.control.alpha_pinene_dict, {})

    def test_is_valid_kappa_points(self):
        self.assertEqual(self.control.valid_kappa_points, {})

    def test_sigma(self):
        self.assertEqual(self.control.sigma, 0.072)

    def test_temp(self):
        self.assertEqual(self.control.temp, 298.15)

    def test_dd_1(self):
        self.assertEqual(self.control.dd_1, 280)

    def test_i_kappa_1(self):
        self.assertEqual(self.control.i_kappa_1, 0.00567)

    def test_dd_2(self):
        self.assertEqual(self.control.dd_2, 100)

    def test_i_kappa_2(self):
        self.assertEqual(self.control.i_kappa_2, 0.6)

    def test_solubility(self):
        self.assertEqual(self.control.solubility, 0.03)

    def test_kappa_excel(self):
        self.assertEqual(self.control.kappa_excel, None)


class TestSetAttributesDefault(TestController):
    def test_scans(self):
        self.control.scans = -1
        controller.Controller.set_attributes_default(self.control)
        self.assertEqual(self.control.scans, [])

    def test_counts_to_conc_conv(self):
        self.control.counts_to_conc_conv = -1
        controller.Controller.set_attributes_default(self.control)
        self.assertEqual(self.control.counts_to_conc_conv, 0)

    def test_data_files(self):
        self.control.data_files = -1
        controller.Controller.set_attributes_default(self.control)
        self.assertEqual(self.control.data_files, None)

    def test_ccnc_data(self):
        self.control.ccnc_data = -1
        controller.Controller.set_attributes_default(self.control)
        self.assertEqual(self.control.ccnc_data, None)

    def test_smps_data(self):
        self.control.smps_data = -1
        controller.Controller.set_attributes_default(self.control)
        self.assertEqual(self.control.smps_data, None)

    def experiment_date(self):
        self.control.counts_to_conc_conv = -1
        controller.Controller.set_attributes_default(self.control)
        self.assertEqual(self.control.experiment_date, None)

    def smooth_method(self):
        self.control.counts_to_conc_conv = -1
        controller.Controller.set_attributes_default(self.control)
        self.assertEqual(self.control.smooth_method, "Savitzky-Golay filter")

    def base_shift_factor(self):
        self.control.counts_to_conc_conv = -1
        controller.Controller.set_attributes_default(self.control)
        self.assertEqual(self.control.base_shift_factor, 0)

    def test_curr_scan_index(self):
        self.control.curr_scan_index = -1
        controller.Controller.set_attributes_default(self.control)
        self.assertEqual(self.control.curr_scan_index, 0)

    def test_b_limits(self):
        self.control.b_limits = -1
        controller.Controller.set_attributes_default(self.control)
        self.assertEqual(self.control.b_limits, [0.5, 1.5])

    def test_asym_limits(self):
        self.control.asym_limits = -1
        controller.Controller.set_attributes_default(self.control)
        self.assertEqual(self.control.asym_limits, [0.75, 1.5])

    def test_stage(self):
        self.control.stage = -1
        controller.Controller.set_attributes_default(self.control)
        self.assertEqual(self.control.stage, "init")

    def test_save_name(self):
        self.control.save_name = -1
        controller.Controller.set_attributes_default(self.control)
        self.assertEqual(self.control.save_name, None)

    def test_kappa_calculate_dict(self):
        self.control.kappa_calculate_dict = -1
        controller.Controller.set_attributes_default(self.control)
        self.assertEqual(self.control.kappa_calculate_dict, {})

    def test_alpha_pinene_dict(self):
        self.control.alpha_pinene_dict = -1
        controller.Controller.set_attributes_default(self.control)
        self.assertEqual(self.control.alpha_pinene_dict, {})

    def test_is_valid_kappa_points(self):
        self.control.valid_kappa_points = -1
        controller.Controller.set_attributes_default(self.control)
        self.assertEqual(self.control.valid_kappa_points, {})
