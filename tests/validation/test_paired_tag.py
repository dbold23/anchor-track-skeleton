"""Paired CATS+AXY harmonization tests."""
from __future__ import annotations
import numpy as np
import pandas as pd
import pytest
from anchor.validation import paired_tag as PT

def test_align_clocks_xcorr_recovers_known_offset():
    """Two tags observing the same physical signal but with shifted local clocks
    must yield a peak at the true offset.

    Setup: a master signal exists in absolute physical time. CATS records
    physical t ∈ [0, 100]; AXY records physical t ∈ [true_offset, 100 + true_offset].
    Each tag reports its samples with its own clock starting at zero, so the
    same physical event has cats_t = axy_t + true_offset → CATS clock is
    "ahead" of AXY by true_offset seconds.
    """
    ...

def test_harmonize_to_rate_downsamples():
    """50 Hz CATS → 25 Hz AXY-rate via anti-aliased decimation."""
    ...

def test_cross_tag_agreement_perfect_when_identical():
    """Identical state series → kappa = 1, accuracy = 1."""
    ...

def test_cross_tag_agreement_handles_disagreement():
    """Mostly-agree should give κ near 1 but accuracy < 1."""
    ...

def test_cross_tag_agreement_length_mismatch_errors():
    ...

def test_cross_tag_agreement_drops_nan():
    ...

def test_align_clocks_xcorr_uses_start_times():
    """Tags whose records start at different clock readings: the offset must
    include the start-time difference, not just the correlation lag."""
    ...
