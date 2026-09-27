"""HTTP clients for tide / water-level sources, with on-disk caching.

Network I/O lives in this module so ``anchor.track.tides`` stays a pure
math layer that's deterministic in tests. All HTTP calls go through
``urllib.request`` (stdlib only — no new runtime dependency) with a
3-try exponential backoff (1s, 4s, 16s) and 30-second socket timeout.

Cache policy
------------
Successful responses are written to ``data/external/tides/`` keyed by
(source, station, t0_date, t1_date). A registry JSON tracks what's
cached. The dispatcher in ``tides.get_tide_series`` reads the cache
first, then network if ``allow_network=True``, then falls through to
the synthetic harmonic with a warning.

Sources implemented:
    - NOAA CO-OPS historical water level (station 9413450 = Monterey CA)
    - NERRS SWMP water-level loggers (station IDs like ``elkvmwq``)

NERRS SWMP requires a free CDMO web-form registration to access the
JSON API. Without an API key the fetcher raises ``SWMPRegistrationRequired``
which the dispatcher catches and degrades cleanly to NOAA.
"""
from __future__ import annotations
import json
import socket
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Optional
import numpy as np
import pandas as pd
from anchor.trajectory.tides import TideSeries
NOAA_HTTP_TIMEOUT_S = 30.0
NOAA_RETRIES = 3
NOAA_BACKOFF_S = (1, 4, 16)

class SWMPRegistrationRequired(RuntimeError):
    """Raised when SWMP API access requires CDMO registration that's
    not configured."""

def _ensure_dir(p: Path) -> Path:
    ...

def _cache_key(source: str, station: str, t0: pd.Timestamp, t1: pd.Timestamp) -> str:
    ...

def _load_cache(cache_dir: Path, key: str) -> Optional[dict]:
    ...

def _save_cache(cache_dir: Path, key: str, payload: dict) -> None:
    ...

def _http_get_json_with_backoff(url: str) -> dict:
    """GET JSON with exponential backoff + 30s timeout."""
    ...

def _noaa_payload_to_tide_series(payload: dict, station: str, source_label: str) -> TideSeries:
    ...

def fetch_noaa_water_level(station: str, t0_utc: pd.Timestamp, t1_utc: pd.Timestamp, *, allow_network: bool=True, cache_dir: Optional[Path]=None) -> TideSeries:
    """NOAA CO-OPS historical water level → TideSeries.

    Cache-first; falls back to network only if ``allow_network=True``;
    raises if neither path produces samples.
    """
    ...

def fetch_swmp_water_level(station: str, t0_utc: pd.Timestamp, t1_utc: pd.Timestamp, *, allow_network: bool=True, cache_dir: Optional[Path]=None) -> TideSeries:
    """NERRS SWMP in-slough water level → TideSeries.

    The CDMO API requires registration and an API key — this is a stub
    that reads from cache only. If you have an account, drop your key in
    ``data/external/tides/_swmp_key.txt`` (single line) and the network
    path will be enabled.

    Stations of interest:
        elkvmwq  — Vierra Mouth (lower slough)
        elknmwq  — North Marsh (upper slough)
        elkapwq  — Azevedo Pond
    """
    ...
