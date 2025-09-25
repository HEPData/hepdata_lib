"""hepdata_lib main."""

import os
import shutil
import tarfile
import warnings
from collections import defaultdict
from decimal import Decimal
from re import match as rematch
import numpy as np
import yaml

# try to use LibYAML bindings if possible
try:
    from yaml import CLoader as Loader, CSafeDumper as Dumper
except ImportError:
    from yaml import Loader, SafeDumper as Dumper
from yaml.representer import SafeRepresenter

from hepdata_validator.full_submission_validator import FullSubmissionValidator
from hepdata_lib import helpers
from hepdata_lib.root_utils import RootFileReader

MAPPING_TAG = yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG


def dict_representer(dumper, data):
    """represent dict."""
    return dumper.represent_dict(data.items())


def dict_constructor(loader, node):
    """construct dict."""
    return defaultdict(loader.construct_pairs(node))

yaml.add_representer(defaultdict, SafeRepresenter.represent_dict)
Dumper.add_representer(defaultdict, dict_representer)
Loader.add_constructor(MAPPING_TAG, dict_constructor)

Dumper.add_representer(str,
                       SafeRepresenter.represent_str)
yaml.add_representer(np.str_,
                       SafeRepresenter.represent_str)

# Display deprecation warnings
warnings.filterwarnings("always", category=DeprecationWarning, module="hepdata_lib")

__version__ = "0.20.0"

