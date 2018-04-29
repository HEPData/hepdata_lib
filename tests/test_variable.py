#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""Test Variable."""
import random
from unittest import TestCase
import test_utilities
from hepdata_lib import Variable


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
