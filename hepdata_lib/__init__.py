"""hepdata_lib main."""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
import os
import fnmatch
import math
from collections import defaultdict
import subprocess
import warnings
import shutil
import yaml
# try to use LibYAML bindings if possible
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper
from yaml.representer import SafeRepresenter
import numpy as np
import ROOT as r


MAPPING_TAG = yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG


def dict_representer(dumper, data):
    """represent dict."""
    return dumper.represent_dict(data.iteritems())


def dict_constructor(loader, node):
    """construct dict."""
    return defaultdict(loader.construct_pairs(node))


Dumper.add_representer(defaultdict, dict_representer)
Loader.add_constructor(MAPPING_TAG, dict_constructor)

Dumper.add_representer(str,
                       SafeRepresenter.represent_str)


# Display deprecation warnings
warnings.filterwarnings("always", category=DeprecationWarning, module="hepdata_lib")

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

class Variable(object):
    """A Variable is a wrapper for a list of values + some meta data."""

    # pylint: disable=too-many-instance-attributes
    # Eight is reasonable in this case.

    def __init__(self, name, is_independent=True, is_binned=True, units=""):
        self.name = name
        self.is_independent = is_independent
        self.is_binned = is_binned
        self.qualifiers = []
        self.units = units
        # needed to make pylint happy, see https://github.com/PyCQA/pylint/issues/409
        self._values = None
        self.values = []
        self.uncertainties = []
        self.digits = 5

    @property
    def values(self):
        """Value getter."""
        return self._values

    @values.setter
    def values(self, value_list):
        """Value Setter."""
        if self.is_binned:
            self._values = [(float(x[0]), float(x[1])) for x in value_list]
        else:
            self._values = [x if isinstance(x, str) else float(x) for x in value_list]

    def scale_values(self, factor):
        """Multiply each value by constant factor. Also applies to uncertainties."""
        if not self.is_binned:
            self.values = [factor * x for x in self.values]
        else:
            self.values = [(factor * x[0], factor * x[1])
                           for x in self.values]

        for unc in self.uncertainties:
            unc.scale_values(factor)

    def add_qualifier(self, name, value, units=""):
        """Add a qualifier."""
        qualifier = {}
        qualifier["name"] = name
        qualifier["value"] = value  # if type(value) == str else float(value)
        if units:
            qualifier["units"] = units
        self.qualifiers.append(qualifier)

    def add_uncertainty(self, uncertainty):
        """
        Add an uncertainty.

        If the Variable object already has values assigned to it,
        it is required that the value list of the Uncertainty object
        has the same length as the list of Variable values.

        If the list of values of the Variable is empty, no requirement
        is applied on the length of the list of Uncertainty values.
        """
        if not isinstance(uncertainty, Uncertainty):
            raise TypeError("Expected 'Uncertainty', instead got '{0}'.".format(type(uncertainty)))

        lenvar = len(self.values)
        lenunc = len(uncertainty.values)
        if lenvar and (lenvar is not lenunc):
            raise ValueError("Length of uncertainty list ({0})" \
            "is not the same as length of Variable" \
            "values list ({1})!.".format(lenunc, lenvar))
        self.uncertainties.append(uncertainty)

    def make_dict(self):
        """
        Return all data in this Variable as a dictionary.

        The dictionary structure follows the hepdata conventions,
        so that dumping this dictionary to YAML will give a file
        that hepdata can read.

        Uncertainties associated to this Variable are also written into
        the dictionary.

        This function is intended to be called internally by the Submission object.
        Except for debugging purposes, no user should have to call this function.
        """
        tmp = {}
        tmp["header"] = {"name": self.name, "units": self.units}

        if self.qualifiers:
            tmp["qualifiers"] = self.qualifiers

        tmp["values"] = []

        for i in range(len(self._values)):
            valuedict = defaultdict(list)

            if self.is_binned:
                valuedict["low"] = relative_round(self._values[i][0],
                                                  self.digits)
                valuedict["high"] = relative_round(self._values[i][1],
                                                   self.digits)
            else:
                valuedict["value"] = relative_round(self._values[i],
                                                    self.digits)

            for unc in self.uncertainties:
                if unc.is_symmetric:
                    valuedict['errors'].append({
                        "symerror":
                        relative_round(unc.values[i], self.digits),
                        "label":
                        unc.label
                    })
                else:
                    valuedict['errors'].append({
                        "asymerror": {
                            "minus":
                            relative_round(unc.values[i][0], self.digits),
                            "plus":
                            relative_round(unc.values[i][1], self.digits)
                        },
                        "label": unc.label
                    })
            tmp["values"].append(valuedict)
        return tmp


