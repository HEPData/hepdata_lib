# !/usr/bin/env python
# -*- coding:utf-8 -*-
"""Test Submission."""
import os
from builtins import bytes
from unittest import TestCase
from hepdata_lib import Submission, Table, Variable, Uncertainty

class TestSubmission(TestCase):
    """Test the Submission class."""
    def test_add_table_typechecks(self):
        """Test the type checks in the add_table function."""

        # Verify that the type check works
        test_submission = Submission()
        test_table = Table("Some Table")
        test_variable = Variable("Some Variable")
        test_uncertainty = Uncertainty("Some Uncertainty")
        try:
            test_submission.add_table(test_table)
        except TypeError:
            self.fail("Submission.add_table raised an unexpected TypeError.")

        with self.assertRaises(TypeError):
            test_submission.add_table(5)
        with self.assertRaises(TypeError):
            test_submission.add_table([1, 3, 5])
        with self.assertRaises(TypeError):
            test_submission.add_table("a string")
        with self.assertRaises(TypeError):
            test_submission.add_table(test_variable)
        with self.assertRaises(TypeError):
            test_submission.add_table(test_uncertainty)

    def test_additional_resource_size(self):
        """Test the file checks in the add_additional_variable function."""

        testpath = "./testfile.dat"
        test_submission = Submission()

        # Check with non-existant file
        with self.assertRaises(RuntimeError):
            test_submission.add_additional_resource("Some description", testpath, copy_file=True)

        # Check with file that is too big
        size = int(2e8) # bytes in 200 MB
        with open(testpath, "wb") as testfile:
            testfile.write(bytes("\0" * size, "utf-8"))
        with self.assertRaises(RuntimeError):
            test_submission.add_additional_resource("Some description", testpath, copy_file=True)

        # Clean up
        os.remove(testpath)

        # Check with file that is not too big.
        size = int(5e7) # bytes in 50 MB
        with open(testpath, "wb") as testfile:
            testfile.write(bytes("\0" * size, "utf-8"))
        try:
            test_submission.add_additional_resource("Some description", testpath, copy_file=True)
        except RuntimeError:
            self.fail("Submission.add_additional_resource raised an unexpected RuntimeError.")

        # Clean up
        os.remove(testpath)

    def test_yaml_dump(self):
        """Test yaml.dump()."""

        test_submission = Submission()
        # test_table = Table("Some Table")
        # test_variable = Variable("Some Variable")
        # test_uncertainty = Uncertainty("Some Uncertainty")
        try:
            test_submission.create_files("test_output")
        except TypeError:
            self.fail("Submission.create_files raised an unexpected TypeError.")
