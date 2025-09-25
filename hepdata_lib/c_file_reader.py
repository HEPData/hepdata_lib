""".C file reader"""
import io
from array import array
try:
    from ROOT import TGraph, TGraphErrors  # pylint: disable=no-name-in-module
except ImportError as e:  # pragma: no cover
    print(f'Cannot import ROOT: {str(e)}')
import hepdata_lib.root_utils as ru
from hepdata_lib.helpers import check_file_existence

class CFileReader:
    """Reads ROOT Objects from .C files"""

    def __init__(self, cfile):
        """Initializing cfile"""
        self._cfile = None
        self.cfile = cfile

    def __del__(self):
        if self._cfile:
            self._cfile.close()

    @property
    def cfile(self):
        """The .C file this reader reads from."""
        return self._cfile

    @cfile.setter
    def cfile(self, cfile):
        """
        Define the '.C' file to read from.
        """
        if isinstance(cfile, str):
            if not cfile.lower().endswith(".c"):
                raise RuntimeError(
                    "CFileReader: Input file is not a .C file (name does not end in .C)!"
                    )
            if check_file_existence(cfile):
                self._cfile = open(cfile, encoding='utf-8')  # pylint: disable=consider-using-with
        else:
            if isinstance(cfile, io.TextIOBase):
                self._cfile = cfile
            else:
                raise ValueError(
                    "CFileReader: Encountered unknown type of variable passed as cfile argument: "
                    + str(type(cfile)))
        if not self._cfile:
            raise OSError("CFileReader: File not opened properly.")

    def get_graphs(self):
        """Parse the .C file trying to find TGraph objects"""

        # Getting tgraph variables and names
        found_graphs = self.find_graphs()
        graphs = found_graphs[0]
        tgraph_names = found_graphs[1]
        tgraph_errors = found_graphs[2]
        error_names = found_graphs[3]
        list_of_tgraphs = []

        # Creating and adding TGraphs to a dictionary
        dict_of_graphs = self.create_tgraph_dict(graphs, list_of_tgraphs)
        list_of_tgraphs = zip(tgraph_names, dict_of_graphs)

        # Creating and adding TGraphsErrors to a dictionary
        dict_of_graphs = self.create_tgrapherrors_dict(tgraph_errors)
        list_of_errors = zip(error_names, dict_of_graphs)

        # Combining dictionaries
        graph_object = {}
        graph_object.update(list_of_tgraphs)
        graph_object.update(list_of_errors)
        all_graphs = graph_object

        # Returning a complete dictionary
        return all_graphs

    def create_tgraph_dict(self, graph_list, list_of_tgraphs):
        """Function to create pyroot TGraph dict"""

        # Adding tgraphs into a dictionary
        y_values = []
        x_values = []
        graphs = graph_list
        count = 0
        while count < len(graphs) -1:
            xvalues = self.read_graph(graphs[count])
            yvalues = self.read_graph(graphs[count+1])
            for value in xvalues:
                x_values.append(value)
            for value in yvalues:
                y_values.append(value)
            tgraph = self.create_tgraph(x_values, y_values)
            tgraph = dict(tgraph)
            list_of_tgraphs.append(tgraph)
            count += 2
            y_values = []
            x_values = []

        return list_of_tgraphs

    def create_tgrapherrors_dict(self, graph_list):
        """Function to create pyroot TGraphErrors dict"""

        # Adding TGraphErrors into a dictionary
        y_values = []
        x_values = []
        dy_values = []
        dx_values = []
        list_of_tgraphs = []
        count = 0
        while count < len(graph_list) -1:
            xvalues = self.read_graph(graph_list[count])
            yvalues = self.read_graph(graph_list[count+1])
            dxvalues = self.read_graph(graph_list[count+2])
            dyvalues = self.read_graph(graph_list[count+3])
            for value in xvalues:
                x_values.append(value)
            for value in yvalues:
                y_values.append(value)
            for value in dxvalues:
                dx_values.append(value)
            for value in dyvalues:
                dy_values.append(value)
            tgraph_error = self.create_tgrapherrors(x_values, y_values, dx_values, dy_values)
            tgraph_error = dict(tgraph_error)
            list_of_tgraphs.append(tgraph_error)
            count += 4
            y_values = []
            x_values = []
            dy_values = []
            dx_values = []

        return list_of_tgraphs

    def create_tgrapherrors(self, x_value, y_value, dx_value, dy_value):
        """Function to create pyroot TGraphErrors object"""

        # Creating pyroot TGraphErrors object
        x_values = array('i')
        y_values = array('i')
        dx_values = array('i')
        dy_values = array('i')
        length = len(x_value)
        if (all(isinstance(x, int) for x in x_value)
                and all(isinstance(x, int) for x in y_value)
                and all(isinstance(x, int) for x in dx_value)
                and all(isinstance(x, int) for x in dy_value)):
            y_values = array('i')
            x_values = array('i')
            dx_values = array('i')
            dy_values = array('i')
        else:
            y_values = array('d')
            x_values = array('d')
            dx_values = array('d')
            dy_values = array('d')
        for value in range(length):
            x_values.append(x_value[value])
            y_values.append(y_value[value])
            dx_values.append(dx_value[value])
            dy_values.append(dy_value[value])
        try:
            t_object = TGraphErrors(length, x_values, y_values, dx_values, dy_values)
        except TypeError as err:
            raise TypeError("Invalid value in TGraphErrors constructor!") from err
        graph = ru.get_graph_points(t_object)

        return graph

    def create_tgraph(self, x_value, y_value):
        """Function to create pyroot TGraph object"""

        # Creating pyroot TGraph object
        x_values = array('i')
        y_values = array('i')
        length = len(x_value)
        if (all(isinstance(x, int) for x in x_value)
                and all(isinstance(x, int) for x in y_value)):
            y_values = array('i')
            x_values = array('i')
        else:
            y_values = array('d')
            x_values = array('d')
        for value in range(length):
            x_values.append(x_value[value])
            y_values.append(y_value[value])
        try:
            t_object = TGraph(length, x_values, y_values)
        except TypeError as err:
            raise TypeError("Invalid value in TGraph constructor!") from err
        graph = ru.get_graph_points(t_object)

        return graph

    def check_for_comments(self, line):
        """Check line for comment"""

        _line = line
        ignoreline = 0
        continueline = False
        if _line.startswith('/*'):
            continueline = True
            ignoreline = 1
            return continueline, ignoreline, _line

        if _line.startswith('//'):
            continueline = True
            ignoreline = 0
            return continueline, ignoreline, _line

        if '/*' in _line:
            _line = _line.split('/*', 1)[0]
            _line = _line.rstrip()
            continueline = False
            ignoreline = 1
            return continueline, ignoreline, _line

        if '//' in _line:
            _line = _line.split('//', 1)[0]
            _line = _line.rstrip()
            continueline = False
            ignoreline = 0
            return continueline, ignoreline, _line

        if '*/' in _line:
            _line = _line.split('*/', 1)[1]
            _line = _line.rstrip()
            continueline = False
            ignoreline = 0
            return continueline, ignoreline, _line
        return continueline, ignoreline, _line

    def find_graphs(self):
        """Find all TGraphs in .C file"""
        # pylint: disable=too-many-branches
        # pylint: disable=too-many-statements
        # pylint: disable=too-many-locals

        c_file = self.cfile
        tgraph_names = []
        tgrapherror_names = []
        normal_objects = []
        error_objects = []
        tgraphs = []
        tgraph_errors = []
        start = 0
        ignore = 0
        counter = 0
        #Parsing .C file for variables and names
        for line in c_file.readlines():
            checkline = self.check_for_comments(line)
            ignore = checkline[1]
            if checkline[0] is True:
                continue
            line = checkline[2]
            if(("TGraphErrors(" in line) and ("(" in line) and
               (ignore == 0)):
                start = 2
                splitline = line.split('(', 1)[1].split(')')[0]
                splitlines = splitline.split(',')
                for i in splitlines:
                    j = i.replace(' ', '')
                    error_objects.append(j)
                continue
            if(("TGraph(" in line) and ("(" in line) and
               (ignore == 0)):
                start = 1
                splitline = line.split('(', 1)[1].split(')')[0]
                splitlines = splitline.split(',')
                for i in splitlines:
                    j = i.replace(' ', '')
                    normal_objects.append(j)
                continue
            if(("SetName(" in line) and ("(" in line) and (ignore == 0) and (counter < 5)):
                if start == 1:
                    try:
                        tgraph_names.append(line.split('"', 1)[1].split('"')[0])
                    except IndexError as err:
                        tgraph_names = 'null'
                        raise IndexError("index out of range") from err
                    start = 0
                    counter = 0
                if start == 2:
                    try:
                        tgrapherror_names.append(line.split('"', 1)[1].split('"')[0])
                    except IndexError as err:
                        tgrapherror_names = 'null'
                        raise IndexError("index out of range") from err
                    start = 0
                    counter = 0

            #Adding a default name, if no name is found
            if start == 1:
                counter += 1
            if start == 2:
                counter += 1
            if ((start == 1) and (counter >= 5)):
                tgraph_names.append("tgraph")
                start = 0
                counter = 0
            if ((start == 2) and (counter >= 5)):
                tgrapherror_names.append("tgraph")
                start = 0
                counter = 0

        for item in normal_objects:
            for subitem in item.split(","):
                if subitem.isdigit() is False:
                    tgraphs.append(subitem)
        for item in error_objects:
            for subitem in item.split(","):
                if subitem.isdigit() is False:
                    tgraph_errors.append(subitem)

        return tgraphs, tgraph_names, tgraph_errors, tgrapherror_names

    def read_graph(self, graphname):
        """Function to read values of a graph"""
        # pylint: disable=too-many-branches
        # pylint: disable=too-many-statements

        c_file = self.cfile
        objects = []
        values = []
        start = 0
        ignore = 0
        c_file.seek(0, 0)

        # Finding values from the correct object
        for line in c_file.readlines():
            checkline = self.check_for_comments(line)
            ignore = checkline[1]
            if checkline[0] is True:
                continue
            line = checkline[2]
            if((graphname in line) and ("{" in line) and ignore == 0
               and (not "}" in line)):
                splitline = line.split(graphname, 1)[1]
                splitline = splitline.split('{', 1)[1].split(',')[0].replace(' ', '')
                try:
                    try:
                        _test = float(splitline)
                        objects.append(splitline)
                        start = 1
                    except ValueError:
                        _test = int(splitline)
                        objects.append(splitline)
                        start = 1
                except ValueError:
                    start = 1
                    continue
                start = 1
                continue
            if((graphname in line) and ("{" in line) and ignore == 0
               and ("}" in line)):
                if start == 1:
                    splitline = line.split("}", 1)[0]
                    objects.append(splitline)
                splitline = line.split(graphname, 1)[1]
                if ("{" in splitline) and ("}" in splitline):
                    splitline = splitline.split('{', 1)[1].split('}')[0]
                    splitlines = splitline.split(',')
                    for i in splitlines:
                        j = i.replace(' ', '')
                        objects.append(j)
                else:
                    continue
            if "}" in line:
                if start == 1:
                    splitline = line.split("}", 1)[0]
                    try:
                        try:
                            _test = float(splitline)
                            objects.append(splitline)
                            start = 0
                        except ValueError:
                            _test = int(splitline)
                            objects.append(splitline)
                            start = 0
                    except ValueError:
                        start = 0
                        continue
                start = 0
            if start == 1:
                objects.append(line.split(",")[0])
        for i in objects:
            try:
                try:
                    values.append(int(i))
                except ValueError:
                    values.append(float(i))
            except ValueError as err:
                raise ValueError("Value is not a number in variable:", graphname) from err
        return values
