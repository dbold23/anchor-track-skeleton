"""Online corpus K-calibration tests."""
from __future__ import annotations
import numpy as np
import pandas as pd
import pytest
from anchor.validation import online_corpus as OC

def test_compute_k_basic():
    """K = U / (L · TBF) on a known hand-computed value."""
    ...

def test_compute_k_drops_invalid_rows():
    ...

def test_compute_k_array_swim_speed_length_check():
    ...

def test_bootstrap_k_returns_ci():
    ...

def test_bootstrap_k_handles_empty():
    ...

def test_aggregate_corpus_uniform_vs_per_clip():
    """Per-clip weighting reduces influence of one over-long clip."""
    ...

def test_aggregate_corpus_invalid_weight_by_errors():
    ...

def test_online_corpus_entry_dataclass():
    ...
