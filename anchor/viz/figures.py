"""Composed Anchor figures built from :mod:`anchor.viz.marks`.

:func:`track_figure` is the signature view: the reconstructed track over the
water column, its uncertainty drawn as a lens pinned at the anchor fixes, the
path coloured by behaviour, and three linked strips on a shared clock
(uncertainty, depth, ethogram) beside it.
"""
from __future__ import annotations
from pathlib import Path
from typing import Optional
import matplotlib.pyplot as plt
import numpy as np
from anchor.viz import marks, theme

def _radial_sigma(stds: np.ndarray) -> np.ndarray:
    ...

@theme.styled
def track_figure(means_xy: np.ndarray, cov_xy: Optional[np.ndarray]=None, *, t_s: Optional[np.ndarray]=None, states: Optional[np.ndarray]=None, depth_m: Optional[np.ndarray]=None, release=None, end=None, end_label: str='recovery', end_is_fix: bool=True, forward_means_xy: Optional[np.ndarray]=None, forward_stds: Optional[np.ndarray]=None, smoothed_stds: Optional[np.ndarray]=None, bathy: Optional[dict]=None, title: str='Reconstructed track', subtitle: Optional[str]=None, receipt: Optional[str]=None, save_to: Optional[str | Path]=None):
    """The signature Anchor track figure.

    ``means_xy`` (N, 2) and ``cov_xy`` (N, 2, 2) are the posterior the
    figure is about (the smoothed one when there is one). ``release`` /
    ``end`` are objects with ``.x``, ``.y`` and optionally ``.sigma_m``.
    ``bathy`` is ``{"depth": 2-D array, "extent": (x0, x1, y0, y1)}``.
    Strips on the right are drawn only for the series that are supplied.
    """
    ...
