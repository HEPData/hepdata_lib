#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""Test helpers."""
from unittest import TestCase

import numpy as np

import test_utilities # pylint: disable=unused-import
from hepdata_lib.helpers import relative_round


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
