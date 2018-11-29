"""hepdata_lib utilities to interact with ROOT data formats."""

from collections import defaultdict
import numpy as np
import ROOT as r
from hepdata_lib.helpers import check_file_existence

class RootFileReader(object):
    """Easily extract information from ROOT histograms, graphs, etc"""

    def __init__(self, tfile):
        self._tfile = None
        self.tfile = tfile

    def __del__(self):
        if self._tfile:
            self._tfile.Close()

    @property
    def tfile(self):
        """The TFile this reader reads from."""
        return self._tfile

    @tfile.setter
    def tfile(self, tfile):
        """
        Define the TFile to read from.

        :param tfile: ROOT file to read from.
        Can either be an already open TFile or a path to the file on disk.
        :type tfile: TFile or str
        """
        if isinstance(tfile, str):
            if not tfile.endswith(".root"):
                raise RuntimeError(
                    "RootFileReader: Input file is not a ROOT file (name does not end in .root)!"
                    )
            if check_file_existence(tfile):
                self._tfile = r.TFile(tfile)
        elif isinstance(tfile, r.TFile):
            self._tfile = tfile
        else:
            raise ValueError(
                "RootReader: Encountered unkonown type of variable passed as tfile argument: "
                + str(type(tfile)))

        if not self._tfile:
            raise IOError("RootReader: File not opened properly.")

    def retrieve_object(self, path_to_object):
        """
        Generalized function to retrieve a TObject from a file.

        There are two use cases:
        1)  The object is saved under the exact path given.
        In this case, the function behaves identically to TFile.Get.
        2)  The object is saved as a primitive in a TCanvas.
        In this case, the path has to be formatted as
        PATH_TO_CANVAS/NAME_OF_PRIMITIVE


        :param path_to_object: Absolute path in current TFile.
        :type path_to_object: str.
        :returns: TObject -- The object corresponding to the given path.
        """
        obj = self.tfile.Get(path_to_object)

        # If the Get operation was successful, just return
        # Otherwise, try canvas approach
        if obj:
            return obj
        parts = path_to_object.split("/")
        path_to_canvas = "/".join(parts[0:-1])
        name = parts[-1]

        try:
            canv = self.tfile.Get(path_to_canvas)
            assert canv
            for entry in list(canv.GetListOfPrimitives()):
                if entry.GetName() == name:
                    return entry

            # Didn't find anything. Print available primitives to help user debug.
            print("Available primitives in TCanvas '{0}':".format(
                path_to_canvas))
            for entry in list(canv.GetListOfPrimitives()):
                print("Name: '{0}', Type: '{1}'.".format(
                    entry.GetName(), type(entry)))
            assert False
            return entry

        except AssertionError:
            raise IOError(
                "Cannot find any object in file {0} with path {1}".format(
                    self.tfile, path_to_object))

    def read_graph(self, path_to_graph):
        """Extract lists of X and Y values from a TGraph.

        :param path_to_graph: Absolute path in the current TFile.
        :type path_to_graph: str

        :returns: dict -- For a description of the contents,
            check the documentation of the get_graph_points function.

        """
        graph = self.retrieve_object(path_to_graph)
        return get_graph_points(graph)

    def read_hist_2d(self, path_to_hist, **kwargs):
        # pylint: disable=anomalous-backslash-in-string
        r"""Read in a TH2.

        :param path_to_hist: Absolute path in the current TFile.
        :type path_to_hist: str
        :param \**kwargs: See below

        :Keyword Arguments:
            * *xlim* (``tuple``) --
                limit x-axis range to consider (xmin, xmax)
            * *ylim* (``tuple``) --
                limit y-axis range to consider (ymin, ymax)
            * *force_symmetric_errors* --
                Force readout of symmetric errors instead of determining type automatically

        :returns: dict -- For a description of the contents,
            check the documentation of the get_hist_2d_points function
        """
        xlim = kwargs.pop('xlim', (None, None))
        ylim = kwargs.pop('ylim', (None, None))
        force_symmetric_errors = kwargs.pop('force_symmetric_errors', False)
        if kwargs:
            raise TypeError('Unexpected **kwargs: %r' % kwargs)
        assert isinstance(xlim, (tuple, list))
        assert isinstance(ylim, (tuple, list))
        assert len(xlim) == 2
        assert len(ylim) == 2
        if xlim[0] and xlim[1]:
            assert all(isinstance(val, (int, float)) for val in xlim)
            assert xlim[0] < xlim[1]
        if ylim[0] and ylim[1]:
            assert all(isinstance(val, (int, float)) for val in ylim)
            assert ylim[0] < ylim[1]

        hist = self.retrieve_object(path_to_hist)
        return get_hist_2d_points(hist, xlim=xlim, ylim=ylim,
                                  force_symmetric_errors=force_symmetric_errors)

    def read_hist_1d(self, path_to_hist, **kwargs):
        # pylint: disable=anomalous-backslash-in-string
        r"""Read in a TH1.

        :param path_to_hist: Absolute path in the current TFile.
        :type path_to_hist: str
        :param \**kwargs: See below

        :Keyword Arguments:
            * *xlim* (``tuple``) --
                limit x-axis range to consider (xmin, xmax)
            * *force_symmetric_errors* --
                Force readout of symmetric errors instead of determining type automatically

        :returns: dict -- For a description of the contents,
            check the documentation of the get_hist_1d_points function
        """
        xlim = kwargs.pop('xlim', (None, None))
        force_symmetric_errors = kwargs.pop('force_symmetric_errors', False)
        if kwargs:
            raise TypeError('Unexpected **kwargs: %r' % kwargs)
        assert isinstance(xlim, (tuple, list))
        assert len(xlim) == 2
        if xlim[0] and xlim[1]:
            assert all(isinstance(val, (int, float)) for val in xlim)
            assert xlim[0] < xlim[1]

        hist = self.retrieve_object(path_to_hist)
        return get_hist_1d_points(hist, xlim=xlim, force_symmetric_errors=force_symmetric_errors)


    def read_tree(self, path_to_tree, branch_name):
        """Extract a list of values from a tree branch.

        :param path_to_tree: Absolute path in the current TFile.
        :type path_to_tree: str

        :param branch_name: Name of branch to read.
        :type branch_name: str

        :returns: list -- The values saved in the tree branch.

        """
        tree = self.tfile.Get(path_to_tree)
        if not tree or not isinstance(tree, r.TTree):
            raise RuntimeError("No TTree found for path '{0}'.".format(path_to_tree))
        values = []
        for event in tree:
            try:
                values.append(getattr(event, branch_name))
            except AttributeError:
                msg = "The TTree does not have a branch with name '{0}'.".format(branch_name)
                raise RuntimeError(msg)
        return values

    def read_limit_tree(self,
                        path_to_tree="limit",
                        branchname_x="mh",
                        branchname_y="limit"):
        """
        Read in CMS combine limit tree.

        :param path_to_tree: Absolute path in the current TFile
        :type path_to_tree: str

        :param branchname_x: Name of the branch that identifies each of the toys/parameter points.
        :type branchname_x: str

        :param branchname_y: Name of the branch that contains the limit values.
        :type branchname_y: str

        :returns: list -- Lists with 1+5 entries per
            toy/parameter point in the file.
            The entries correspond to the one number
            in the x branch and the five numbers in the y branch.

        """
        # store in multidimensional numpy array
        tree = self.tfile.Get(path_to_tree)
        points = int(tree.GetEntries() / 6)
        values = np.empty((points, 7))
        limit_values = []
        actual_index = 0
        for index, event in enumerate(tree):
            limit_values.append(getattr(event, branchname_y))
            # every sixth event starts a new limit value
            if index % 6 == 5:
                x_value = getattr(event, branchname_x)
                values[actual_index] = [x_value] + limit_values
                limit_values = []
                actual_index += 1
        return values

