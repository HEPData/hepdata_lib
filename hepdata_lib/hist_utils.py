"""hepdata_lib utilities for interacting with scikit-hep hist histograms"""
from typing import Tuple, Optional, Union, List, Dict
import numpy

from hepdata_lib import Table, Variable, Uncertainty

# scikit-hep hist package
import hist
import hist.intervals


def read_hist(h: hist.Hist, flow: bool = False) -> Dict[str, numpy.ndarray]:
    """
    Converting the scikit-hep histogram in to a dictionary of numpy arrays that
    can be used for hepdata_lib Variable and Uncertainty declaration.

    For all axes define in the histogram, a `hepdata_lib.Variable` with
    `is_independent=True` should be declared. The `values` of this variable will
    be stored in the return dictionary following the axes names.

    Overflow and underflow bin will be handled using a single flag for all axes,
    so be sure to declare/modify histogram axes properties according to your
    needs.

    The storage content will be returned as is, so additional uncertainty
    processing will need to be handled by the user using the return values.
    """
    axes_entries = [_get_histaxis_array(ax, flow=flow) for ax in h.axes]
    axes_entries = numpy.meshgrid(*axes_entries)

    ## Getting axes return values
    readout = {ax.name: axes_entries[idx].flatten() for idx, ax in enumerate(h.axes)}

    ## Getting the histogram return values
    view = h.view(flow=flow)

    _storage_keys = {
        hist.storage.Weight: ["value", "variance"],
        hist.storage.Mean: ["value", ""],
    }

    if h.storage_type is hist.storage.Int64 or h.storage_type is hist.storage.Double:
        readout["hist_value"] = view.flatten()
    elif h.storage_type in _storage_keys:
        for key in _storage_keys[h.storage_type]:
            readout["hist_" + key] = view[key].flatten()
    else:
        raise NotImplementedError(
            f"Storage type {h.storage_type} currently not implemented"
        )

    return readout


def _get_histaxis_array(axis, flow: bool) -> numpy.ndarray:
    """
    Given an axis array, return the bin entries and a numpy array.

    For continuous axes, the return will be a Nx2 array of bin edge pairs. For
    categorical axes, the return will be a N array of bin content values. If the
    flow is set to true, the function will also add the overflow/underflow bins
    according to the settings found in axis.traits. For categorical axis, this
    will include an extra `__UNDETERMINED__` entry or a +1 entry.
    """

    ## Getting the entries as a simple list
    entries = [x for x in axis]

    ## Adding overflow bin
    if flow and axis.traits.overflow:
        if isinstance(axis, hist.axis.StrCategory):
            entries.append("__UNDETERMINED__")
        elif isinstance(axis, hist.axis.IntCategory):
            entries.append(entries[-1] + 1)
        else:
            entries.append((axis.edges[-1], numpy.inf))

    ## Adding underflow bin
    if flow and axis.traits.underflow:
        entries = [(-numpy.inf, axis.edges[0])] + entries

    ## Converting to numpy array
    if axis.traits.continuous:
        return numpy.array(entries, dtype="f,f")
    else:
        return numpy.array(entries)


def hist_as_variable(
    var_name,
    h: hist.Hist,
    flow: bool = False,
    uncertainty: Optional[Dict[str, Union[str, hist.Hist, numpy.ndarray]]] = None,
    **kwargs,
) -> Variable:
    """
    Returning this histogram entries as a Variable object, with a simpler
    interface for modifying uncertainty
    """
    if uncertainty is None:
        uncertainty = {}

    readout = read_hist(h, flow=flow)
    var = Variable(
        var_name,
        is_independent=False,
        is_binned=False,
        **kwargs,
    )
    var.values = readout["hist_value"]

    def _make_unc_array(x):
        if isinstance(x, float):
            return numpy.ones_like(readout["hist_value"]) * x
        elif isinstance(x, numpy.ndarray):
            return x
        elif isinstance(x, hist.Hist):
            return read_hist(x, flow=flow)["hist_value"]
        else:
            raise NotImplementedError(f"Unknown uncertainty format! {type(x)}")

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
            lo, up = _make_unc_array(unc_proc[0]), _make_unc_array(unc_proc[1])
            arr = [x for x in zip(lo, up)]
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
    if symmetric:
        if "hist_variance" not in readout.keys():
            numpy.sqrt(readout["hist_value"])
        else:  # Effective number of events
            sw, sw2 = readout["hist_value"], readout["hist_variance"]
            n_events = numpy.divide(
                sw**2, sw2, out=numpy.zeros_like(sw), where=(sw2 != 0)
            )
            rel_unc = numpy.divide(
                numpy.sqrt(n_events),
                n_events,
                out=numpy.zeros_like(sw),
                where=(n_events != 0),
            )
            return sw * rel_unc
        return numpy.sqrt(n_events)
    else:
        sw, sw2 = readout["hist_value"], readout["hist_value"]
        if "hist_variance" in readout.keys():
            sw2 = readout["hist_variance"]
        lo, up = hist.intervals.poisson_interval(sw, sw2)
        lo, up = lo - sw, up - sw
        return [x for x in zip(lo, up)]


def create_hist_base_table(
    table_name: str,
    h: hist.Hist,
    flow: bool = False,
    axes_rename: Optional[Dict[str, str]] = None,  # Additional axes proces
    axes_units: Optional[Dict[str, str]] = None,  # Additional axes proces
) -> Table:
    """
    Preparing the table based on hist, allows for the additional exclusion of
    axes via a list of string names
    """
    if axes_rename is None:
        axes_rename = {}
    if axes_units is None:
        axes_units = {}
    table = Table(table_name)

    readout = read_hist(h)

    for ax in h.axes:
        var_name = ax.name
        if ax.name in axes_rename:
            var_name = axes_rename[ax.name]
        elif ax.label:
            var_name = ax.label
        var = Variable(
            var_name,
            is_independent=True,
            is_binned=ax.traits.continuous,
            units=axes_units.get(ax.name, ""),
        )
        var.values = readout[ax.name]
        table.add_variable(var)

    return table
