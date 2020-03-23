"""hepdata_lib main."""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import fnmatch
import math
import os
import shutil
import subprocess
import warnings
from collections import defaultdict

import yaml

# try to use LibYAML bindings if possible
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper
from yaml.representer import SafeRepresenter

from hepdata_lib import helpers
from hepdata_lib.root_utils import RootFileReader

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
        tmp["header"] = {"name": self.name}
        if self.units:
            tmp["header"]["units"] = self.units
            

        if self.qualifiers:
            tmp["qualifiers"] = self.qualifiers

        tmp["values"] = []

        for i in range(len(self._values)):
            valuedict = defaultdict(list)

            if self.is_binned:
                valuedict["low"] = helpers.relative_round(self._values[i][0],
                                                          self.digits)
                valuedict["high"] = helpers.relative_round(self._values[i][1],
                                                           self.digits)
            else:
                valuedict["value"] = helpers.relative_round(self._values[i],
                                                            self.digits)

            for unc in self.uncertainties:
                if unc.is_symmetric:
                    valuedict['errors'].append({
                        "symerror":
                            helpers.relative_round(unc.values[i], self.digits),
                        "label":
                            unc.label
                    })
                else:
                    valuedict['errors'].append({
                        "asymerror": {
                            "minus":
                                helpers.relative_round(unc.values[i][0], self.digits),
                            "plus":
                                helpers.relative_round(unc.values[i][1], self.digits)
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
            command_ok = helpers.execute_command(command)
            if not command_ok:
                print("ImageMagick does not seem to be installed \
                       or is not in the path - not adding any images.")
                break
            command = "convert -thumbnail 240x179 {outdir}/{image} {outdir}/{thumb}".format(
                outdir=outdir, image=out_image_file, thumb=thumb_out_image_file)
            helpers.execute_command(command)
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
            helpers.check_file_existence(location)
            helpers.check_file_size(location, upper_limit=100)
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
            helpers.check_file_existence(ifile)
            helpers.check_file_size(ifile, upper_limit=100)
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
        for yaml_file in helpers.find_all_matching(outdir, "*.yaml"):
            tar.add(yaml_file)
        for png_file in helpers.find_all_matching(outdir, "*.png"):
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
