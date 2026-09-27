"""HTTP client for NOAA NDBC buoy wind data, with on-disk caching.

Mirrors the structure of ``anchor.track.tide_fetch``: stdlib-only
(``urllib`` + ``json``), 3-try exponential backoff, and a JSON cache
under ``data/external/wind/`` keyed by ``(station, t0_date, t1_date)``.

Two NDBC endpoints are tried in order:

1. **realtime2** (``https://www.ndbc.noaa.gov/data/realtime2/{station}.txt``)
   — covers the most recent ~45 days. Single space-delimited text file.
2. **stdmet monthly archive** — for older windows. The exact URL varies
   by month/year and the format is the same space-delimited text. We
   probe ``view_text_file.php?filename=<station><MMM><YYYY>.txt.gz&dir=data/stdmet/<MMM>/``
   for the months covering the requested window.

Both endpoints return the same plain-text format:

    #YY  MM DD hh mm WDIR WSPD GST  WVHT  ... (column header)
    #yr  mo dy hr mn degT m/s  m/s   m    ... (units row)
    2026 03 18 00 00 270 5.4   6.8   ...
    ...

We extract WDIR (wind-from direction, deg true) and WSPD (m/s) and
convert to (u_east, v_north) using the standard meteorological
convention: a 270° wind blows *from* the west, so the vector is
(+u, 0). General formula:

    u_east  = -WSPD * sin(WDIR_rad)    # wind toward east when WDIR=270°
    v_north = -WSPD * cos(WDIR_rad)    # wind toward south when WDIR=0° (N)
"""
from __future__ import annotations
import gzip
import logging
import socket
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
import numpy as np
import pandas as pd
from anchor.trajectory.tide_fetch import _load_cache, _save_cache
from anchor.trajectory.wind import WindSeries
NDBC_HTTP_TIMEOUT_S = 30.0
NDBC_BACKOFF_S = (1, 4, 16)

def _month_digit(month: int) -> str:
    """NDBC month-suffix in current-year monthly archive URLs.

    Months 1-9 use the digit; Oct/Nov/Dec become 'a'/'b'/'c'.
    """
    ...

def _cache_key(station: str, t0: pd.Timestamp, t1: pd.Timestamp) -> str:
    ...

def _http_get_text_with_backoff(url: str) -> str:
    """GET text body with exponential backoff + 30 s timeout.

    Auto-decodes gzip when the URL ends in ``.gz``. 404 responses
    short-circuit (no retry) so callers can fall through to the next
    archive tier without waiting through the 1+4+16 s backoff.
    """
    ...

def parse_ndbc_text(text: str) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Parse an NDBC stdmet text payload → (timestamps_utc, u_east_mps, v_north_mps).

    Skips lines beginning with ``#`` (header + units rows) and lines
    where WDIR or WSPD are missing data sentinels (``MM`` or ``999``).
    """
    ...

def _payload_to_wind_series(payload: dict, station: str, source_label: str) -> WindSeries:
    """Convert a cached payload back to a WindSeries.

    Cache layout: ``{"text": <raw text>, "fetched_utc": iso}`` (we cache
    raw text to keep the parse logic deterministic).
    """
    ...

def _try_realtime2(station: str) -> Optional[str]:
    """Realtime2 covers most recent ~45 days. Returns text on success."""
    ...

def _try_historical(station: str, year: int) -> Optional[str]:
    """Closed-year yearly stdmet archive (years strictly < current_utc_year).

    Files live at ``/data/historical/stdmet/{station}h{YYYY}.txt.gz``.
    """
    ...

def _try_monthly(station: str, year: int, month: int) -> Optional[str]:
    """Current-year monthly stdmet archive.

    Files live at ``/data/stdmet/{Mon}/{station}.txt`` (plain text, no
    year suffix). Only the most-recently-completed month per station is
    served — earlier months from the current year fall back to
    ``view_text_file.php`` or the historical archive once the year closes.
    The ``year`` parameter is unused at the URL level but retained in
    the signature for caller compatibility.
    """
    ...

def fetch_ndbc_wind(station: str, t0_utc: pd.Timestamp, t1_utc: pd.Timestamp, *, allow_network: bool=True, cache_dir: Optional[Path]=None) -> WindSeries:
    """NDBC stdmet wind → WindSeries.

    Cache-first; falls back to network only if ``allow_network=True``;
    raises if neither path produces samples. The dispatcher in
    ``anchor.track.wind.get_wind_series`` translates the raise into a
    fallback to the next source / Gaussian σ-budget.
    """
    ...

def _months_in_range(t0: pd.Timestamp, t1: pd.Timestamp) -> list[tuple[int, int]]:
    """List (year, month) pairs covering [t0, t1] inclusive."""
    ...

def _has_no_data_in_range(text: str, t0: pd.Timestamp, t1: pd.Timestamp) -> bool:
    """Quick check: does the text cover any sample inside [t0, t1]?

    Realtime2 only covers ~45 days, so when the deployment is older the
    text will parse fine but contain no in-range samples — we then need
    to fall through to the monthly archive.
    """
    ...
