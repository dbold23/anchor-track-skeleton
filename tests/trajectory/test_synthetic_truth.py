"""Self-consistency of the known-truth generators in anchor.trajectory.synthetic.

Observations are generated from ``heading`` and ``speed``, and filters are
scored against ``x`` / ``y``. The two must describe the same motion, or a
filter is scored against a track its own inputs cannot produce.
"""
from __future__ import annotations
import numpy as np
from anchor.trajectory.synthetic import simulate_truth, simulate_truth_free_space

class _FlatBathy:

    def lookup_xy(self, x, y):
        ...

def _box(half):
    ...

def _step_residual(truth, dt, current=(0.0, 0.0)):
    ...

def test_polygon_bounces_keep_positions_consistent_with_heading_and_speed():
    """A small box forces many wall contacts. Before the fix the animal stood
    still at each one while its heading and speed said it kept swimming, so dead
    reckoning the truth's own channels left the box."""
    ...

def test_a_current_drifts_the_free_space_ground_track():
    ...

def test_no_current_is_bit_identical_to_the_pinned_generator():
    """The golden smoother numbers are pinned on this output."""
    ...
