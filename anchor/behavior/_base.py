"""Shared types and persistence for the behavior subpackage.

`FittedClassifier` is the unified dataclass produced by both unsupervised
(`hmm.fit_*`) and supervised (`supervised.fit_supervised`) paths so downstream
consumers (CLI, plot helpers, parquet writers) are method-agnostic.
"""
from __future__ import annotations
import pickle
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
import numpy as np
import pandas as pd

@dataclass
class FittedClassifier:
    model: object
    feature_names: list[str]
    scaler: object

def save_model(fitted: FittedClassifier, path: str | Path) -> None:
    ...

def load_model(path: str | Path) -> FittedClassifier:
    ...

def predict_from_features(fitted: FittedClassifier, features_df: pd.DataFrame, time_col: Optional[str]=None) -> pd.DataFrame:
    """Apply a saved classifier to a new feature DataFrame.

    Re-uses the model's stored feature_names + scaler so the new data is
    projected into the same standardized space the model trained on. This
    is the bridge that lets us run an AXY-trained HMM against CATS-derived
    features (or vice versa) for paired-tag cross-validation.

    Returns a DataFrame with columns ``t``, ``state`` (int), ``state_label``
    (str, if label_map is set), and ``state_prob_*`` (one column per
    HMM/GMM component when supported by the model).
    """
    ...
