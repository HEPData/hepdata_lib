#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""Test RootFileReader."""
import random
from unittest import TestCase
import test_utilities
from hepdata_lib import RootFileReader
import numpy as np
import ROOT
import os

class TestRootFileReader(TestCase):
    """Test the RootFileReader class."""

    def test_read_graph_tgraph(self):
        """
        Test the behavior of the read_graph function
        when reading a TGraph from file.
        """
        N = 20
        filepath = "testfile.root"
        name = "testgraph"

        x = np.random.uniform(-1e3,1e3,N)
        y = np.random.uniform(-1e3,1e3,N)

        # Create a graph and write to file
        g = ROOT.TGraph()
        for i, (ix,iy) in enumerate(zip(x,y)):
            g.SetPoint(i,ix,iy)

        f = ROOT.TFile(filepath,"RECREATE")
        f.cd()
        g.Write(name)
        f.Close()

        # Read graph back from file
        reader = RootFileReader(filepath)
        data = reader.read_graph(name)

        self.assertTrue(set(data.keys()) == set(["x","y"]))
        self.assertTrue(all(data["x"] == x))
        self.assertTrue(all(data["y"] == y))

        # Clean up
        os.remove(filepath)

    def test_read_graph_tgrapherros(self):
        """
        Test the behavior of the read_graph function
        when reading a TGraphErrors from file.
        """
        N = 20
        filepath = "testfile.root"
        name = "testgraph"

        x = np.random.uniform(-1e3,1e3,N)
        dx = np.random.uniform(-1e3,1e3,N)
        y = np.random.uniform(-1e3,1e3,N)
        dy = np.random.uniform(-1e3,1e3,N)

        # Create a graph and write to file
        g = ROOT.TGraphErrors()
        for i, (ix,iy,idx,idy) in enumerate(zip(x,y,dx,dy)):
            g.SetPoint(i,ix,iy)
            g.SetPointError(i,idx,idy)
        f = ROOT.TFile(filepath,"RECREATE")
        f.cd()
        g.Write(name)
        f.Close()

        # Read graph back from file
        reader = RootFileReader(filepath)
        data = reader.read_graph(name)

        self.assertTrue(set(data.keys()) == set(["x","y","dx","dy"]))
        self.assertTrue(all(data["x"] == x))
        self.assertTrue(all(data["y"] == y))
        self.assertTrue(all(data["dx"] == dx))
        self.assertTrue(all(data["dy"] == dy))

        # Clean up
        os.remove(filepath)

    def test_read_graph_tgrapherros(self):
        """
        Test the behavior of the read_graph function
        when reading a TGraphAsymmErrors from file.
        """
        N = 20
        filepath = "testfile.root"
        name = "testgraph"

        x = np.random.uniform(-1e3,1e3,N)
        dx1 = np.random.uniform(0,1e3,N)
        dx2 = np.random.uniform(0,1e3,N)
        y = np.random.uniform(-1e3,1e3,N)
        dy1 = np.random.uniform(0,1e3,N)
        dy2 = np.random.uniform(0,1e3,N)

        # Create a graph and write to file
        g = ROOT.TGraphAsymmErrors()
        for i, (ix,iy,idx1,idx2,idy1,idy2) in enumerate(zip(x,y,dx1,dx2,dy1,dy2)):
            g.SetPoint(i,ix,iy)
            g.SetPointError(i,idx1,idx2,idy1,idy2)
        f = ROOT.TFile(filepath,"RECREATE")
        f.cd()
        g.Write(name)
        f.Close()

        # Read graph back from file
        reader = RootFileReader(filepath)
        data = reader.read_graph(name)

        self.assertTrue(set(data.keys()) == set(["x","y","dx","dy"]))
        self.assertTrue(all(data["x"] == x))
        self.assertTrue(all(data["y"] == y))

        # Downward error has a minus sign -> flip
        self.assertTrue(data["dx"] == zip([-tmp for tmp in dx1],dx2))
        self.assertTrue(data["dy"] == zip([-tmp for tmp in dy1],dy2))

        # Clean up
        os.remove(filepath)


