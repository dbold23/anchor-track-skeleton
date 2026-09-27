"""Smoke + edge-case tests for the polygon hard constraint."""
from __future__ import annotations
from pathlib import Path
import numpy as np
import pytest
import rasterio
from anchor.trajectory.polygon_constraint import PolygonConstraint
GRID_ORIGIN_X = 607435.6438194573
GRID_ORIGIN_Y = 4078430.5299427244
GRID_RES_M = 4.362170287190048
GRID_WIDTH = 1351
GRID_HEIGHT = 1670

@pytest.fixture(scope='module')
def grid_tif(tmp_path_factory) -> Path:
    """Empty single-band GeoTIFF carrying the Elkhorn bathymetry grid."""
    ...

@pytest.fixture(scope='module')
def poly(grid_tif: Path) -> PolygonConstraint:
    ...

def test_polygon_loads_and_has_water_cells(poly: PolygonConstraint):
    ...

def test_known_interior_point_is_inside(poly: PolygonConstraint):
    ...

def test_far_point_is_outside(poly: PolygonConstraint):
    ...

def test_vectorized_lookup_matches_per_point(poly: PolygonConstraint):
    ...
