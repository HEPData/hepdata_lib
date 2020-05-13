# !/usr/bin/env python
# -*- coding:utf-8 -*-
"""Test Output."""
from __future__ import print_function
import os
from collections import defaultdict
from unittest import TestCase
import shutil
import yaml
from hepdata_lib import Submission, Table, Variable

class TestOutput(TestCase):
    """Test output"""

    def test_yaml_output(self):
        """Test yaml dump"""

        # Create test dictionary
        testlist = [("x", 1.2), ("x", 2.2), ("y", 0.12), ("y", 0.22)]
        testdict = defaultdict(list)
        for key, value in testlist:
            testdict[key].append(value)

        # Create test submission
        test_submission = Submission()
        testdir = "./output"
        test_table = Table("TestTable")
        x_variable = Variable("X", is_independent=True, is_binned=False)
        x_variable.values = testdict['x']
        y_variable = Variable("Y", is_independent=False, is_binned=False)
        y_variable.values = testdict['y']
        test_table.add_variable(x_variable)
        test_table.add_variable(y_variable)
        test_submission.add_table(test_table)
        test_submission.create_files(testdir)

        # Test read yaml file
        try:
            with open("output/testtable.yaml", 'r') as testfile:
                testyaml = yaml.safe_load(testfile)
        except yaml.YAMLError as exc:
            print(exc)

        # Test compare yaml file to string
        testtxt = ("dependent_variables:\n- header:\n    name: Y\n  values:\n" +
                   "  - value: 0.12\n  - value: 0.22\nindependent_variables:\n" +
                   "- header:\n    name: X\n  values:\n  - value: 1.2\n  - value: 2.2\n")
        testfile = open("output/testtable.yaml", 'r')
        testyaml = testfile.read()

        self.assertEqual(str(testyaml), testtxt)
        self.addCleanup(os.remove, "submission.tar.gz")
        self.addCleanup(shutil.rmtree, testdir)
        self.doCleanups()