class AdditionalResourceMixin:
    """Functionality related to additional materials."""

    def __init__(self):
        self.files_to_copy = []
        self.additional_resources = []

    def add_additional_resource(self, description, location, *, copy_file=False, file_type=None,
                                resource_license=None):
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
        :type description: string

        :param location: Can be either a URL pointing to a web-based resource or a local file path.
        :type location: string

        :param copy_file: If set to true, will attempt to copy a local file to the tar ball.
        :type copy_file: bool

        :param file_type: Type of the resource file (None, "HistFactory" or "ProSelecta").
        :type file_type: string

        :param resource_license: License information comprising name, url and optional description.
        :type resource_license: dict
        """

        #pylint: disable=too-many-arguments

        resource = {}
        resource["description"] = description
        if copy_file:
            helpers.check_file_existence(location)
            helpers.check_file_size(location, upper_limit=100)
            resource["location"] = os.path.basename(location)
            self.files_to_copy.append(location)
        else:
            resource["location"] = location

        if file_type:
            resource["type"] = file_type

        # Confirm that license does not contain extra keys,
        # and has the mandatory name and description values
        if resource_license:

            if not isinstance(resource_license, dict):
                raise ValueError("resource_license must be a dictionary.")

            # Get the license dict keys as a set
            license_keys = set(resource_license.keys())

            # Create sets for both possibilities
            mandatory_keys = {"name", "url"}
            all_keys = mandatory_keys.union(["description"])

            # If license matches either of the correct values
            if license_keys in (mandatory_keys, all_keys):
                resource["license"] = resource_license
            else:
                raise ValueError("Incorrect resource_license format: "
                                 "resource_license must be a dictionary containing a "
                                 "name, url and optional description.")

        self.additional_resources.append(resource)

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

class Variable:
    """A Variable is a wrapper for a list of values + some meta data."""

    # pylint: disable=too-many-instance-attributes
    # Eight is reasonable in this case.

    def __init__(self, name, *, is_independent=True, is_binned=True, units="", values=None,
                 zero_uncertainties_warning=True):
        # pylint: disable=too-many-arguments
        self.name = name
        self.is_independent = is_independent
        self.is_binned = is_binned
        self.qualifiers = []
        self.units = units
        self.zero_uncertainties_warning = zero_uncertainties_warning
        # needed to make pylint happy, see https://github.com/PyCQA/pylint/issues/409
        self._values = None
        self.values = values if values else []
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
            # Check that the input is well-formed
            try:
                assert all(len(x) == 2 for x in value_list)
            except (AssertionError, TypeError, ValueError) as err:
                msg = "For binned Variables, values should be tuples of length two: \
                                 (lower bin edge, upper bin edge)."
                raise ValueError(msg) from err

            # All good
            self._values = [
                            (
                             helpers.sanitize_value(x[0]),
                             helpers.sanitize_value(x[1])
                            ) for x in value_list
                            ]
        else:
            # Check that the input is well-formed
            try:
                parsed_values = [helpers.sanitize_value(x) for x in value_list]
            except (TypeError, ValueError) as err:
                raise ValueError("Malformed input for unbinned variable: ", value_list) from err
            self._values = parsed_values

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
        if self.is_independent:
            raise RuntimeError("Qualifiers are not allowed for independent variables.")
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
            raise TypeError(f"Expected 'Uncertainty', instead got '{type(uncertainty)}'.")

        lenvar = len(self.values)
        lenunc = len(uncertainty.values)
        if lenvar and (lenvar != lenunc):
            raise ValueError(f"Length of uncertainty list ({lenunc})" \
                             "is not the same as length of Variable" \
                             f"values list ({lenvar})!.")
        self.uncertainties.append(uncertainty)

    def make_dict(self):
        # pylint: disable=too-many-branches
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

        nonzero_uncs = helpers.any_uncertainties_nonzero(
                                                        self.uncertainties,
                                                        size=len(self._values)
                                                        )
        for i, value in enumerate(self._values):
            valuedict = defaultdict(list)

            if self.is_binned:
                valuedict["low"] = helpers.relative_round(value[0],
                                                          self.digits)
                valuedict["high"] = helpers.relative_round(value[1],
                                                           self.digits)
            else:
                valuedict["value"] = helpers.relative_round(value,
                                                            self.digits)
            # An uncertainty entry is only appended
            # if at least one of the uncertainties is not zero.
            if nonzero_uncs[i]:
                for unc in self.uncertainties:
                    if unc.values[i] is None:
                        continue
                    if unc.is_symmetric:
                        valuedict['errors'].append({
                            "symerror":
                                helpers.relative_round(unc.values[i], self.digits),
                            "label":
                                unc.label
                        })
                    else:
                        sum_unc = Decimal(float(unc.values[i][0]) + float(unc.values[i][1]))
                        if sum_unc.is_zero():
                            valuedict['errors'].append({
                                "symerror":
                                    helpers.relative_round(unc.values[i][1], self.digits),
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
            elif self.uncertainties and self.zero_uncertainties_warning:
                print(
                    "Warning: omitting 'errors' since all uncertainties " \
                    f"are zero for bin {i+1} of variable '{self.name}'."
                    )
                print(
                    "Note that bins with zero content should preferably " \
                    "be omitted completely from the HEPData table."
                    )
            tmp["values"].append(valuedict)
        return tmp


class Table(AdditionalResourceMixin):
    """
    A table is a collection of variables.

    It also holds meta-data such as a general description,
    the location within the paper, etc.
    """

    # pylint: disable=too-many-instance-attributes

    def __init__(self, name):
        super().__init__()
        self._name = None
        self.name = name
        self.variables = []
        self.related_tables = []
        self.description = "Example description"
        self.location = "Example location"
        self.keywords = {}
        self.image_files = set()
        self.data_license = {}

    @property
    def name(self):
        """Name getter."""
        return self._name

    @name.setter
    def name(self, name):
        """Name setter."""
        if len(name) > 64:
            raise ValueError("Table name must not be longer than 64 characters: " + name)
        self._name = name

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

        if not isinstance(file_path, str):
            raise TypeError(f"Expected string argument, instead got: '{type(file_path)}'.")
        file_path = os.path.expanduser(file_path)
        if os.path.exists(file_path):
            self.image_files.add(file_path)
        else:
            raise RuntimeError(f"Cannot find image file: {file_path}")

    def add_related_doi(self, doi):
        """
        Appends a DOI string to the related_tables list.

        :param doi: The table DOI.
        :type doi: string
        """
        # Checking against the regex, this also happens in the validator.
        pattern = r"^10\.17182\/hepdata\.\d+\.v\d+\/t\d+$"
        match = rematch(pattern, doi)
        if match:
            to_string = str(doi)
            self.related_tables.append(to_string)
        else:
            raise ValueError(f"DOI does not match the correct pattern: {pattern}.")

    def add_data_license(self, name, url, description=None):
        """
        Verify and store the given license data.

        :param name: The license name
        :type name: string
        :param url: The license URL
        :type url: string
        :param description: The (optional) license description
        :type description: string
        """
        license_data = {}

        if name:
            license_data["name"] = name
        else:
            raise ValueError("You must insert a value for the license's name.")

        if url:
            license_data["url"] = url
        else:
            raise ValueError("You must insert a value for the license's url.")

        if description:
            license_data["description"] = description

        self.data_license = license_data

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
        if not isinstance(outdir, str):
            raise TypeError(f"Expected string argument, instead got: '{type(outdir)}'.")

        for image_file in self.image_files:
            if not os.path.isfile(image_file):
                raise RuntimeError(f"File {image_file} does not exist!")
            if not os.path.exists(outdir):
                os.makedirs(outdir)

            # PNG file is named same as input file except for extension
            # Thumbnail is named with a '_thumb' prefix
            png_output_base = os.path.splitext(os.path.basename(image_file))[0] + ".png"
            thumbnail_output_base = "thumb_" + png_output_base

            # Absolute paths for further use
            png_output_path = os.path.join(outdir, png_output_base)
            thumbnail_output_path = os.path.join(outdir, thumbnail_output_base)


            # Convert to full-size PNG image
            # Only executed if output is missing or out of date
            if helpers.file_is_outdated(png_output_path, image_file):
                helpers.convert_pdf_to_png(image_file, png_output_path)
            else:
                print(f"Full-size PNG file {png_output_path} is newer than its source file. \
                       Remove the thumbnail file or use create_files(remove_old=True)\
                           to force recreation.")

            if helpers.file_is_outdated(thumbnail_output_path, png_output_path):
                helpers.convert_png_to_thumbnail(png_output_path, thumbnail_output_path)
            else:
                print("Thumbnail PNG file {thumbnail_output_path} is newer than its source file. \
                       Remove the thumbnail file or use create_files(remove_old=True)\
                           to force recreation.")

            image = {}
            image["description"] = "Image file"
            image["location"] = os.path.basename(png_output_path)
            thumbnail = {}
            thumbnail["description"] = "Thumbnail image file"
            thumbnail["location"] = os.path.basename(thumbnail_output_path)
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
            raise TypeError(f"Unknown object type: {str(type(variable))}")

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
            outdir, f'{shortname}.yaml')
        with open(outfile_path, 'w', encoding='utf-8') as outfile:
            yaml.dump(table, outfile, default_flow_style=False)

        # Add entry to central submission file
        submission_path = os.path.join(outdir, 'submission.yaml')
        with open(submission_path, 'a+', encoding='utf-8') as submissionfile:
            submission = {}
            submission["name"] = self.name
            submission["description"] = self.description
            submission["location"] = self.location
            if self.related_tables:
                submission["related_to_table_dois"] = self.related_tables
            submission["data_file"] = f'{shortname}.yaml'
            submission["keywords"] = []
            if self.additional_resources:
                submission["additional_resources"] = self.additional_resources
            if self.data_license:
                submission["data_license"] = self.data_license

            for name, values in list(self.keywords.items()):
                submission["keywords"].append({"name": name, "values": values})

            yaml.dump(
                submission,
                submissionfile,
                default_flow_style=False,
                explicit_start=True)
        return os.path.basename(outfile_path)


class Submission(AdditionalResourceMixin):
    """
    Top-level object of a HEPData submission.

    Holds all the lower-level objects and controls writing.
    """

    def __init__(self):
        super().__init__()
        self.tables = []
        self.comment = ""
        self.record_ids = []
        self.related_records = []
        self.add_additional_resource(
            "Created with hepdata_lib " + __version__,
            "https://doi.org/10.5281/zenodo.1217998")

    @staticmethod
    def get_license():
        """Return the default license."""
        data_license = {}
        data_license["name"] = "CC0"
        data_license["url"] = "https://creativecommons.org/publicdomain/zero/1.0/"
        data_license["description"] = (
            "CC0 enables reusers to distribute, remix, adapt, and build upon the material "
            "in any medium or format, with no conditions.")
        return data_license

    def add_table(self, table):
        """Append table to tables list.

        :param table: The table to be added.
        :type table: Table.
        """
        if isinstance(table, Table):
            self.tables.append(table)
        else:
            raise TypeError(f"Unknown object type: {str(type(table))}")

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

    def add_record_id(self, r_id, r_type):
        """Append record_id to record_ids list."""
        # should add some type checks
        record_id = {}
        record_id["id"] = int(r_id)
        record_id["type"] = r_type
        self.record_ids.append(record_id)

    def add_related_recid(self, r_id):
        """
        Appends a record ID to the related_records list.
        :param r_id: The record's ID
        :type r_id: integer
        """

        try:
            recid = int(r_id)
        except Exception as exc:
            raise TypeError(f"Expected 'Integer', instead got '{type(r_id)}'.") from exc
        if recid > 0:
            self.related_records.append(recid)
        else:
            raise ValueError("Please enter a valid integer above 0.")

    def read_abstract(self, filepath):
        """
        Read in the abstracts file.

        :param filepath: Path to text file containing abstract.
        :type filepath: string.
        """
        with open(filepath, encoding='utf-8') as afile:
            raw = str(afile.read())
        raw = raw.replace("\r\n", "")
        raw = raw.replace("\n", "")

        self.comment = raw

    def files_to_copy_nested(self):
        """
        List files-to-copy for this Submission and nested daughters
        """
        files = self.files_to_copy
        for table in self.tables:
            files = files + table.files_to_copy
        return files

    def create_files(self, outdir=".", validate=True, remove_old=False):
        """
        Create the output files.

        Implicitly triggers file creation for all tables that have been added to the submission,
        all variables associated to the tables and all uncertainties associated to the variables.

        If `validate` is True, the hepdata-validator package will be used to validate the
        output tar ball.

        If `remove_old` is True, the output directory will be deleted before recreation.
        """
        if remove_old and os.path.exists(outdir):
            shutil.rmtree(outdir)

        if not os.path.exists(outdir):
            os.makedirs(outdir)

        # Write general info about submission
        submission = {}
        submission["data_license"] = self.get_license()
        submission["comment"] = self.comment
        if self.related_records:
            submission["related_to_hepdata_records"] = self.related_records

        if self.additional_resources:
            submission["additional_resources"] = self.additional_resources
        if self.record_ids:
            submission["record_ids"] = self.record_ids

        with open(os.path.join(outdir, 'submission.yaml'), 'w', encoding='utf-8') as outfile:
            yaml.dump(
                submission,
                outfile,
                default_flow_style=False,
                explicit_start=True)

        # Write all the tables
        for table in self.tables:
            table.write_output(outdir)
            table.copy_files(outdir)

        # Copy additional resource files
        self.copy_files(outdir)

        # Put everything into a tarfile
        files_to_add = []
        files_to_add.extend(helpers.find_all_matching(outdir, "*.yaml"))
        files_to_add.extend(helpers.find_all_matching(outdir, "*.png"))
        files_to_add.extend(
            [os.path.join(outdir, os.path.basename(x)) for x in  self.files_to_copy_nested()]
        )
        tarfile_path = "submission.tar.gz"
        with tarfile.open(tarfile_path, "w:gz") as tar:
            for filepath in files_to_add:
                tar.add(
                        filepath,
                        arcname=os.path.basename(filepath)
                        )

        if validate:
            full_submission_validator = FullSubmissionValidator()
            is_archive_valid = full_submission_validator.validate(archive=tarfile_path)
            if not is_archive_valid:
                for filename in full_submission_validator.get_messages():
                    full_submission_validator.print_errors(filename)
            assert is_archive_valid, "The tar ball is not valid"

class Uncertainty:
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
            self._values = list(map(helpers.sanitize_value,values))
        else:
            self._values = [tuple(map(helpers.sanitize_value, x)) for x in values]

    def set_values_from_intervals(self, intervals, nominal):
        """
        Set values relative to set of nominal values.
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
