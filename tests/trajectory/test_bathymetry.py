"""Smoke test for the SDB raster lookup wrapper."""
from __future__ import annotations
from pathlib import Path
import numpy as np
import pytest
from anchor.trajectory.bathymetry import REFERENCE_SIGMA_M, BathyLookup

@skipif_no_raster
def test_lookup_inside_aoi_returns_finite_values():
    ...

@skipif_no_raster
def test_lookup_outside_aoi_is_uninformative():
    ...

@skipif_no_raster
def test_log_likelihood_peaks_at_bathy_depth():
    ...

@skipif_no_raster
def test_log_likelihood_outside_aoi_is_zero():
    ...

def test_log_likelihood_delegates_to_the_violation_logpdf(simple_bathy):
    """`log_likelihood` is a lon/lat wrapper, not a second implementation:
    it must agree exactly with the two-sided mode at zero extra sigma."""
    ...
