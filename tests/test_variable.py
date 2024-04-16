#!/usr/bin/env python
"""Test Variable."""
import random
from unittest import TestCase
from hepdata_lib import Variable, Uncertainty
from .test_utilities import tuple_compare


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
            assert(all(tuple_compare(x, y)
                       for x, y in zip(testvar.values, scaled_values)))

            # Check that inverse also works
            testvar.scale_values(1. / factor)
            self.assertTrue(all(tuple_compare(x, y)
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

    def test_add_qualifier(self):
        """Test the 'add_qualifier' function"""

        # Initialize dependent variable
        var = Variable("testvar")
        var.is_binned = False
        var.values = range(5)
        var.is_independent = False

        # This should work fine
        try:
            var.add_qualifier("Some Name 1", "Some value 1", "Some unit 1")
            var.add_qualifier("Some Name 2", "Some value 2")
        except RuntimeError:
            self.fail("Variable.add_qualifier raised an unexpected RuntimeError.")

        # For an independent variable, an exception should be raised
        var.is_independent = True
        with self.assertRaises(RuntimeError):
            var.add_qualifier("Some Name 3", "Some value 3")
        with self.assertRaises(RuntimeError):
            var.add_qualifier("Some Name 4", "Some value 4", "Some unit 4")

    def test_make_dict(self):
        """Test the make_dict function."""

        var = Variable("testvar")

        # With or without units
        for units in ["", "GeV"]:
            var.units = units

            # Binned
            var.is_binned = False
            var.values = [1, 2, 3]
            var.make_dict()

            # Unbinned
            var.is_binned = True
            var.values = [(0, 1), (1, 2), (2, 3)]
            var.make_dict()

        # With symmetric uncertainty
        unc1 = Uncertainty("unc1")
        unc1.is_symmetric = True
        unc1.values = [random.random() for _ in range(len(var.values))]
        var.add_uncertainty(unc1)
        var.make_dict()

        # With asymmetric uncertainty
        unc2 = Uncertainty("unc2")
        unc2.is_symmetric = False
        unc2.values = [(-random.random(), random.random()) for _ in range(len(var.values))]
        var.add_uncertainty(unc2)
        var.make_dict()

        # With qualifiers (which only apply to dependent variables)
        var.is_independent = False
        var.add_qualifier("testqualifier1", 1, units="GeV")
        var.add_qualifier("testqualifier2", 1, units="")
        var.make_dict()

    def test_constructor(self):
        """Test the constructor of the Variable class."""

        binned_values = [(1, 2), (2, 3), (3, 4)]
        unbinned_values = [1, 2, 3, 4]
        binned_values_wrong_length = [(1, 2, 3), (4, 5, 6)]

        # Should work fine: Binned
        try:

            _var = Variable("testvar", is_binned=True, values=binned_values)
        except ValueError:
            self.fail("Variable constructor raised unexpected ValueError.")

        # Should work fine: Unbinned
        try:
            _var = Variable("testvar", is_binned=False, values=unbinned_values)
        except ValueError:
            self.fail("Variable constructor raised unexpected ValueError.")

        # Wrong type of argument
        with self.assertRaises(ValueError):
            _var = Variable("testvar", is_binned=True, values=unbinned_values)

        # Other way around
        with self.assertRaises(ValueError):
            _var = Variable("testvar", is_binned=False, values=binned_values)

        # Tuples, but wrong length
        with self.assertRaises(ValueError):
            _var = Variable("testvar", is_binned=False, values=binned_values_wrong_length)
