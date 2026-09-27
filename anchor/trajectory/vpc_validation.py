"""Verified-Position-Correction validation — how far is the track from truth?

Two complementary diagnostics for a VP-anchored reconstruction:

- :func:`vp_residuals` — *fit* residuals: distance between the reconstructed
  position and each Verified Position used to constrain it. Near-zero by
  construction at tight-σ fixes; useful as a sanity check and to show the filter
  honoured its anchors.

- :func:`leave_one_out_drift` — *held-out* error: drop one interior VP, rerun
  the reconstruction without it, and measure how far the unconstrained track
  drifts from the held-out fix. This is the honest accuracy estimate (Dewhirst
  et al. 2016 reported 2D-RMS error vs fix density this way) and the figure
  reviewers expect for a dead-reckoning method.

Both return per-VP rows plus a summary with RMSE / median / max / P90 (m).
"""
from __future__ import annotations
from typing import Callable
import numpy as np

def _summary(errors: np.ndarray) -> dict:
    ...

def vp_residuals(means: np.ndarray, verified_positions) -> dict:
    """Distance between the reconstructed mean position and each fix it used.

    Parameters
    ----------
    means
        ``(n_steps, 2)`` reconstructed mean (x, y) per step, in the VPs' CRS.
    verified_positions
        A :class:`~anchor.trajectory.verified_positions.VerifiedPositionSet`.

    Returns
    -------
    dict with ``per_vp`` (list of {t_idx, label, sigma_m, error_m}) and a
    flattened summary (``rmse_m``, ``median_m``, ``max_m``, ``p90_m``, ``n``).
    """
    ...

def leave_one_out_drift(verified_positions, reconstruct_fn: Callable, n_steps: int) -> dict:
    """Held-out drift error via leave-one-Verified-Position-out.

    For each *interior* VP (excludes the t=0 release and the terminal step),
    rebuild the reconstruction with that fix removed and measure the distance
    between the held-out fix and the reconstructed mean position at its time.

    Parameters
    ----------
    verified_positions
        The full :class:`VerifiedPositionSet` (release + interior + end).
    reconstruct_fn
        Callable ``(held_out_set) -> means`` returning an ``(n_steps, 2)`` array
        of reconstructed mean positions when run with the reduced VP set. The
        caller supplies this so the validator stays decoupled from the (heavy)
        particle-filter driver.
    n_steps
        Track length, used to identify interior fixes.

    Returns
    -------
    dict with ``per_vp`` (list of {t_idx, label, sigma_m, error_m}) and a
    flattened summary. Empty (NaN summary) when there are no interior fixes.
    """
    ...
