#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""Utilities for tests."""

import os
import random
import string

import ROOT
from future.utils import raise_from


def float_compare(x_val, y_val, precision=1e-6):
    '''Helper function to check that two numbers are equal within float precision.'''
    if y_val == 0:
        return x_val == 0
    if abs((x_val - y_val) / y_val) < precision:
        return True
    return False


def tuple_compare(x_tup, y_tup):
    '''Helper function to check that two tuples are equal within float precision.'''
    same = True
    for pair in zip(x_tup, y_tup):
        same &= float_compare(pair[0], pair[1])
    return same

def histogram_compare_1d(hist1, hist2):
    '''
    Helper function to check that two 1D histograms are equivalent.
    Will check:
        * Number of bins
        * Bin edges
        * Bin contents
        * Bin errors
    '''
    bin_functions_to_check = [
        "GetBinContent",
        "GetBinErrorUp",
        "GetBinErrorLow"
    ]
    try:
        assert hist1.GetNbinsX() == hist2.GetNbinsX()

        for ibin in range(0, hist1.GetNbinsX()+2):
            for function in bin_functions_to_check:
                val1 = getattr(hist1, function)(ibin)
                val2 = getattr(hist2, function)(ibin)
                assert float_compare(val1, val2)
    except AssertionError:
        return False

    return True


def get_random_id(length=12):
    """
    Return random ID string of given length.
    Useful for temporary files, etc.
    """
    return "".join(random.sample(string.ascii_uppercase+string.digits, length))


def remove_if_exist(path_to_file):
    """Remove file if it exists."""
    if os.path.exists(path_to_file):
        os.remove(path_to_file)

def make_tmp_root_file(path_to_file='tmp_{RANDID}.root', mode="RECREATE",
                       close=False, testcase=None):
    """
    Create a temporary ROOT file.
    :param path_to_file: path where the file should be created.
                         Can be absolute or relative.
                         If the path contains the token '{RANDID}', it is
                         replaced with a random alphanumerical ID string.
    :type path_to_file: string
    :param mode: File creation mode to use (must be valid ROOT file mode)
    :type mode: string
    :param close: If True, close the file immediately and return only the path to the file.
    :type close: bool
    :param testcase: The test case calling this function. If given, the test case addCleanup
                     function is used to register the temporary file for eventual deletion.
    """

    if "{RANDID}" in path_to_file:
        try:
            path_to_file = path_to_file.format(RANDID=get_random_id())
        except IndexError as err:
            raise_from(IOError("String substitution failed. Your input path should not \
                           have any braces except possibly for the {RANDID} token!"), err)

    rfile = ROOT.TFile(path_to_file, mode)

    if not rfile:
        raise RuntimeError("Failed to create temporary file: {}".format(path_to_file))

    if testcase:
        testcase.addCleanup(remove_if_exist, path_to_file)

    if close:
        rfile.Close()
        return path_to_file
    return rfile
