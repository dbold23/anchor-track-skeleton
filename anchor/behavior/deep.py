"""Deep-learning behaviour classifier (DeepConvLSTM + self-attention).

State-of-the-art accelerometer behaviour classification is shifting from
handcrafted-feature gradient boosting to deep models on *raw* tri-axial
acceleration: a DeepConvLSTM with multi-head self-attention (four conv layers →
LSTM → attention → head) outperformed LightGBM/XGBoost on 119 features in
seabirds (Otsuka et al. 2024, *Methods Ecol Evol*). That has **not** been
demonstrated on elasmobranchs — so this module is both a feature and a
testbed for a publishable result: run it head-to-head against
``fit_supervised`` under the same subject-level LOSO protocol.

Optional: requires the ``deep`` extra (``pip install -e .[deep]`` → PyTorch).
Imported lazily; the rest of anchor never depends on torch.

Data contract: raw windowed acceleration ``X`` of shape
``(n_windows, n_channels, window_len)`` (e.g. ``accX_dyn/accY_dyn/accZ_dyn``).
Use :func:`make_windows` to build it from a processed time series. The classifier
exposes the sklearn-style ``fit`` / ``predict`` / ``predict_proba`` surface so it
drops into the same evaluation harness as the shallow models.
"""
from __future__ import annotations
from typing import Optional
import numpy as np

def make_windows(signal: np.ndarray, window: int, step: int, labels: Optional[np.ndarray]=None):
    """Slice a ``(time, channels)`` series into ``(n_windows, channels, window)``.

    With per-sample ``labels``, each window gets a majority-vote label and the
    function returns ``(windows, window_labels)``; otherwise just ``windows``.
    """
    ...

def _torch():
    ...

def build_model(n_channels: int, n_classes: int, conv_filters: int=32, kernel: int=5, lstm_hidden: int=64, attention: bool=True):
    """Construct the DeepConvLSTM(+attention) ``nn.Module`` (see module docstring)."""
    ...

class DeepConvLSTMClassifier:
    """sklearn-style wrapper around the DeepConvLSTM model.

    ``fit(X, y)`` / ``predict(X)`` / ``predict_proba(X)`` with ``X`` of shape
    ``(n_windows, n_channels, window_len)``. Labels may be ints or strings.
    """

    def __init__(self, conv_filters: int=32, lstm_hidden: int=64, attention: bool=True, epochs: int=30, lr: float=0.001, batch_size: int=64, weight_decay: float=0.0001, balance: bool=True, seed: int=0, device: str='cpu'):
        ...

    def fit(self, X, y):
        ...

    def _logits(self, X):
        ...

    def predict_proba(self, X):
        ...

    def predict(self, X):
        ...
