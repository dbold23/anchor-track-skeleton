"""Subject-level cross-validation splitters."""
from __future__ import annotations
import numpy as np
import pandas as pd
import pytest
from anchor.behavior import cv

def _subjects(spec: dict[str, int]) -> np.ndarray:
    """spec={'A': 3, 'B': 2} -> array(['A','A','A','B','B'])."""
    ...

def test_loso_yields_one_fold_per_subject():
    ...

def test_loso_partitions_indices():
    ...

def test_loso_requires_two_subjects():
    ...

def test_stratified_kfold_keeps_subjects_intact():
    ...

def test_stratified_kfold_falls_back_to_loso_when_k_too_big():
    ...

def test_aggregate_fold_metrics():
    ...

def test_aggregate_empty():
    ...

def test_load_pooled_features(tmp_path, monkeypatch):
    """Two synthetic per-deployment features parquets pool correctly."""
    ...
from anchor.kinematics import features as F

def _mk_labeled(features_dir, dep_id, labels, seed):
    """Write a per-deployment feature parquet with a ``label`` column.

    ``labels`` is a list with one entry per window; use ``None`` for unlabeled.
    Feature columns are signal-separated by label so a classifier can learn.
    """
    ...

def test_load_labeled_features_drops_unlabeled_and_aligns(tmp_path):
    ...

def test_load_labeled_features_min_confidence(tmp_path):
    ...

def test_evaluate_supervised_loso_structure_and_separable():
    ...

def test_evaluate_supervised_loso_handles_imbalance():
    ...

def test_stratified_kfold_rejects_k_below_two():
    ...

def test_aggregate_skips_undefined_fold_metrics():
    ...
