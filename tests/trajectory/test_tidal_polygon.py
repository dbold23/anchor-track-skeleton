"""Unit tests for the tide-aware polygon mask stack.

Asserts the stack behaves like Elkhorn physics dictates:
    - Low-tide wet area is much smaller than high-tide wet area
    - The deep channel (Kirby Park area, ~5 m below MLLW) is wet at all levels
    - A known mudflat point is dry at low tide and wet at high tide
    - Static PolygonConstraint and TidalPolygonConstraint share the
      ``is_inside(x, y, tide_m_mllw=...)`` signature
"""
from __future__ import annotations
import numpy as np
import pyproj
import pytest
from anchor.trajectory.polygon_constraint import PolygonConstraint, TidalPolygonConstraint
from anchor.trajectory.sites.elkhorn import ELKHORN_BATHY_TIF, ELKHORN_OUTLINE_GEOJSON, ELKHORN_TIDE_POLYGON_STACK

def _lonlat_to_utm(lon, lat):
    ...

@skipif_no_stack
def test_stack_loads():
    ...

@skipif_no_stack
def test_low_tide_shrinks_wet_area():
    ...

@skipif_no_stack
def test_release_point_wet_at_high_tide():
    """The bat ray release point at Kirby Park reach must be wet at
    typical mid-to-high tide levels (η ≥ 0.5 m above MLLW) — that's the
    range the actual deployment spanned. The upper-slough channel is
    shallow enough that the point may legitimately go dry at extreme
    low spring tides."""
    ...

@skipif_no_stack
def test_extreme_low_tide_excludes_more_than_high_tide_does():
    """The most basic physics check: more cells flooded at high tide than
    at low tide. Don't pin to exact ratios — just monotone."""
    ...

@skipif_no_stack
def test_static_polygon_signature_compat():
    ...

@skipif_no_stack
def test_tidal_is_inside_requires_tide_arg():
    ...

@skipif_no_stack
def test_nearest_level_lookup():
    ...

@skipif_no_stack
def test_out_of_bounds_returns_false():
    ...
