"""Supervised behavior classification on video-labeled feature windows.

The supervised path (W3 in the paper plan) uses CATS onboard-video labels
imported via `anchor.behavior.labels`, projected to feature windows, and fit
with RF or XGBoost wrapped in `CalibratedClassifierCV` (isotonic, cv=5).
"""
from __future__ import annotations
import numpy as np

def fit_supervised(X: np.ndarray, y: np.ndarray, estimator: str='random_forest', calibrate: bool=True, balance: bool=True, random_state: int=0):
    """Supervised behavior classifier on video-labeled feature windows.

    Parameters
    ----------
    X
        Standardized feature matrix, shape (n_windows, n_features).
    y
        Integer or string labels per window (from `labels.labels_to_windows`).
    estimator
        `"random_forest"` (sklearn RF, default) or `"xgboost"`.
    calibrate
        Wrap the estimator in `CalibratedClassifierCV` (isotonic, cv=5) for
        well-calibrated probability outputs.
    balance
        Counter behavior-class imbalance with balanced sample weights
        (inverse class frequency). Applied uniformly across estimators as a
        single mechanism — neither model carries its own ``class_weight`` — so
        rare elasmobranch behaviours (e.g. burst swimming, headshaking) are not
        swamped by abundant cruising. See `anchor.behavior.metrics` for why
        imbalance is the dominant pitfall here (Brewster et al. 2018).
    random_state
        Seed for the base estimator.

    Returns
    -------
    A fitted classifier with `predict` and `predict_proba` methods.
    """
    ...

def _build_base_estimator(estimator: str, random_state: int=0):
    ...
