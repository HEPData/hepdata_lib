#!/usr/bin/env python
"""Test CFileReader."""
from unittest import TestCase
import os
import numpy as np
import pytest
from hepdata_lib.c_file_reader import CFileReader

@pytest.mark.needs_root
class TestCFileReader(TestCase):
    """Test the CFileReader class."""

    def test_cfile_setter(self):
        """
        Test the behavior of the CFileReader setters.
        """

        # Check with nonexistent file that ends in .C
        with self.assertRaises(RuntimeError):
            _reader = CFileReader("/path/to/nowhere/butEndsIn.C")
        # Check with lowercase .c
        with self.assertRaises(RuntimeError):
            _reader = CFileReader("/path/to/nowhere/butEndsIn.c")

        # Check with existent file that does not end in .C
        _file = "text.txt"
        with open(_file, "w", encoding="utf-8") as testfile:
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

        # Finally, try with good calls
        _cfile = "test.C"
        with open(_cfile, "w", encoding="utf-8") as testfile:
            testfile.write("TGraph* c = new TGraph(60, x_values, y_values)")

        self.addCleanup(os.remove, _cfile)

        # Use file name for opening
        try:
            _reader = CFileReader(_cfile)
        # pylint: disable=W0702
        except:
            self.fail("CFileReader raised an unexpected exception.")
        # pylint: enable=W0702

        # Use opened file (io.TextIOBase)
        try:
            with open(_cfile, encoding="utf-8") as testfile:
                _reader = CFileReader(testfile)
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
        with open(test_file, "w", encoding="utf-8") as testfile:
            testfile.write(
                'void test() {\n'
                'Double_t Graph0_fx1[2] = {1,2};\n' +
                'Double_t Graph0_fy1[2] = { \n3,\n2};' +
                'TGraph *graph = new TGraph(2,Graph0_fx1,Graph0_fy1);\n' +
                'graph->SetName("Graph0");\n' +
                'Double_t Graph0_fx2[5] ={ 1.2, 2.2 };\n' +
                'Double_t Graph0_fy2[5] = { \n0.123345, \n0.343564};\n' +
                'graph = new TGraph( 5, Graph0_fx2,Graph0_fy2);\n' +
                'graph->SetName("Graph1");\n' +
                'Double_t Graph2_fx1001[30] = {1.2,\n1.3};\n' +
                'Double_t Graph2_fy1001[30] = {0.03306888,\n0.0234779};\n' +
                'Double_t Graph2_fex1001[30] = {0,\n0};' +
                'Double_t Graph2_fey1001[30] = {  0 ,0  };' +
                'TGraphErrors gre = TGraphErrors(30,Graph2_fx1001,Graph2_fy1001,' +
                'Graph2_fex1001,Graph2_fey1001);\n' +
                'gre.SetName("Graph2");}'
            )
        graph0_x = [1, 2]
        graph0_y = [3, 2]
        graph1_x = [1.2, 2.2]
        graph1_y = [0.123345, 0.343564]
        graph0_x = [1, 2]
        graph0_y = [3, 2]
        graph2_x = [1.2, 1.3]
        graph2_y = [0.03306888, 0.0234779]
        graph2_dx = [0, 0]
        graph2_dy = [0, 0]
        reader = CFileReader(test_file)
        tgraphs = reader.get_graphs()

        self.assertTrue(tgraphs["Graph0"]["x"] == graph0_x)
        self.assertTrue(tgraphs["Graph0"]["y"] == graph0_y)
        self.assertTrue(tgraphs["Graph1"]["x"] == graph1_x)
        self.assertTrue(tgraphs["Graph1"]["y"] == graph1_y)
        self.assertTrue(tgraphs["Graph2"]["x"] == graph2_x)
        self.assertTrue(tgraphs["Graph2"]["y"] == graph2_y)
        self.assertTrue(tgraphs["Graph2"]["dx"] == graph2_dx)
        self.assertTrue(tgraphs["Graph2"]["dy"] == graph2_dy)

        # Testing with invalid x and y values
        with open(test_file, "w", encoding="utf-8") as testfile:
            testfile.write(
                'void test() {\n' +
                'Double_t Graph0_fx1[2] = {test,test};\n' +
                'Double_t Graph0_fy1[2] = { \ntest,\ntest};\n' +
                'TGraph *graph = new TGraph(2,Graph0_fx1,Graph0_fy1);\n' +
                'graph->SetName("Graph0");}'
            )
        reader = CFileReader(test_file)
        with self.assertRaises(ValueError):
            reader.get_graphs()

        # Testing graphs with half float falf int values
        with open(test_file, "w", encoding="utf-8") as testfile:
            testfile.write(
                'void test() {\n' +
                'Double_t Graph0_fx1[2] = {1,2};\n' +
                'Double_t Graph0_fy1[2] = { \n3.23423,\n2.23423};' +
                'TGraph *graph = new TGraph(2,Graph0_fx1,Graph0_fy1);\n' +
                'graph->SetName("Graph0");\n' +
                'Double_t Graph2_fx1001[30] = {1,\n2};\n' +
                'Double_t Graph2_fy1001[30] = {3.2,\n2.1};\n' +
                'Double_t Graph2_fex1001[30] = {0,\n0};\n' +
                'Double_t Graph2_fey1001[30] = {  0 ,0  };\n' +
                'TGraphErrors gre = TGraphErrors(30,Graph2_fx1001,Graph2_fy1001,' +
                'Graph2_fex1001,Graph2_fey1001);\n' +
                'gre.SetName("Graph2");}')

        reader = CFileReader(test_file)
        tgraphs = reader.get_graphs()
        self.assertTrue(tgraphs["Graph0"]["x"] == [1.0, 2.0])
        self.assertTrue(tgraphs["Graph0"]["y"] == [3.23423, 2.23423])
        self.assertTrue(tgraphs["Graph2"]["x"] == [1.0, 2.0])
        self.assertTrue(tgraphs["Graph2"]["y"] == [3.2, 2.1])
        self.assertTrue(tgraphs["Graph2"]["dx"] == [0, 0])
        self.assertTrue(tgraphs["Graph2"]["dy"] == [0, 0])

        # Testing graphs without name
        with open(test_file, "w", encoding="utf-8") as testfile:
            testfile.write(
                'void test() {\n' +
                'Double_t Graph0_fx2[5] ={ 1.2, 2.2 };\n' +
                'Double_t Graph0_fy2[5] = { \n0.123345, \n0.343564};\n' +
                'graph = new TGraph( 5, Graph0_fx2,Graph0_fy2);\n' +
                'Double_t Graph2_fx1001[30] = {1,\n2};\n' +
                'Double_t Graph2_fy1001[30] = {3.2,\n2.1};\n' +
                'Double_t Graph2_fex1001[30] = {0,\n0};\n' +
                'Double_t Graph2_fey1001[30] = {  0 ,0  };\n' +
                'TGraphErrors gre = TGraphErrors(30,Graph2_fx1001,Graph2_fy1001,' +
                'Graph2_fex1001,Graph2_fey1001);}')

        reader = CFileReader(test_file)
        tgraphs = reader.get_graphs()
        self.assertTrue(set(tgraphs.keys()) == {"tgraph"})

        self.addCleanup(os.remove, test_file)
        self.doCleanups()

    def test_create_tgrapherrors(self):
        """Test function to create pyroot TGraph object"""

        # Create a valid pyroot TGraphErrors object
        _length = 10
        x_value = np.random.uniform(-1e3, 1e3, _length)
        y_value = np.random.uniform(-1e3, 1e3, _length)
        dx_value = np.random.uniform(0, 0, _length)
        dy_value = np.random.uniform(0, 0, _length)

        c_file = "test.C"
        with open(c_file, "w", encoding="utf-8") as testfile:
            testfile.write('test')
        reader = CFileReader(c_file)
        graph = reader.create_tgrapherrors(x_value, y_value, dx_value, dy_value)

        self.assertTrue(set(graph.keys()) == {"x", "y", "dx", "dy"})
        self.assertTrue(all(graph["x"] == x_value))
        self.assertTrue(all(graph["y"] == y_value))

        # Testing TGraphErrors with int values only
        x_value = [1, 2, 3]
        y_value = [3, 2, 1]
        dx_value = [0, 0, 0]
        dy_value = [0, 0, 0]
        reader = CFileReader(c_file)
        with self.assertRaises(TypeError):
            reader.create_tgrapherrors(x_value, y_value, dx_value, dy_value)

        self.addCleanup(os.remove, c_file)
        self.doCleanups()

    def test_create_tgraph(self):
        """Test function to create pyroot TGraph object"""

        # Create a valid pyroot TGraph object
        _length = 10
        x_value = np.random.uniform(-1e3, 1e3, _length)
        y_value = np.random.uniform(-1e3, 1e3, _length)
        c_file = "test.C"
        with open(c_file, "w", encoding="utf-8") as testfile:
            testfile.write('test')
        reader = CFileReader(c_file)
        graph = reader.create_tgraph(x_value, y_value)

        self.assertTrue(set(graph.keys()) == {"x", "y"})
        self.assertTrue(all(graph["x"] == x_value))
        self.assertTrue(all(graph["y"] == y_value))
        self.addCleanup(os.remove, c_file)
        self.doCleanups()

    def test_find_graphs(self):
        """Test function to find TGraph variable names"""

        # Test normal TGraph object
        c_file = "test.C"
        with open(c_file, "w", encoding="utf-8") as testfile:
            testfile.write('void test() {\n' +
                           'TGraph *graph = new TGraph(5,Graph0_fx1,Graph0_fy1);' +
                           '\ngraph->SetName("Graph0");}')
        reader = CFileReader(c_file)
        objects = reader.find_graphs()
        test1 = objects[0]
        test2 = objects[1]
        names = ["Graph0_fx1", "Graph0_fy1"]
        graphs = ["Graph0"]
        self.assertTrue(test1 == names)
        self.assertTrue(test2 == graphs)

        # Test with whole line in comment
        with open(c_file, "w", encoding="utf-8") as testfile:
            testfile.write('void test() {\n' +
                           '//TGraph *graph = new TGraph(5,Graph0_fx1,Graph0_fy1);' +
                           '\n//graph->SetName("Graph0");}')
        reader = CFileReader(c_file)
        objects = reader.find_graphs()
        test1 = objects[0]
        test2 = objects[1]
        self.assertFalse(test1 == names)
        self.assertFalse(test2 == graphs)

        # Test with comment block
        with open(c_file, "w", encoding="utf-8") as testfile:
            testfile.write('void test() {\n' +
                           'TGraph *graph = new TGraph(5,Graph0_fx1,Graph0_fy1);' +
                           '\n/*graph->SetName("Graph0"*/);}')
        reader = CFileReader(c_file)
        objects = reader.find_graphs()
        test1 = objects[0]
        test2 = objects[1]
        self.assertTrue(test1 == names)
        self.assertListEqual(test1, names)
        self.assertFalse(test2 == graphs)

        self.addCleanup(os.remove, c_file)
        self.doCleanups()

        # Test with whitespaces
        with open(c_file, "w", encoding="utf-8") as testfile:
            testfile.write('void test() {\n' +
                           'TGraph *graph = new TGraph(5   ,Graph0_fx1  ,Graph0_fy1);' +
                           '\ngraph->SetName("Graph0"   );}')
        reader = CFileReader(c_file)
        objects = reader.find_graphs()
        test1 = objects[0]
        test2 = objects[1]
        self.assertTrue(test1 == names)
        self.assertTrue(test2 == graphs)

        # Test with line breaks
        with open(c_file, "w", encoding="utf-8") as testfile:
            testfile.write('void test() {\n' +
                           'TGraph *graph = new TGraph(5,\n Graph0_fx1, Graph0_fy1);' +
                           '\ngraph->SetName(\n"Graph0");}')
        reader = CFileReader(c_file)
        with self.assertRaises(IndexError):
            reader.find_graphs()

    def test_read_graph(self):
        """Test function to read values"""

        # Testing with a good .C file
        graph_names = ["Graph0_fx1", "Graph0_fy1"]
        c_file = "test.C"
        with open(c_file, "w", encoding="utf-8") as testfile:
            testfile.write('void test() {\n' +
                           'Double_t Graph0_fx1[5] = { ' +
                           '\n1.2,\n1.3};\n' +
                           'Double_t Graph0_fy1[5] = { \n0.1666473,\n' +
                           '0.1284744};\n}')
        reader = CFileReader(c_file)
        x_values = reader.read_graph(graph_names[0])
        y_values = reader.read_graph(graph_names[1])
        test_xvalues = [1.2, 1.3]
        test_yvalues = [0.1666473, 0.1284744]
        self.assertListEqual(test_xvalues, x_values)
        self.assertListEqual(test_yvalues, y_values)

        # Testing with invalid values
        with open(c_file, "w", encoding="utf-8") as testfile:
            testfile.write('void test() {\n' +
                           'Double_t Graph0_fx1[5] = { ' +
                           '\ntest,\n%&/};\n' +
                           'Double_t Graph0_fy1[5] = { \n!"#,\n' +
                           '"testing"};}')
        with self.assertRaises(ValueError):
            reader.read_graph(graph_names[0])
        with self.assertRaises(ValueError):
            reader.read_graph(graph_names[1])

        # Testing lines that end in comment
        with open(c_file, "w", encoding="utf-8") as testfile:
            testfile.write('void test() {\n' +
                           'Double_t Graph0_fx1[5] = { //Comment ' +
                           '\n1.2,//Comment\n1.3};\n' +
                           'Double_t Graph0_fy1[5] = { \n0.1666473, //Comment\n' +
                           '0.1284744};}')
        x_values = reader.read_graph(graph_names[0])
        y_values = reader.read_graph(graph_names[1])
        self.assertListEqual(test_xvalues, x_values)
        self.assertListEqual(test_yvalues, y_values)

        # Testing lines that start with comment
        with open(c_file, "w", encoding="utf-8") as testfile:
            testfile.write('void test() {\n' +
                           'Double_t Graph0_fx1[5] = { ' +
                           '\n//1.2,\n1.3};\n' +
                           'Double_t Graph0_fy1[5] = { \n0.1666473,\n' +
                           '0.1284744};}')
        test_xvalues = [1.3]
        test_yvalues = [0.1666473, 0.1284744]
        x_values = reader.read_graph(graph_names[0])
        y_values = reader.read_graph(graph_names[1])
        self.assertListEqual(test_xvalues, x_values)
        self.assertListEqual(test_yvalues, y_values)

        # Testing lines with comment block
        with open(c_file, "w", encoding="utf-8") as testfile:
            testfile.write('void test() {\n' +
                           '/*Double_t Graph0_fx1[5] = { ' +
                           '\n1.2,\n1.3*/};\n' +
                           'Double_t Graph0_fy1[5] = { \n0.1666473,\n' +
                           '0.1284744};}')
        test_xvalues = []
        test_yvalues = [0.1666473, 0.1284744]
        x_values = reader.read_graph(graph_names[0])
        y_values = reader.read_graph(graph_names[1])
        self.assertListEqual(test_xvalues, x_values)
        self.assertListEqual(test_yvalues, y_values)
        self.addCleanup(os.remove, c_file)
        self.doCleanups()

    def test_check_for_comments(self):
        """Test function to read values"""

        # Test with a clean line
        test_line = "This is just a test"
        c_file = "test.C"
        with open(c_file, "w", encoding="utf-8") as testfile:
            testfile.write('test')
        reader = CFileReader(c_file)
        line_test = reader.check_for_comments(test_line)

        self.assertTrue(line_test[0] is False)
        self.assertTrue(line_test[1] == 0)
        self.assertTrue(line_test[2] == test_line)

        # Test with a comment block starting in the middle
        test_line = "This is /*just a test"
        c_file = "test.C"
        with open(c_file, "w", encoding="utf-8") as testfile:
            testfile.write('test')
        reader = CFileReader(c_file)
        line_test = reader.check_for_comments(test_line)
        self.assertTrue(line_test[0] is False)
        self.assertTrue(line_test[1] == 1)
        self.assertTrue(line_test[2] == "This is")

        # Test with a comment block that ends in mid line
        test_line = "This is */ just a test"
        c_file = "test.C"
        with open(c_file, "w", encoding="utf-8") as testfile:
            testfile.write('test')
        reader = CFileReader(c_file)
        line_test = reader.check_for_comments(test_line)

        self.assertTrue(line_test[0] is False)
        self.assertTrue(line_test[1] == 0)
        self.assertTrue(line_test[2] == " just a test")

        # Test with whole line in a comment
        test_line = "//This is just a test"
        c_file = "test.C"
        with open(c_file, "w", encoding="utf-8") as testfile:
            testfile.write('test')
        reader = CFileReader(c_file)
        line_test = reader.check_for_comments(test_line)
        self.assertTrue(line_test[0])
        self.assertTrue(line_test[1] == 0)
        self.assertTrue(line_test[2] == test_line)

        self.addCleanup(os.remove, c_file)
        self.doCleanups()
