"""Uncertainty-propagated utilization distributions + energy seascapes."""
from __future__ import annotations
import numpy as np
import pytest
from anchor import spaceuse as SU

def _two_cluster_samples(T=20, K=50, seed=0):
    """First half of timesteps sit at cluster A, second half at B (K jittered)."""
    ...

def test_points_from_samples_flatten_and_weights():
    ...

def test_points_from_samples_validates():
    ...

def test_kde_occupancy_normalized_and_peaked():
    ...

def test_isopleth_mask_nested_and_areas_increase():
    ...

def test_home_range_area_increases_with_level():
    ...

def test_energy_weighting_shifts_mass_to_high_energy_region():
    """The core novelty: weighting by energy concentrates the UD where energy
    is spent, not merely where the animal was."""
    ...

def test_write_geotiff_roundtrip(tmp_path):
    ...

def test_isopleths_geojson_structure():
    ...

def test_kde_ignores_nan_weights():
    ...

def test_kde_rejects_negative_weights():
    ...

def test_kde_warns_on_points_outside_bounds():
    ...