class Table(object):
    """
    A table is a collection of variables.

    It also holds meta-data such as a general description,
    the location within the paper, etc.
    """

    def __init__(self, name):
        self.name = name
        self.variables = []
        self.description = "Example description"
        self.location = "Example location"
        self.keywords = {}
        self.additional_resources = []
        self.image_files = set([])

    def add_image(self, file_path, outdir=None):
        """
        Add an image file to the table.

        This function only stores the path to the image.
        Any additional processing will be done later
        (see write_images function).

        :param file_path: Path to the image file.
        :type file_path: string

        :param outdir: Deprecated.
        """
        if outdir:
            msg = """
                  The 'outdir' argument to 'add_image' is deprecated.
                  It is ignored for now, but will be removed in the future.
                  """
            warnings.warn(msg, DeprecationWarning)

        if os.path.exists(file_path):
            self.image_files.add(file_path)
        else:
            raise RuntimeError("Cannot find image file: {0}".format(file_path))


    def write_output(self, outdir):
        """
        Write the table files into the output directory.

        :param outdir: Path to output directory.
                       Will be created if it doesn't exist.
        :type outdir: string
        """
        self.write_images(outdir)
        self.write_yaml(outdir)

    def write_images(self, outdir):
        """
        Write image files and thumbnails into the output directory.

        :param outdir: Path to output directory.
                       Will be created if it doesn't exist.
        :type outdir: string
        """
        for image_file in self.image_files:
            if not os.path.isfile(image_file):
                raise RuntimeError("File %s does not exist!" % image_file)
            if not os.path.exists(outdir):
                os.makedirs(outdir)
            out_image_file = "{}.png".format(
                os.path.splitext(image_file)[0].rsplit("/", 1)[1])
            thumb_out_image_file = "thumb_" + out_image_file
            # first convert to png, then create thumbnail
            command = "convert -flatten -fuzz 1% -trim +repage {} {}/{}".format(
                image_file, outdir, out_image_file)
            command_ok = execute_command(command)
            if not command_ok:
                print("ImageMagick does not seem to be installed \
                       or is not in the path - not adding any images.")
                break
            command = "convert -thumbnail 240x179 {}/{} {}/{}".format(
                outdir, out_image_file, outdir, thumb_out_image_file)
            execute_command(command)
            image = {}
            image["description"] = "Image file"
            image["location"] = out_image_file
            thumbnail = {}
            thumbnail["description"] = "Thumbnail image file"
            thumbnail["location"] = thumb_out_image_file
            self.additional_resources.append(image)
            self.additional_resources.append(thumbnail)

    def add_variable(self, variable):
        """
        Add a variable to the table

        :param variable: Variable to add.
        :type variable: Variable.
        """
        if isinstance(variable, Variable):
            self.variables.append(variable)
        else:
            raise TypeError("Unknown object type: {0}".format(str(type(variable))))

    def write_yaml(self, outdir="."):
        """
        Write the table (and all its variables) to a YAML file.

        This function is intended to be called internally by the Submission object.
        Except for debugging purposes, no user should have to call this function.
        """
        # Put all variables together into a table and write
        table = {}
        table["independent_variables"] = []
        table["dependent_variables"] = []
        for var in self.variables:
            table["independent_variables" if var.is_independent else
                  "dependent_variables"].append(var.make_dict())

        if not os.path.exists(outdir):
            os.makedirs(outdir)

        shortname = self.name.lower().replace(" ", "_")
        outfile_path = os.path.join(
            outdir, '{NAME}.yaml'.format(NAME=shortname))
        with open(outfile_path, 'w') as outfile:
            yaml.dump(table, outfile, default_flow_style=False)

        # Add entry to central submission file
        submission_path = os.path.join(outdir, 'submission.yaml')
        with open(submission_path, 'a+') as submissionfile:

            submission = {}
            submission["name"] = self.name
            submission["description"] = self.description
            submission["location"] = self.location
            submission["data_file"] = '{NAME}.yaml'.format(NAME=shortname)
            submission["keywords"] = []
            if self.additional_resources:
                submission["additional_resources"] = self.additional_resources

            for name, values in list(self.keywords.items()):
                submission["keywords"].append({"name": name, "values": values})

            yaml.dump(
                submission,
                submissionfile,
                default_flow_style=False,
                explicit_start=True)
        return os.path.basename(outfile_path)

