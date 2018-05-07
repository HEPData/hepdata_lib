#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""Test Variable."""
import random
from unittest import TestCase
import test_utilities
from hepdata_lib import Variable, Uncertainty


class TestVariable(TestCase):
    """Test the Variable class."""
    def test_scale_values(self):
        '''Test behavior of Variable.scale_values function'''
        values = list(zip(range(0, 5, 1), range(1, 6, 1)))

        testvar = Variable("testvar")
        testvar.is_binned = True
        testvar.units = "GeV"
        testvar.values = values

        self.assertTrue(testvar.values == values)

        for factor in [random.uniform(0, 10000) for x in range(100)]:
            # Check that scaling works
            testvar.scale_values(factor)
            scaled_values = [(factor * x[0], factor * x[1]) for x in values]
            assert(all(test_utilities.tuple_compare(x, y)
                       for x, y in zip(testvar.values, scaled_values)))

            # Check that inverse also works
            testvar.scale_values(1. / factor)
            self.assertTrue(all(test_utilities.tuple_compare(x, y)
                                for x, y in zip(testvar.values, values)))

    def test_add_uncertainty(self):
        '''Test behavior of Variable.add_uncertainty function'''
        var = Variable("testvar")
        var.is_binned = False

        var.values = range(5)

        # Normal behavior
        unc = Uncertainty("testunc")
        unc.is_symmetric = True
        unc.values = [x * 0.1 for x in var.values]

        var.add_uncertainty(unc)

        self.assertTrue(len(var.uncertainties) == 1)
        self.assertTrue(var.uncertainties[0] == unc)

        # Reset variable but leave uncertainty as is
        var.uncertainties = []
        var.values = []
        var.add_uncertainty(unc)

        self.assertTrue(len(var.uncertainties) == 1)
        self.assertTrue(var.uncertainties[0] == unc)

        # Exception testing
        var.values = range(5)

        def wrong_input_type():
            '''Call add_uncertainty with invalid input type.'''
            var.add_uncertainty("this is not a proper input argument")
        self.assertRaises(TypeError, wrong_input_type)

        def wrong_input_properties():
            '''Call add_uncertainty with invalid input properties.'''
            unc2 = Uncertainty("testunc2")
            unc2.is_symmetric = True
            unc2.values = unc.values + [3]
            var.add_uncertainty(unc2)
        self.assertRaises(ValueError, wrong_input_properties)
