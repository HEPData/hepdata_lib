"""hepdata_lib utilities for interacting with scikit-hep hist histograms"""
from typing import Dict, Optional, Union

# scikit-hep hist package
import hist
import hist.intervals
import numpy

from hepdata_lib import Table, Uncertainty, Variable


def read_hist(histo: hist.Hist, flow: bool = False) -> Dict[str, numpy.ndarray]:
    """
    Converting the scikit-hep histogram in to a dictionary of numpy arrays that
    can be used for hepdata_lib Variable and Uncertainty declaration.

    For all axes define in the histogram, a `hepdata_lib.Variable` with
    `is_independent=True` should be declared. The `values` of this variable
    will be stored in the return dictionary following the axes names.

    Overflow and underflow bin will be handled using a single flag for all
    axes, so be sure to declare/modify histogram axes properties according to
    your needs.

    The storage content will be returned as is, so additional uncertainty
    processing will need to be handled by the user using the return values.
    """
    axes_entries = [_get_histaxis_array(ax, flow=flow) for ax in reversed(histo.axes)]
    axes_entries = numpy.meshgrid(*axes_entries)

    # Getting axes return values
    readout = {
        ax.name: axes_entries[idx].flatten()
        for idx, ax in enumerate(reversed(histo.axes))
    }

    # Getting the histogram return values
    view = histo.view(flow=flow)

    if view.dtype.names is None:  # Single value storages
        readout["hist_value"] = view.flatten()
    else:
        for var_name in view.dtype.names:
            readout["hist_" + var_name] = view[var_name].flatten()

    return readout


def _get_histaxis_array(axis, flow: bool) -> numpy.ndarray:
    """
    Given an axis array, return the bin entries and a numpy array.

    For continuous axes, the return will be a Nx2 array of bin edge pairs. For
    categorical axes, the return will be a N array of bin content values. If
    the flow is set to true, the function will also add the overflow/underflow
    bins according to the settings found in axis.traits. For categorical axis,
    this will include an extra `"__UNDETERMINED__"` entry (for StrCategory) or
    an +1 entry (for IntCategory).
    """

    # Getting the entries as a simple list
    entries = list(axis)

    # Adding overflow bin
    if flow and axis.traits.overflow:
        if isinstance(axis, hist.axis.StrCategory):
            entries.append("__UNDETERMINED__")
        elif isinstance(axis, hist.axis.IntCategory):
            entries.append(entries[-1] + 1)
        elif isinstance(axis, hist.axis.Integer):
            entries.append(numpy.inf)
        else:
            entries.append((axis.edges[-1], numpy.inf))

    # Adding underflow bin
    if flow and axis.traits.underflow:
        if isinstance(axis, hist.axis.Integer):
            entries = [-numpy.inf] + entries
        else:
            entries = [(-numpy.inf, axis.edges[0])] + entries

    # Converting to numpy array
    if axis.traits.continuous:
        entries = numpy.array(entries, dtype="f,f")
    else:
        entries = numpy.array(entries)

    return entries


