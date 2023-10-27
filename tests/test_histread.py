#!/usr/bin/env python
"""Test scikit-hep reading"""
from unittest import TestCase
import numpy as np
import hist
from hepdata_lib.hist_utils import *


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
        try:
            readout = read_hist(TestHistUtils.base_hist)
        except:
            self.fail("Histogram reading raised an unexpected exception.")

        # Checking dimension compatibility
        self.assertTrue(len(readout["dataset"]) == len(readout["flavor"]))
        self.assertTrue(len(readout["dataset"]) == len(readout["eta"]))
        self.assertTrue(len(readout["dataset"]) == len(readout["pt"]))

        # Clean up
        self.doCleanups()
