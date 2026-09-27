"""Deep-learning behaviour classifier (DeepConvLSTM + self-attention).

Skipped cleanly when the optional ``deep`` extra (PyTorch) is absent.
"""
from __future__ import annotations
import numpy as np
import pytest
from anchor.behavior import deep as D

def test_make_windows_shapes_and_labels():
    ...

def test_make_windows_without_labels():
    ...

def _separable_windows(n_per_class=60, window=32, seed=0):
    """Two classes: low- vs high-amplitude oscillation on a 3-channel window."""
    ...

def test_build_model_forward_shape():
    ...

def test_classifier_learns_separable_classes():
    ...

def test_predict_proba_normalized():
    ...

def test_classifier_handles_string_labels():
    ...
