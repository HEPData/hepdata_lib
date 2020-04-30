""".C file reader"""

import io
from array import array
from ROOT import TGraph
import hepdata_lib.root_utils as ru
from hepdata_lib.helpers import check_file_existence

class CFileReader(object):
    """Reads TGraphs from '.C' files"""

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
            if not cfile.endswith(".C"):
                raise RuntimeError(
                    "CFileReader: Input file is not a .C file (name does not end in .C)!"
                    )
            if check_file_existence(cfile):
                self._cfile = open(cfile, "r")
        elif isinstance(cfile, io.TextIOBase):
            self._cfile = cfile
        else:
            raise ValueError(
                "CFileReader: Encountered unkonown type of variable passed as cfile argument: "
                + str(type(cfile)))

        if not self._cfile:
            raise IOError("CFileReader: File not opened properly.")

    def get_graphs(self):
        """Function to read the .C file"""

        found_graphs = self.find_graphs()
        graphs = found_graphs[0]
        graph_names = found_graphs[1]
        y_values = ['d']
        x_values = ['d']
        list_of_tgraphs = []
        count = 0

        # Creating and adding TGraphs to a dictionary
        while count < len(graphs) -1:
            x_values = self.read_graph(graphs[count])
            y_values = self.read_graph(graphs[count+1])
            tgraph = self.create_tgraph(x_values, y_values)
            tgraph = dict(tgraph)
            list_of_tgraphs.append(tgraph)
            count += 2

        graph_object = zip(graph_names, list_of_tgraphs)
        all_graphs = dict(graph_object)

        return all_graphs

    def create_tgraph(self, x_value, y_value):
        """Function to create pyroot TGraph object"""
        # pylint: disable=no-self-use
        x_values = array('d')
        y_values = array('d')
        length = len(x_value)

        for value in range(length):
            x_values.append(x_value[value])
            y_values.append(y_value[value])
        t_object = TGraph(length, x_values, y_values)
        graph = ru.get_graph_points(t_object)

        return graph

    def find_graphs(self):
        """Find all TGraphs in .C file"""

        c_file = self.cfile
        names = []
        objects = []
        graphs = []
        start = 0
        ignore = 0

        for line in c_file.readlines():
            if line.startswith('/*') or '/*' in line:
                ignore = 1
                continue
            if '*/' in line:
                ignore = 0
                continue
            if line.startswith('//'):
                continue
            if(("TGraph(" in line) and ("(" in line) and
               (ignore == 0) and (line.startswith('//') is False)):
                start = 1
                objects.append(line.split('(', 1)[1].split(')')[0])
                continue
            if(("SetName(" in line) and ("(" in line) and
               (ignore == 0) and (line.startswith('//') is False)):
                if start == 1:
                    try:
                        names.append(line.split('"', 1)[1].split('"')[0])
                    except IndexError:
                        names = 'null'
                        raise IndexError("index out of range")
                start = 0

        for item in objects:
            for subitem in item.split(","):
                if subitem.isdigit() is False:
                    graphs.append(subitem)

        return graphs, names

    def read_graph(self, graphname):
        """Function to read values of a graph"""

        c_file = self.cfile
        values = []
        start = 0
        ignore = 0
        c_file.seek(0, 0)

        # Finding values from the correct object
        for line in c_file.readlines():
            if line.startswith('/*') or '/*' in line:
                ignore = 1
                continue
            if '*/' in line:
                ignore = 0
                continue
            if line.startswith('//'):
                continue
            if((graphname in line) and ("{" in line) and
               (ignore == 0) and (line.startswith('//') is False)):
                start = 1
                continue
            if "}" in line and line.startswith('//') is False:
                if start == 1:
                    values.append(float(line.split("}")[0]))
                start = 0
            if start == 1 and line.startswith('//') is False:
                values.append(float(line.split(",")[0]))

        return values
