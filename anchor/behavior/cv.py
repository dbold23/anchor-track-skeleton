"""Subject-level cross-validation for behavior classifiers.

Wilson et al. 2025 (J Anim Ecol) shows that 79% of accelerometer-based behavior
classification studies use within-subject or window-level splits, which leak
subject-specific signal into test folds and overstate accuracy. This module
provides the split types that survive that critique:

- ``leave_one_subject_out`` — one held-out subject per fold; all others train.
- ``subject_stratified_kfold`` — k folds, subjects never split across folds.

The helpers operate on a 1-D ``subjects`` array parallel to the pooled feature
matrix (one label per window); pool features with ``load_pooled_features``.
"""
from __future__ import annotations
from pathlib import Path
from typing import Iterable, Iterator, Optional
import numpy as np
import pandas as pd
from anchor.kinematics import features as F
from anchor.ingest import io

def load_pooled_features(deployment_ids: Iterable[str], features_dir: str | Path='data/features', include_depth: bool=False) -> tuple[np.ndarray, np.ndarray, list[str], pd.DataFrame]:
    """Concatenate feature matrices across deployments.

    Returns:
        X: (n_windows_total, n_features) pooled feature matrix after dropna.
        subjects: (n_windows_total,) array of deployment_id strings per row.
        feature_names: column names of X.
        meta: the pooled metrics DataFrame (pre-dropna rows included, with a
              ``subject`` column) so callers can look up timestamps etc.
    """
    ...

def load_labeled_features(deployment_ids: Iterable[str], features_dir: str | Path='data/features', label_col: str='label', include_depth: bool=False, min_confidence: float=0.0, confidence_col: str='label_confidence') -> tuple[np.ndarray, np.ndarray, np.ndarray, list[str]]:
    """Pool *labeled* feature windows across deployments for supervised eval.

    Keeps only rows with a non-null ``label_col`` (and ``confidence_col`` >=
    ``min_confidence`` when that column is present), then builds the feature
    matrix on exactly those rows so ``X``, ``y``, and ``subjects`` stay aligned
    through the same NaN-feature drop that :func:`build_feature_matrix` applies.

    Returns ``(X, y, subjects, feature_names)`` with one row per labeled window.
    """
    ...

def leave_one_subject_out(subjects: np.ndarray) -> Iterator[tuple[np.ndarray, np.ndarray, str]]:
    """Yield (train_idx, test_idx, holdout_subject) for each unique subject."""
    ...

def subject_stratified_kfold(subjects: np.ndarray, k: int, random_state: int=0) -> Iterator[tuple[np.ndarray, np.ndarray, list[str]]]:
    """k folds where subjects never split across folds.

    If ``k`` exceeds the subject count, falls back to LOSO.
    """
    ...

def aggregate_fold_metrics(results: list[dict]) -> dict:
    """Collapse per-fold metric dicts into mean/std across folds.

    Each fold dict is expected to contain scalar metrics under the same keys.
    Non-numeric values (e.g., the subject identifier) are preserved as a list.
    """
    ...

def evaluate_supervised_loso(X: np.ndarray, y: np.ndarray, subjects: np.ndarray, estimator: str='random_forest', calibrate: bool=False, balance: bool=True, random_state: int=0, label_names: Optional[dict]=None) -> dict:
    """Leave-one-subject-out evaluation of a supervised behavior classifier.

    For each held-out subject: standardize on the training subjects only (the
    scaler is fit on train and applied to test, so there is no leakage), fit
    ``fit_supervised`` on the rest, predict the held-out windows, and score with
    :func:`anchor.behavior.metrics.classification_metrics`. This is the driver
    that turns the LOSO splitter + the per-class metrics into the headline
    rigor check the paper needs (subject-level CV, per-class F1, balanced
    accuracy) — guarding against the pseudo-replication that random-row CV hides.

    ``calibrate`` defaults to False here: the isotonic ``CalibratedClassifierCV``
    runs an inner cv=5 that is fragile when a held-out fold leaves a class with
    <5 training samples, and evaluation cares about discrimination, not the
    probability calibration used at deployment time.

    Returns ``{"folds": [...], "aggregate": {...}, "pooled": {...}}`` where
    ``folds`` is per-subject flat metrics, ``aggregate`` is mean/std across
    folds, and ``pooled`` is :func:`classification_metrics` over all held-out
    predictions concatenated (the matrix to report).
    """
    ...
