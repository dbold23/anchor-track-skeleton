"""Standard-format export for reconstructed tracks — interoperability layer.

anchor reconstructs tracks in a projected CRS (UTM metres) and, until now, only
rendered them into an HTML report. To be useful to the wider movement-ecology
community a track must leave anchor in the formats those tools read:

- **GeoJSON** — universal GIS interchange (QGIS, web maps, geopandas). One
  ``LineString`` for the path plus per-vertex ``Point`` features carrying time,
  positional σ, and behaviour state.
- **Movebank CSV** — the de-facto animal-movement repository schema
  (``timestamp``, ``location-long``, ``location-lat``,
  ``individual-local-identifier`` …), so anchor tracks drop straight into
  Movebank / MoveApps and downstream R packages (move2, ctmm, aniMotum).
- **NetCDF (CF-1.8 ``trajectory``)** — the biologging-community archival format
  (self-describing, CF/ACDD attributes), suitable for Zenodo/ERDDAP/IOOS-ATN.

Everything is built on a tidy *track DataFrame* (:func:`track_dataframe`):
columns ``t`` (s), ``x``/``y`` (projected, in ``crs``), ``lon``/``lat``, and
optional ``sigma_x_m``/``sigma_y_m``/``sigma_m``, ``state``/``state_label``,
``depth_m``. Reconstructions assemble it from the filter/smoother arrays; the
``anchor export`` CLI reads it back from parquet.
"""
from __future__ import annotations
import json
from pathlib import Path
from typing import Optional
import numpy as np
import pandas as pd

def reproject_lonlat(x, y, crs: str):
    """Project ``(x, y)`` arrays from ``crs`` to WGS84 lon/lat."""
    ...

def track_dataframe(t_s, x, y, crs: str, sigma_x_m=None, sigma_y_m=None, states=None, state_labels=None, depth_m=None) -> pd.DataFrame:
    """Assemble a tidy track DataFrame from reconstruction arrays.

    ``x``/``y`` are in ``crs`` (e.g. UTM metres); ``lon``/``lat`` are derived.
    ``sigma_x_m``/``sigma_y_m`` are per-step 1σ position uncertainty; their
    quadrature sum is stored as ``sigma_m``. ``states`` (int) and
    ``state_labels`` (str) are optional behaviour annotations; ``depth_m`` an
    optional depth channel.
    """
    ...

def _ensure_lonlat(df: pd.DataFrame, crs: Optional[str]) -> pd.DataFrame:
    """Return a copy of ``df`` guaranteed to have lon/lat columns."""
    ...

def _utc_naive(t0_utc) -> pd.Timestamp:
    """``t0_utc`` as a naive UTC timestamp.

    A timezone-aware value (e.g. ``2026-03-18T10:00-07:00``) is converted to
    UTC first; dropping the offset instead would shift every exported
    timestamp by the UTC offset. A naive value is taken to already be UTC.
    """
    ...

def _timestamps(df: pd.DataFrame, t0_utc) -> Optional[pd.DatetimeIndex]:
    """Absolute UTC timestamps from ``t`` seconds + ``t0_utc`` (None if no t0)."""
    ...

def _json_value(v):
    """A JSON-safe scalar: None for missing/non-finite, int for integers."""
    ...

def to_geojson(df: pd.DataFrame, crs: Optional[str]=None, t0_utc=None, stride: int=1, line: bool=True, points: bool=True) -> dict:
    """Build a GeoJSON FeatureCollection (WGS84) for a track.

    A ``LineString`` of the full path (when ``line``) plus one ``Point`` per
    ``stride``-th step (when ``points``) carrying ``t``, timestamp, ``sigma_m``,
    and behaviour state as properties. GeoJSON is always WGS84 per RFC 7946.
    """
    ...

def write_geojson(df: pd.DataFrame, path: str | Path, **kwargs) -> Path:
    ...

def to_movebank(df: pd.DataFrame, individual_id: str, t0_utc, crs: Optional[str]=None) -> pd.DataFrame:
    """Build a Movebank-conformant DataFrame.

    Movebank requires real timestamps, so ``t0_utc`` is mandatory. Emits the
    core Movebank columns; positional σ rides along as ``location-error-numerical``
    (Movebank's recognised accuracy field), depth as ``height-above-ellipsoid``
    negated (depth below surface), and behaviour as ``comments``.
    """
    ...

def write_movebank_csv(df: pd.DataFrame, path: str | Path, individual_id: str, t0_utc, crs: Optional[str]=None) -> Path:
    ...

def write_netcdf(df: pd.DataFrame, path: str | Path, t0_utc=None, crs: Optional[str]=None, individual_id: str='unknown', title: str='anchor reconstructed track') -> Path:
    """Write a CF-1.8 ``trajectory``-featureType NetCDF file.

    Uses ``netCDF4`` when available, else falls back to NetCDF3 via
    ``scipy.io.netcdf_file`` (scipy is a core dependency, so export always
    works). Variables: ``time``, ``lat``, ``lon``, and any of ``depth``,
    ``sigma_m``, ``state`` present. Coordinates follow CF; global attributes
    follow CF + ACDD so the file is self-describing for archives.
    """
    ...

def export_track(df: pd.DataFrame, path: str | Path, fmt: str, crs: Optional[str]=None, t0_utc=None, individual_id: str='unknown', stride: int=1) -> Path:
    """Dispatch to the right writer by ``fmt`` (geojson | movebank | netcdf)."""
    ...
