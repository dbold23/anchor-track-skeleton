"""Block-downsampling helpers must tolerate a block with no finite sample.

``np.nanmean`` emits ``RuntimeWarning: Mean of empty slice`` for an all-NaN
row. ``pyproject.toml`` sets ``filterwarnings = error``, so before the fix any
deployment whose leading second carried no valid heading/speed/tailbeat sample
aborted the ingest outright. Three real-data tests hit exactly that once the
deploy windows moved (first finite ``tb_freq_inst`` is sample 19 untrimmed and
271 on the trimmed parquet, so the first 25-sample block is empty).

These tests need no config, no data and no window: they exercise the helpers
directly and fail on the pre-fix code with ``RuntimeWarning: Mean of empty
slice``.
"""
from __future__ import annotations
import warnings
import numpy as np
import pytest
from anchor.trajectory.axy_ingest import _block_mean, _circular_mean_blocks, _nanmean_rows

@pytest.fixture
def leading_empty_block() -> np.ndarray:
    """50 samples whose first 25-sample block is entirely NaN."""
    ...

def test_block_mean_empty_leading_block_is_nan_not_a_warning(leading_empty_block):
    ...

def test_circular_mean_blocks_empty_leading_block_is_nan_not_a_warning(leading_empty_block):
    ...

def test_partial_block_still_averages_the_finite_samples():
    ...

def test_nanmean_rows_matches_nanmean_wherever_nanmean_is_defined():
    ...
