"""Mahalanobis change-detection + rotation test (tagtools-parity stats)."""
from __future__ import annotations
import numpy as np
import pytest
from anchor.kinematics import stats as S

def test_mahalanobis_zero_at_mean():
    ...

def test_mahalanobis_flags_outlier():
    ...

def test_mahalanobis_accepts_1d():
    ...

def test_detect_change_points_finds_regime_shift():
    ...

def test_rotation_test_detects_real_association():
    ...

def test_rotation_test_null_when_no_association():
    ...

def test_rotation_test_validates_inputs():
    ...

def test_rotation_test_nan_does_not_fake_significance():
    ...

def test_rotation_test_rejects_unknown_statistic():
    ...

def test_mahalanobis_nan_rows_get_nan_distance():
    ...

def test_change_points_calibrated_to_reference():
    ...