class Submission(object):
    """
    Top-level object of a HEPData submission.

    Holds all the lower-level objects and controls writing.
    """

    def __init__(self):
        self.tables = []
        self.comment = ""
        self.additional_resources = []
        self.record_ids = []
        self.files_to_copy = []

    @staticmethod
    def get_license():
        """Return the default license."""
        data_license = {}
        data_license["name"] = "cc-by-4.0"
        data_license["url"] = "https://creativecommons.org/licenses/by/4.0/"
        data_license[
            "description"] = "The content can be shared and adapted but you must\
             give appropriate credit and cannot restrict access to others."
        return data_license

    def add_table(self, table):
        """Append table to tables list.

        :param table: The table to be added.
        :type table: Table.
        """
        if isinstance(table, Table):
            self.tables.append(table)
        else:
            raise TypeError("Unknown object type: {0}".format(str(type(table))))

    def add_link(self, description, location):
        """
        Append link to additional_resources list.

        :param description: Description of what the link refers to.
        :type description: string.

        :param location: URL to link to.
        :type location: string
        """
        # should check for working URL
        link = {}
        link["description"] = description
        link["location"] = location
        self.additional_resources.append(link)

    def add_additional_resource(self, description, location, copy_file=False):
        """
        Add any kind of additional resource.
        If copy_file is set to False, the location and description will be added as-is.
        This is useful e.g. for the case of providing a URL to a web-based resource.

        If copy_file is set to True, we will try to copy the file from the location you have given
        into the output directory. This only works if the location is a local file.
        If the location you gave does not exist or points to a file larger than 100 MB,
        a RuntimeError will be raised.
        While the file checks are performed immediately (i.e. the file must exist when this
        function is called), the actual copying only happens once create_files function of the
        submission object is called.

        :param description: Description of what the resource is.
        :type description: string.

        :param location: Can be either a URL pointing to a web-based resource or a local file path.
        :type: string

        :param copy_file: If set to true, will attempt to copy a local file to the tar ball.
        :type copy_file: bool
        """

        resource = {}
        resource["description"] = description
        if copy_file:
            check_file_existence(location)
            check_file_size(location, upper_limit=100)
            resource["location"] = os.path.basename(location)
        else:
            resource["location"] = location

        self.additional_resources.append(resource)
        self.files_to_copy.append(location)

    def add_record_id(self, r_id, r_type):
        """Append record_id to record_ids list."""
        # should add some type checks
        record_id = {}
        record_id["id"] = int(r_id)
        record_id["type"] = r_type
        self.record_ids.append(record_id)

    def read_abstract(self, filepath):
        """
        Read in the abstracts file.

        :param filepath: Path to text file containing abstract.
        :type filepath: string.
        """
        with open(filepath) as afile:
            raw = str(afile.read())
        raw = raw.replace("\r\n", "")
        raw = raw.replace("\n", "")

        self.comment = raw

    def copy_files(self, outdir):
        """
        Copy the files in the files_to_copy list to the output directory.

        :param outdir: Output directory path to copy to.
        :type outdir: string
        """
        for ifile in self.files_to_copy:
            check_file_existence(ifile)
            check_file_size(ifile, upper_limit=100)
            shutil.copy2(ifile, outdir)

    def create_files(self, outdir="."):
        """
        Create the output files.

        Implicitly triggers file creation for all tables that have been added to the submission,
        all variables associated to the tables and all uncertainties associated to the variables.
        """
        if not os.path.exists(outdir):
            os.makedirs(outdir)

        # Write general info about submission
        submission = {}
        submission["data_license"] = self.get_license()
        submission["comment"] = self.comment

        if self.additional_resources:
            submission["additional_resources"] = self.additional_resources
        if self.record_ids:
            submission["record_ids"] = self.record_ids

        with open(os.path.join(outdir, 'submission.yaml'), 'w') as outfile:
            yaml.dump(
                submission,
                outfile,
                default_flow_style=False,
                explicit_start=True)

        # Write all the tables
        for table in self.tables:
            table.write_output(outdir)

        # Copy additional resource files
        self.copy_files(outdir)

        # Put everything into a tarfile
        import tarfile
        tar = tarfile.open("submission.tar.gz", "w:gz")
        for yaml_file in find_all_matching(outdir, "*.yaml"):
            tar.add(yaml_file)
        for png_file in find_all_matching(outdir, "*.png"):
            tar.add(png_file)
        for additional in self.files_to_copy:
            tar.add(os.path.join(outdir, os.path.basename(additional)))

        tar.close()


