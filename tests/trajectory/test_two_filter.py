"""Tests for the bidirectional (two-filter) particle smoother.

Synthetic-track validation: simulate a ground-truth path with known
release + recovery endpoints, run forward filter, backward filter, and
the two-filter smoother. Assert that:

    1. Backward filter at t=T concentrates near the recovery anchor
       just like the forward filter at t=0 concentrates near release.
    2. The two-filter smoother's posterior at the midpoint is *tighter*
       than the forward filter alone at the midpoint (key value-prop).
    3. Smoothed track endpoints fall close to the known release/recovery.
    4. The smoothed bias/scale posterior on a deployment with known
       injected bias recovers it within 2σ.
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
from anchor.trajectory.end_anchor import EndAnchor
from anchor.trajectory.polygon_constraint import PolygonConstraint
from anchor.trajectory.release_anchor import ReleaseAnchor
from anchor.trajectory.synthetic import simulate_observations, simulate_truth
from anchor.trajectory.two_filter import run_backward_filter, two_filter_smoother
from anchor.trajectory.animate_filter import run_filter_with_snapshots

def _load_polygon_in_raster_crs(geojson_path: Path, raster_crs):
    ...

@pytest.fixture
def synthetic_track_with_endpoints():
    """Build a synthetic track + observations + release/recovery anchors."""
    ...

@skipif_missing
def test_backward_filter_concentrates_at_recovery(synthetic_track_with_endpoints):
    ...

@skipif_missing
def test_two_filter_tightens_midpoint_posterior(synthetic_track_with_endpoints):
    """At the midpoint of the deployment the forward filter alone has
    accumulated drift; the smoothed posterior should be tighter."""
    ...

@skipif_missing
def test_two_filter_endpoints_close_to_anchors(synthetic_track_with_endpoints):
    ...
