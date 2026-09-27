"""Smoke tests for the NHD + OSM fetchers (cache-only paths).

Live HTTP isn't exercised in CI — `--no-network` paths only. The cache
files committed during the v2 derivation are the test fixtures.
"""
from __future__ import annotations
from pathlib import Path
import pytest
from anchor.trajectory.site_geometry.nhd_fetch import fetch_nhd_waterbodies
from anchor.trajectory.site_geometry.osm_fetch import fetch_osm_water

@skipif_no_nhd
def test_nhd_cache_loads():
    """Pull the same bbox we used at derivation time, allow_network=False."""
    ...

@skipif_no_osm
def test_osm_cache_loads():
    ...

def test_nhd_no_cache_no_network_raises(tmp_path):
    ...

def test_osm_no_cache_no_network_raises(tmp_path):
    ...
