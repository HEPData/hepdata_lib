#!/usr/bin/env python
# -*- coding:utf-8 -*-
import random
from unittest import TestCase
from test_utilities import *
from hepdata_lib import Variable, Uncertainty


class TestUncertainty(TestCase):
    def test_scale_values(self):
        '''Test behavior of Uncertainty.scale_values function'''
        values = range(0, 300, 1)
        uncertainty = [x + random.uniform(0, 2) for x in values]

        testvar = Variable("testvar")
        testvar.is_binned = False
        testvar.units = "GeV"
        testvar.values = values

        testunc = Uncertainty("testunc")
        testunc.is_symmetric = True
        testunc.values = uncertainty
        testvar.uncertainties.append(testunc)

        assert(testvar.values == values)
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
