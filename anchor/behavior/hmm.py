"""Unsupervised behavior classification: GMM + HMM.

Gaussian Mixture (`fit_gmm`) and Hidden Markov Model (`fit_hmm`) share a
unified dispatch via `fit_model(method, X, k)` and expose the same
`predict_proba` / `score_log_likelihood` / `means_` API downstream. GMM stays
available for quick unsupervised baselines; HMM adds temporal smoothing and is
the default going forward (Leos-Barajas 2017).
"""
from __future__ import annotations
import warnings
from typing import Optional
import numpy as np
from sklearn.mixture import GaussianMixture

def fit_gmm(X: np.ndarray, k: int=4, random_state: int=0) -> GaussianMixture:
    """Full-covariance Gaussian Mixture on standardized features."""
    ...

def fit_hmm(X: np.ndarray, k: int=4, random_state: int=0):
    """Full-covariance Gaussian HMM on standardized features.

    Markov transitions smooth state sequences over time (Leos-Barajas 2017).
    Emission means and covariances are warm-started from a GMM fit to avoid
    the degenerate initializations hmmlearn's random init produces on
    well-separated data. Emits a RuntimeWarning if EM does not converge.
    """
    ...

def fit_model(method: str, X: np.ndarray, k: int=4, random_state: int=0):
    """Dispatch on classifier method; returns a fitted sklearn/hmmlearn model."""
    ...

def predict_states(model, X: np.ndarray) -> np.ndarray:
    """Most-likely per-window state. GMM: argmax posterior. HMM: Viterbi path."""
    ...

def predict_proba(model, X: np.ndarray) -> np.ndarray:
    """Per-window posterior probabilities, shape (n_windows, k)."""
    ...

def score_log_likelihood(model, X: np.ndarray) -> float:
    """Per-sample average log-likelihood (sign-consistent across GMM and HMM)."""
    ...

def label_clusters_post_hoc(centroids: np.ndarray, feature_names: list[str], hint: Optional[list[str]]=None) -> dict[int, str]:
    """Order clusters by activity level and assign the hint labels.

    Activity score = z(vedba_mean) + z(jerk_mean) + z(tb_freq_mean).
    Lowest score, first label (typically "rest"); highest, last ("burst").
    """
    ...
