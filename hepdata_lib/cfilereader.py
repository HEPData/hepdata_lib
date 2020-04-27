""".C file reader"""

import collections
from collections import defaultdict
import numpy as np
import hepdata_lib
import ROOT
import io
from ROOT import TGraph
from array import array
from hepdata_lib.helpers import check_file_existence
import hepdata_lib.root_utils as ru

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

        found_graphs = self.find_Graphs()
        graphs = found_graphs[0]
        graph_names = found_graphs[1]
        y_values = [ 'd' ]
        x_values = [ 'd' ]
        list_of_tgraphs = []
        count = 0

        while count < len(graphs) -1:
            name = graphs[count]
            x_values = self.read_Graph(graphs[count])  
            y_values = self.read_Graph(graphs[count+1])
            tgraph = self.create_TGraph(x_values, y_values)
            tgraph = dict(tgraph)
            list_of_tgraphs.append(tgraph)
            count += 2

        graph_object = zip(graph_names, list_of_tgraphs)
        all_Graphs = dict(graph_object)

        return all_Graphs

    def create_TGraph(self, x, y):
        """Function to create pyroot TGraph object"""

        x_values = array( 'd' )
        y_values = array( 'd' )
        length = len(x)

        for value in range( length ):
            x_values.append(x[value])
            y_values.append(y[value])
        t_object = TGraph( length, x_values, y_values )
        graph = ru.get_graph_points(t_object)

        return graph

    def find_Graphs(self):
        """Find all TGraphs in .C file"""

        c_file = self.cfile
        names = []
        objects = []
        graphs = []
        start = 0
        
        for line in c_file.readlines():
            if '//' in line: continue
            if ("TGraph(" in line) and ("(" in line):
                start=1
                objects.append(line.split('(', 1)[1].split(')')[0])
                continue
            if("SetName(" in line) and ("(" in line):
                if start == 1:
                    names.append(line.split('(', 1)[1].split(')')[0])
                start = 0
        for item in objects:
            for subitem in item.split(","):
                if(subitem.isdigit() == False):
                    graphs.append(subitem)

        return graphs, names

    def read_Graph(self, graphname):
        """Function to read values of a graph"""

        c_file = self.cfile
        values=[]
        start=0
        c_file.seek(0, 0)

        for line in c_file.readlines():
            if '//' in line: continue
            if (graphname in line) and ("{" in line):
                start=1
                continue
            if "}" in line:
                if start==1: values.append(float(line.split("}")[0]) )
                start=0
            if start==1:
                values.append(float(line.split(",")[0]) )

        return values

  #  def getErrors(self,down,up,nominal):
  #      i=0
  #      errup =[]
  #      errdown=[]
  #      for n in nominal:
  #          errdown.append(down[i]-n)
  #          errup.append(up[i]-n)
  #          print(str(n) + " +- "+ str(errup[-1])+" "+str(errdown[-1]))
  #          i+=1

  #      return errdown,errup

  #  def makeDict(self,x,y):
  #      d ={}
  #      ati=0
  #      for i in x:
  #          d[i]=[]
  #      for i in range(0,len(x)):
  #          d[x[i]].append(y[i])
  #      return d

  #  def makeLists(self,dic):
  #      up=[]
  #      down=[]
  #      keys = sorted(dic.keys())
  #      for k in keys:
  #          for i in range(0,len(dic[k])):
  #              if i ==0:
  #                  up.append(dic[k][0])
  #              if i ==1:
  #                  down.append(dic[k][1])
  #      return up,down,keys