def get_hist_2d_points(hist, **kwargs):
    # pylint: disable=anomalous-backslash-in-string,too-many-locals
    r"""
    Get points from a TH2.

    :param hist: Histogram to extract points from
    :type hist: TH2D
    :param \**kwargs: See below

    :Keyword Arguments:
        * *xlim* (``tuple``) --
            limit x-axis range to consider (xmin, xmax)
        * *ylim* (``tuple``) --
            limit y-axis range to consider (ymin, ymax)
        * *force_symmetric_errors* --
                Force readout of symmetric errors instead of determining type automatically

    :returns: dict -- Lists of x/y/z values saved in dictionary.
        Corresponding keys are "x"/"y" for the values of the bin center on the
        respective axis. The bin edges may be found under "x_edges" and "y_edges"
        as a list of tuples (lower_edge, upper_edge).
        The bin contents and errors are stored under the "z" key.
        Bin content errors are stored under the "dz" key as either a list of floats (symmetric case)
        or a list of down/up tuples (asymmetric).
        Symmetric errors are returned if the histogram error option
        TH1::GetBinErrorOption() returns TH1::kNormal.
    """
    xlim = kwargs.pop('xlim', (None, None))
    ylim = kwargs.pop('ylim', (None, None))
    force_symmetric_errors = kwargs.pop('force_symmetric_errors', False)
    if kwargs:
        raise TypeError('Unexpected **kwargs: %r' % kwargs)
    assert isinstance(xlim, (tuple, list))
    assert isinstance(ylim, (tuple, list))
    assert len(xlim) == 2
    assert len(ylim) == 2
    if xlim[0] and xlim[1]:
        assert all(isinstance(val, (int, float)) for val in xlim)
        assert xlim[0] < xlim[1]
    if ylim[0] and ylim[1]:
        assert all(isinstance(val, (int, float)) for val in ylim)
        assert ylim[0] < ylim[1]

    points = {}
    for key in ["x", "y", "x_edges", "y_edges", "z", "dz"]:
        points[key] = []

    ixmin = hist.GetXaxis().FindBin(xlim[0]) if xlim[0] is not None else 1
    ixmax = hist.GetXaxis().FindBin(xlim[1]) if xlim[1] is not None else hist.GetNbinsX() + 1
    iymin = hist.GetYaxis().FindBin(ylim[0]) if ylim[0] is not None else 1
    iymax = hist.GetYaxis().FindBin(ylim[1]) if ylim[1] is not None else hist.GetNbinsY() + 1
    symmetric = (hist.GetBinErrorOption() == r.TH1.kNormal)
    if force_symmetric_errors:
        symmetric = True
    for x_bin in range(ixmin, ixmax):
        x_val = hist.GetXaxis().GetBinCenter(x_bin)
        width_x = hist.GetXaxis().GetBinWidth(x_bin)
        for y_bin in range(iymin, iymax):
            y_val = hist.GetYaxis().GetBinCenter(y_bin)
            z_val = hist.GetBinContent(x_bin, y_bin)

            if symmetric:
                dz_val = hist.GetBinError(x_bin, y_bin)
            else:
                dz_val = (- hist.GetBinErrorLow(x_bin, y_bin),
                          hist.GetBinErrorUp(x_bin, y_bin))

            width_y = hist.GetYaxis().GetBinWidth(y_bin)

            points["x"].append(x_val)
            points["x_edges"].append((x_val - width_x / 2, x_val + width_x / 2))

            points["y"].append(y_val)
            points["y_edges"].append((y_val - width_y / 2, y_val + width_y / 2))

            points["z"].append(z_val)
            points["dz"].append(dz_val)

    return points


