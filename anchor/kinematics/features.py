"""Sliding-window feature extraction for behavior classification.

The core ``summarize_window_metrics`` follows the notebook prototype and is
augmented to emit ODBA, pitch/roll, and depth derivatives so the downstream
GMM has a richer feature vector. ``build_feature_matrix`` + ``standardize`` are
new wrappers for the classifier.
"""
from __future__ import annotations
import logging
from typing import Optional
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from anchor.kinematics.core import DEFAULT_MIN_PERIOD_S, detect_tailbeat_peaks, noise_floor_prominence, tailbeat_frequency_from_peaks
SNR_GATE_FACTOR = 1.0

def summarize_window_metrics(df: pd.DataFrame, fs: float, axis_col: str='accY_dyn', window_s: float=20.0, step_s: float=5.0, time_col: str='t', include_depth: bool=False, smooth_sigma: float=2.0, min_period_s: float=DEFAULT_MIN_PERIOD_S, prominence: Optional[float]=None) -> pd.DataFrame:
    """Sliding-window features across a whole deployment.

    O(n + k) in deployment length: pulls each column into a numpy array once,
    then uses ``np.searchsorted`` on the (sorted) time vector to locate window
    boundaries by integer index. The previous ``df[mask]`` loop was O(n·k) and
    took >12 minutes on the 11 M-row white shark deployment.

    ``prominence`` is the absolute peak-prominence threshold in g, forwarded to
    :func:`~anchor.kinematics.core.detect_tailbeat_peaks` for every window and
    resolved **once for the whole deployment**: the previous code let each
    window recompute a scale-free ``0.5 * std(smoothed)``, so a rest window of
    pure sensor noise reported a tail-beat frequency (~1.26 Hz at
    sigma = 0.003 g). The deployment's tail-beat-band noise floor is measured
    once alongside it and is what the SNR gate is keyed to — see
    :data:`SNR_GATE_FACTOR`.

    Windows with fewer than two detected peaks report ``0.0`` for every
    tail-beat statistic, not NaN, so that "no tail beat" survives into the
    feature matrix instead of being dropped by ``dropna``.
    """
    ...

def build_feature_matrix(metrics: pd.DataFrame, include_depth: bool=False, extra: Optional[list[str]]=None) -> tuple[np.ndarray, list[str]]:
    """Extract a numeric ``(n_windows, n_features)`` matrix from the window table.

    Rows with any NaN in the chosen feature columns are dropped.
    """
    ...

def standardize(X: np.ndarray) -> tuple[np.ndarray, StandardScaler]:
    """Zero-mean unit-variance, preserving the fitted scaler for re-use."""
    ...
