# !/usr/bin/env python
"""Test execute_command() function."""
from unittest import TestCase
from hepdata_lib.helpers import execute_command

class TestExecuteCommand(TestCase):
    """Test execute_command() function."""
    def test_execute_command(self):
        """Test the function with existing and non-existing commands."""

        test_command_good = "ls"
        test_command_bad = "nonsense"
        test_command_bad_exit = "ls nonexist"

        self.assertTrue(execute_command(test_command_good))

        self.assertFalse(execute_command(test_command_bad))

        with self.assertRaises(RuntimeError):
            execute_command(test_command_bad_exit)
