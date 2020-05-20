"""hepdata_lib helper functions."""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import subprocess
import fnmatch
import math
import numpy as np
import itertools

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

    if value == 0 or isinstance(value, str) or np.isnan(value) or np.isinf(value):
        return value

    if isinstance(value, tuple):
        return (relative_round(x, relative_digits) for x in value)

    value_precision = math.ceil(math.log10(abs(value)))

    absolute_digits = max(0,-value_precision + relative_digits)

    return round(value, int(absolute_digits))


def getNumberPrecision(value):

    if value == 0 or isinstance(value, str) or np.isnan(value) or np.isinf(value):
        return value
    if isinstance(value, tuple):
        return (getNumberPrecision(x) for x in value)

    return math.ceil(math.log10(abs(value)))


def getValuePrecisionWrtReference(value,reference):
    """
    relative precision of first argument with respect to the second one 
    value and reference must be of the same type
    usually they are float, but should also work for tuples

    : param value: first value
    : type  value: float

    : param reference: reference value (usually the uncertainty on value)
    : type  reference: float
    """
    return getNumberPrecision(value) - getNumberPrecision(reference)


def roundValueToDecimals(cont, valKey="y", decimals=3):

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

    for i,v in enumerate(cont[valKey]):        
        if isinstance(v, tuple):
            cont[valKey][i] = (round(v[0], decimals),
                               round(v[1], decimals)
                           )
        else:
            cont[valKey][i] = round(v,decimals)


def roundValueAndUncertaintyToDecimals(cont, valKey="y", uncKey="dy", decimals=3):

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

    for i,(v,e) in enumerate(itertools.izip(cont[valKey],cont[uncKey])):        
        cont[valKey][i] = round(v,decimals)
        if isinstance(e, tuple):
            cont[uncKey][i] = (round(e[0], decimals),
                               round(e[1], decimals)
                           )
        else:
            cont[uncKey][i] = round(e,decimals)


def roundValueAndUncertainty(cont, valKey="y", uncKey="dy", sigDigitsUnc=2):
    
    """
    round values and uncertainty according to the precision of the uncertainty,
    and also round uncertainty to a given number of significant digits
    Typical usage:
         reader = RootFileReader("rootfile.root")
         data = reader.read_hist_1d("histogramName")    
         roundValueAndUncertainty(data,"y","dy",2)
    will round data["y"] to match the precision of data["dy"] for each element, after
    rounding each element of data["dy"] to 2 significant digits
    e.g. 26.5345 +/- 1.3456 --> 26.5 +/- 1.3
    
    : param cont : dictionary as returned e.g. by RootFileReader::read_hist_1d()
    : type  cont : dictionary

    : param sigDigitsUnc: how many significant digits used to round the uncertainty
    : type  sigDigitsUnc: integer
    """

    sigDigitsUnc = int(sigDigitsUnc)

    for i,(v,e) in enumerate(itertools.izip(cont[valKey],cont[uncKey])):        
        if isinstance(e, tuple):
            """
            case for TGraphAsymmErrors with e = (elow,ehigh), the central value is rounded 
            using the significant digits of the largest of the two uncertainties,
            the smaller uncertainty would be rounded accordingly (at least 1 digit)
            usually lower and higher uncertainties will be of the same order of magnitude
            or at most different by 1 order (like +0.132  -0.083), in which case, 
            if choosing 2 significant digits, the rounding should result in +0.13  -0.08
            """
            maxabse = 0.0
            minIndex = 0
            # set default precision for both sides of uncertainty
            sigDigitsUncNtuple = [sigDigitsUnc, sigDigitsUnc]
            if abs(e[0]) < abs(e[1]):
                maxabse = abs(e[1])
                minIndex = 0
                relativePrecision = getValuePrecisionWrtReference(e[0],e[1])
            else:
                maxabse = abs(e[0])
                minIndex = 1
                relativePrecision = getValuePrecisionWrtReference(e[1],e[0])
            # update precision on smaller uncertainty (at least 1 significant digit)
            sigDigitsUncNtuple[minIndex] = int(max(1,sigDigitsUnc+relativePrecision))
            cont[uncKey][i] = (relative_round(e[0], sigDigitsUncNtuple[0]),
                               relative_round(e[1], sigDigitsUncNtuple[1])
                           )
            cont[valKey][i] = relative_round(v,int(sigDigitsUnc+getValuePrecisionWrtReference(v,maxabse)))
        else:
            # standard case for TH1 or TGraphErrors, uncertainty is a single value
            cont[uncKey][i] = relative_round(e,sigDigitsUnc)
            cont[valKey][i] = relative_round(v,int(sigDigitsUnc+getValuePrecisionWrtReference(v,e)))


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
