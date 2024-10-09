# !/usr/bin/env python
"""Test Submission."""
import os
import shutil
import string
from unittest import TestCase
import tarfile
from hepdata_lib import Submission, Table, Variable, Uncertainty
from .test_utilities import tmp_directory_name

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
        self.addCleanup(os.remove, testpath)

        # Check with non-existent file
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
            test_submission.add_additional_resource("Some description", testpath,
                                                    copy_file=True, file_type="HistFactory")
        except RuntimeError:
            self.fail("Submission.add_additional_resource raised an unexpected RuntimeError.")

        # Clean up
        self.doCleanups()

    def test_create_files(self):
        """Test create_files() for Submission."""

        # Set test directory/file pat
        testdir = tmp_directory_name()
        testpath = "./testfile.txt"

        with open(testpath, "a", encoding="utf-8") as f:
            f.close()

        self.addCleanup(os.remove, testpath)

        # Create submission and set values for testing
        test_submission = Submission()
        test_submission.add_record_id(1657397, "inspire")
        test_submission.add_related_recid(111)
        test_submission.add_additional_resource("Some description", testpath,
                                                copy_file=True, file_type="HistFactory")
        # Create table and set test values
        test_table = Table("test")
        test_table.add_related_doi("10.17182/hepdata.1.v1/t1")
        test_submission.add_table(test_table)

        test_submission.create_files(testdir)

        self.doCleanups()

    def test_create_files_with_removal(self):
        """Test the removal of old files in create_files()"""
        testdir = tmp_directory_name()

        # Step 1: Create test directory containing random file
        os.makedirs(testdir)
        self.addCleanup(shutil.rmtree, testdir)
        testfile = os.path.join(testdir, "test.txt")
        with open(testfile, "w", encoding="utf-8") as f:
            f.write("test")
        self.assertTrue(os.path.isfile(testfile))

        # Step 2: Create submission and write output to test directory
        # Without overwriting of files
        test_submission = Submission()
        tab = Table("test")
        test_submission.add_table(tab)
        test_submission.create_files(testdir, remove_old=False)

        # Test file should still exist
        self.assertTrue(os.path.isfile(testfile))

        # Step 3: Recreate submission files with removal
        test_submission.create_files(testdir, remove_old=True)

        # Test file should no longer exist
        self.assertFalse(os.path.isfile(testfile))


    def test_read_abstract(self):
        """Test read_abstract function."""
        some_string = string.ascii_lowercase

        testfile = "testfile.txt"
        self.addCleanup(os.remove, testfile)

        with open(testfile, "w", encoding="utf-8") as f:
            f.write(some_string)

        test_submission = Submission()
        test_submission.read_abstract(testfile)

        self.assertEqual(test_submission.comment, some_string)

        self.doCleanups()

    def test_nested_files_to_copy(self):
        """Test that file copying works when tables have files."""
        # Create random test file
        testfile = "testfile.txt"
        with open(testfile, "w", encoding="utf-8") as f:
            f.write("test")
        self.addCleanup(os.remove, testfile)

        # Output files
        testdirectory = "./testout"
        self.addCleanup(shutil.rmtree, testdirectory)
        self.addCleanup(os.remove, "submission.tar.gz")

        # Add resource to table, add table to Submission
        sub = Submission()
        tab = Table('test')
        tab.add_additional_resource("a_resource",testfile, copy_file=True)
        sub.add_table(tab)

        # Write outputs
        sub.create_files(testdirectory)

        # Check that test file is actually in the tar ball
        with tarfile.open("submission.tar.gz", "r:gz") as tar:
            try:
                tar.getmember(testfile)
            except KeyError:
                self.fail("Submission.create_files failed to write all files to tar ball.")

    def test_add_related_doi(self):
        """Test insertion and retrieval of recid values in the Table object"""
        # Possibly unnecessary boundary testing
        test_data = [
            {"doi": "10.17182/hepdata.1.v1/t1", "error": False},
            {"doi": "10.17182/hepdata.1", "error": ValueError},
            {"doi": "10.17182/hepdata.1.v1", "error": ValueError},
            {"doi": "10.17182/hepdata.1.v1/a2", "error": ValueError},
            {"doi": "not_valid", "error": ValueError},
            {"doi": 1, "error": TypeError},
        ]
        table = Table("Table")
        for test in test_data:
            if test["error"]:
                self.assertRaises(test["error"], table.add_related_doi, test["doi"])
            else:
                table.add_related_doi(test["doi"])
                assert test["doi"] == table.related_tables[-1]
        assert len(table.related_tables) == 1

    def test_add_related_recid(self):
        """Test insertion and retrieval of recid values in the Submission object"""
        test_data = [
            {"recid": 1, "error": False},
            {"recid": "1", "error": False},
            {"recid": -1, "error": ValueError},
            {"recid": "a", "error": TypeError}
        ]
        sub = Submission()
        for test in test_data:
            if test["error"]:
                self.assertRaises(test["error"], sub.add_related_recid, test["recid"])
            else:
                sub.add_related_recid(test["recid"])
                assert int(test["recid"]) == sub.related_records[-1]
        assert len(sub.related_records) == 2

    def test_add_data_license(self):
        """Test addition of data license entries to the Table class"""
        test_data = [
            {"expected_err": None, "data_license": ["name", "url", "desc"]},  # Valid, full
            {"expected_err": None, "data_license": ["name", "url", None]},  # Valid, no desc
            {"expected_err": ValueError, "data_license": ["name", None, "desc"]},  # Error, no url
            {"expected_err": ValueError, "data_license": [None, "url", "desc"]}  # Error, no name
        ]
        tab = Table("Table")  # Test table class
        for test in test_data:
            # Check if an error is expected here or not
            if test["expected_err"]:
                self.assertRaises(test["expected_err"], tab.add_data_license, *test["data_license"])
            else:
                # Check data exists and is correct
                tab.add_data_license(*test["data_license"])
                assert tab.data_license["name"] == test["data_license"][0]
                assert tab.data_license["url"] == test["data_license"][1]
