# !/usr/bin/env python
# -*- coding:utf-8 -*-
"""Test Submission."""
from unittest import TestCase
from hepdata_lib import Submission, Table, Variable, Uncertainty

class TestSubmission(TestCase):
    """Test the Submission class."""
    def test_add_table(self):
        """Test the add_table function."""

        # Verify that the type check works
        test_submission = Submission()
        test_table = Table("Some Tale")
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
