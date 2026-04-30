"""hepdata_lib helper functions."""

import os
import subprocess
import fnmatch
import math
import numpy as np


## File and command functions

def execute_command(command):
    """
    Execute shell command using subprocess.
    If executable does not exist, return False.
    For other errors raise RuntimeError.
    Else return True on success.

    :param command: Command to execute.
    :type command: string
    """

    subprocess_args = {
        "args": command,
        "stdin": subprocess.PIPE,
        "stdout": subprocess.PIPE,
        "stderr": subprocess.PIPE,
        "shell": True,
        "universal_newlines": True
    }
    with subprocess.Popen(**subprocess_args) as proc:
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


def convert_pdf_to_png(source, target):
    """
    Wrapper for the ImageMagick convert utility.

    :param source: Source file in PDF format.
    :type source: str
    :param target: Output file in PNG format.
    :type target: str
    """
    assert os.path.exists(source), f"Source file does not exist: {source}"

    command = f"convert -flatten -density 300 -fuzz 1% -trim +repage {source} {target}"
    command_ok = execute_command(command)
    if not command_ok:
        print("ImageMagick does not seem to be installed \
                or is not in the path - not adding any images.")


def convert_png_to_thumbnail(source, target):
    """
    Wrapper for the ImageMagick convert utility in thumbnail mode.

    :param source: Source file in PNG format.
    :type source: str
    :param target: Output thumbnailfile in PNG format.
    :type target: str
    """

    command = f"convert -thumbnail 240x179 {source} {target}"
    command_ok = execute_command(command)

    if not command_ok:
        print("ImageMagick does not seem to be installed \
                or is not in the path - not adding any images.")


def file_is_outdated(file_path, reference_file_path):
    """
    Check if the given file is outdated compared to the reference file.

    Also returns true if the reference file does not exist.

    :param file_path: Path to the file to check.
    :type file_path: str
    :param reference_file_path: Path to the reference file.
    :type reference_file_path: str
    """
    if not os.path.exists(reference_file_path):
        raise RuntimeError(f"Reference file does not exist: {reference_file_path}")
    if not os.path.exists(file_path):
        return True

    modification_outdated = os.path.getmtime(file_path) < os.path.getmtime(reference_file_path)
    change_outdated = os.path.getctime(file_path) < os.path.getctime(reference_file_path)

    return modification_outdated | change_outdated


def find_all_matching(path, pattern):
    """Utility function that works like 'find' in bash."""
    if not os.path.exists(path):
        raise RuntimeError(f"Invalid path '{path}'")
    result = []
    for root, _, files in os.walk(path):
        for thisfile in files:
            if fnmatch.fnmatch(thisfile, pattern):
                result.append(os.path.join(root, thisfile))
    return result


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
        raise RuntimeError(f"File too big: '{path_to_file}'. Maximum allowed value is {upper_limit}"
        + "MB.")
    if lower_limit and size < lower_limit:
        raise RuntimeError(f"File too small: '{path_to_file}'."
        + f"Minimal allowed value is {lower_limit} MB.")



## Value type, formatting and numerical-precision functions

def sanitize_value(value):
    """
    Handle conversion of input types for internal storage.

    :param value: User-side input value to sanitize.
    :type value: string, int, NoneType, or castable to float

    Strings, integers and None are left alone,
    everything else is converted to float.
    """
    if isinstance(value, str):
        return value
    if isinstance(value, int):
        return value
    if value is None:
        return value
    return float(value)


def get_number_precision(value):
    """
    Get the scale of an input value, i.e. its rounded-up power of 10.
    Exact integer powers of 10 are assigned the same scale/precision as smaller numbers
    For example
    get_number_precision(10.0) = 1
    get_number_precision(10.001) = 2
    get_number_precision(9.999) = 1
    """

    if isinstance(value, tuple):
        return tuple(get_number_precision(x) for x in value)

    # if value is tuple, value == 0 might cause ValueError saying that
    # 'The truth value of an array with more than one element is ambiguous'
    # Thus, tuple is evaluated above
    if value == 0 or isinstance(value, str) or np.isnan(value) or np.isinf(value):
        return value

    return math.ceil(math.log10(abs(value)))


def get_number_size(value, rtn_for_zero=float("nan")):
    """A near synonym for get_number_precision, with an optional
    argument to return for values equal to zero (and hence with no
    well-defined order of magnitude).

    This feature is provided since returning 0 or 0.0 can lead to
    over-rounding if one uncertainty component is zero. The default
    value is NaN, but e.g. None or -float("inf") might sometimes be
    more appropriate.

    : param value : number to evaluate
    : type  value : float or tuple[float]

    : returns : order of magnitude (rounded-up power of 10) of ``value``,
                normally integer except in the zero-value failure mode

    """

    # handle tuples like get_number_precision does
    if isinstance(value, tuple):
        return tuple(get_number_size(x) for x in value)

    if value == 0:
        return rtn_for_zero

    return get_number_precision(value)


