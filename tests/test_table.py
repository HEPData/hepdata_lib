# !/usr/bin/env python
# -*- coding:utf-8 -*-
"""Test Table."""
from unittest import TestCase
from hepdata_lib import Table, Variable, Uncertainty

class TestTable(TestCase):
    """Test the Table class."""
    def test_add_variable(self):
        """Test the add_variable function."""

        # Verify that the type check works
        test_table = Table("Some variable")
        test_variable = Variable("Some variable")
        test_uncertainty = Uncertainty("Some Uncertainty")
        try:
            test_table.add_variable(test_variable)
        except TypeError:
            self.fail("Table.add_variable raised an unexpected TypeError.")

        with self.assertRaises(TypeError):
            test_table.add_variable(5)
        with self.assertRaises(TypeError):
            test_table.add_variable([1, 3, 5])
        with self.assertRaises(TypeError):
            test_table.add_variable("a string")
        with self.assertRaises(TypeError):
            test_table.add_variable(test_uncertainty)

    def test_yaml_dump(self):
        """Test yaml.dump() for Table."""

        test_table = Table("Some Table")
        test_variable = Variable("Some Variable")
        test_table.add_variable(test_variable)
        try:
            test_table.write_yaml("test_output")
        except TypeError:
            self.fail("Table.test_table raised an unexpected TypeError.")