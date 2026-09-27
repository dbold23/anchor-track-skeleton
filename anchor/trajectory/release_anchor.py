"""Release-point anchor for the particle filter.

For an AXY-only deployment with no acoustic positioning, the only known
"observation" of position is the release point itself (recorded by the
field crew at deployment). We use it as a tight Gaussian prior on (x, y)
applied at t=0.

This is structurally identical to a single VPS fix: bivariate Gaussian
log-likelihood. It just happens to be the only one.
"""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np
from anchor.trajectory._gaussian_fix import isotropic_gaussian_logpdf, lonlat_to_xy

@dataclass
class ReleaseAnchor:
    """Gaussian likelihood on the release position.

    ``sigma_m`` is the **per-axis** 1σ: an isotropic 2-D Gaussian whose
    x and y marginals each have standard deviation ``sigma_m`` (total
    2-D radial spread ``sqrt(2) * sigma_m``). Same convention as
    ``EndAnchor``, ``VerifiedPosition`` and a GPS fix's quoted
    horizontal σ.
    """
    x: float
    y: float
    sigma_m: float = 5.0

    @classmethod
    def from_lonlat(cls, lon: float, lat: float, sigma_m: float=5.0, target_crs: str='EPSG:32610') -> 'ReleaseAnchor':
        ...

    def log_likelihood(self, px: np.ndarray, py: np.ndarray) -> np.ndarray:
        ...
