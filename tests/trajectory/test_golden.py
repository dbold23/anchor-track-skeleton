"""Golden-number tests for the FFBS smoother, pinned on a free-space synthetic.

These run anywhere: :func:`simulate_truth_free_space` needs no raster and no
polygon, so unlike the rest of ``tests/trajectory`` nothing here skips on a
clean checkout.

The headline defect these pin is the **FFBS stride bug**. The forward filter
runs at every step but snapshots every ``--snapshot-stride`` steps (default 6).
The smoother hops snapshot-to-snapshot, so its backward kernel has to describe
a whole stride-6 interval. Before the fix it was handed the per-step ``dt`` and
the heading/speed sampled *at* the snapshot, so the predicted displacement was
1/6 of reality and the kernel variance was 1/6 of reality. Numbers recorded on
this fixture, comparing stride-6 smoothing against stride-1 smoothing over the
same forward particles:

===========================  =============  ==============
quantity                     old code       fixed code
===========================  =============  ==============
mean |Δ| vs stride-1 track     20.5 m          1.29 m
max  |Δ| vs stride-1 track     28.6 m          2.54 m
RMSE vs known truth            22.3 m          4.06 m
===========================  =============  ==============

so the tolerances below (5 m mean, 8 m RMSE) pass on the fixed code and fail by
a wide margin on the old code. ``test_stride1_kernel_is_unchanged`` is the
regression anchor in the other direction: at stride 1, and with no current
field, the stride-integrated kernel must reproduce the old per-step kernel
*exactly*. With a current field it deliberately does not: the old kernel
omitted current advection entirely, so integrating it changes the smoothed
track at every stride, stride 1 included.
"""
from __future__ import annotations
import numpy as np
import pytest
from anchor.trajectory.particle_filter import SSCALE, STATE_DIM, FilterConfig, ParticleFilter, ffbs_smoother, integrate_snapshot_intervals
from anchor.trajectory.synthetic import simulate_observations, simulate_truth_free_space
DT = 1.0
N_STEPS = 601
STRIDE = 6
TRUE_SCALE = 1.1
N_SMOOTH = 60

@pytest.fixture(scope='module')
def forward_run():
    """One forward filter run, snapshotting *every* step.

    Snapshot stride is a property of what the caller keeps, not of the filter,
    so subsampling this single history gives stride-1 and stride-6 smoother
    inputs that share identical forward particles. That isolates the smoother
    kernel as the only difference between the two.
    """
    ...

def _smooth(forward_run, steps, *, integrated):
    """FFBS over the given snapshot grid, with or without stride integration."""
    ...

def _mean_track(samples):
    ...

def test_stride1_kernel_is_unchanged(forward_run):
    """At stride 1, with no current, the integrated kernel reproduces the old one.

    ``ffbs_smoother`` returns copies of actual forward particles, so identical
    ancestor choices mean bit-identical output. The rotation identity
    ``s·(cos b·Sx + sin b·Sy) == s·u·dt·sin(ψ + b)`` differs only in
    floating-point rounding, far below anything that can flip a sampled index.

    This fixture has no current field, so the integrated current is zero. Where
    one is present the two kernels differ by construction at any stride, the
    old one having no current term at all.
    """
    ...

def test_stride6_agrees_with_stride1(forward_run):
    """Stride-6 smoothing must track stride-1 smoothing. Old code: 20.5 m."""
    ...

def test_stride6_smoothed_track_recovers_truth(forward_run):
    """Smoothed mean track and end position vs known truth. Old RMSE: 22.3 m."""
    ...

def test_golden_numbers(forward_run):
    """Tight pins so a refactor that moves the arithmetic is caught.

    Everything here is deterministic: seeded ``default_rng`` in the truth,
    the observations, the filter and the smoother.
    """
    ...

def test_integrate_snapshot_intervals_matches_the_forward_filter():
    """The interval integral must equal what ``predict`` actually accumulates.

    Direct check of the factorization the smoother relies on: for a constant
    bias/scale, stepping the forward model six times and rotating the
    integrated displacement once must land in the same place.
    """
    ...

def _kernel_probe(particle_xy, endpoint, current_disp):
    """One backward-sampling step over a hand-placed particle cloud.

    The candidate ancestors sit 100 m apart, the endpoint is fixed, the
    interval's heading/speed displacement is zero and the kernel sigma is 1 m,
    so the kernel is effectively one-hot: the ancestor drawn is whichever one's
    *predicted* position lands on the endpoint. That makes the integrated
    current directly observable — shifting the prediction by ``current_disp``
    moves the pick by a whole 100 m, with no statistics in the way.

    Returns the smoothed t=0 position.
    """
    ...

@pytest.mark.parametrize('axis, particles, endpoint, current_disp, without_current, with_current', [('x', [(0.0, 0.0), (100.0, 0.0), (200.0, 0.0)], (100.0, 0.0), (100.0, 0.0), (100.0, 0.0), (0.0, 0.0)), ('y', [(0.0, 0.0), (0.0, 100.0), (0.0, 200.0)], (0.0, 100.0), (0.0, 100.0), (0.0, 100.0), (0.0, 0.0))])
def test_backward_kernel_applies_the_integrated_current(axis, particles, endpoint, current_disp, without_current, with_current):
    """The kernel must advect its prediction by the interval's current.

    This is the one part of the stride fix that moves numbers on the *default*
    production path (``--current-source`` defaults to ``tide-derivative``), so
    it gets an exact, hand-computed check rather than a tolerance. Dropping
    either ``+ cur_x`` or ``+ cur_y`` from the kernel makes the with-current
    case pick the same ancestor as the without-current case, and this fails.
    """
    ...

def test_current_displacements_move_the_smoothed_track(forward_run):
    """End to end: a current field is not silently dropped by the smoother.

    The probe above pins the kernel arithmetic; this pins that the argument
    still reaches it through the real fixture. A 0.15 m/s current over stride-6
    intervals is a 0.9 m nudge per hop, which the smoother compounds backwards
    from the fixed endpoint into a track-wide shift.
    """
    ...
