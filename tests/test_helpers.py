#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""Test helpers."""
from unittest import TestCase

import numpy as np

from hepdata_lib.helpers import relative_round
from hepdata_lib.helpers import round_value_and_uncertainty


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
        for index in range(len(cont["val"])):
            self.assertTrue(cont["val"][index] == cont["val_round"][index])
            self.assertTrue(cont["unc"][index] == cont["unc_round"][index])

        # Test format is
        # (container, key_for_values, key_for_uncertanties, significant_digits)
        # uncertainty has two value, as it would be the case with TGraphAsymmErrors
        cont_asymm_err = {"val": [1.23456, 0.123],
                          "unc": [(0.00123, 0.0123), (0.012, 0.12)],
                          "val_round": [1.235, 0.12],
                          "unc_round": [(0.001, 0.012), (0.01, 0.12)]}
        # round to two significant digits
        round_value_and_uncertainty(cont_asymm_err, "val", "unc", 2)
        for index in range(len(cont_asymm_err["val"])):
            self.assertTrue(cont_asymm_err["val"] == cont_asymm_err["val_round"])
            self.assertTrue(cont_asymm_err["unc"] == cont_asymm_err["unc_round"])
