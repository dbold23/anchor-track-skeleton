"""Posterior-uncertainty visualization helpers for the trajectory pipeline.

Currently exposes one primitive — `confidence_ellipse` — and one
convenience wrapper — `add_ellipse_track` — that plug into any matplotlib
axes whose data coordinates are in metres (UTM). Designed for the FFBS
smoother panel where we have full 2×2 xy covariance per step; degrades
gracefully when a single eigenvalue collapses near zero (grounded
post-detach particles concentrate in 1-D filaments).

Construction follows Carsten Schelp's transform method
(https://carstenschelp.github.io/2018/09/14/Plot_Confidence_Ellipse_001.html):
draw a unit circle, then scale by Cholesky factors of the cov + rotate.
This avoids the eigendecomposition rotation bugs that bite when one
eigenvalue is near-zero or when xy correlation is high.

The 1σ-equivalent radius in 2-D (df=2) is sqrt(chi2.ppf(0.6827, 2)) ≈
1.515; for 95% it's ≈ 2.448. We default to (0.6827, 0.95) — the inner
ellipse is filled with low alpha, the outer is an outline.
"""
from __future__ import annotations
from typing import Optional, Sequence
import matplotlib.patches
import matplotlib.transforms as mpl_transforms
import numpy as np
from scipy.stats import chi2

def _radius_for_confidence(confidence: float) -> float:
    """Scale factor on the unit ellipse for a 2-DOF confidence level."""
    ...

def confidence_ellipse(mean_xy: np.ndarray, cov_xy: np.ndarray, *, confidence: float=0.6827, regularize: float=1e-06, **patch_kwargs) -> matplotlib.patches.Ellipse:
    """Build a single matplotlib Ellipse patch for one (mean, cov) pair.

    Parameters
    ----------
    mean_xy : array-like, shape (2,)
        Centre of the ellipse in data coordinates.
    cov_xy : array-like, shape (2, 2)
        2×2 covariance matrix. Singular cases are handled by adding
        ``regularize * I`` before the Schelp transform.
    confidence : float, default 0.6827
        Probability mass enclosed (default = 1σ-equivalent in 2-D).
    regularize : float, default 1e-6
        Floor added to the diagonal before the Cholesky-style transform
        (rad²). Prevents degenerate near-zero eigenvalues from blowing
        up. 1e-6 m² ≈ 1 mm — invisible at any reasonable map zoom.
    **patch_kwargs
        Passed through to matplotlib.patches.Ellipse (facecolor,
        edgecolor, alpha, linewidth, zorder, label, ...).
    """
    ...

def add_ellipse_track(ax, means_xy: np.ndarray, cov_xy_track: np.ndarray, *, every_n: int=50, confidences: Sequence[float]=(0.6827, 0.95), color: Optional[str]=None, fill_alpha: float=0.18, outline_lw: float=0.8, zorder: float=6, label: Optional[str]=None) -> int:
    """Overlay confidence ellipses at thinned timesteps along a track.

    Parameters
    ----------
    ax : matplotlib axes
        Target axes (data coordinates in metres / UTM).
    means_xy : array-like, shape (N, 2)
        Posterior-mean (x, y) at each step.
    cov_xy_track : array-like, shape (N, 2, 2)
        Posterior 2×2 xy covariance at each step.
    every_n : int, default 50
        Render every Nth ellipse to avoid clutter; the caller typically
        sizes this to land on ~30 ellipses across the track.
    confidences : sequence of float
        One ellipse per confidence level. Default (0.6827, 0.95) =
        1σ-equivalent filled + 95 % outline.
    color : str, optional
        Common color for fill + outline. Defaults to the Anchor theme's
        envelope colour (``anchor.viz.theme``). For a continuous envelope
        rather than discrete ellipses, see ``anchor.viz.marks.lens``.
    fill_alpha : float
        Alpha on the inner (1σ) ellipse.
    outline_lw : float
        Line width on the outer (95 %) ellipse.
    label : str, optional
        Legend label applied to the *first* rendered ellipse.

    Returns
    -------
    int
        Number of ellipses actually drawn (handy for asserts in tests).
    """
    ...
