"""Tag-frame -> body-frame mount rotation (design 3.5 row 1, Phase 0 R1).

The last test is the one that pins the *sign*: it drives the forward simulator,
whose mount offset is ground truth, through the real ingest and asserts the
recovered body-pitch bias collapses. Everything above it is algebra.
"""
from __future__ import annotations
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import pytest
from anchor.kinematics.mount import AXES_ROTATION_LIMIT_DEG, apply_mount_rotation, is_body_aligned, mount_rotation, normalize_axes_rotation_deg
SIM_MOUNT_DEG = (5.0, -12.0, 20.0)

def _frame(n: int=64, seed: int=0) -> pd.DataFrame:
    ...

def test_zero_rotation_is_a_no_op_and_does_not_copy():
    ...

def test_round_trip_through_the_inverse_mount():
    """Rotating by a mount and then by its inverse returns the original frame."""
    ...

def test_rotation_preserves_vector_norms_and_leaves_other_columns_alone():
    ...

def test_matches_the_documented_composition():
    """v_body = Rz(yaw) Ry(pitch) Rx(roll) v_tag, applied forward, not inverted."""
    ...

def test_a_frame_without_magnetometer_columns_still_rotates_the_accelerometer():
    ...

def test_a_frame_with_no_vector_columns_warns_rather_than_silently_passing(caplog):
    ...

def test_normalize_accepts_three_finite_bounded_numbers():
    ...

@pytest.mark.parametrize('bad, match', [([1.0, 2.0], '2 value'), ([1.0, 2.0, 3.0, 4.0], '4 value'), ([1.0, float('nan'), 3.0], 'finite'), ([1.0, 2.0, float('inf')], 'finite'), ([0.0, 0.0, 350.0], 'outside'), ([-181.0, 0.0, 0.0], 'outside'), (['a', 0.0, 0.0], 'not a number'), ('0,0,0', 'three numbers')])
def test_normalize_rejects_bad_axes_rotation(bad, match):
    ...

def test_the_limit_is_the_documented_one():
    ...

def _sim_pitch_error(rotation_deg, tmp_path):
    """Body-pitch error (deg) of a slip-free simulated record after *rotation_deg*.

    Generates an AXY-5 CSV with a known mount, runs it through the real ingest,
    the species low-pass and ``add_pitch_roll``, and differences against the
    simulator's own body-pitch label. Returns ``(mean, std)``.
    """
    ...

def test_mount_rotation_collapses_sim_pitch_bias(tmp_path):
    """The mount offset is the pitch bias, and this rotation removes it.

    Ground truth is the simulator's, so this pins the *sign* and the *order* of
    the ZYX composition rather than restating it. Measured, slip disabled,
    seed 7: uncorrected -9.58 +/- 9.75 deg; corrected -0.08 +/- 0.84 deg.
    Inverting the rotation, or dropping the yaw factor, both fail the std bound
    below (-20.3 +/- 18.6 and +0.29 +/- 9.19 respectively).
    """
    ...
