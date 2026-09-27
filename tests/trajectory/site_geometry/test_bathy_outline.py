"""Unit tests for the bathymetric flood-fill outline derivation.

Synthetic-raster path: build a tiny topobathy raster with known wet/dry
geometry, run the derivation, assert the recovered polygon matches.

Real-raster path: skipif the Elkhorn bathy raster isn't on disk;
otherwise verify reasonable component counts and that the bat ray
release point is inside the derived outline.
"""
from __future__ import annotations
from pathlib import Path
import numpy as np
import pytest
import rasterio
from rasterio.transform import from_origin
import shapely.geometry as sg
from anchor.trajectory.site_geometry.bathy_outline import derive_outline_from_bathy, sweep_tide_levels, write_outline_geojson

def _write_synthetic_bathy(path: Path, h=20, w=20):
    """3x3 channel of bathy=2m surrounded by elevation=-2m (dry land)
    written as a UTM-10N raster."""
    ...

def test_synthetic_recovery(tmp_path):
    ...

def test_synthetic_low_tide_excludes_intertidal(tmp_path):
    ...

def test_synthetic_seed_dry_raises(tmp_path):
    ...

def test_synthetic_writeout_round_trip(tmp_path):
    ...

@skipif_no_bathy
def test_real_bathy_release_point_inside():
    """The bat ray release point must be inside the derived outline at
    a typical-spring-high tide level."""
    ...

@skipif_no_bathy
def test_real_bathy_open_ocean_outside():
    """A point in Monterey Bay west of the slough mouth must be outside
    the derived outline (the bbox clip prevents the flood from leaking
    into the bay)."""
    ...

@skipif_no_bathy
def test_real_bathy_morph_closing_idempotent_at_high_iters():
    """Heavy morphological closing shouldn't change the outline more
    than ~5% — this guards against a bug where iterations bleed into
    structurally different geometry."""
    ...

@skipif_no_bathy
def test_real_bathy_tide_sweep_monotone():
    """Wet area must monotonically grow as tide rises."""
    ...
