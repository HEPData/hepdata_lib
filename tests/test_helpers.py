#!/usr/bin/env python
"""Test helpers."""
from unittest import TestCase

import numpy as np

from hepdata_lib.helpers import relative_round
from hepdata_lib.helpers import get_number_precision
from hepdata_lib.helpers import get_value_precision_wrt_reference
from hepdata_lib.helpers import round_value_and_uncertainty
from hepdata_lib.helpers import file_is_outdated


class TestHelpers(TestCase):
    """Test the helper functions."""
    def test_relative_round(self):
        '''Test behavior of Variable.scale_values function'''
        # Some values are mapped onto themselves
        eigenvalues = [np.inf, 0, 'astring']
        for prec in range(10):
            for eig in eigenvalues:
                self.assertTrue(relative_round(eig, prec) == eig)
            self.assertTrue(np.isnan(relative_round(np.nan, prec)))

        # Test format is
        # (original value, number of digits, rounded value)
        values = [
            (1.23456, 1, 1.0),
            (12.3456, 1, 10),
            (12.3456, 3, 12.3),
            (12.3456, 5, 12.346),
        ]
        for original, digits, result in values:
            rounded = relative_round(original, digits)
            self.assertTrue(rounded == result)


    def test_get_number_precision(self):
        '''Test behavior of get_number_precision function'''

        # Some values are mapped onto themselves
        eigenvalues = [np.inf, 0, 'astring']
        for eig in eigenvalues:
            self.assertTrue(get_number_precision(eig) == eig)
        self.assertTrue(np.isnan(get_number_precision(np.nan)))

        # test case with single value
        # test format is (original value, precision)
        values = [
            (12.5, 2),
            (1.25, 1),
            (0.125, 0),
            (0.0125, -1)
        ]
        for value, prec in values:
            precision = get_number_precision(value)
            self.assertTrue(precision == prec)

        # test case with ntuple (e.g. with two values)
        # test format is (original value, precision)
        # both original value and precision are ntuples (with two elements)
        ntuples = {
            (12.5, 1.25) : (2, 1),
            (0.125, 0.0125) : (0, -1)
        }
        for original_values, target_precisions in ntuples.items():
            precisions = get_number_precision(original_values)
            self.assertTrue(precisions == target_precisions)


    def test_get_value_precision_wrt_reference(self):
        '''Test behavior of get_value_precision_wrt_reference function'''

        # test format is (value, reference, relative precision)
        values = [
            (12.5, 0.08, 3),
            (1.25, 102.4, -2),
            (0.0, 0.002, 2),
            (10.0, 9, 0)
        ]
        for val, ref, prec in values:
            precision = get_value_precision_wrt_reference(val, ref)
            self.assertTrue(precision == prec)

        # test wrong input type
        with self.assertRaises(ValueError):
            get_value_precision_wrt_reference(1.23, "bad")
        with self.assertRaises(ValueError):
            get_value_precision_wrt_reference(1.23, (1.2, 3.4))
        with self.assertRaises(ValueError):
            get_value_precision_wrt_reference("bad", (1.2, 3.4))


    def test_round_value_and_uncertainty(self):
        '''Test behavior of round_value_and_uncertainty function'''

        # Test format is
        # (container, key_for_values, key_for_uncertanties, significant_digits)
        # uncertainty has a single value
        cont = {"val": [1.23456, 1234.56, 0.0012345, 0.123],
                "unc": [0.00123, 1.23, 0.012, 0.12],
                "val_round": [1.2346, 1234.6, 0.001, 0.12],
                "unc_round": [0.0012, 1.2, 0.012, 0.12]}
        # round to two significant digits
        round_value_and_uncertainty(cont, "val", "unc", 2)
        self.assertTrue(cont["val"] == cont["val_round"])
        self.assertTrue(cont["unc"] == cont["unc_round"])

        # Test format is
        # (container, key_for_values, key_for_uncertanties, significant_digits)
        # uncertainty has two value, as it would be the case with TGraphAsymmErrors
        cont_asymm_err = {"val": [1.23456, 0.123],
                          "unc": [(0.00123, 0.0123), (0.012, 0.12)],
                          "val_round": [1.235, 0.12],
                          "unc_round": [(0.001, 0.012), (0.01, 0.12)]}
        # round to two significant digits
        round_value_and_uncertainty(cont_asymm_err, "val", "unc", 2)
        self.assertTrue(cont_asymm_err["val"] == cont_asymm_err["val_round"])
        self.assertTrue(cont_asymm_err["unc"] == cont_asymm_err["unc_round"])

    def test_file_is_outdated(self):
        '''Test behavior of file_is_outdated function'''
        with self.assertRaises(RuntimeError):
            file_is_outdated(None, 'non_existing_file.png')
