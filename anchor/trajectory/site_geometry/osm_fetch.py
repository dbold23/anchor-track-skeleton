"""OpenStreetMap waterbody fetcher (Overpass API).

OSM is crowd-sourced from satellite imagery and ground truth. For
Elkhorn it's mapped reasonably well — the slough has explicit
``natural=water`` polygons and ``waterway=river/stream`` linear
features. We pull both as a third independent source for the slough
boundary, which is useful as a cross-check against NHD (federal) and
bathymetric flood-fill (DEM-derived).

Source attribution: © OpenStreetMap contributors, ODbL.
Endpoint: <https://overpass-api.de/api/interpreter>

Usage
-----
    from anchor.trajectory.site_geometry.osm_fetch import fetch_osm_water
    polys = fetch_osm_water(
        bbox_lonlat=(-121.80, 36.78, -121.73, 36.86),
    )
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
import shapely.ops
HTTP_TIMEOUT_S = 60.0
RETRIES = 3
BACKOFF_S = (2, 8, 32)

def _cache_key(bbox: tuple[float, float, float, float]) -> str:
    ...

def _http_post(url: str, body: str) -> dict:
    ...

def _build_overpass_query(bbox: tuple[float, float, float, float]) -> str:
    """Overpass QL: fetch all closed ways + multipolygon relations tagged
    ``natural=water`` OR ``waterway=*`` within bbox."""
    ...

def _parse_overpass_geoms(payload: dict) -> list[shapely.geometry.Polygon]:
    """Materialize closed ways + multipolygon relations into polygons.

    Overpass returns elements as a flat list of nodes / ways / relations.
    Closed ways become polygons. Relations of type=multipolygon need to
    have their member ways stitched: outer rings minus inner rings.
    """
    ...

def fetch_osm_water(bbox_lonlat: tuple[float, float, float, float], *, allow_network: bool=True, cache_dir: Optional[Path]=None) -> list[shapely.geometry.Polygon]:
    """Fetch OSM ``natural=water`` polygons in bbox via Overpass."""
    ...
