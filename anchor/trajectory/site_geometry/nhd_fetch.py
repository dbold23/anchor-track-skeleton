"""USGS National Hydrography Dataset (NHD) waterbody fetcher.

NHD is the federal government's authoritative geospatial database for
surface water in the US. The National Map's NHD MapServer exposes a
WGS84 REST API (no auth) that returns GeoJSON. We use the NHDArea +
NHDWaterbody layers — the former captures slough/estuary polygons, the
latter captures named lakes/ponds. For Elkhorn Slough, NHDArea has a
labeled "Estuary" polygon that exactly matches the canonical slough
boundary (modulo NHD's typical ~10 m generalization).

Source attribution: <https://hydro.nationalmap.gov/arcgis/rest/services>
NHDPlus High Resolution layer set; current at the date of fetch.

Usage
-----
    from anchor.trajectory.site_geometry.nhd_fetch import fetch_nhd_waterbodies
    polys = fetch_nhd_waterbodies(
        bbox_lonlat=(-121.80, 36.78, -121.73, 36.86),
    )
    # polys is a list of shapely.geometry.Polygon in WGS84

Cache layout
------------
    data/external/site_geometry/nhd_<bbox>.json
"""
from __future__ import annotations
import hashlib
import json
import socket
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Optional
import shapely.geometry
HTTP_TIMEOUT_S = 30.0
RETRIES = 3
BACKOFF_S = (1, 4, 16)
NHD_AREA_LAYER = 8
NHD_WATERBODY_LAYER = 9

def _cache_key(bbox: tuple[float, float, float, float], layer_ids: tuple[int, ...]) -> str:
    ...

def _http_get_json(url: str) -> dict:
    ...

def _query_nhd_layer(layer_id: int, bbox_lonlat: tuple[float, float, float, float]) -> list[shapely.geometry.Polygon]:
    ...

def fetch_nhd_waterbodies(bbox_lonlat: tuple[float, float, float, float], *, layers: tuple[int, ...]=(NHD_AREA_LAYER, NHD_WATERBODY_LAYER), allow_network: bool=True, cache_dir: Optional[Path]=None) -> list[shapely.geometry.Polygon]:
    """Fetch all NHD waterbody polygons intersecting bbox_lonlat.

    Concatenates results from each requested layer; deduplicates exact
    duplicates (which can happen when NHD-Area and NHD-Waterbody share
    a feature). Caches the parsed result on disk.
    """
    ...
