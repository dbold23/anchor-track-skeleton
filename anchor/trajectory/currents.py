"""Spatially-varying tidal-current field for the trajectory filter.

Currents in Elkhorn Slough are tidally driven and vary along the
slough's main axis: ~0.5 m/s peaks at the Hwy 1 mouth, ~0.1 m/s at
Kirby Park (Largier 1996). Ignoring them in the dead-reckoning step
biases every position estimate by the integral of unobserved current
over time — for a 4-hr deployment that's O(km).

Two construction routes:

1. ``CurrentField.from_tide_series(tide, centerline, decay_profile, K)`` —
   *Default.* Drives mouth current as ``u_mouth(t) = K · dη/dt(t)`` from
   real NOAA water-level data, applies along-channel spatial decay using
   a hand-drawn centerline polyline + a Largier-1996-published decay
   profile. Direction: the local centerline tangent; cross-channel
   component zero.

2. ``CurrentField.from_csv(...)`` — Upload route. CSV columns
   ``timestamp_utc, u_along_mps`` (signed: + = flood / inland).
   Otherwise same spatial-decay machinery.

Both produce a ``CurrentField`` instance with one method:
``uv_at(x, y, t_utc)`` returning per-particle ``(u, v)`` in m/s
(east, north) in the centerline's CRS.

References
----------
- Largier 1996 (Estuaries 19) — channel velocity profile.
- Caffrey et al. 2002 — tidal-prism volumes for K calibration.
- Friedrichs & Aubrey 1988 — tidal-prism / channel-area scaling theory.
"""
from __future__ import annotations
import json
from dataclasses import dataclass
from pathlib import Path
import numpy as np
import pandas as pd
import pyproj
import shapely.geometry
import shapely.ops
from anchor.trajectory.tides import TideSeries

@dataclass
class Centerline:
    """A polyline through the slough's main channel, projected into the
    same CRS as the bathymetry / polygon. Used to project a particle's
    position onto the nearest channel point and recover the local
    along-channel tangent."""
    coords_utm: np.ndarray
    arc_length_m: np.ndarray

    @classmethod
    def from_geojson(cls, geojson_path: str | Path, target_crs: str='EPSG:32610') -> 'Centerline':
        ...

    @property
    def total_length_m(self) -> float:
        ...

    def project(self, x: np.ndarray, y: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """For each (x, y), return (arc_length_m, local_tangent_bearing_rad).

        Tangent is the unit vector along the nearest segment, oriented in the
        direction of increasing arc-length. Bearing returned as the angle
        in the East–North plane (radians, math convention: 0 = +East,
        π/2 = +North).
        """
        ...

@dataclass(frozen=True, eq=False)
class TideDerivativeDriver:
    """Mouth current as ``K · dη/dt(t)`` off a :class:`TideSeries`."""
    tide: TideSeries
    prism_K_m: float

    def __call__(self, t_utc) -> np.ndarray:
        ...

@dataclass(frozen=True, eq=False)
class SampledSeriesDriver:
    """Mouth current linearly interpolated from an uploaded sample series.

    Timestamps are held as int64 nanoseconds since the epoch — the form
    ``np.interp`` needs — so no conversion happens per filter step.
    """
    timestamps_ns: np.ndarray
    u_along_mps: np.ndarray

    def __call__(self, t_utc) -> np.ndarray:
        ...

@dataclass(frozen=True, eq=False)
class ZeroDriver:
    """No current at any time — the control field."""

    def __call__(self, t_utc) -> np.ndarray:
        ...

@dataclass
class CurrentField:
    """Tidal current field: ``uv_at(x, y, t_utc)`` returns per-particle
    ``(u_east, v_north)`` in m/s.

    Internals:
        - ``_temporal``: callable ``t_utc → mouth_along_mps``. Either
          derived from a TideSeries (via dη/dt × K) or from an uploaded
          CSV time series. Must be picklable — see the driver classes
          above — because the latent grid ships whole fields to worker
          processes.
        - ``centerline``: spatial coordinate frame.
        - ``decay_profile``: ((arc_m, factor), ...) piecewise-linear
          along-channel scaling.
    """
    centerline: Centerline
    decay_profile: tuple[tuple[float, float], ...]
    _temporal: callable
    label: str

    @classmethod
    def from_tide_series(cls, tide: TideSeries, centerline: Centerline, decay_profile: tuple[tuple[float, float], ...], prism_K_m: float) -> 'CurrentField':
        """Mouth current = K · dη/dt(t). The constant K comes from the
        upper-slough tidal prism divided by the channel cross-section
        (Friedrichs & Aubrey 1988); for Elkhorn K ≈ 1e4 m yields ~0.5 m/s
        peak — see ``ELKHORN_TIDAL_PRISM_K_M``."""
        ...

    @classmethod
    def from_csv(cls, csv_path: str | Path, centerline: Centerline, decay_profile: tuple[tuple[float, float], ...]) -> 'CurrentField':
        """User-supplied along-channel mouth current series.

        CSV must have columns ``timestamp_utc`` (parseable to
        ``pd.Timestamp``) and ``u_along_mps`` (positive = flood / inland)."""
        ...

    @classmethod
    def zero(cls, centerline: Centerline) -> 'CurrentField':
        ...

    def _decay_at(self, arc_m: np.ndarray) -> np.ndarray:
        ...

    def uv_at(self, x: np.ndarray, y: np.ndarray, t_utc) -> np.ndarray:
        """Return shape ``(N, 2)`` of (u_east, v_north) m/s.

        ``x, y`` are particle UTM coords in the centerline's CRS;
        ``t_utc`` is a single timestamp (broadcast over particles)."""
        ...
