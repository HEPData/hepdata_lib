# !/usr/bin/env python
# -*- coding:utf-8 -*-
"""Test Table."""
import re
import os
import shutil
from unittest import TestCase

from hepdata_lib import Table, Variable, Uncertainty, helpers

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


    def test_write_yaml(self):
        """Test write_yaml() for Table."""

        test_table = Table("Some Table")
        test_variable = Variable("Some Variable")
        test_table.add_variable(test_variable)
        testdir = "test_output"
        self.addCleanup(shutil.rmtree, testdir)
        try:
            test_table.write_yaml(testdir)
        except TypeError:
            self.fail("Table.write_yaml raised an unexpected TypeError.")
        with self.assertRaises(TypeError):
            test_table.write_yaml(None)
        self.doCleanups()

    def test_add_image(self):
        # Get test PDF
        some_pdf = "%s/minimal.pdf" % os.path.dirname(__file__)

        test_table = Table("Some Table")

        # This should work fine
        try:
            try:
                test_table.add_image(some_pdf)
            except RuntimeError:
                self.fail("Table.add_image raised an unexpected RuntimeError.")
        except TypeError:
                self.fail("Table.add_image raised an unexpected TypeError.")

        # Try wrong argument types
        wrong_type = [None, 5, {}, []]
        for argument in wrong_type:
            with self.assertRaises(TypeError):
                test_table.add_image(argument)

        # Try non-existing paths:
        nonexisting = ["/a/b/c/d/e","./daskjl/aksj/asdasd.pdf"]
        for argument in nonexisting:
            with self.assertRaises(RuntimeError):
                test_table.add_image(argument)


    def test_write_images(self):
        """Test the write_images function."""

        test_table = Table("Some Table")

        # Get test PDF
        some_pdf = "%s/minimal.pdf" % os.path.dirname(__file__)

        # This should work fine
        test_table.add_image(some_pdf)
        testdir = "test_output"
        self.addCleanup(shutil.rmtree, testdir)
        try:
            test_table.write_images(testdir)
        except TypeError:
            self.fail("Table.write_images raised an unexpected TypeError.")

        # Try wrong type of input argument
        bad_arguments = [None, 5, {}, []]
        for argument in bad_arguments:
            with self.assertRaises(TypeError):
                test_table.write_images(argument)
        self.doCleanups()
