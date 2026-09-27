"""Standard-format track export: GeoJSON / Movebank CSV / NetCDF."""
from __future__ import annotations
import importlib.util
import json
import sys
import numpy as np
import pandas as pd
import pytest
from anchor import export as EX

def _track(n=10):
    ...

def test_track_dataframe_reprojects_and_sigma():
    ...

def test_geojson_structure():
    ...

def test_geojson_coords_are_lonlat_order():
    ...

def test_geojson_from_xy_without_lonlat_uses_crs():
    ...

def test_write_geojson_roundtrip(tmp_path):
    ...

def test_movebank_columns_and_timestamps():
    ...

def test_movebank_requires_t0():
    ...

@pytest.mark.parametrize('force_scipy', [pytest.param(False, marks=pytest.mark.skipif(not HAS_NETCDF4, reason='netCDF4 not installed'), id='netcdf4'), pytest.param(True, id='scipy-fallback')])
def test_netcdf_written_and_readable(tmp_path, monkeypatch, force_scipy):
    ...

def test_export_track_dispatch(tmp_path):
    ...

def test_tz_aware_t0_is_converted_to_utc():
    ...

def test_geojson_is_strict_json_with_int_states():
    ...
