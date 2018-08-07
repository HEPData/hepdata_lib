"""hepdata_lib helper functions."""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import subprocess
import fnmatch
import math
import numpy as np

def execute_command(command):
    """
    Execute shell command using subprocess.
    If executable does not exist, return False.
    For other errors raise RuntimeError.
    Else return True on success.

    :param command: Command to execute.
    :type command: string
    """
    proc = subprocess.Popen(
        command,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True,
        universal_newlines=True)
    exit_code = proc.wait()
    if exit_code == 127:
        print("Command does not exist:", command)
        return False
    if exit_code != 0:
        result = ""
        for line in proc.stderr:
            result = result + line
        raise RuntimeError(result)
    return True

def find_all_matching(path, pattern):
    """Utility function that works like 'find' in bash."""
    if not os.path.exists(path):
        raise RuntimeError("Invalid path '{0}'".format(path))
    result = []
    for root, _, files in os.walk(path):
        for thisfile in files:
            if fnmatch.fnmatch(thisfile, pattern):
                result.append(os.path.join(root, thisfile))
    return result


def relative_round(value, relative_digits):
    """Rounds to a given relative precision"""
    if value == 0:
        return 0
    if isinstance(value, str) or np.isnan(value):
        return value

    value_precision = math.ceil(math.log10(abs(value)))

    absolute_digits = -value_precision + relative_digits
    if absolute_digits < 0:
        absolute_digits = 0

    return round(value, int(absolute_digits))


def check_file_existence(path_to_file):
    """
    Check that the given file path exists.
    If not, raise RuntimeError.

    :param path_to_file: File path to check.
    :type path_to_file: string
    """
    if not os.path.exists(path_to_file):
        raise RuntimeError("Cannot find file: " + path_to_file)
    return True

def check_file_size(path_to_file, upper_limit=None, lower_limit=None):
    """
    Check that the file size is between the upper and lower limits.
    If not, raise RuntimeError.

    :param path_to_file: File path to check.
    :type path_to_file: string

    :param upper_limit: Upper size limit in MB.
    :type upper_limit: float

    :param lower_limit: Lower size limit in MB.
    :type lower_limit: float
    """
    size = 1e-6 * os.path.getsize(path_to_file)
    if upper_limit and size > upper_limit:
        raise RuntimeError("File too big: '{0}'. Maximum allowed value is {1} \
                            MB.".format(path_to_file, upper_limit))
    if lower_limit and size < lower_limit:
        raise RuntimeError("File too small: '{0}'. Minimal allowed value is {1} \
                            MB.".format(path_to_file, lower_limit))
