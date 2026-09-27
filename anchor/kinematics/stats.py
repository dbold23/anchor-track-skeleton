"""Change-detection and randomization statistics for tag time series.

Two well-established biologging analyses, mirroring the `tagtools`/`animaltags`
toolkit (Mahalanobis change detection and the rotation test), implemented in
pure NumPy so they slot into anchor's kinematics layer:

- :func:`mahalanobis_distance` / :func:`detect_change_points` — flag where a
  multivariate kinematic signature (e.g. dynamic acceleration, pitch, roll)
  departs from a baseline distribution. Useful for unsupervised behaviour-change
  and gear/posture-shift detection without labels.
- :func:`rotation_test` — a circular-rotation randomization test for whether a
  per-sample signal is elevated (or depressed) during a set of events relative
  to chance, preserving each signal's autocorrelation. The standard biologging
  way to ask "is this behaviour really associated with these events?" without the
  i.i.d. assumption that inflates ordinary permutation tests.
"""
from __future__ import annotations
from typing import Optional
import numpy as np

def mahalanobis_distance(X: np.ndarray, ref_mean: Optional[np.ndarray]=None, ref_cov: Optional[np.ndarray]=None, ref_slice: Optional[slice]=None, ridge: float=1e-09) -> np.ndarray:
    """Per-row Mahalanobis distance of ``X`` from a reference distribution.

    ``X`` is ``(n_samples, n_features)``. The reference mean/covariance default to
    the whole series, or to ``ref_slice`` of it (e.g. a known-baseline window), or
    can be supplied directly. A small ``ridge`` stabilizes the covariance inverse.

    Returns the ``(n_samples,)`` distance (already square-rooted). Rows with any
    non-finite feature get a NaN distance and are left out of the reference.
    """
    ...

def detect_change_points(X: np.ndarray, threshold: Optional[float]=None, quantile: float=0.99, min_gap: int=1, ref_slice: Optional[slice]=None) -> dict:
    """Flag samples whose Mahalanobis distance exceeds a threshold.

    ``threshold`` defaults to the ``quantile`` of the reference distances: the
    ``ref_slice`` baseline when given, so only departures from that baseline are
    flagged. Without a baseline the reference is the whole series, which by
    construction flags about ``1 - quantile`` of samples even on pure noise;
    pass ``ref_slice`` or an explicit ``threshold`` for a calibrated detector.
    ``min_gap`` merges detections at most that many samples apart into one
    change point (the index of local-max distance). Returns
    ``{distance, threshold, indices}``.
    """
    ...

def rotation_test(signal: np.ndarray, event_mask: np.ndarray, n_rotations: int=10000, statistic: str='mean', seed: int=0, alternative: str='two-sided') -> dict:
    """Circular-rotation randomization test for event-associated signal levels.

    Asks whether ``signal`` during the events marked by boolean ``event_mask`` is
    higher/lower than chance. The null distribution is built by **circularly
    rotating the event mask** by random offsets — this preserves both the number
    of event samples and the autocorrelation structure of the signal, unlike an
    i.i.d. permutation test (which over-rejects on autocorrelated tag data).

    ``statistic`` is ``"mean"`` (default) or ``"sum"`` of the signal over events.
    ``alternative`` is ``"greater"``, ``"less"``, or ``"two-sided"``. NaN samples
    (tag gaps) are ignored in both the observed and the null statistics.

    Returns ``{observed, p_value, null_mean, null_std, n_rotations}``.
    """
    ...
