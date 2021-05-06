"""hepdata_lib helper functions."""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import subprocess
import fnmatch
import math
import numpy as np
from six.moves import zip

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


def get_number_precision(value):
    """
    Get precision of an input value.
    Exact integer powers of 10 are assigned same precision of smaller numbers
    For example
    get_number_precision(10.0) = 1
    get_number_precision(10.001) = 2
    get_number_precision(9.999) = 1
    """

    if isinstance(value, tuple):
        return (get_number_precision(x) for x in value)

    # if value is tuple, value == 0 might cause ValueError saying that
    # 'The truth value of an array with more than one element is ambiguous'
    # Thus, tuple is evaluated above
    if value == 0 or isinstance(value, str) or np.isnan(value) or np.isinf(value):
        return value

    return math.ceil(math.log10(abs(value)))


def relative_round(value, relative_digits):
    """Rounds to a given relative precision"""

    if isinstance(value, tuple):
        return (relative_round(x, relative_digits) for x in value)

    if value == 0 or isinstance(value, str) or np.isnan(value) or np.isinf(value):
        return value

    value_precision = get_number_precision(value)
    absolute_digits = -value_precision + relative_digits

    return round(value, int(absolute_digits))


def get_value_precision_wrt_reference(value, reference):
    """
    relative precision of first argument with respect to the second one
    value and reference are both float and/or int
    value can be float when reference is an int and viceversa

    : param value: first value
    : type  value: float, int

    : param reference: reference value (usually the uncertainty on value)
    : type  reference: float, int
    """

    this_function = "get_value_precision_wrt_reference()"
    good_types = [int, float]
    arguments = [value, reference]

    # first check all arguments have appropriate type
    for input_arg in arguments:
        if not any(isinstance(input_arg, x) for x in good_types):
            raise ValueError("Unsupported input type passed to " + this_function)

    return get_number_precision(value) - get_number_precision(reference)


def round_value_to_decimals(cont, key="y", decimals=3):
    """
    round all values in a dictionary to some decimals in one go
    default round to 3 digits after period
    possible use case: correlations where typical values are within -1,1

    : param cont : dictionary as returned e.g. by RootFileReader::read_hist_1d()
    : type  cont : dictionary

    : param decimals: how many decimals for the rounding
    : type  decimals: integer
    """

    decimals = int(decimals)

    for i, val in enumerate(cont[key]):
        if isinstance(val, tuple):
            cont[key][i] = (round(val[0], decimals), round(val[1], decimals))
        else:
            cont[key][i] = round(val, decimals)


def round_value_and_uncertainty_to_decimals(cont, val_key="y", unc_key="dy", decimals=3):
    """
    round values and uncertainty to some decimals
    default round to 3 digits after period
    possible use case: correlations where typical values are within -1,1

    : param cont : dictionary as returned e.g. by RootFileReader::read_hist_1d()
    : type  cont : dictionary

    : param decimals: how many decimals for the rounding
    : type  decimals: integer
    """

    decimals = int(decimals)

    for i, (val, unc) in enumerate(zip(cont[val_key], cont[unc_key])):
        cont[val_key][i] = round(val, decimals)
        if isinstance(unc, tuple):
            cont[unc_key][i] = (round(unc[0], decimals), round(unc[1], decimals))
        else:
            cont[unc_key][i] = round(unc, decimals)


def round_value_and_uncertainty(cont, val_key="y", unc_key="dy", sig_digits_unc=2):
    """
    round values and uncertainty according to the precision of the uncertainty,
    and also round uncertainty to a given number of significant digits
    Typical usage:
         reader = RootFileReader("rootfile.root")
         data = reader.read_hist_1d("histogramName")
         round_value_and_uncertainty(data,"y","dy",2)
    will round data["y"] to match the precision of data["dy"] for each element, after
    rounding each element of data["dy"] to 2 significant digits
    e.g. 26.5345 +/- 1.3456 --> 26.5 +/- 1.3

    : param cont : dictionary as returned e.g. by RootFileReader::read_hist_1d()
    : type  cont : dictionary

    : param sig_digits_unc: how many significant digits used to round the uncertainty
    : type  sig_digits_unc: integer
    """

    sig_digits_unc = int(sig_digits_unc)

    for i, (val, unc) in enumerate(zip(cont[val_key], cont[unc_key])):
        if isinstance(unc, tuple):
            # case for TGraphAsymmErrors with unc = (elow,ehigh), the central value is rounded
            # using the significant digits of the largest of the two uncertainties,
            # the smaller uncertainty would be rounded accordingly (at least 1 digit)
            # usually lower and higher uncertainties will be of the same order of magnitude
            # or at most different by 1 order (like +0.132  -0.083), in which case,
            # if choosing 2 significant digits, the rounding should result in +0.13  -0.08
            max_absunc = 0.0
            index_min_unc = 0
            # set default precision for both sides of uncertainty
            sig_digits_unc_ntuple = [sig_digits_unc, sig_digits_unc]
            if abs(unc[0]) < abs(unc[1]):
                max_absunc = abs(unc[1])
                index_min_unc = 0
                relative_precision = get_value_precision_wrt_reference(unc[0], unc[1])
            else:
                max_absunc = abs(unc[0])
                index_min_unc = 1
                relative_precision = get_value_precision_wrt_reference(unc[1], unc[0])
            # update precision on smaller uncertainty (at least 1 significant digit)
            sig_digits_unc_ntuple[index_min_unc] = int(max(1, sig_digits_unc + relative_precision))
            cont[unc_key][i] = (relative_round(unc[0], sig_digits_unc_ntuple[0]),
                                relative_round(unc[1], sig_digits_unc_ntuple[1]))
            val_precision = get_value_precision_wrt_reference(val, max_absunc)
            sig_digits_val = int(sig_digits_unc + val_precision)
            cont[val_key][i] = relative_round(val, sig_digits_val)
        else:
            # standard case for TH1 or TGraphErrors, uncertainty is a single value
            cont[unc_key][i] = relative_round(unc, sig_digits_unc)
            val_precision = get_value_precision_wrt_reference(val, unc)
            sig_digits_val = int(sig_digits_unc + val_precision)
            cont[val_key][i] = relative_round(val, sig_digits_val)


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


def any_uncertainties_nonzero(uncertainties, size):
    """
    Return a mask of bins where any of the uncertainties is nonzero.
    """
    nonzero = np.zeros(size, dtype=bool)

    for unc in uncertainties:
        if unc.is_symmetric:
            nonzero = nonzero | (np.array(unc.values) != 0)
        else:
            nonzero = nonzero | np.any((np.array(unc.values) != 0),axis=1)
    return nonzero

def sanitize_value(value):
    """
    Handle conversion of input types for internal storage.

    :param value: User-side input value to sanitize.
    :type value: string, int, or castable to float

    Strings and integers are left alone,
    everything else is converted to float.
    """
    if isinstance(value,str):
        return value
    if isinstance(value,int):
        return value
    return float(value)
