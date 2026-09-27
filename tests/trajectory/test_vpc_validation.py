"""Verified-Position-Correction drift validation."""
from __future__ import annotations
import numpy as np
from anchor.trajectory import vpc_validation
from anchor.trajectory.verified_positions import VerifiedPosition, VerifiedPositionSet

def _vp(t_idx, x, y, label='fix'):
    ...

def test_vp_residuals_zero_for_perfect_track():
    ...

def test_vp_residuals_measures_offset():
    ...

def test_vp_residuals_skips_out_of_range_steps():
    ...

def test_leave_one_out_holds_out_each_interior_fix():
    ...

def test_leave_one_out_empty_when_no_interior():
    ...