class Uncertainty(object):
    """
    Store information about an uncertainty on a variable

    Uncertainties can be symmetric or asymmetric.
    The main information is stored as one (two) lists in the symmetric (asymmetric) case.
    The list entries are the uncertainty for each of the list entries in the corresponding Variable.
    """

    def __init__(self, label, is_symmetric=True):
        self.label = label
        self.is_symmetric = is_symmetric
        # needed to make pylint happy, see https://github.com/PyCQA/pylint/issues/409
        self._values = None
        self.values = []

    @property
    def values(self):
        """
        Value getter.

        :returns: list -- values, either as a direct list of values if uncertainty is symmetric,
            or list of tuples if it is asymmetric.
        """
        return self._values

    @values.setter
    def values(self, values):
        """
        Value setter.

        :param values: New values to set.
        :type values: list

        """
        if self.is_symmetric:
            try:
                assert all([x >= 0 for x in values])
            except AssertionError:
                raise ValueError(
                    "Uncertainty::set_values: Wrong signs detected!\
                     For symmetric uncertainty, all uncertainty values should be >=0."
                )
            self._values = values
        else:
            try:
                assert all([x[1] >= 0 for x in values])
                assert all([x[0] <= 0 for x in values])
            except AssertionError:
                raise ValueError(
                    "Uncertainty::set_values: Wrong signs detected!\
                    For asymmetric uncertainty, first element of uncertainty tuple\
                    should be <=0, second >=0."
                )
            self._values = [(float(x[0]), float(x[1])) for x in values]


    def set_values_from_intervals(self, intervals, nominal):
        """
        Set values relative to set of nominal valuesself.
        Useful if you do not have the actual uncertainty available,
        but the upper and lower boundaries of an interval.

        :param intervals: Lower and upper interval boundaries
        :type intervals: List of tuples of two floats

        :param nominal: Interval centers
        :type nominal: List of floats
        """
        subtracted_values = [(x[0] - ref, x[1] - ref) for x, ref in zip(intervals, nominal)]
        self.values = subtracted_values

    def scale_values(self, factor):
        """
        Multiply each value by constant factor.

        :param factor: Value to multiply by.
        :type factor: float
        """
        if self.is_symmetric:
            self.values = [factor * x for x in self.values]
        else:
            self.values = [(factor * x[0], factor * x[1])
                           for x in self.values]


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
            if os.path.exists(tfile) and tfile.endswith(".root"):
                self._tfile = r.TFile(tfile)
            else:
                raise IOError("RootReader: File does not exist: " + tfile)
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
        else:
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

    def read_hist_2d(self, path_to_hist):
        """Read in a TH2.

        :param path_to_hist: Absolute path in the current TFile.
        :type path_to_hist: str

        :returns: dict -- For a description of the contents,
            check the documentation of the get_hist_2d_points function
        """
        hist = self.retrieve_object(path_to_hist)
        return get_hist_2d_points(hist)

    def read_hist_1d(self, path_to_hist):
        """Read in a TH1.

        :param path_to_hist: Absolute path in the current TFile.
        :type path_to_hist: str

        :returns: dict -- For a description of the contents,
            check the documentation of the get_hist_1d_points function
        """
        hist = self.retrieve_object(path_to_hist)
        return get_hist_1d_points(hist)

    def read_tree(self, path_to_tree, branch_name):
        """Extract a list of values from a tree branch.

        :param path_to_tree: Absolute path in the current TFile.
        :type path_to_tree: str

        :param branch_name: Name of branch to read.
        :type branch_name: str

        :returns: list -- The values saved in the tree branch.

        """
        tree = self.tfile.Get(path_to_tree)

        values = []
        for event in tree:
            values.append(getattr(event, branch_name))
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


