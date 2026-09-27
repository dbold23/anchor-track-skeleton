"""Per-site constants (AOI bbox, polygon outline path, magnetic declination).

Add a new site by creating a sibling module that exports the same constant
names; the trajectory pipeline is otherwise site-agnostic. Reuse the shared
``BBox`` defined here for the site's area-of-interest bounds.
"""
from __future__ import annotations
from typing import NamedTuple

class BBox(NamedTuple):
    lon_min: float
    lat_min: float
    lon_max: float
    lat_max: float

    def as_tuple(self) -> tuple[float, float, float, float]:
        ...
