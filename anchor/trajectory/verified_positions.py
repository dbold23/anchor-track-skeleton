"""Verified Positions (VPs) — periodic ground-truth fixes for drift correction.

Dead-reckoning accumulates position error ~t², so a reconstructed track decouples
from truth unless it is pinned to occasional known locations. The biologging
standard (Gunner et al. 2021, *Anim Biotelemetry*; Dewhirst et al. 2016) is
**Verified Position Correction (VPC)**: between each pair of Verified Positions —
GPS surface fixes, acoustic detections, a recapture coordinate — the track is
adjusted toward the fixes. Dewhirst showed 1 fix / 5 min cut 2D-RMS error to
15–38 m.

anchor's :class:`~anchor.trajectory.release_anchor.ReleaseAnchor` and
:class:`~anchor.trajectory.end_anchor.EndAnchor` are each a single VP (at t=0 and
t=T). This module generalises them to an arbitrary *series* of fixes at any
timestep, which the particle filter applies through its existing
``update_vps`` Gaussian likelihood and the FFBS smoother folds into backward
sampling. A :class:`VerifiedPosition` is therefore structurally identical to a
release/end anchor — same bivariate-Gaussian log-likelihood — it just carries a
timestep index so many can be threaded through one reconstruction.
"""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator, Optional, Sequence
import numpy as np
from anchor.trajectory._gaussian_fix import isotropic_gaussian_logpdf, lonlat_to_xy

@dataclass
class VerifiedPosition:
    """A single ground-truth position fix at a known timestep.

    Parameters
    ----------
    t_idx
        Filter step index this fix applies to (0-based, same grid as the track).
    x, y
        Coordinates in ``crs``.
    sigma_m
        **Per-axis** 1σ horizontal uncertainty (m): an isotropic 2-D Gaussian
        whose x and y marginals each have this standard deviation (total 2-D
        radial spread ``sqrt(2) * sigma_m``). Same convention as
        ``ReleaseAnchor`` and ``EndAnchor``. Handheld/animal GPS ~3–5 m;
        acoustic positioning is larger and depends on HPE (~1 + 0.2·HPE per
        Smith 2013).
    crs
        EPSG of (x, y); UTM 10N for Elkhorn by default.
    label
        Free-text provenance (e.g. ``"gps_surface"``, ``"acoustic"``,
        ``"recovery"``); carried through to the VPC validation report.
    """
    t_idx: int
    x: float
    y: float
    sigma_m: float = 10.0

    @classmethod
    def from_lonlat(cls, t_idx: int, lon: float, lat: float, sigma_m: float=10.0, target_crs: str='EPSG:32610', label: str='fix') -> 'VerifiedPosition':
        ...

    def log_likelihood(self, px: np.ndarray, py: np.ndarray) -> np.ndarray:
        """Bivariate-Gaussian log-likelihood of particles given this fix.

        Identical form to ``ReleaseAnchor``/``EndAnchor`` — the only difference
        is that a VP knows *when* it applies. That includes the normaliser:
        this is a 2-D density, so it is ``2*pi*sigma**2``, not the 1-D
        ``sigma*sqrt(2*pi)`` this used to carry (commit ``bb41a0f`` fixed the
        two anchors and left the VP behind). The constant cancels wherever a
        single VP is normalised on its own, but it is wrong by
        ``log(sqrt(2*pi)/sigma)`` nats whenever fixes of different σ are
        compared — or a VP is compared with an anchor.
        """
        ...

class VerifiedPositionSet:
    """An ordered collection of :class:`VerifiedPosition` indexed by timestep.

    At most one fix per timestep (the filter applies one Gaussian update per
    step). Construct from explicit step indices, from datetimes against the
    track's clock, or from a CSV.
    """

    def __init__(self, positions: Sequence[VerifiedPosition]):
        ...

    def __len__(self) -> int:
        ...

    def __iter__(self) -> Iterator[VerifiedPosition]:
        ...

    def __bool__(self) -> bool:
        ...

    def at(self, t_idx: int) -> Optional[VerifiedPosition]:
        """The fix at exactly ``t_idx``, or None."""
        ...

    def steps(self) -> list[int]:
        ...

    def interior(self, n_steps: int) -> 'VerifiedPositionSet':
        """Fixes strictly inside ``(0, n_steps-1)`` — excludes the t=0 release
        and the terminal step (handled by the release/end anchors)."""
        ...

    @classmethod
    def from_lonlat_fixes(cls, fixes: Sequence[tuple], target_crs: str='EPSG:32610', default_sigma_m: float=10.0) -> 'VerifiedPositionSet':
        """Build from ``(t_idx, lon, lat[, sigma_m[, label]])`` tuples."""
        ...

    @classmethod
    def from_time_fixes(cls, times: Sequence, lons: Sequence[float], lats: Sequence[float], t0_utc, base_hz: float, sigmas_m: Optional[Sequence[float]]=None, labels: Optional[Sequence[str]]=None, target_crs: str='EPSG:32610', default_sigma_m: float=10.0, n_steps: Optional[int]=None) -> 'VerifiedPositionSet':
        """Build from wall-clock fix times mapped to the track's step grid.

        ``t_idx = round((t - t0_utc) * base_hz)``. Fixes that map outside
        ``[0, n_steps)`` (when ``n_steps`` is given) are dropped — a fix logged
        after the tag detached should not anchor the attached-period filter.
        """
        ...

    @classmethod
    def from_csv(cls, path: str | Path, t0_utc, base_hz: float, time_col: str='time', lon_col: str='lon', lat_col: str='lat', sigma_col: str='sigma_m', label_col: str='label', target_crs: str='EPSG:32610', default_sigma_m: float=10.0, n_steps: Optional[int]=None) -> 'VerifiedPositionSet':
        """Load fixes from a CSV with datetime + lon/lat (+ optional sigma/label)."""
        ...
