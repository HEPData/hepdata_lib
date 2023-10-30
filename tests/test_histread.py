#!/usr/bin/env python
"""Test scikit-hep reading"""
from unittest import TestCase
import numpy as np
import hist
import hist.intervals
from hepdata_lib.hist_utils import read_hist, hist_as_variable, create_hist_base_table


class TestHistUtils(TestCase):
    """Test the hist_utils functions."""

    base_hist = hist.Hist(
        hist.axis.StrCategory(["data", "QCD", "ttbar"], name="dataset"),
        hist.axis.IntCategory([-1, 0, 4, 5], name="flavor"),
        hist.axis.Regular(60, -3, +3, name="eta"),
        hist.axis.Regular(50, 0, 500, name="pt"),
        storage=hist.storage.Weight(),
    )
    rng = np.random.default_rng(seed=123_456_789)

    base_hist.fill(  ## For mock data
        dataset="data",
        flavor=-1,
        eta=rng.normal(0, 2.0, size=123_456),
        pt=rng.exponential(100, size=123_456),
    )
    base_hist.fill(  ## For Mock QCD
        dataset="QCD",
        flavor=rng.choice([0, 4, 5], size=1_000_000, p=[0.8, 0.15, 0.05]),
        eta=rng.normal(0.0, 2.0, size=1_000_000),
        pt=rng.exponential(100, size=1_000_000),
        weight=0.123456 * 2 * rng.random(size=1_000_000),
    )
    base_hist.fill(  ## For mock ttbar
        dataset="ttbar",
        flavor=rng.choice([0, 4, 5], size=1_000_000, p=[0.45, 0.1, 0.45]),
        eta=rng.normal(0.0, 1.5, size=1_000_000),
        pt=rng.exponential(200, size=1_000_000),
        weight=0.01 * 2 * rng.random(size=1_000_000),
    )

    def test_default_read(self):
        """
        Ensure basic readout function generates arrays with compatible
        dimensions with given the base-level histogram.
        """
        try:
            readout = read_hist(TestHistUtils.base_hist)
        except:
            self.fail("Histogram reading raised an unexpected exception.")

        # Checking dimension compatibility
        self.assertTrue(len(readout["dataset"]) == len(readout["flavor"]))
        self.assertTrue(len(readout["dataset"]) == len(readout["eta"]))
        self.assertTrue(len(readout["dataset"]) == len(readout["pt"]))
        self.doCleanups()

    def test_projection_read(self):
        """
        Ensure basic readout function generates arrays with compatible
        dimensions with histogram slicing operations.
        """
        # Default read with simple projection
        try:
            read1 = read_hist(
                TestHistUtils.base_hist[{"dataset": "data", "flavor": sum}]
            )
            read2 = read_hist(TestHistUtils.base_hist[{"dataset": "QCD", "flavor": 0j}])
        except:
            self.fail("Histogram reading raised an unexpected exception.")
        # Checking dimension compatibility
        self.assertTrue(len(read1["eta"]) == len(read1["pt"]))
        self.assertTrue(len(read1["eta"]) == len(read2["pt"]))
        self.assertTrue(np.all(read1["eta"] == read2["eta"]))
        self.assertTrue(np.all(read1["pt"] == read2["pt"]))

        # Clean up
        self.doCleanups()

    def test_uncertainty_generation(self):
        """
        Exhaustively testing automatic variable generation with all defined
        uncertainty formats
        """

        d_h = TestHistUtils.base_hist[{"dataset": "data"}]
        q_h = TestHistUtils.base_hist[{"dataset": "QCD"}]
        t_h = TestHistUtils.base_hist[{"dataset": "ttbar"}]

        d_arr = d_h.view(flow=True)["value"].flatten()
        unc_arr = np.ones_like(d_arr) * np.random.random(size=d_arr.shape[0])
        try:
            auto_var = hist_as_variable(
                "testing",
                d_h,
                flow=True,
                uncertainty={
                    "symmetric stat": "poisson_sym",
                    "asymmetric stat": "poisson_asym",
                    "symmetric float": 1.5,
                    "asymmetric float": (1.5, 2.2),
                    "symmetric array": unc_arr,
                    "asymmetric array": (-0.8 * unc_arr, unc_arr),
                    "symmetric histogram": q_h,
                    "asymmetric histogram": (q_h, t_h),
                },
            )
        except:
            self.fail("Unexpected exception of automatic uncertainty generation.")

        def check_val(arr1, arr2):
            return self.assertTrue(
                np.all(np.isclose(arr1, arr2) | np.isnan(arr1) | np.isnan(arr2))
            )

        check_val(auto_var.values, d_arr)
        # Symmetric Poisson
        check_val(auto_var.uncertainties[0].values, np.sqrt(d_arr))

        # Asymmetric Poisson
        _l, _u = hist.intervals.poisson_interval(d_arr)
        _l, _u = _l - d_arr, _u - d_arr
        check_val(auto_var.uncertainties[1].values, list(zip(_l, _u)))

        # Flat uncertainties
        check_val(auto_var.uncertainties[2].values, 1.5)
        check_val(auto_var.uncertainties[3].values, (1.5, 2.2))

        # Array defined uncertainties
        check_val(auto_var.uncertainties[4].values, unc_arr)
        check_val(auto_var.uncertainties[5].values, list(zip(-0.8 * unc_arr, unc_arr)))

        # Histogram defined uncertainties
        q_arr = q_h.view(flow=True)["value"].flatten()
        t_arr = t_h.view(flow=True)["value"].flatten()
        check_val(auto_var.uncertainties[6].values, q_arr)
        check_val(auto_var.uncertainties[7].values, list(zip(q_arr, t_arr)))

        self.doCleanups()

    def test_table_generation(self):
        """
        Base table generation with base histogram
        """
        _rename_ = {
            "dataset": "Data set",
            "flavor": "Jet flavor",
            "eta": r"Jet $\eta$",
            "pt": r"Jet $p_{T}$",
        }
        _units_ = {"pt": "GeV"}
        try:
            table = create_hist_base_table(
                "my_table",
                TestHistUtils.base_hist,
                axes_rename=_rename_,
                axes_units=_units_,
            )
        except:
            self.fail("Unexpected exception of table generation.")

        readout = read_hist(TestHistUtils.base_hist)

        for idx, (name, new_name) in enumerate(_rename_.items()):
            # Checking rename
            self.assertTrue(table.variables[idx].name == new_name)
            self.assertTrue(table.variables[idx].units == _units_.get(name, ""))
            self.assertTrue(len(table.variables[idx].values) == len(readout[name]))

        self.doCleanups()
