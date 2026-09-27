"""The position-fix maths shared by ``ReleaseAnchor``, ``EndAnchor`` and
``VerifiedPosition``.

All three are an isotropic 2-D Gaussian on (x, y) with a **per-axis** 1σ.
They carried three copies of this code, and one of them kept the wrong
normaliser after the other two were fixed (commit ``bb41a0f``); one copy
keeps them from drifting apart again.
"""
from __future__ import annotations
import numpy as np
import pyproj

def lonlat_to_xy(lon: float, lat: float, target_crs: str) -> tuple[float, float]:
    """WGS84 lon/lat to (x, y) in ``target_crs``."""
    ...

def isotropic_gaussian_logpdf(px: np.ndarray, py: np.ndarray, x: float, y: float, sigma_m: float) -> np.ndarray:
    """Log-density of particles at (px, py) under N((x, y), sigma_m² I)."""
    ...