def get_hist_2d_points(hist):
    """
    Get points from a TH2.

    :param hist: Histogram to extract points from
    :type hist: TH2D

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
    points = {}
    for key in ["x", "y", "x_edges", "y_edges", "z", "dz"]:
        points[key] = []

    symmetric = (hist.GetBinErrorOption() == r.TH1.kNormal)
    for x_bin in range(1, hist.GetNbinsX() + 1):
        x_val = hist.GetXaxis().GetBinCenter(x_bin)
        width_x = hist.GetXaxis().GetBinWidth(x_bin)
        for y_bin in range(1, hist.GetNbinsY() + 1):
            y_val = hist.GetYaxis().GetBinCenter(y_bin)
            z_val = hist.GetBinContent(x_bin, y_bin)

            if symmetric:
                dz_val = hist.GetBinError(x_bin, y_bin)
            else:
                dz_val = (- hist.GetBinErrorLow(x_bin, y_bin),
                          hist.GetBinErrorUp(x_bin, y_bin))

            width_y = hist.GetXaxis().GetBinWidth(y_bin)

            points["x"].append(x_val)
            points["x_edges"].append((x_val - width_x / 2, x_val + width_x / 2))

            points["y"].append(y_val)
            points["y_edges"].append((y_val - width_y / 2, y_val + width_y / 2))

            points["z"].append(z_val)
            points["dz"].append(dz_val)

    return points



def get_hist_1d_points(hist):
    """
    Get points from a TH1.

    :param hist: Histogram to extract points from
    :type hist: TH1D

    :returns: dict -- Lists of x/y values saved in dictionary.
        Corresponding keys are "x" for the value of the bin center.
        The bin edges may be found under "x_edges" as a list of tuples (lower_edge, upper_edge).
        The bin contents are stored under the "y" key.
        Bin content errors are stored under the "dy" key as either a list of floats (symmetric case)
        or a list of down/up tuples (asymmetric).
        Symmetric errors are returned if the histogram error option
        TH1::GetBinErrorOption() returns TH1::kNormal.
    """
    points = {}
    for key in ["x", "y", "x_edges", "dy"]:
        points[key] = []

    symmetric = (hist.GetBinErrorOption() == r.TH1.kNormal)
    for x_bin in range(1, hist.GetNbinsX() + 1):
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