def hist_as_variable(
    var_name,
    histo: hist.Hist,
    flow: bool = False,
    uncertainty: Optional[Dict[str, Union[str, hist.Hist, numpy.ndarray]]] = None,
    **kwargs,
) -> Variable:
    """
    Returning this histogram entries as a Variable object, with a simpler
    interface for automatically generating values uncertainties.

    The `h` and `flow` inputs are passed directly to the `read_hist` method to
    extract the value to be used for the variable.

    The `uncertainty` is a dictionary defining how uncertainties should be
    defined. Dictionary keys are used as the name of the uncertainty, while the
    value defines how the uncertainty should be constructed. This can either
    be:

    - `str`: either "poisson_asym" or "poisson_sym", indicating to extract
      Poisson uncertainty directly from the histogram values. (Either the
      asymmetric Garwood interval defined by `hist.intervals` or a simply,
      symmetric `sqrt(n)`.)
    - `float`: A flat uncertainty to be used on all bins.
    - `numpy.ndarray`: An array indicating the uncertainty for each bin. The
      array should be compatible with the output of `read_hist['hist_values']`
    - `hist.Hist`: The histogram with bin values indicating the uncertainty to
      be used for each bin. The histogram should be compatible with the input
      histogram.
    - `tuple(T,T)` where `T` can either be a `float`, `numpy.ndarray` or
      `hist.Hist`. This is used to indicate asymmetric uncertainties, following
      the lower/upper ordering convention of hepdata_lib
    """
    if uncertainty is None:
        uncertainty = {}

    readout = read_hist(histo, flow=flow)
    var = Variable(
        var_name,
        is_independent=False,
        is_binned=False,
        **kwargs,
    )
    var.values = readout["hist_value"]

    def _make_unc_array(unc_val):
        if isinstance(unc_val, float):
            return numpy.ones_like(readout["hist_value"]) * unc_val
        if isinstance(unc_val, numpy.ndarray):
            return unc_val.flatten()
        if isinstance(unc_val, hist.Hist):
            return read_hist(unc_val, flow=flow)["hist_value"]
        raise NotImplementedError(f"Unknown uncertainty format! {type(unc_val)}")

    for unc_name, unc_proc in uncertainty.items():
        is_symmetric = None
        if isinstance(unc_proc, str):
            if unc_proc == "poisson_sym":  # Symmetric poisson uncertainty
                is_symmetric = True
                arr = _make_poisson_unc_array(readout, is_symmetric)
            elif unc_proc == "poisson_asym":  # Asymmetric poisson uncertainty
                is_symmetric = False
                arr = _make_poisson_unc_array(readout, is_symmetric)
            else:
                raise NotImplementedError(f"Unknown uncertainty process {unc_proc}")
        elif isinstance(unc_proc, tuple):  # Asymmetric uncertainty
            is_symmetric = False  #
            assert len(unc_proc) == 2, "Asymmetric uncertainty can only have 2 entries"
            _lo, _up = _make_unc_array(unc_proc[0]), _make_unc_array(unc_proc[1])
            arr = list(zip(_lo, _up))
        else:  # Assuming symmetric error
            is_symmetric = True
            arr = _make_unc_array(unc_proc)

        assert len(arr) == len(readout["hist_value"]), "Mismatch array formats"

        unc_var = Uncertainty(unc_name, is_symmetric=is_symmetric)
        unc_var.values = arr
        var.add_uncertainty(unc_var)

    return var


def _make_poisson_unc_array(
    readout: Dict[str, numpy.ndarray], symmetric: bool
) -> numpy.ndarray:
    """
    Given the results of `read_hist`, extract the Poisson uncertainty using
    hist.intervals. Automatically detecting the histogram storage type to
    handle weighted uncertainties
    """
    if symmetric:
        if "hist_variance" not in readout.keys():
            n_events = numpy.sqrt(readout["hist_value"])
            unc_arr = numpy.sqrt(n_events)
        else:  # Effective number of events
            _sw, _sw2 = readout["hist_value"], readout["hist_variance"]
            n_events = numpy.divide(
                _sw**2, _sw2, out=numpy.zeros_like(_sw), where=(_sw2 != 0)
            )
            rel_unc = numpy.divide(
                numpy.sqrt(n_events),
                n_events,
                out=numpy.zeros_like(_sw),
                where=(n_events != 0),
            )
            unc_arr = _sw * rel_unc
    else:
        _sw, _sw2 = readout["hist_value"], readout["hist_value"]
        if "hist_variance" in readout.keys():
            _sw2 = readout["hist_variance"]
        _lo, _up = hist.intervals.poisson_interval(_sw, _sw2)
        _lo, _up = _lo - _sw, _up - _sw
        # Suppressing the NAN for zero-entry events
        _lo = numpy.nan_to_num(_lo, nan=0.0)
        _up = numpy.nan_to_num(_up, nan=0.0)
        unc_arr = list(zip(_lo, _up))

    return unc_arr


def create_hist_base_table(
    table_name: str,
    histo: hist.Hist,
    flow: bool = False,
    axes_rename: Optional[Dict[str, str]] = None,
    axes_units: Optional[Dict[str, str]] = None,
) -> Table:
    """
    Preparing the table based on hist. This constructs just the histogram axis
    as the table variable. Histogram entries should be added via the
    `hist_as_variable` method.
    """
    if axes_rename is None:
        axes_rename = {}
    if axes_units is None:
        axes_units = {}
    table = Table(table_name)

    readout = read_hist(histo, flow=flow)

    for axis in histo.axes:
        var_name = axis.name
        if axis.name in axes_rename:
            var_name = axes_rename[axis.name]
        elif axis.label:
            var_name = axis.label
        var = Variable(
            var_name,
            is_independent=True,
            is_binned=axis.traits.continuous,
            units=axes_units.get(axis.name, ""),
        )
        var.values = readout[axis.name]
        table.add_variable(var)

    return table
