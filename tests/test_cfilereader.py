#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""Test CFileReader."""
from __future__ import print_function
from unittest import TestCase
from array import array
import os
import numpy as np
from ROOT import TGraph
import hepdata_lib.root_utils as ru
from hepdata_lib.c_file_reader import CFileReader

class TestCFileReader(TestCase):
    """Test the CFileReader class."""

    def test_cfile_setter(self):
        """
        Test the behavior of the CFileReader setters.
        """

        # Check with nonexistant file that ends in .C
        with self.assertRaises(RuntimeError):
            _reader = CFileReader("/path/to/nowhere/butEndsIn.C")

        # Check with existant file that does not end in .C
        _file = "text.txt"
        with open(_file, "w") as testfile:
            testfile.write("TEST CONTENT")

        self.addCleanup(os.remove, _file)
        with self.assertRaises(RuntimeError):
            _reader = CFileReader(_file)

        # Check with wrong input type
        with self.assertRaises(ValueError):
            _reader = CFileReader(5)
        with self.assertRaises(ValueError):
            _reader = CFileReader([])
        with self.assertRaises(ValueError):
            _reader = CFileReader({})

        # Finally, try a good call
        _cfile = "test.C"
        with open(_cfile, "w") as testfile:
            testfile.write("TGraph* c = new TGraph(60, Graph1, Graph2)")

        self.addCleanup(os.remove, _cfile)

        try:
            _reader = CFileReader(_cfile)
        # pylint: disable=W0702
        except:
            self.fail("CFileReader raised an unexpected exception.")
        # pylint: enable=W0702
        # Clean up
        self.doCleanups()

    def test_get_graphs(self):
        """Test function for getting TGraphs from .C file"""

        # Test create a valid dictionary of TGraphs
        test_file = "test.C"
        with open(test_file, "w") as testfile:
            testfile.write('Double_t Graph0_fx1[5] = {' +
                           '\n1.2,\n1.3};' +
                           '\nDouble_t Graph0_fy1[5] = { ' +
                           '\n0.1666473,\n0.1284744};\nTGraph *graph =' +
                           'new TGraph(5,Graph0_fx1,Graph0_fy1);\n' +
                           'graph->SetName' +
                           '("Graph0");\nDouble_t Graph0_fx2[5] =' +
                           '{ \n1.2,\n1.3};' +
                           '\nDouble_t Graph0_fy2[5] = { \n0.1666473,' +
                           '\n0.1284744};' +
                           '\nTGraph *graph = new TGraph(5,' +
                           'Graph0_fx2,Graph0_fy2);' +
                           '\ngraph->SetName("Graph1");')

        graph0_x = [1.2, 1.3]
        graph0_y = [0.1666473, 0.1284744]
        graph1_x = [1.2, 1.3]
        graph1_y = [0.1666473, 0.1284744]
        reader = CFileReader(test_file)
        tgraphs = reader.get_graphs()

        self.assertTrue(tgraphs["Graph0"]["x"] == graph0_x)
        self.assertTrue(tgraphs["Graph0"]["y"] == graph0_y)
        self.assertTrue(tgraphs["Graph1"]["x"] == graph1_x)
        self.assertTrue(tgraphs["Graph1"]["y"] == graph1_y)

        self.addCleanup(os.remove, test_file)
        self.doCleanups()

    def test_create_tgraph(self):
        """Test function to create pyroot TGraph object"""

        # Create a valid pyroot TGraph object
        x_values = array('d')
        y_values = array('d')
        _length = 2
        x_value = np.random.uniform(-1e3, 1e3, _length)
        y_value = np.random.uniform(-1e3, 1e3, _length)

        for value in range(_length):
            x_values.append(x_value[value])
            y_values.append(y_value[value])
        t_object = TGraph(_length, x_values, y_values)
        graph = ru.get_graph_points(t_object)

        self.assertTrue(set(graph.keys()) == set(["x", "y"]))
        self.assertTrue(all(graph["x"] == x_value))
        self.assertTrue(all(graph["y"] == y_value))

        self.doCleanups()

    def test_find_graphs(self):
        """Test function to find TGraph variable names"""

        # Test normal TGraph object
        c_file = "test.C"
        with open(c_file, "w") as testfile:
            testfile.write('TGraph *graph = new TGraph(5,Graph0_fx1,Graph0_fy1);' +
                           '\ngraph->SetName("Graph0");')
        reader = CFileReader(c_file)
        objects = reader.find_graphs()
        names = ["Graph0_fx1", "Graph0_fy1"]
        graphs = ['Graph0']

        self.assertListEqual(objects[0], names)
        self.assertListEqual(objects[1], graphs)

        # Test with whitespaces
        with open(c_file, "w") as testfile:
            testfile.write('TGraph *graph = new TGraph(5   ,Graph0_fx1  ,Graph0_fy1);' +
                           '\ngraph->SetName("Graph0"    );')
        objects = reader.find_graphs()
        self.assertFalse(objects[0] == names)
        self.assertFalse(objects[1] == graphs)

        # Test with line breaks
        with open(c_file, "w") as testfile:
            testfile.write('TGraph *graph = new TGraph(5,\nGraph0_fx1,Graph0_fy1);' +
                           '\ngraph->SetName("Graph0");')
        objects = reader.find_graphs()
        self.assertFalse(objects[0] == names)
        self.assertFalse(objects[1] == graphs)

        # Test comment at the end of line
        with open(c_file, "w") as testfile:
            testfile.write('TGraph *graph = new TGraph(5,\nGraph0_fx1,Graph0_fy1);' +
                           '\ngraph->SetName("Graph0"); //comment')
        objects = reader.find_graphs()
        self.assertFalse(objects[0] == names)
        self.assertFalse(objects[1] == graphs)

        # Test with line in comment
        with open(c_file, "w") as testfile:
            testfile.write('//TGraph *graph = new TGraph(5,\nGraph0_fx1,Graph0_fy1);' +
                           '\ngraph->SetName("Graph0");')
        objects = reader.find_graphs()
        self.assertFalse(objects[0] == names)
        self.assertFalse(objects[1] == graphs)

        # Test with comment block
        with open(c_file, "w") as testfile:
            testfile.write('TGraph *graph = new TGraph(/*5,\nGraph0_fx1,Graph0_fy1);' +
                           '\ngraph->SetName("Graph0"*/);')
        objects = reader.find_graphs()
        self.assertFalse(objects[0] == names)
        self.assertFalse(objects[1] == graphs)

        self.addCleanup(os.remove, c_file)
        self.doCleanups()

    def test_read_graph(self):
        """Test function to read values"""

        # Testing with a good .C file
        graph_names = ["Graph0_fx1", "Graph0_fy1"]
        c_file = "test.C"
        with open(c_file, "w") as testfile:
            testfile.write('Double_t Graph0_fx1[5] = { ' +
                           '\n1.2,\n1.3};\n' +
                           'Double_t Graph0_fy1[5] = { \n0.1666473,\n' +
                           '0.1284744};')
        reader = CFileReader(c_file)
        x_values = reader.read_graph(graph_names[0])
        y_values = reader.read_graph(graph_names[1])
        test_xvalues = [1.2, 1.3]
        test_yvalues = [0.1666473, 0.1284744]
        self.assertListEqual(test_xvalues, x_values)
        self.assertListEqual(test_yvalues, y_values)

        # Testing lines that end in comment
        with open(c_file, "w") as testfile:
            testfile.write('Double_t Graph0_fx1[5] = { //Comment ' +
                           '\n1.2,//Comment\n1.3};\n' +
                           'Double_t Graph0_fy1[5] = { \n0.1666473, //Comment\n' +
                           '0.1284744};')
        x_values = reader.read_graph(graph_names[0])
        y_values = reader.read_graph(graph_names[1])
        self.assertListEqual(test_xvalues, x_values)
        self.assertListEqual(test_yvalues, y_values)

        # Testing lines that start with comment
        with open(c_file, "w") as testfile:
            testfile.write('Double_t Graph0_fx1[5] = { ' +
                           '\n//1.2,\n1.3};\n' +
                           'Double_t Graph0_fy1[5] = { \n0.1666473,\n' +
                           '0.1284744};')
        test_xvalues = [1.3]
        test_yvalues = [0.1666473, 0.1284744]
        x_values = reader.read_graph(graph_names[0])
        y_values = reader.read_graph(graph_names[1])
        self.assertListEqual(test_xvalues, x_values)
        self.assertListEqual(test_yvalues, y_values)
        self.doCleanups()

        # Testing lines with comment block
        with open(c_file, "w") as testfile:
            testfile.write('Double_t Graph0_fx1[5] = {/*  ' +
                           '\n1.2,\n1.3*/};\n' +
                           'Double_t Graph0_fy1[5] = { \n0.1666473,\n' +
                           '0.1284744};')
        test_xvalues = []
        test_yvalues = [0.1666473, 0.1284744]
        x_values = reader.read_graph(graph_names[0])
        y_values = reader.read_graph(graph_names[1])
        self.assertListEqual(test_xvalues, x_values)
        self.assertListEqual(test_yvalues, y_values)
        self.doCleanups()
