"""Wind data — math layer.

Counterpart to ``anchor.track.tides``: a ``WindSeries`` dataclass + an
interpolator + a network-aware dispatcher. The fetcher itself lives in
``anchor.track.wind_fetch`` so this module stays deterministic and
test-friendly.

Used by ``anchor.track.detachment.estimate_detachment_position`` for
Allen-1999 leeway: a buoyant surface tag drifts with a fraction (~2.5%)
of the local 10 m wind. When wind data is available the leeway term is
deterministic; when it isn't, the caller falls back to a Gaussian
σ-inflation budget instead.

Conventions
-----------
- Components are *eastward* (``u_east_mps``) and *northward*
  (``v_north_mps``) in m/s, the oceanographic convention. The fetcher
  converts NDBC ``WDIR`` (wind-from direction in degrees true) to
  vector components.
- Timestamps are ``datetime64[ns]`` UTC (``timestamps_utc``).
"""
from __future__ import annotations
import logging
from dataclasses import dataclass
from typing import Optional
import numpy as np
import pandas as pd

@dataclass
class WindSeries:
    """Hourly 10 m wind vector time series."""
    timestamps_utc: np.ndarray
    u_east_mps: np.ndarray
    v_north_mps: np.ndarray
    source: str

    def __post_init__(self) -> None:
        ...

    def __len__(self) -> int:
        ...

def wind_at(ws: WindSeries, t_utc) -> np.ndarray:
    """Linearly interpolate the wind vector at ``t_utc``.

    Returns
    -------
    np.ndarray of shape ``(2,)``: ``[u_east, v_north]`` in m/s.

    Out-of-range queries are clamped to the nearest endpoint (better than
    extrapolating wind, which has no meaningful physical model beyond
    the data window).
    """
    ...

def get_wind_series(t0_utc, t1_utc, *, source: str='ndbc:46092', fallback_source: Optional[str]='ndbc:46042', allow_network: bool=True) -> Optional[WindSeries]:
    """Cache-first dispatcher with one fallback source.

    Parameters
    ----------
    source, fallback_source
        Strings of the form ``"ndbc:<station>"``. Moss Landing M1 (46092)
        is closest to Elkhorn; Monterey buoy (46042) is the offshore
        fallback. Pass ``fallback_source=None`` to disable fallback.

    Returns
    -------
    WindSeries on success, or ``None`` if neither source produced data
    (cache miss + network off, or the station has no data for the
    requested window). Returning ``None`` is intentional — the caller
    in ``estimate_detachment_position`` falls back to a Gaussian σ
    budget when wind isn't available, which is cleaner than raising.
    """
    ...
