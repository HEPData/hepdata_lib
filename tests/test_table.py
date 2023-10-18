# !/usr/bin/env python
"""Test Table."""
import os
import shutil
from unittest import TestCase

from hepdata_lib import Table, Variable, Uncertainty
from .test_utilities import tmp_directory_name

class TestTable(TestCase):
    """Test the Table class."""

    def test_name_checks(self):
        """Test the table name checks."""

        # This should work fine
        good_name = "64 characters or fewer"
        try:
            good_table = Table(good_name)
        except ValueError:
            self.fail("Table initializer raised unexpected ValueError.")

        self.assertEqual(good_name, good_table.name)

        # Check name that is too long
        too_long_name = "x"*100

        # In the initializer
        with self.assertRaises(ValueError):
            _bad_table = Table(too_long_name)

        # Using the setter
        with self.assertRaises(ValueError):
            good_table.name = too_long_name

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
        testdir = tmp_directory_name()
        self.addCleanup(shutil.rmtree, testdir)
        try:
            test_table.write_yaml(testdir)
        except TypeError:
            self.fail("Table.write_yaml raised an unexpected TypeError.")
        with self.assertRaises(TypeError):
            test_table.write_yaml(None)
        self.doCleanups()

    def test_add_image(self):
        """Get test PDF"""
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
        nonexisting = ["/a/b/c/d/e", "./daskjl/aksj/asdasd.pdf"]
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
        testdir = tmp_directory_name()
        self.addCleanup(shutil.rmtree, testdir)
        try:
            test_table.write_images(testdir)
        except TypeError:
            self.fail("Table.write_images raised an unexpected TypeError.")

        # Check that output file exists
        expected_file = os.path.join(testdir, "minimal.png")
        self.assertTrue(os.path.exists(expected_file))

        # Try wrong type of input argument
        bad_arguments = [None, 5, {}, []]
        for argument in bad_arguments:
            with self.assertRaises(TypeError):
                test_table.write_images(argument)
        self.doCleanups()

    def test_write_images_multiple_executions(self):
        """
        write_images is supposed to only recreate output PNG
        files if the output file does not yet exist or is outdated
        relative to the input file.
        """

        test_table = Table("Some Table")
        some_pdf = "%s/minimal.pdf" % os.path.dirname(__file__)
        test_table.add_image(some_pdf)
        testdir = "test_output"
        self.addCleanup(shutil.rmtree, testdir)

        expected_main_file = os.path.join(testdir, "minimal.png")
        expected_thumbnail_file = os.path.join(testdir, "thumb_minimal.png")

        # Output files should not yet exist
        self.assertTrue(not os.path.exists(expected_main_file))
        self.assertTrue(not os.path.exists(expected_thumbnail_file))

        # Run the function
        test_table.write_images(testdir)

        # Output files now exist
        self.assertTrue(os.path.exists(expected_main_file))
        self.assertTrue(os.path.exists(expected_thumbnail_file))

        # Make sure that output is not recreated if input file is unchanged
        modified_time_main = os.path.getmtime(expected_main_file)
        modified_time_thumbnail = os.path.getmtime(expected_thumbnail_file)
        test_table.write_images(testdir)
        self.assertEqual(modified_time_main, os.path.getmtime(expected_main_file))
        self.assertEqual(modified_time_thumbnail, os.path.getmtime(expected_thumbnail_file))


        # Make sure that a change in input file triggers recreation
        os.utime(some_pdf, None)
        test_table.write_images(testdir)
        self.assertTrue(modified_time_main < os.path.getmtime(expected_main_file))
        self.assertTrue(modified_time_thumbnail < os.path.getmtime(expected_thumbnail_file))





    def test_add_additional_resource(self): # pylint: disable=no-self-use
        """Test the add_additional_resource function."""
        test_table = Table("Some Table")
        test_table.add_additional_resource("some link","www.cern.ch")

    def test_copy_files(self):
        """Test the copy_files function."""
        test_table = Table("Some Table")
        some_pdf = "%s/minimal.pdf" % os.path.dirname(__file__)
        testdir = tmp_directory_name()
        self.addCleanup(shutil.rmtree, testdir)
        os.makedirs(testdir)

        test_table.add_additional_resource("a plot",some_pdf, copy_file=True)
        test_table.copy_files(testdir)
