#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""Test RootFileReader."""
from __future__ import print_function
from unittest import TestCase
from array import array
import os
import ctypes
import numpy as np
import ROOT
from test_utilities import float_compare, tuple_compare, histogram_compare_1d, make_tmp_root_file
from hepdata_lib.root_utils import RootFileReader


class TestRootFileReader(TestCase):
    """Test the RootFileReader class."""

    def test_tfile_setter(self):
        """
        Test the behavior of the RootFileReader member setters.
        """

        # Check with nonexistant file that ends in .root
        with self.assertRaises(RuntimeError):
            _reader = RootFileReader("/path/to/nowhere/butEndsIn.root")

        # Check with existant file that does not end in .root
        path_to_file = "test.txt"
        self.addCleanup(os.remove, path_to_file)

        with open(path_to_file, "w") as testfile:
            testfile.write("TEST CONTENT")

        with self.assertRaises(RuntimeError):
            _reader = RootFileReader(path_to_file)

        # Check with wrong input type
        with self.assertRaises(ValueError):
            _reader = RootFileReader(5)
        with self.assertRaises(ValueError):
            _reader = RootFileReader([])
        with self.assertRaises(ValueError):
            _reader = RootFileReader({})

        # Finally, try a good call
        path_to_file = make_tmp_root_file(close=True, testcase=self)

        try:
            _reader = RootFileReader(path_to_file)
        # pylint: disable=W0702
        except:
            self.fail("RootFileReader raised an unexpected exception.")
        # pylint: enable=W0702
        # Clean up
        self.doCleanups()

    def test_read_graph_tgraph(self):
        """
        Test the behavior of the read_graph function
        when reading a TGraph from file.
        """
        N = 20
        name = "testgraph"

        x = np.random.uniform(-1e3, 1e3, N)
        y = np.random.uniform(-1e3, 1e3, N)

        # Create a graph and write to file
        g = ROOT.TGraph()
        for i, (ix, iy) in enumerate(zip(x, y)):
            g.SetPoint(i, ix, iy)

        testfile = make_tmp_root_file(testcase=self)
        testfile.cd()
        g.Write(name)
        testfile.Close()

        # Read graph back from file
        reader = RootFileReader(testfile.GetName())
        data = reader.read_graph(name)

        self.assertTrue(set(data.keys()) == set(["x", "y"]))
        self.assertTrue(all(data["x"] == x))
        self.assertTrue(all(data["y"] == y))

        # Clean up
        self.doCleanups()

    def test_read_graph_tgrapherrors(self):
        """
        Test the behavior of the read_graph function
        when reading a TGraphErrors from file.
        """
        # pylint: disable-msg=too-many-locals
        N = 20
        name = "testgraph"

        x = np.random.uniform(-1e3, 1e3, N)
        dx = np.random.uniform(-1e3, 1e3, N)
        y = np.random.uniform(-1e3, 1e3, N)
        dy = np.random.uniform(-1e3, 1e3, N)

        # Create a graph and write to file
        g = ROOT.TGraphErrors()
        for i, (ix, iy, idx, idy) in enumerate(zip(x, y, dx, dy)):
            g.SetPoint(i, ix, iy)
            g.SetPointError(i, idx, idy)
        testfile = make_tmp_root_file(testcase=self)
        testfile.cd()
        g.Write(name)
        testfile.Close()

        # Read graph back from file
        reader = RootFileReader(testfile.GetName())
        data = reader.read_graph(name)

        # Check consistency
        for key in ["x", "y", "dx", "dy"]:
            self.assertTrue(key in set(data.keys()))
        self.assertTrue(all(data["x"] == x))
        self.assertTrue(all(data["y"] == y))
        self.assertTrue(all(data["dx"] == dx))
        self.assertTrue(all(data["dy"] == dy))

        # Clean up
        self.doCleanups()

    def test_read_graph_tgrapherrors2(self):
        """
        Test the behavior of the read_graph function
        when reading a TGraphAsymmErrors from file.
        """
        # pylint: disable-msg=too-many-locals
        N = 20
        name = "testgraph"

        x = np.random.uniform(-1e3, 1e3, N)
        dx1 = np.random.uniform(0, 1e3, N)
        dx2 = np.random.uniform(0, 1e3, N)
        y = np.random.uniform(-1e3, 1e3, N)
        dy1 = np.random.uniform(0, 1e3, N)
        dy2 = np.random.uniform(0, 1e3, N)

        # Create a graph and write to file
        g = ROOT.TGraphAsymmErrors()
        for i, (ix, iy, idx1, idx2, idy1, idy2) in enumerate(zip(x, y, dx1, dx2, dy1, dy2)):
            g.SetPoint(i, ix, iy)
            g.SetPointError(i, idx1, idx2, idy1, idy2)
        testfile = make_tmp_root_file(testcase=self)
        testfile.cd()
        g.Write(name)
        testfile.Close()

        # Read graph back from file
        reader = RootFileReader(testfile.GetName())
        data = reader.read_graph(name)

        # Check consistency
        for key in ["x", "y", "dx", "dy"]:
            self.assertTrue(key in set(data.keys()))

        self.assertTrue(all(data["x"] == x))
        self.assertTrue(all(data["y"] == y))

        # Downward error has a minus sign -> flip
        self.assertTrue(data["dx"] == list(zip([-tmp for tmp in dx1], dx2)))
        self.assertTrue(data["dy"] == list(zip([-tmp for tmp in dy1], dy2)))

        # Clean up
        self.doCleanups()

    def test_read_hist_1d_symmetric_errors(self):
        """Test the read_hist_1d function for a histogram with symmetric errors."""
        name = "test"

        # Create test histogram
        N = 100
        x_values = [0.5 + x for x in range(N)]
        y_values = list(np.random.uniform(-1e3, 1e3, N))
        dy_values = list(np.random.uniform(0, 1e3, N))
        x_edges = []
        hist = ROOT.TH1D("test1d_symm", "test1d_symm", N, 0, N)
        for i in range(1, hist.GetNbinsX()+1):
            hist.SetBinContent(i, y_values[i-1])
            hist.SetBinError(i, dy_values[i-1])

            c = hist.GetBinCenter(i)
            w = hist.GetBinWidth(i)
            x_edges.append((c-0.5*w, c+0.5*w))

        testfile = make_tmp_root_file(testcase=self)
        testfile.cd()
        hist.Write(name)
        testfile.Close()

        reader = RootFileReader(testfile.GetName())
        points = reader.read_hist_1d(name)

        # Check consistency
        for key in ["x", "y", "dy", "x_edges"]:
            self.assertTrue(key in set(points.keys()))
        self.assertTrue(all(float_compare(*tup) for tup in zip(points["x"], x_values)))
        self.assertTrue(all(float_compare(*tup) for tup in zip(points["y"], y_values)))
        self.assertTrue(all(float_compare(*tup) for tup in zip(points["dy"], dy_values)))
        self.assertTrue(all(tuple_compare(*tup) for tup in zip(points["x_edges"], x_edges)))

        # Clean up
        self.doCleanups()

    def test_read_hist_1d_range(self):
        """Test the read_hist_1d function for a histogram with symmetric errors."""

        # Create test histogram
        N = 100
        xmin = 20
        xmax = 80
        x_values = [0.5 + x for x in range(xmin, xmax)]
        y_values = list(np.random.uniform(-1e3, 1e3, xmax-xmin))
        dy_values = list(np.random.uniform(0, 1e3, xmax-xmin))

        testname = "test1d_symm"
        hist = ROOT.TH1D(testname, testname, N, 0, N)
        for i in range(xmin, xmax):
            hist.SetBinContent(i+1, y_values[i-xmin])
            hist.SetBinError(i+1, dy_values[i-xmin])


        testfile = make_tmp_root_file(testcase=self)
        testfile.cd()
        hist.Write(testname)
        testfile.Close()

        reader = RootFileReader(testfile.GetName())

        # pass too many axis limits
        with self.assertRaises(TypeError):
            reader.read_hist_1d(testname, xlim=(xmin, xmax), ylim=(xmin, xmax))
        # pass wrong axis limits or parameter
        with self.assertRaises(TypeError):
            reader.read_hist_1d(testname, ylim=(xmin, xmax))
        # pass xmax < xmin (wrong ordering)
        with self.assertRaises(AssertionError):
            reader.read_hist_1d(testname, xlim=(xmax, xmin))
        # pass too many parameters as single axis limit
        with self.assertRaises(AssertionError):
            reader.read_hist_1d(testname, xlim=(xmin, xmax, 5))
        # pass non-float/-int as first item
        with self.assertRaises(AssertionError):
            reader.read_hist_1d(testname, xlim=("5", xmax))
        # pass non-float/-int as second item
        with self.assertRaises(AssertionError):
            reader.read_hist_1d(testname, xlim=(xmin, "12"))
        # pass set instance (needs to be ordered tuple or list)
        with self.assertRaises(AssertionError):
            reader.read_hist_1d(testname, xlim={xmin, xmax})
        # pass wrong instance
        with self.assertRaises(AssertionError):
            reader.read_hist_1d(testname, xlim="some string")

        points = reader.read_hist_1d(testname, xlim=(xmin, xmax))

        # Check consistency
        for key in ["x", "y", "dy"]:
            self.assertTrue(key in set(points.keys()))

        self.assertTrue(all(float_compare(*tup) for tup in zip(points["x"], x_values)))
        self.assertTrue(all(float_compare(*tup) for tup in zip(points["y"], y_values)))
        self.assertTrue(all(float_compare(*tup) for tup in zip(points["dy"], dy_values)))

        # Clean up
        self.doCleanups()

    def test_read_hist_1d_asymmetric_errors(self):
        """Test the read_hist_1d function for a histogram with asymmetric errors."""
        # Create test histogram
        n_bin = 17
        n_fill = 1000
        testname = "test1d_asymm"
        hist = ROOT.TH1D(testname, testname, n_bin, 0, 1)
        hist.SetBinErrorOption(ROOT.TH1.kPoisson)

        for val in np.random.normal(loc=0.5, scale=0.15, size=n_fill):
            hist.Fill(val)

        # Extract values
        x_values = []
        y_values = []
        dy_values = []
        for i in range(1, hist.GetNbinsX()):
            x_values.append(hist.GetBinCenter(i))
            y_values.append(hist.GetBinContent(i))
            dy_values.append((-hist.GetBinErrorLow(i), hist.GetBinErrorUp(i)))

        # Write to file
        testfile = make_tmp_root_file(testcase=self)
        testfile.cd()
        hist.Write(testname)
        testfile.Close()

        # Read back
        reader = RootFileReader(testfile.GetName())
        points = reader.read_hist_1d(testname)

        # Check consistency
        for key in ["x", "y", "dy"]:
            self.assertTrue(key in set(points.keys()))

        self.assertTrue(all(float_compare(*tup) for tup in zip(points["x"], x_values)))
        self.assertTrue(all(float_compare(*tup) for tup in zip(points["y"], y_values)))
        self.assertTrue(all(tuple_compare(*tup) for tup in zip(points["dy"], dy_values)))

        # Clean up
        self.doCleanups()


    def test_read_hist_1d_asymmetric_force_symmetric_errors(self):
        """Test the read_hist_1d function for a histogram with asymmetric errors
        forcing symmetric errors to be used."""
        _fpath = "testfile.root"

        # Create test histogram
        n_bin = 17
        n_fill = 1000
        testname = "test1d_asymm"
        hist = ROOT.TH1D(testname, testname, n_bin, 0, 1)
        hist.SetBinErrorOption(ROOT.TH1.kPoisson)

        for val in np.random.normal(loc=0.5, scale=0.15, size=n_fill):
            hist.Fill(val)

        # Extract values
        x_values = []
        y_values = []
        dy_values = []
        for i in range(1, hist.GetNbinsX()):
            x_values.append(hist.GetBinCenter(i))
            y_values.append(hist.GetBinContent(i))
            dy_values.append(hist.GetBinError(i))

        # Write to file
        testfile = make_tmp_root_file(testcase=self)
        testfile.cd()
        hist.Write(testname)
        testfile.Close()

        # Read back
        reader = RootFileReader(testfile.GetName())
        points = reader.read_hist_1d(testname, force_symmetric_errors=True)

        # Check consistency
        for key in ["x", "y", "dy"]:
            self.assertTrue(key in set(points.keys()))

        self.assertTrue(all(float_compare(*tup) for tup in zip(points["x"], x_values)))
        self.assertTrue(all(float_compare(*tup) for tup in zip(points["y"], y_values)))
        self.assertTrue(all(float_compare(*tup) for tup in zip(points["dy"], dy_values)))

        # Clean up
        self.doCleanups()


    def test_read_hist_1d_bin_labels(self):
        """Test the read_hist_1d function with bin labels."""
        name = "test"

        # Create test histogram
        N = 100
        y_values = list(np.random.uniform(-1e3, 1e3, N))
        dy_values = list(np.random.uniform(0, 1e3, N))
        labels = list(map(str,dy_values))

        hist = ROOT.TH1D("test1d_labels", "test1d_labels", N, 0, N)
        for i in range(1, hist.GetNbinsX()+1):
            hist.SetBinContent(i, y_values[i-1])
            hist.SetBinError(i, dy_values[i-1])
            hist.GetXaxis().SetBinLabel(i, labels[i-1])

        testfile = make_tmp_root_file(testcase=self)
        testfile.cd()
        hist.Write(name)
        testfile.Close()

        reader = RootFileReader(testfile.GetName())
        points = reader.read_hist_1d(name)

        self.assertTrue("x_labels" in points.keys())

        self.assertTrue(all(tup[0]==tup[1] for tup in zip(points["x_labels"], labels)))

        # Clean up
        self.doCleanups()

    def test_read_hist_2d_bin_labels(self):
        """Test the read_hist_2d function with bin labels."""
        name = "test"

        # Create test histogram
        Nx = 13
        Ny = 37
        y_values = np.random.uniform(-1e3, 1e3, (Nx,Ny))
        xlabels = ["X{0}".format(i) for i in range(Nx)]
        ylabels = ["Y{0}".format(i) for i in range(Ny)]

        hist = ROOT.TH2D("test2d_labels", "test2d_labels", Nx, 0, Nx, Ny, 0, Ny)
        for i in range(Nx):
            for j in range(Ny):
                hist.Fill(i,j,y_values[i,j])
                hist.GetXaxis().SetBinLabel(i+1, xlabels[i])
                hist.GetYaxis().SetBinLabel(j+1, ylabels[j])

        testfile = make_tmp_root_file(testcase=self)
        testfile.cd()
        hist.Write(name)
        testfile.Close()

        reader = RootFileReader(testfile.GetName())
        points = reader.read_hist_2d(name)

        self.assertTrue("x_labels" in points.keys())
        self.assertTrue("y_labels" in points.keys())

        # The output ordering is
        # [(x=0,y=0), (x=0,y=1), ...]
        for i in range(Nx):
            for j in range(Ny):
                index = i*Ny + j
                self.assertTrue(
                    points["x_labels"][index]==xlabels[i]
                )
                self.assertTrue(
                    points["y_labels"][index]==ylabels[j]
                )
        # Clean up
        self.doCleanups()

    def test_read_hist_2d_symmetric_errors(self):
        """Test the read_hist_2d function with symmetric errors."""
        # pylint: disable-msg=too-many-locals
        # Create test histogram
        NX = 100
        NY = 100
        x_values = [0.5 + x for x in range(NX)]
        y_values = [0.5 + x for x in range(NY)]
        z_values = np.random.uniform(-1e3, 1e3, (NX, NY))
        dz_values = np.random.uniform(0, 1e3, (NX, NY))

        testname = "test2d_sym"
        hist = ROOT.TH2D(testname, testname, NX, 0, NX, NY, 0, NY)

        for ix in range(1, hist.GetNbinsX()+1):
            for iy in range(1, hist.GetNbinsY()+1):
                ibin = hist.GetBin(ix, iy)
                hist.SetBinContent(ibin, z_values[ix-1][iy-1])
                hist.SetBinError(ibin, dz_values[ix-1][iy-1])

        backup_hist = hist.Clone("backup")

        # Write to file
        testfile = make_tmp_root_file(testcase=self)
        testfile.cd()
        hist.Write(testname)
        testfile.Close()

        # Read back
        reader = RootFileReader(testfile.GetName())
        points = reader.read_hist_2d(testname)

        # Check keys
        for key in ["x", "y", "z", "dz"]:
            self.assertTrue(key in points.keys())

        # Check length
        for v in points.values():
            self.assertTrue(len(v) == NX*NY)

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
        self.doCleanups()



    def test_read_hist_2d_range(self):
        """Test the read_hist_2d function with symmetric errors."""
        # pylint: disable-msg=too-many-statements
        # pylint: disable-msg=too-many-locals
        # Create test histogram
        NX = 100
        NY = 100
        xmin = 20
        xmax = 80
        ymin = 30
        ymax = 90
        x_values = [0.5 + x for x in range(xmin, xmax)]
        y_values = [0.5 + x for x in range(ymin, ymax)]
        z_values = np.random.uniform(-1e3, 1e3, (xmax-xmin, ymax-ymin))
        dz_values = np.random.uniform(0, 1e3, (xmax-xmin, ymax-ymin))

        testname = "test2d_sym"
        hist = ROOT.TH2D(testname, testname, NX, 0, NX, NY, 0, NY)

        for ix in range(xmin, xmax):
            for iy in range(ymin, ymax):
                ibin = hist.GetBin(ix+1, iy+1)
                hist.SetBinContent(ibin, z_values[ix-xmin][iy-ymin])
                hist.SetBinError(ibin, dz_values[ix-xmin][iy-ymin])

        backup_hist = hist.Clone("backup")

        testfile = make_tmp_root_file(testcase=self)
        hist.SetDirectory(testfile)
        hist.Write("test2d_sym")
        testfile.Close()

        reader = RootFileReader(testfile.GetName())

        # pass too many axis limits
        with self.assertRaises(TypeError):
            reader.read_hist_2d(testname, xlim=(xmin, xmax), ylim=(ymin, ymax), zlim=(ymin, ymax))
        # pass non-existing axis limit/parameter
        with self.assertRaises(TypeError):
            reader.read_hist_2d(testname, zlim=(xmin, xmax))
        # pass wrong order (xmax < xmin)
        with self.assertRaises(AssertionError):
            reader.read_hist_2d(testname, ylim=(xmax, xmin))
        # pass too many parameters as single axis limit
        with self.assertRaises(AssertionError):
            reader.read_hist_2d(testname, ylim=(xmin, xmax, 5))
        # pass wrong type as first item
        with self.assertRaises(AssertionError):
            reader.read_hist_2d(testname, ylim=("5", xmax))
        # pass wrong type as second item
        with self.assertRaises(AssertionError):
            reader.read_hist_2d(testname, ylim=(xmin, "12"))
        # pass set instance (needs ordered datatype: tuple or list)
        with self.assertRaises(AssertionError):
            reader.read_hist_2d(testname, xlim={xmin, xmax})
        # pass wrong instance
        with self.assertRaises(AssertionError):
            reader.read_hist_2d(testname, xlim="some string")

        points = reader.read_hist_2d(testname, xlim=(xmin, xmax), ylim=(ymin, ymax))

        # Check keys
        for key in ["x", "y", "z", "dz"]:
            self.assertTrue(key in points.keys())

        # Check length
        for v in points.values():
            self.assertTrue(len(v) == (xmax-xmin)*(ymax-ymin))

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
        self.doCleanups()

    def test_read_hist_2d_asymmetric_errors(self):
        """Test the read_hist_2d function with asymmetric errors
        forcing symmetric errors to be used."""
        # pylint: disable-msg=too-many-locals
        _fpath = "testfile.root"

        # Create test histogram
        NX = 17
        NY = 17
        n_fill = 1000

        hist = ROOT.TH2D("test2d_asym", "test2d_asym", NX, 0, 1, NY, 0, 1)
        hist.SetBinErrorOption(ROOT.TH1.kPoisson)
        for val in np.random.normal(loc=0.5, scale=0.15, size=(n_fill, 2)):
            hist.Fill(*val)

        backup_hist = hist.Clone("backup")

        # Write to file
        testfile = make_tmp_root_file(testcase=self)

        hist.SetDirectory(testfile)
        hist.Write("test2d_asym")
        testfile.Close()

        # Read back
        reader = RootFileReader(testfile.GetName())
        points = reader.read_hist_2d("test2d_asym")

        # Check keys
        for key in ["x", "y", "z", "dz"]:
            self.assertTrue(key in points.keys())

        # Check length
        for v in points.values():
            self.assertTrue(len(v) == NX*NY)

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
            self.assertTrue(tuple_compare(
                (-backup_hist.GetBinErrorLow(ibinx.value, ibiny.value),
                 backup_hist.GetBinErrorUp(ibinx.value, ibiny.value)), dz))

        # Clean up
        self.doCleanups()


    def test_read_hist_2d_asymmetric_force_symmetric_errors(self):
        """Test the read_hist_2d function with asymmetric errors."""
        # pylint: disable-msg=too-many-locals
        _fpath = "testfile.root"

        # Create test histogram
        NX = 17
        NY = 17
        n_fill = 1000

        hist = ROOT.TH2D("test2d_asym", "test2d_asym", NX, 0, 1, NY, 0, 1)
        hist.SetBinErrorOption(ROOT.TH1.kPoisson)
        for val in np.random.normal(loc=0.5, scale=0.15, size=(n_fill, 2)):
            hist.Fill(*val)

        backup_hist = hist.Clone("backup")

        # Write to file
        testfile = make_tmp_root_file(testcase=self)

        hist.SetDirectory(testfile)
        hist.Write("test2d_asym")
        testfile.Close()

        # Read back
        reader = RootFileReader(testfile.GetName())
        points = reader.read_hist_2d("test2d_asym", force_symmetric_errors=True)

        # Check keys
        for key in ["x", "y", "z", "dz"]:
            self.assertTrue(key in points.keys())

        # Check length
        for v in points.values():
            self.assertTrue(len(v) == NX*NY)

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
            self.assertTrue(float_compare(
                backup_hist.GetBinError(ibinx.value, ibiny.value), dz))

        # Clean up
        self.doCleanups()


    def test_read_tree(self):
        """Test the read_tree function."""

        n_fill = 1000
        branchname = "testbranch"
        path_to_tree = "testpath"
        # Set up some test data, put into TTree and write to file
        data = np.random.normal(loc=0.5, scale=0.15, size=n_fill)

        number = array("f", [0])
        tree = ROOT.TTree()
        tree.Branch(branchname, number, "test/F")
        for inumber in data:
            number[0] = inumber
            tree.Fill()

        testfile = make_tmp_root_file(testcase=self)
        tree.Write(path_to_tree)
        if testfile:
            testfile.Close()

        # Read data back and check consistency
        reader = RootFileReader(testfile.GetName())
        try:
            data_readback = reader.read_tree(path_to_tree, branchname)
        except RuntimeError:
            self.fail("RootFileReader.read_tree raised an unexpected RuntimeError!")
        self.assertIsInstance(data_readback, list)
        self.assertTrue(all((float_compare(values[0], values[1])
                             for values in zip(data, data_readback))))

        # Try reading a nonexistant branch from an existing tree
        with self.assertRaises(RuntimeError):
            reader.read_tree(path_to_tree, "some_random_name")

        # Try reading a nonexistant tree
        with self.assertRaises(RuntimeError):
            reader.read_tree("some/random/path", "some_random_name")

        # Clean up
        self.doCleanups()

    def test_retrieve_object_failure(self):
        '''Check that retrieve_object fails the way it should.'''
        path_to_file = make_tmp_root_file(close=True, testcase=self)

        reader = RootFileReader(path_to_file)

        with self.assertRaises(IOError):
            reader.retrieve_object("Some/Nonsense/Path")

        # Clean up
        self.doCleanups()

    def test_retrieve_object_canvas(self):
        '''Check that retrieve_object correctly reads from canvas.'''
        # Disable graphical output
        ROOT.gROOT.SetBatch(ROOT.kTRUE)

        # Create test histogram, plot on canvas, save to file
        tfile = make_tmp_root_file(testcase=self)
        histogram = ROOT.TH1D("testhist", "testhist", 10, 0, 1)
        path_to_file = tfile.GetName()

        canvas = ROOT.TCanvas()
        histogram.Draw("HIST")
        canvas.Write("canvas")

        reference = histogram.Clone("reference")
        reference.SetDirectory(0)
        if tfile:
            tfile.Close()

        # Read it back
        reader = RootFileReader(path_to_file)
        try:
            readback = reader.retrieve_object("canvas/testhist")
        except IOError:
            print("RootFileReader.retrieve_object raised unexpected IOError!")
            self.fail()

        self.assertTrue(readback)
        self.assertTrue(
            histogram_compare_1d(reference, readback)
            )

        # Clean up
        self.doCleanups()
