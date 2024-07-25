#!/usr/bin/env python
"""Test Uncertainty."""
import random
from unittest import TestCase
from hepdata_lib import Variable, Uncertainty
from .test_utilities import float_compare, tuple_compare


class TestUncertainty(TestCase):
    """Test the Uncertainty class."""

    def test_scale_values(self):
        '''Test behavior of Uncertainty.scale_values function'''
        values = list(range(0, 300, 1))
        uncertainty = [x + random.uniform(0, 2) for x in values]

        testvar = Variable("testvar")
        testvar.is_binned = False
        testvar.units = "GeV"
        testvar.values = values

        testunc = Uncertainty("testunc")
        testunc.is_symmetric = True
        testunc.values = uncertainty
        testvar.uncertainties.append(testunc)

        assert testvar.values == values
        self.assertTrue(testunc.values == uncertainty)

        for factor in [random.uniform(0, 10000) for x in range(100)]:
            # Check that scaling works
            testvar.scale_values(factor)
            scaled_values = [factor * x for x in values]
            scaled_uncertainty = [factor * x for x in uncertainty]
            self.assertTrue(all(float_compare(x, y)
                                for x, y in zip(testvar.values, scaled_values)))
            self.assertTrue(all(float_compare(x, y)
                                for x, y in zip(testunc.values, scaled_uncertainty)))

            # Check that inverse also works
            testvar.scale_values(1. / factor)
            self.assertTrue(all(float_compare(x, y)
                                for x, y in zip(testvar.values, values)))
            self.assertTrue(all(float_compare(x, y)
                                for x, y in zip(testunc.values, uncertainty)))

    def test_set_values_from_intervals(self):
        '''Test behavior of Uncertainy.test_set_values_from_intervals function'''

        # Dummy central values and variations relative to central value
        npoints = 100
        values = list(range(0, npoints, 1))
        uncertainty = [(-random.uniform(0, 1), random.uniform(0, 1))
                       for _ in range(npoints)]

        # Convert +- error to interval bounds
        intervals = [(val + unc_minus, val + unc_plus)
                     for val, (unc_minus, unc_plus) in zip(values, uncertainty)]

        # Reference uses "normal" assignment
        refunc = Uncertainty("reference_unc")
        refunc.is_symmetric = False
        refunc.values = uncertainty

        # Test uses new function
        testunc = Uncertainty("test_unc")
        testunc.is_symmetric = False
        testunc.set_values_from_intervals(intervals, nominal=values)

        # Check that both agree
        self.assertTrue(all((tuple_compare(tup1, tup2)
                        for tup1, tup2 in zip(testunc.values, refunc.values))))

    def test_mixed_uncertainties(self):
        '''Test behavior in case of symmetric and asymmetric uncertainties'''

        # Create a Variable with random values
        var = Variable("testvar")
        var.is_binned = False
        var.values = [1, 2, 3, 4]
        var.make_dict()

        # Add mixed uncertainties, declaring asymmetric type in order to allow up/down variations
        unc = Uncertainty("fake_unc")
        unc.is_symmetric = False
        unc.values = [(-1, 1), (-1.5, 2), (-3, 2), (-2.5, 2.5)]
        var.add_uncertainty(unc)
        dictionary = var.make_dict()

        # Verify the pattern: the correct one VS output of the make_dict() function
        pattern = ['symerror', 'asymerror', 'asymerror', 'symerror']
        self.assertTrue((list(dictionary['values'][i]['errors'][0].keys())[
                        0], value) for i, value in enumerate(pattern))

    def test_zero_uncertainties(self):
        '''Test cases where a data point has zero uncertainties'''

        # Asymmetric uncertainties
        var = Variable("testvar", is_binned=False, values=[1, 2, 3, 4])
        unc = Uncertainty("fake_unc", is_symmetric=False)
        unc.values = [(-1, 1), (-1.5, 2), (0, 0), (-2.5, 2.5)]
        var.add_uncertainty(unc)
        dictionary = var.make_dict()
        # Check that 'errors' key is missing only if zero uncertainties
        self.assertTrue(all('errors' in dictionary['values'][i] for i in [0, 1, 3]))
        self.assertTrue('errors' not in dictionary['values'][2])

        # Symmetric uncertainties (and use "zero_uncertainties_warning=False" option)
        var = Variable("testvar", is_binned=False, values=[1, 2, 3, 4],
                       zero_uncertainties_warning=False)
        unc = Uncertainty("fake_unc", is_symmetric=True)
        unc.values = [1, 1.5, 0, 2.5]
        var.add_uncertainty(unc)
        dictionary = var.make_dict()
        # Check that 'errors' key is missing only if zero uncertainties
        self.assertTrue(all('errors' in dictionary['values'][i] for i in [0, 1, 3]))
        self.assertTrue('errors' not in dictionary['values'][2])

    def test_inhomogenous_uncertainties(self):
        '''Test cases where an uncertainty only applies to a subset of the bins'''
        var = Variable("testvar", is_independent=False, is_binned=False, values=[1,2,3],
                       zero_uncertainties_warning=False)
        unc_a = Uncertainty('errorA', is_symmetric=True)
        unc_a.values = [ 0.1, 0.2, None ]
        var.add_uncertainty(unc_a)
        unc_b = Uncertainty('errorB', is_symmetric=True)
        unc_b.values = [ 0.1, 0.2, 0.3 ]
        var.add_uncertainty(unc_b)
        dictionary = var.make_dict()
        self.assertTrue(len([ errs['label'] for i in [0,1,2] \
                                            for errs in dictionary['values'][i]['errors'] \
                                            if errs['label'] == 'errorA'])==2)
