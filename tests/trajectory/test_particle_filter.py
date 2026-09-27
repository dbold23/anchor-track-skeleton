"""Synthetic-data recovery test for the particle filter.

End-to-end:
  1. Load v1 SDB raster + bay polygon
  2. Generate a known-truth shark track inside the polygon
  3. Generate noisy AXY + sparse VPS observations
  4. Run the particle filter
  5. Verify the posterior-mean track stays within a credible region of truth
"""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import pyproj
import pytest
import shapely.geometry
from shapely.ops import transform as shapely_transform
from anchor.trajectory.bathymetry import BathyLookup
from anchor.trajectory.particle_filter import FilterConfig, ParticleFilter, ffbs_smoother
from anchor.trajectory.synthetic import simulate_observations, simulate_truth

def _load_polygon_in_raster_crs(geojson_path: Path, raster_crs):
    ...

def _interior_seed(poly: shapely.geometry.MultiPolygon, bathy: BathyLookup):
    """Pick a starting point that's inside the polygon AND has finite bathy."""
    ...

@skipif_missing
def test_particle_filter_recovers_synthetic_track():
    ...

@skipif_missing
def test_particle_filter_recovers_heading_bias_and_speed_scale():
    """Inject a known heading bias and speed scale into the observations;
    verify the filter recovers them within a few posterior σ."""
    ...

@skipif_missing
def test_ffbs_smoother_tightens_latent_params():
    """Smoothed posterior on bias/scale should be tighter and less biased
    than the forward-only filter's posterior at the same final time."""
    ...

@skipif_missing
def test_particle_filter_diverges_without_vps():
    """Sanity check: without VPS fixes, errors grow vs the with-VPS case."""
    ...

def _free_space_filter(n_particles: int=64) -> ParticleFilter:
    """Filter with no raster and no polygon — nothing here needs fixtures."""
    ...

def test_resample_without_collapse_is_not_counted():
    ...

def test_total_weight_collapse_is_counted_and_logged(caplog):
    """A -inf-everywhere resample used to reset to uniform silently."""
    ...

def test_maybe_resample_forwards_the_step_index(caplog):
    ...

def test_single_surviving_particle_is_not_a_collapse():
    """One finite weight is degenerate but still informative — not a collapse."""
    ...
