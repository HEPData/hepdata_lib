#!/usr/bin/env python
"""Test RootFileReader."""
from unittest import TestCase
from array import array
import os
import ctypes
import numpy as np
import pytest
try:
    import ROOT
except ImportError as e:
    print(f'Cannot import ROOT: {str(e)}')
from hepdata_lib.root_utils import (RootFileReader, get_graph_points,
                                    get_hist_1d_points, get_hist_2d_points)
from .test_utilities import float_compare, tuple_compare, histogram_compare_1d, make_tmp_root_file


@pytest.mark.needs_root
class TestRootFileReader(TestCase):
    # pylint: disable=R0904
    """Test the RootFileReader class."""

    def test_tfile_setter(self):
        """
        Test the behavior of the RootFileReader member setters.
        """

        # Check with nonexistent file that ends in .root
        with self.assertRaises(RuntimeError):
            _reader = RootFileReader("/path/to/nowhere/butEndsIn.root")

        # Check with existing file that does not end in .root
        path_to_file = "test.txt"
        self.addCleanup(os.remove, path_to_file)

        with open(path_to_file, "w", encoding="utf-8") as testfile:
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
        tfile = make_tmp_root_file(testcase=self)

        try:
            _reader = RootFileReader(path_to_file)
            _reader = RootFileReader(tfile)
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
        n = 20
        name = "testgraph"

        x = np.random.uniform(-1e3, 1e3, n)
        y = np.random.uniform(-1e3, 1e3, n)

        # Create a graph and write to file
        g = ROOT.TGraph()  # pylint: disable=no-member
        for i, (ix, iy) in enumerate(zip(x, y)):
            g.SetPoint(i, ix, iy)

        testfile = make_tmp_root_file(testcase=self)
        testfile.cd()
        g.Write(name)
        testfile.Close()

        # Read graph back from file
        reader = RootFileReader(testfile.GetName())
        data = reader.read_graph(name)

        self.assertTrue(set(data.keys()) == {"x", "y"})
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
        n = 20
        name = "testgraph"

        x = np.random.uniform(-1e3, 1e3, n)
        dx = np.random.uniform(-1e3, 1e3, n)
        y = np.random.uniform(-1e3, 1e3, n)
        dy = np.random.uniform(-1e3, 1e3, n)

        # Create a graph and write to file
        g = ROOT.TGraphErrors()  # pylint: disable=no-member
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
        n = 20
        name = "testgraph"

        x = np.random.uniform(-1e3, 1e3, n)
        dx1 = np.random.uniform(0, 1e3, n)
        dx2 = np.random.uniform(0, 1e3, n)
        y = np.random.uniform(-1e3, 1e3, n)
        dy1 = np.random.uniform(0, 1e3, n)
        dy2 = np.random.uniform(0, 1e3, n)

        # Create a graph and write to file
        g = ROOT.TGraphAsymmErrors()  # pylint: disable=no-member
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

    def test_read_tefficiency(self):
        """
        Test the behavior of the read_teff function
        when reading a TEfficiency from file.
        """
        name = "teff"

        teff = ROOT.TEfficiency(name, name, 2, 0, 2)  # pylint: disable=no-member
        teff.Fill(True, 0.5)
        teff.Fill(False, 0.5)
        teff.Fill(False, 1.5)

        testfile = make_tmp_root_file(testcase=self)
        testfile.cd()
        teff.Write(name)
        testfile.Close()

        # Read graph back from file
        reader = RootFileReader(testfile.GetName())
        data = reader.read_teff(name)

        self.assertEqual(data["x"], [0.5, 1.5])
        self.assertEqual(data["y"], [0.5, 0.0])

        # Clean up
        self.doCleanups()


    def test_read_hist_1d_symmetric_errors(self):
        """Test the read_hist_1d function for a histogram with symmetric errors."""
        name = "test"

        # Create test histogram
        n = 100
        x_values = [0.5 + x for x in range(n)]
        y_values = list(np.random.uniform(-1e3, 1e3, n))
        dy_values = list(np.random.uniform(0, 1e3, n))
        x_edges = []
        hist = ROOT.TH1D("test1d_symm", "test1d_symm", n, 0, n)  # pylint: disable=no-member
        for i in range(1, hist.GetNbinsX()+1):
            hist.SetBinContent(i, y_values[i-1])
            hist.SetBinError(i, dy_values[i-1])

            center = hist.GetBinCenter(i)
            width = hist.GetBinWidth(i)
            x_edges.append((center-0.5*width, center+0.5*width))

        testfile = make_tmp_root_file(testcase=self)
        testfile.cd()
        hist.Write(name)
        testfile.Close()

        reader = RootFileReader(testfile.GetName())
        points = reader.read_hist_1d(name)

        # Check consistency
        for key in ["x", "y", "dy", "x_edges"]:
            self.assertTrue(key in set(points))
        self.assertTrue(all(float_compare(*tup) for tup in zip(points["x"], x_values)))
        self.assertTrue(all(float_compare(*tup) for tup in zip(points["y"], y_values)))
        self.assertTrue(all(float_compare(*tup) for tup in zip(points["dy"], dy_values)))
        self.assertTrue(all(tuple_compare(*tup) for tup in zip(points["x_edges"], x_edges)))

        # Clean up
        self.doCleanups()

    def test_read_hist_1d_range(self):
        """Test the read_hist_1d function for a histogram with symmetric errors."""

        # Create test histogram
        n = 100
        xmin = 20
        xmax = 80
        x_values = [0.5 + x for x in range(xmin, xmax)]
        y_values = list(np.random.uniform(-1e3, 1e3, xmax-xmin))
        dy_values = list(np.random.uniform(0, 1e3, xmax-xmin))

        testname = "test1d_symm"
        hist = ROOT.TH1D(testname, testname, n, 0, n)  # pylint: disable=no-member
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
            self.assertTrue(key in set(points))

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
        hist = ROOT.TH1D(testname, testname, n_bin, 0, 1)  # pylint: disable=no-member
        hist.SetBinErrorOption(ROOT.TH1.kPoisson)  # pylint: disable=no-member

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
            self.assertTrue(key in set(points))

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
        hist = ROOT.TH1D(testname, testname, n_bin, 0, 1)  # pylint: disable=no-member
        hist.SetBinErrorOption(ROOT.TH1.kPoisson)  # pylint: disable=no-member

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
            self.assertTrue(key in set(points))

        self.assertTrue(all(float_compare(*tup) for tup in zip(points["x"], x_values)))
        self.assertTrue(all(float_compare(*tup) for tup in zip(points["y"], y_values)))
        self.assertTrue(all(float_compare(*tup) for tup in zip(points["dy"], dy_values)))

        # Clean up
        self.doCleanups()


    def test_read_hist_1d_bin_labels(self):
        """Test the read_hist_1d function with bin labels."""
        name = "test"

        # Create test histogram
        n = 100
        y_values = list(np.random.uniform(-1e3, 1e3, n))
        dy_values = list(np.random.uniform(0, 1e3, n))
        labels = list(map(str,dy_values))

        hist = ROOT.TH1D("test1d_labels", "test1d_labels", n, 0, n)  # pylint: disable=no-member
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

        self.assertTrue("x_labels" in points)

        self.assertTrue(all(tup[0]==tup[1] for tup in zip(points["x_labels"], labels)))

        # Clean up
        self.doCleanups()

    def test_read_hist_2d_bin_labels(self):
        """Test the read_hist_2d function with bin labels."""
        name = "test"

        # Create test histogram
        nx = 13
        ny = 37
        y_values = np.random.uniform(-1e3, 1e3, (nx,ny))
        xlabels = [f"X{i}" for i in range(nx)]
        ylabels = [f"Y{i}" for i in range(ny)]

        hist = ROOT.TH2D("test2d_labels", "test2d_labels", nx, 0, nx, ny, 0, ny)  # pylint: disable=no-member
        for i in range(nx):
            for j in range(ny):
                hist.Fill(i,j,y_values[i,j])
                hist.GetXaxis().SetBinLabel(i+1, xlabels[i])
                hist.GetYaxis().SetBinLabel(j+1, ylabels[j])

        testfile = make_tmp_root_file(testcase=self)
        testfile.cd()
        hist.Write(name)
        testfile.Close()

        reader = RootFileReader(testfile.GetName())
        points = reader.read_hist_2d(name)

        self.assertTrue("x_labels" in points)
        self.assertTrue("y_labels" in points)

        # The output ordering is
        # [(x=0,y=0), (x=0,y=1), ...]
        for i in range(nx):
            for j in range(ny):
                index = i*ny + j
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
        nx = 100
        ny = 100
        x_values = [0.5 + x for x in range(nx)]
        y_values = [0.5 + x for x in range(ny)]
        z_values = np.random.uniform(-1e3, 1e3, (nx, ny))  # pylint: disable=no-member
        dz_values = np.random.uniform(0, 1e3, (nx, ny))

        testname = "test2d_sym"
        hist = ROOT.TH2D(testname, testname, nx, 0, nx, ny, 0, ny)  # pylint: disable=no-member

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
            self.assertTrue(key in points)

        # Check length
        for v in points.values():
            self.assertTrue(len(v) == nx*ny)

        # Check unordered contents
        self.assertTrue(set(points["x"]) == set(x_values))
        self.assertTrue(set(points["y"]) == set(y_values))

        # Look up original bins and compare
        for x, y, z, dz in zip(points["x"], points["y"], points["z"], points["dz"]):
            ibin = backup_hist.Fill(x, y, 0)
            ibinx = ctypes.c_int(0)
            ibiny = ctypes.c_int(0)
            ibinz = ctypes.c_int(0)
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
        nx = 100
        ny = 100
        xmin = 20
        xmax = 80
        ymin = 30
        ymax = 90
        x_values = [0.5 + x for x in range(xmin, xmax)]
        y_values = [0.5 + x for x in range(ymin, ymax)]
        z_values = np.random.uniform(-1e3, 1e3, (xmax-xmin, ymax-ymin))
        dz_values = np.random.uniform(0, 1e3, (xmax-xmin, ymax-ymin))

        testname = "test2d_sym"
        hist = ROOT.TH2D(testname, testname, nx, 0, nx, ny, 0, ny)  # pylint: disable=no-member

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
            self.assertTrue(key in points)

        # Check length
        for v in points.values():
            self.assertTrue(len(v) == (xmax-xmin)*(ymax-ymin))

        # Check unordered contents
        self.assertTrue(set(points["x"]) == set(x_values))
        self.assertTrue(set(points["y"]) == set(y_values))

        # Look up original bins and compare
        for x, y, z, dz in zip(points["x"], points["y"], points["z"], points["dz"]):
            ibin = backup_hist.Fill(x, y, 0)
            ibinx = ctypes.c_int(0)
            ibiny = ctypes.c_int(0)
            ibinz = ctypes.c_int(0)
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
        nx = 17
        ny = 17
        n_fill = 1000

        hist = ROOT.TH2D("test2d_asym", "test2d_asym", nx, 0, 1, ny, 0, 1)  # pylint: disable=no-member
        hist.SetBinErrorOption(ROOT.TH1.kPoisson)  # pylint: disable=no-member
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
            self.assertTrue(key in points)

        # Check length
        for v in points.values():
            self.assertTrue(len(v) == nx*ny)

        # Look up original bins and compare
        for x, y, z, dz in zip(points["x"], points["y"], points["z"], points["dz"]):
            ibin = backup_hist.Fill(x, y, 0)
            ibinx = ctypes.c_int(0)
            ibiny = ctypes.c_int(0)
            ibinz = ctypes.c_int(0)
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
        nx = 17
        ny = 17
        n_fill = 1000

        hist = ROOT.TH2D("test2d_asym", "test2d_asym", nx, 0, 1, ny, 0, 1)  # pylint: disable=no-member
        hist.SetBinErrorOption(ROOT.TH1.kPoisson)  # pylint: disable=no-member
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
            self.assertTrue(key in points)

        # Check length
        for v in points.values():
            self.assertTrue(len(v) == nx*ny)

        # Look up original bins and compare
        for x, y, z, dz in zip(points["x"], points["y"], points["z"], points["dz"]):
            ibin = backup_hist.Fill(x, y, 0)
            ibinx = ctypes.c_int(0)
            ibiny = ctypes.c_int(0)
            ibinz = ctypes.c_int(0)
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
        tree = ROOT.TTree()  # pylint: disable=no-member
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
        self.assertTrue(all(float_compare(values[0], values[1])
                             for values in zip(data, data_readback)))

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
        ROOT.gROOT.SetBatch(ROOT.kTRUE)  # pylint: disable=no-member

        # Create test histogram, plot on canvas, save to file
        tfile = make_tmp_root_file(testcase=self)
        histogram = ROOT.TH1D("testhist", "testhist", 10, 0, 1)  # pylint: disable=no-member
        path_to_file = tfile.GetName()

        canvas = ROOT.TCanvas()  # pylint: disable=no-member
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
        except OSError:
            print("RootFileReader.retrieve_object raised unexpected IOError!")
            self.fail()

        self.assertTrue(readback)
        self.assertTrue(
            histogram_compare_1d(reference, readback)
            )

        # Clean up
        self.doCleanups()

    def test_retrieve_object_stack(self):
        '''Check that retrieve_object correctly reads from stack in canvas.'''
        # Disable graphical output
        ROOT.gROOT.SetBatch(ROOT.kTRUE)  # pylint: disable=no-member

        # Create test histogram, plot on canvas, save to file
        tfile = make_tmp_root_file(testcase=self)
        histogram = ROOT.TH1D("testhist", "testhist", 10, 0, 1)  # pylint: disable=no-member
        stack = ROOT.THStack("teststack","teststack")  # pylint: disable=no-member
        stack.Add(histogram)
        path_to_file = tfile.GetName()

        canvas = ROOT.TCanvas()  # pylint: disable=no-member
        stack.Draw("HIST")
        canvas.Write("canvas")

        reference = histogram.Clone("reference")
        reference.SetDirectory(0)
        if tfile:
            tfile.Close()

        # Read it back
        reader = RootFileReader(path_to_file)
        try:
            readback = reader.retrieve_object("canvas/teststack/testhist")
        except OSError:
            print("RootFileReader.retrieve_object raised unexpected IOError!")
            self.fail()

        self.assertTrue(readback)
        self.assertTrue(
            histogram_compare_1d(reference, readback)
            )

        # Clean up
        self.doCleanups()

    def test_retrieve_object_canvas_tpad(self):
        '''Check that retrieve_object correctly reads from canvas.'''
        # Disable graphical output
        ROOT.gROOT.SetBatch(ROOT.kTRUE)  # pylint: disable=no-member

        # Create test histogram, plot on canvas, save to file
        tfile = make_tmp_root_file(testcase=self)
        histogram = ROOT.TH1D("testhist", "testhist", 10, 0, 1)  # pylint: disable=no-member
        path_to_file = tfile.GetName()

        canvas = ROOT.TCanvas()  # pylint: disable=no-member
        pad1 = ROOT.TPad("pad1","pad1",0,0,1,1)  # pylint: disable=no-member
        pad1.Draw()
        pad1.cd()
        histogram.Draw("HIST")
        canvas.Write("canvas")

        path_to_object = f"canvas/{pad1.GetName()}/{histogram.GetName()}"

        reference = histogram.Clone("reference")
        reference.SetDirectory(0)
        tfile.Write()

        if tfile:
            tfile.Close()

        # Read it back
        reader = RootFileReader(path_to_file)
        try:
            readback = reader.retrieve_object(path_to_object)
        except OSError:
            print("RootFileReader.retrieve_object raised unexpected IOError!")
            self.fail()

        self.assertTrue(readback)
        self.assertTrue(
            histogram_compare_1d(reference, readback)
            )

        # Clean up
        self.doCleanups()

    def test_get_graph_points(self):
        '''Check that get_graph_points with input not a TGraph (or similar) gives an exception.'''
        with self.assertRaises(TypeError):
            get_graph_points(100)

    def test_get_hist_1d_and_2d_points(self):
        '''Check that get_hist_2d_points with wrong kwargs gives an exception.'''
        testname = "test2d_sym"
        xmin = 20
        xmax = 80
        # pass non-existing axis limit/parameter
        with self.assertRaises(TypeError):
            get_hist_1d_points(testname, zlim=(xmin, xmax))
        with self.assertRaises(TypeError):
            get_hist_2d_points(testname, zlim=(xmin, xmax))
