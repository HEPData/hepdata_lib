#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""Test RootFileReader."""
import random
from unittest import TestCase
from test_utilities import float_compare, tuple_compare
from hepdata_lib import RootFileReader
import numpy as np
import ROOT
import os
import array
import ctypes

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
        self.assertTrue(data["dx"] == list(zip([-tmp for tmp in dx1],dx2)))
        self.assertTrue(data["dy"] == list(zip([-tmp for tmp in dy1],dy2)))

        # Clean up
        os.remove(filepath)

    def test_read_hist_1d_symmetric_errors(self):
        """Test the read_hist_1d function."""
        fpath = "testfile.root"

        # Create test histogram
        N = 100
        x_values = [0.5 + x for x in range(N)]
        y_values = list(np.random.uniform(-1e3,1e3,N))
        dy_values = list(np.random.uniform(0,1e3,N))

        hist = ROOT.TH1D("test1d","test1d",N,0,N)
        for i in range(1,hist.GetNbinsX()+1):
            hist.SetBinContent(i,y_values[i-1])
            hist.SetBinError(i,dy_values[i-1])

        f = ROOT.TFile(fpath,"RECREATE")
        hist.SetDirectory(f)
        hist.Write("test")
        f.Close()

        reader = RootFileReader(fpath)
        points = reader.read_hist_1d("test")

        self.assertTrue(set(["x", "y", "x_edges", "dy"]) == set(points.keys()))

        self.assertTrue(all(float_compare(*tup) for tup in zip(points["x"], x_values)))
        self.assertTrue(all(float_compare(*tup) for tup in zip(points["y"], y_values)))
        self.assertTrue(all(float_compare(*tup) for tup in zip(points["dy"], dy_values)))

        # Clean up
        os.remove(fpath)

    def test_read_hist_2d(self):
        """Test the read_hist_2d function."""
        fpath = "testfile.root"

        # Create test histogram
        NX = 100
        NY = 100
        x_values = [0.5 + x for x in range(NX)]
        y_values = [0.5 + x for x in range(NY)]
        z_values = np.random.uniform(-1e3, 1e3, (NX, NY))
        dz_values = np.random.uniform(0, 1e3, (NX, NY))

        hist = ROOT.TH2D("test2d", "test2d", NX, 0 ,NX, NY, 0, NY)

        for ix in range(1,hist.GetNbinsX()+1):
            for iy in range(1,hist.GetNbinsY()+1):
                ibin = hist.GetBin(ix,iy)
                hist.SetBinContent(ibin,z_values[ix-1][iy-1])
                hist.SetBinError(ibin,dz_values[ix-1][iy-1])

        backup_hist = hist.Clone("backup")
        f = ROOT.TFile(fpath,"RECREATE")
        hist.SetDirectory(f)
        hist.Write("test")
        f.Close()

        reader = RootFileReader(fpath)
        points = reader.read_hist_2d("test")

        # Check keys
        self.assertTrue(set(["x", "y", "z", "x_edges", "y_edges", "dz"]) == set(points.keys()))

        # Check length
        for v in points.values():
            self.assertTrue(len(v)==NX*NY)

        # Check unordered contents
        self.assertTrue(set(points["x"]) == set(x_values))
        self.assertTrue(set(points["y"]) == set(y_values))

        # Look up original bins and compare
        for x, y, z, dz in zip(points["x"], points["y"], points["z"], points["dz"]):
            ibin = backup_hist.Fill(x, y, 0)
            ibinx = ctypes.c_int()
            ibiny = ctypes.c_int()
            ibinz = ctypes.c_int()
            backup_hist.GetBinXYZ(ibin, ibinx, ibiny, ibinz)
            self.assertTrue(float_compare(backup_hist.GetXaxis().GetBinCenter(ibinx.value), x))
            self.assertTrue(float_compare(backup_hist.GetYaxis().GetBinCenter(ibiny.value), y))
            self.assertTrue(float_compare(backup_hist.GetBinContent(ibin), z))
            self.assertTrue(float_compare(backup_hist.GetBinError(ibin), dz))
        # Clean up
        os.remove(fpath)