def get_value_precision_wrt_reference(value, reference):
    """
    Get the relative precision (scale) of the first argument with respect to the second one

    ``value`` and ``reference`` are both float and/or int
    ``value`` can be float when reference is an int and vice-versa

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


def get_value_size_wrt_reference(value, reference, size_for_zero=float("nan")):
    """
    Like the get_value_precision_wrt_reference but calling get_number_size
    rather than get_number_precision, and with the optional zero-return
    option of the former.

    ``value`` and ``reference`` are both float and/or int
    ``value`` can be float when reference is an int and vice-versa

    : param value: first value
    : type  value: float, int

    : param reference: reference value (usually the uncertainty on value)
    : type  reference: float, int

    : param size_for_zero: the size value to be used for zero-valued ``value`` or ``reference``
    : type  size_for_zero: float, int
    """

    this_function = "get_value_size_wrt_reference()"
    good_types = [int, float]
    arguments = [value, reference]

    # first check all arguments have appropriate type
    for input_arg in arguments:
        if not any(isinstance(input_arg, x) for x in good_types):
            raise ValueError("Unsupported input type passed to " + this_function)

    return get_number_size(value, size_for_zero) - get_number_size(reference, size_for_zero)


def relative_round(value, relative_digits):
    """Rounds to a given relative precision"""

    if isinstance(value, tuple):
        return tuple(relative_round(x, relative_digits) for x in value)

    if value == 0 or isinstance(value, str) or np.isnan(value) or np.isinf(value):
        return value

    value_precision = get_number_precision(value)
    absolute_digits = -value_precision + relative_digits  # pylint: disable=invalid-unary-operand-type

    return round(value, int(absolute_digits))


def round_multiple(uncs, sig_digits=2, no_round_to_zero=True):
    """
    Round a collection of values to the precision required for the given sd's to
    appear on the larger uncertainty component e.g. +1.3456 -0.2345 @ 2sf --> +1.3 -0.2

    Mainly designed for handling uncertainty (particularly an asymmetric +/- pair),
    but written to be more generally usable. A passed single number will be handled
    transparently, without wrapping in an iterable.

    : param uncs : iterable of values (primarily uncertainties)
    : type  uncs : float or iterable[float]

    : param sig_digits : how many significant digits on the leading component
    : type  sig_digits : integer

    : param no_round_to_zero : if true, ensure always at least one sd per component
    : type  no_round_to_zero : bool

    : returns : float or list/tuple[float]) of rounded values and a list of the digit
                precisions used for each component (this is a list even for scalar
                ``uncs``; note that it can contain NaNs due to zero-valued components)
    """
    try: #< if this fails, uncs isn't iterable -> fall back to scalar
        # get orders of magnitude of each component
        unc_orders = [get_number_size(u) for u in uncs]
        # base the nominal precision on the target number of sd's on the largest component
        ptarget = -int(np.nanmax(unc_orders)) + sig_digits
        # customise the precisions for each component (if instructed to prevent rounding to zero)
        ptargets = [(max(ptarget, -uo+1) if no_round_to_zero else ptarget) for uo in unc_orders]
        # do the (maybe custom) rounding
        newuncs = [round(u, ptargets[i]) for (i, u) in enumerate(uncs)]
        # return as a tuple if the input was a tuple (for ROOT use-case & test consistency)
        if type(uncs) is tuple:
            newuncs = tuple(newuncs)
        return newuncs, ptargets if no_round_to_zero else ptarget
    except TypeError:
        unc_order = get_number_size(uncs)
        newunc = relative_round(uncs, sig_digits)
        return newunc, [-unc_order+sig_digits]


def round_value_and_uncertainty_arrs(vals, uncs, sig_digits_unc=2):
    """
    Round arrays of values and a single uncertainty source according to
    the precision of the uncertainty, row by row, and also round the
    uncertainties to a given number of significant digits.

    Named with the _arrs suffix as the pre-existing, canonically named
    versions operate on dicts from the ROOT reader.

    Operates directly on matched lists of values and uncertainties.
    Tuple-valued uncertainty entries are assumed to be a +- asymm pair
    for that data point, and the larger is used to define the reference
    precision.

    This will round each ``val`` to match the precision of its corresponding
    ``unc``, after rounding each element of ``unc`` to 2 significant digits
    e.g. 26.5345 +/- 1.3456 --> 26.5 +/- 1.3 . At least one sd of the value
    will always be reported, though 100% errors are not commonly published.

    : param vals : y values
    : type  vals : iterable of float

    : param uncs : y uncertainty values
    : type  uncs : iterable of float or tuple[float]

    : param sig_digits_unc: how many significant digits used to round the uncertainty
    : type  sig_digits_unc: integer

    : returns : modified (vals, uncs). Note that arguments are also modified in-place.
    """

    sig_digits_unc = int(sig_digits_unc)

    for i, (val, unc) in enumerate(zip(vals, uncs)):
        # Two possible types for unc:
        # - standard case for TH1 or TGraphErrors: uncertainty is a single value
        # - case for TGraphAsymmErrors: uncertainty is a tuple(elow, ehigh)
        # round_multiple handles both scalar and tuple in a transparent way
        uncs[i], uncprecisions = round_multiple(unc, sig_digits_unc, True)
        valprecision = -get_number_size(val)+1
        vals[i] = round(val, max(int(np.nanmin(uncprecisions)), valprecision))

    return vals, uncs


def round_value_and_multiple_uncertainties_arrs(vals, unclists, sig_digits_unc=2):
    """
    Round values and multiple uncertainty sources according to the precision of the
    largest uncertainty, and also round each (asymm) uncertainty to a given number
    of significant digits.

    Named with the _arrs suffix as the pre-existing, canonically named
    versions operate on dicts from the ROOT reader.

    The rounding of each error source is performed independently, with at least one
    sd always shown. The smallest precision encountered in the error set (i.e. the
    largest uncertainty component) is used to define the precision of the value's
    rounding. At least one sd of the value will always be reported, though 100% errors
    are not commonly published.

    : param cont : dictionary as returned e.g. by ``RootFileReader::read_hist_1d()``
    : type  cont : dictionary

    : param sig_digits_unc: how many significant digits used to round the uncertainty
    : type  sig_digits_unc: integer

    : returns : modified (vals, unclists). Note that arguments are also modified in-place.
    """

    sig_digits_unc = int(sig_digits_unc)

    for ipt, val in enumerate(vals):
        # the value precision will match that of the largest error, but start with this upper bound
        valprecision = max(-get_number_size(val)+sig_digits_unc, sig_digits_unc)
        # get the list of uncertainty sources for the i'th val
        uncs_ipt = [ul[ipt] for ul in unclists]
        # round each error source independently with their larger component getting the target sd's
        minuncprecision = np.inf #< TODO: there's probably a less pessimistic int starting value!
        for iu, u in enumerate(uncs_ipt):
            u_rnd, uprecisions = round_multiple(u, sig_digits_unc, True)
            unclists[iu][ipt] = u_rnd
            minuncprecision = int(np.nanmin(np.hstack((uprecisions, minuncprecision))))
        # round the value to match the precision of the largest error component
        valprecision = min(minuncprecision, valprecision)
        vals[ipt] = round(val, valprecision)

    return vals, unclists


def round_value_and_uncertainty(cont, val_key="y", unc_key="dy", sig_digits_unc=2):
    """
    Round values and uncertainty according to the precision of the uncertainty,
    and also round uncertainty to a given number of significant digits, on a
    dictionary of values and uncertainties like that returned by RootFileReader.

    Typical usage::

         reader = RootFileReader("rootfile.root")
         data = reader.read_hist_1d("histogramName")
         round_value_and_uncertainty(data,"y","dy",2)

    will round ``data["y"]`` to match the precision of ``data["dy"]`` for each
    element, after rounding each element of ``data["dy"]`` to 2 significant digits
    e.g. 26.5345 +/- 1.3456 --> 26.5 +/- 1.3 . At least one sd of the value
    will always be reported, though 100% errors are not commonly published.

    : param cont : dictionary as returned e.g. by ``RootFileReader::read_hist_1d()``
    : type  cont : dictionary

    : param sig_digits_unc: how many significant digits used to round the uncertainty
    : type  sig_digits_unc: integer
    """
    #assert isinstance(cont, dict)
    round_value_and_uncertainty_arrs(cont[val_key], cont[unc_key], sig_digits_unc)


def round_value_to_decimals(cont, key="y", decimals=3):
    """
    Round all values in a dictionary to some decimals in one go.

    The default is to round to 3 digits after the period.
    Possible use case: correlations where typical values are within -1,1

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
    Round values and uncertainty to some decimals.

    The default is to round to 3 digits after the period.
    Possible use case: correlations where typical values are within -1,1

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


def any_uncertainties_nonzero(uncertainties, size):
    """
    Return a mask of bins where any of the uncertainties is nonzero.
    """
    nonzero = np.zeros(size, dtype=bool)

    for unc in uncertainties:

        # Treat one-sided uncertainties as
        tmp = 0 if unc.is_symmetric else (0,0)
        values = np.array([tmp if v is None else v for v in unc.values])
        values[values.astype(str)==''] = 0
        values = values.astype(float)

        if unc.is_symmetric:
            nonzero = nonzero | (values != 0)
        else:
            nonzero = nonzero | np.any(values != 0,axis=1)
    return nonzero
