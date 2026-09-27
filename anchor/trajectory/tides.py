"""Tide-height time series for the trajectory pipeline.

This module is the *math* layer: pure-numpy harmonic sum + a value-class
``TideSeries`` that the filter consumes. Network I/O lives separately in
``anchor.track.tide_fetch`` — that way ``tides`` stays import-cheap and
deterministic for tests.

Sources (highest authority first):
    - NOAA CO-OPS historical water level at Monterey (station 9413450),
      6-min cadence. Real observations, gold standard.
    - NERRS SWMP in-slough loggers (Vierra Mouth, North Marsh) for
      upper-slough corrections. Optional Tier-3 augmentation.
    - Synthetic harmonic from the constituents below — offline fallback
      only, accuracy ±20-30 cm.

The wet condition for any pixel of the bathymetry raster is
``bathy_at_mllw_m + tide_height_m > 0`` (depth-below-MLLW convention),
which is the basis of the tide-aware polygon stack.

References
----------
- Pawlowicz et al. 2002 — t_tide MATLAB toolbox (constituent definitions).
- NOAA CO-OPS station 9413450 (Monterey, CA) constituent table:
  https://tidesandcurrents.noaa.gov/harcon.html?id=9413450
- Caffrey et al. 2002 — *Changes in a California Estuary*, the Elkhorn
  compendium that documents the slough's tidal range and dynamics.
"""
from __future__ import annotations
import datetime as _dt
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
import numpy as np
import pandas as pd

@dataclass(frozen=True)
class HarmonicConstituent:
    name: str
    period_hr: float
    amplitude_m: float
    phase_deg: float
MONTEREY_MSL_OFFSET_M = 0.86

def _hours_since_epoch(t_utc: np.ndarray, epoch: _dt.datetime=_SYNTHETIC_EPOCH) -> np.ndarray:
    ...

def synthetic_tide_height(t_utc: np.ndarray, constituents: tuple[HarmonicConstituent, ...]=MONTEREY_CONSTITUENTS, datum_offset_m: float=MONTEREY_MSL_OFFSET_M) -> np.ndarray:
    """Sum of harmonic constituents → tide height (m above MLLW).

    The constituents oscillate about mean sea level, so ``datum_offset_m``
    (MSL − MLLW) lifts the sum onto the MLLW datum the NOAA fetch and the
    wet-mask thresholds use. Pure-numpy, deterministic, no I/O.
    """
    ...

def synthetic_tide_derivative_mps(t_utc: np.ndarray, constituents: tuple[HarmonicConstituent, ...]=MONTEREY_CONSTITUENTS) -> np.ndarray:
    """dη/dt in m/s — drives the tidal-current model when fetched derivative
    isn't available (currents derived from finite-differencing observed water
    level are used in ``anchor.track.currents``).
    """
    ...

@dataclass
class TideSeries:
    """Tide-height samples + linear interpolator.

    Always sample-based (even the synthetic case discretizes to a regular
    grid). Filter calls ``value_at(t_utc)`` per filter step; this is O(log N)
    via ``np.searchsorted`` once the timestamps are sorted, which they are by
    construction.
    """
    timestamps_utc: np.ndarray
    height_m_mllw: np.ndarray
    source: str

    def __post_init__(self) -> None:
        ...

    @property
    def t0_utc(self) -> pd.Timestamp:
        ...

    @property
    def t1_utc(self) -> pd.Timestamp:
        ...

    def covers(self, t_utc) -> bool:
        ...

    def value_at(self, t_utc) -> float | np.ndarray:
        """Linear-interpolated tide height at ``t_utc`` (single or array)."""
        ...

    def derivative_mps(self, t_utc) -> float | np.ndarray:
        """dη/dt at ``t_utc`` via central difference on the cached samples."""
        ...

    def to_dataframe(self) -> pd.DataFrame:
        ...

def synthetic_tide_series(t0_utc: pd.Timestamp, duration_hr: float=24.0, cadence_min: float=6.0, constituents: tuple[HarmonicConstituent, ...]=MONTEREY_CONSTITUENTS) -> TideSeries:
    ...

def get_tide_series(t0_utc: pd.Timestamp, t1_utc: pd.Timestamp, *, source: str='noaa:9413450', allow_network: bool=True, cache_dir: Optional[Path]=None) -> TideSeries:
    """Return a TideSeries spanning [t0, t1].

    Sources (in fallback order if a fetch fails):
        - "noaa:<station_id>"  — NOAA CO-OPS historical water level (gold standard)
        - "swmp:<station_id>"  — NERRS SWMP in-slough logger (Tier 3)
        - "synthetic"          — harmonic-constituent fallback (offline)

    The fetch is delegated to ``anchor.track.tide_fetch`` so callers that
    only want the math (e.g. tests) don't pay the import cost.

    If ``allow_network`` is False, NOAA/SWMP requests fall back to the
    synthetic source with a printed warning. Tests and Streamlit set
    ``allow_network=False`` by default; CLI scripts default to True.
    """
    ...