def get_hist_1d_points(hist, **kwargs):
    # pylint: disable=anomalous-backslash-in-string
    r"""
    Get points from a TH1.

    :param hist: Histogram to extract points from
    :type hist: TH1D
    :param \**kwargs: See below

    :Keyword Arguments:
        * *xlim* (``tuple``) --
            limit x-axis range to consider (xmin, xmax)
        * *force_symmetric_errors* --
                Force readout of symmetric errors instead of determining type automatically

    :returns: dict -- Lists of x/y values saved in dictionary.
        Corresponding keys are "x" for the value of the bin center.
        The bin edges may be found under "x_edges" as a list of tuples (lower_edge, upper_edge).
        The bin contents are stored under the "y" key.
        Bin content errors are stored under the "dy" key as either a list of floats (symmetric case)
        or a list of down/up tuples (asymmetric).
        Symmetric errors are returned if the histogram error option
        TH1::GetBinErrorOption() returns TH1::kNormal.
    """
    xlim = kwargs.pop('xlim', (None, None))
    force_symmetric_errors = kwargs.pop('force_symmetric_errors', False)
    if kwargs:
        raise TypeError('Unexpected **kwargs: %r' % kwargs)
    assert isinstance(xlim, (tuple, list))
    assert len(xlim) == 2
    if xlim[0] and xlim[1]:
        assert all(isinstance(val, (int, float)) for val in xlim)
        assert xlim[0] < xlim[1]

    points = {}
    for key in ["x", "y", "x_edges", "dy"]:
        points[key] = []

    symmetric = (hist.GetBinErrorOption() == r.TH1.kNormal)
    if force_symmetric_errors:
        symmetric = True
    ixmin = hist.GetXaxis().FindBin(xlim[0]) if xlim[0] is not None else 1
    ixmax = hist.GetXaxis().FindBin(xlim[1]) if xlim[1] is not None else hist.GetNbinsX() + 1
    for x_bin in range(ixmin, ixmax):
        x_val = hist.GetXaxis().GetBinCenter(x_bin)
        width_x = hist.GetXaxis().GetBinWidth(x_bin)

        y_val = hist.GetBinContent(x_bin)
        if symmetric:
            dy_val = hist.GetBinError(x_bin)
        else:
            dy_val = (-hist.GetBinErrorLow(x_bin), hist.GetBinErrorUp(x_bin))

        points["x"].append(x_val)
        points["x_edges"].append((x_val - width_x / 2, x_val + width_x / 2))

        points["y"].append(y_val)
        points["dy"].append(dy_val)

    return points


