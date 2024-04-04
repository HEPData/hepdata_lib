# !/usr/bin/env python
"""Test Output."""
from collections import defaultdict
from unittest import TestCase
import shutil
import os
import yaml
from hepdata_lib import Submission, Table, Variable
from .test_utilities import tmp_directory_name

class TestOutput(TestCase):
    """Test output"""

    def test_yaml_output(self):
        """Test yaml dump"""
        tmp_dir = tmp_directory_name()

        # Create test dictionary
        testlist = [("x", 1.2), ("x", 2.2), ("y", 0.12), ("y", 0.22)]
        testdict = defaultdict(list)
        for key, value in testlist:
            testdict[key].append(value)

        # Create test submission
        test_submission = Submission()
        test_table = Table("TestTable")
        x_variable = Variable("X", is_independent=True, is_binned=False)
        x_variable.values = testdict['x']
        y_variable = Variable("Y", is_independent=False, is_binned=False)
        y_variable.values = testdict['y']
        test_table.add_variable(x_variable)
        test_table.add_variable(y_variable)
        test_submission.add_table(test_table)
        test_submission.create_files(tmp_dir)

        # Test read yaml file
        table_file = os.path.join(tmp_dir, "testtable.yaml")
        try:
            with open(table_file, encoding="utf-8") as testfile:
                testyaml = yaml.safe_load(testfile)
        except yaml.YAMLError as exc:
            print(exc)

        # Test compare yaml file to string
        testtxt = ("dependent_variables:\n- header:\n    name: Y\n  values:\n" +
                   "  - value: 0.12\n  - value: 0.22\nindependent_variables:\n" +
                   "- header:\n    name: X\n  values:\n  - value: 1.2\n  - value: 2.2\n")
        with open(table_file, encoding="utf-8") as testfile:
            testyaml = testfile.read()

        self.assertEqual(str(testyaml), testtxt)
        self.addCleanup(os.remove, "submission.tar.gz")
        self.addCleanup(shutil.rmtree, tmp_dir)
        self.doCleanups()
