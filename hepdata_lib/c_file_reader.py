""".C file reader"""

import io
from array import array
from ROOT import TGraph, TGraphErrors
import hepdata_lib.root_utils as ru
from hepdata_lib.helpers import check_file_existence

class CFileReader(object):
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
                self._cfile = open(cfile, "r")
        elif isinstance(cfile, io.TextIOBase):
            self._cfile = cfile
        else:
            raise ValueError(
                "CFileReader: Encountered unknown type of variable passed as cfile argument: "
                + str(type(cfile)))

        if not self._cfile:
            raise IOError("CFileReader: File not opened properly.")

    def get_graphs(self):
        """Parse the .C file trying to find TGraph objects"""

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

        graph_object = {}
        graph_object.update(list_of_tgraphs)
        graph_object.update(list_of_errors)
        all_graphs = graph_object

        return all_graphs

    def create_tgraph_dict(self, graph_list, list_of_tgraphs):
        """Function to create pyroot TGraph dict"""
        # pylint: disable=no-self-use
        y_values = []
        x_values = []
        graphs = graph_list
        count = 0
        while count < len(graphs) -1:
            xvalues = self.read_graph(graphs[count])
            yvalues = self.read_graph(graphs[count+1])
            try:
                if (all(isinstance(x, int) for x in xvalues)
                        and all(isinstance(x, int) for x in yvalues)):
                    for value in xvalues:
                        x_values.append(value)
                    for value in yvalues:
                        y_values.append(value)
                elif(any(not isinstance(x, int) for x in xvalues)
                     or any(not isinstance(x, int) for x in yvalues)):
                    for value in xvalues:
                        x_values.append(float(value))
                    for value in yvalues:
                        y_values.append(float(value))
            except ValueError:
                raise IndexError("Invalid values. Int or float required.")
            tgraph = self.create_tgraph(x_values, y_values)
            tgraph = dict(tgraph)
            list_of_tgraphs.append(tgraph)
            count += 2
            y_values = []
            x_values = []

        return list_of_tgraphs

    def create_tgrapherrors_dict(self, graph_list):
        """Function to create pyroot TGraphErrors dict"""
        # pylint: disable=no-self-use
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
            try:
                if (all(isinstance(x, int) for x in xvalues)
                        and all(isinstance(x, int) for x in yvalues)
                        and all(isinstance(x, int) for x in dxvalues)
                        and all(isinstance(x, int) for x in dyvalues)):
                    for value in xvalues:
                        x_values.append(value)
                    for value in yvalues:
                        y_values.append(value)
                    for value in xvalues:
                        dx_values.append(value)
                    for value in yvalues:
                        dy_values.append(value)
                elif(any(not isinstance(x, int) for x in xvalues)
                     or any(not isinstance(x, int) for x in xvalues)
                     or any(not isinstance(x, int) for x in dxvalues)
                     or any(not isinstance(x, int) for x in dyvalues)):
                    for value in xvalues:
                        x_values.append(float(value))
                    for value in yvalues:
                        y_values.append(float(value))
                    for value in xvalues:
                        dx_values.append(float(value))
                    for value in yvalues:
                        dy_values.append(float(value))
            except ValueError:
                raise IndexError("Invalid values. Int or float required.")
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
        # pylint: disable=no-self-use
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
        t_object = TGraphErrors(length, x_values, y_values, dx_values, dy_values)
        graph = ru.get_graph_points(t_object)

        return graph

    def create_tgraph(self, x_value, y_value):
        """Function to create pyroot TGraph object"""
        # pylint: disable=no-self-use
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
        t_object = TGraph(length, x_values, y_values)
        graph = ru.get_graph_points(t_object)

        return graph

    def check_for_comments(self, line):
        """Check line for comment"""
        # pylint: disable=no-self-use
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
            _line = _line.split('//', 1)[0]
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
        for line in c_file.readlines():
            checkline = self.check_for_comments(line)
            ignore = checkline[1]
            if checkline[0] is True:
                continue
            line = checkline[2]
            if(("TGraphErrors(" in line) and ("(" in line) and
               (ignore == 0)):
                start = 2
                error_objects.append(line.split('(', 1)[1].split(')')[0])
                continue
            if(("TGraph(" in line) and ("(" in line) and
               (ignore == 0)):
                start = 1
                normal_objects.append(line.split('(', 1)[1].split(')')[0])
                continue
            if(("SetName(" in line) and ("(" in line) and (ignore == 0) and (counter < 5)):
                if start == 1:
                    try:
                        tgraph_names.append(line.split('"', 1)[1].split('"')[0])
                    except IndexError:
                        tgraph_names = 'null'
                        raise IndexError("index out of range")
                    start = 0
                    counter = 0
                if start == 2:
                    try:
                        tgrapherror_names.append(line.split('"', 1)[1].split('"')[0])
                    except IndexError:
                        tgrapherror_names = 'null'
                        raise IndexError("index out of range")
                    start = 0
                    counter = 0
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
            if((graphname in line) and ("{" in line) and ignore == 0):
                start = 1
                continue
            if "}" in line:
                if start == 1:
                    objects.append(line.split("}")[0])
                start = 0
            if start == 1:
                objects.append(line.split(",")[0])
        for i in objects:
            try:
                try:
                    values.append(int(i))
                except ValueError:
                    values.append(float(i))
            except ValueError:
                raise ValueError("Value is not a number in variable:", graphname)
        return values