def get_graph_points(graph):
    """
    Extract lists of X and Y values from a TGraph.

    :param graph: The graph to extract values from.
    :type graph: TGraph, TGraphErrors, TGraphAsymmErrors

    :returns: dict -- Lists of x, y values saved in dictionary (keys are "x" and "y").
        If the input graph is a TGraphErrors (TGraphAsymmErrors),
        the dictionary also contains the errors (keys "dx" and "dy").
        For symmetric errors, the errors are simply given as a list of values.
        For asymmetric errors, a list of tuples of (down,up) values is given.

    """

    # Check input
    if not isinstance(graph, (r.TGraph, r.TGraphErrors, r.TGraphAsymmErrors)):
        raise TypeError(
            "Expected to input to be TGraph or similar, instead got '{0}'".
            format(type(graph)))

    # Extract points
    points = defaultdict(list)

    for i in range(graph.GetN()):
        x_val = r.Double()
        y_val = r.Double()
        graph.GetPoint(i, x_val, y_val)
        points["x"].append(float(x_val))
        points["y"].append(float(y_val))
        if isinstance(graph, r.TGraphErrors):
            points["dx"].append(graph.GetErrorX(i))
            points["dy"].append(graph.GetErrorY(i))
        elif isinstance(graph, r.TGraphAsymmErrors):
            points["dx"].append((-graph.GetErrorXlow(i),
                                 graph.GetErrorXhigh(i)))
            points["dy"].append((-graph.GetErrorYlow(i),
                                 graph.GetErrorYhigh(i)))

    return points
