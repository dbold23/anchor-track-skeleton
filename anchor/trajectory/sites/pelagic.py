"""Pelagic / open-coastal site geometry — for thresher shark deployments.

Threshers (*Alopias vulpinus*) are pelagic/sub-coastal predators in outer
Monterey Bay, off Año Nuevo, and along the central California shelf-break.
Unlike Elkhorn LS/BR (estuarine NHD-consensus polygon hard constraint),
the pelagic case has no land/water polygon to enforce. Instead:

  - **Bathymetry** is the only spatial constraint (soft penalty when over
    a too-shallow cell or above the surface).
  - **Process noise** uses the cruise-dominated regime; no benthic/grounded
    states are modelled (threshers don't sit on the bottom like batoids).
  - **Currents/tides** use shelf-circulation models (not the Largier-1996
    tidal-prism back-propagation tuned for Elkhorn).

This module is paper §4.5.1 open-coastal complement to
:mod:`anchor.trajectory.sites.elkhorn`. WS deployments at Año Nuevo also
fall under this regime (see :mod:`anchor.trajectory.sites.ano_nuevo`).
"""
from __future__ import annotations
from pathlib import Path
from anchor.trajectory.sites import BBox
OUTER_MONTEREY_DECLINATION_DEG_2026 = 12.7
PELAGIC_HAS_POLYGON_CONSTRAINT = False
PELAGIC_HAS_TIDE_AWARE_POLYGON = False

def is_pelagic_site(site_name: str) -> bool:
    """Convenience predicate for dispatching site-geometry mode in the pipeline."""
    ...
