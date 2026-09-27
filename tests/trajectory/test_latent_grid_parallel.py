"""The latent grid actually runs in parallel when a current field is present.

``latent_grid_workers > 1`` runs one node per worker process, and
``ProcessPoolExecutor`` spawns on macOS, so the whole filter payload is pickled
on the way in. ``resolve_grid_workers`` probes that up front and drops to a
sequential run with a printed reason when it cannot — correct numbers, ~8x the
wall clock on a 25-node grid.

Every deployment that has a current field used to trip that probe, because
``CurrentField.from_tide_series`` carried its temporal driver as a local
closure. These tests pin both halves of the fix: the pool is *used* on a run
with a current field, and using it changes nothing but the wall clock — the
per-node log marginals are bit-identical to the sequential run's, as they must
be for a node that is a pure function of ``(node, seed)``.

The companion unit-level pickle tests live in ``test_currents.py``; this file
is the end-to-end statement, on the same free-space synthetic the rest of the
grid suite uses.
"""
from __future__ import annotations
import numpy as np
import pandas as pd
import pytest
from anchor.ingest.config import TrajectoryConfig
from anchor.trajectory.animate_filter import run_filter_with_snapshots
from anchor.trajectory.axy_ingest import IngestedTrack
from anchor.trajectory.currents import Centerline, CurrentField
from anchor.trajectory.release_anchor import ReleaseAnchor
from anchor.trajectory.synthetic import simulate_observations, simulate_truth_free_space
from anchor.trajectory.tides import synthetic_tide_series
from anchor.trajectory.verified_positions import VerifiedPosition, VerifiedPositionSet
DT = 1.0
N_STEPS = 61
N_FILTER_STEPS = 40
VP_PERIOD = 15
VP_SIGMA_M = 3.0
N_PARTICLES = 60
TEST_PRISM_K_M = 1000.0
DECAY_PROFILE = ((0.0, 1.0), (500.0, 0.4), (5000.0, 0.1))

class _AllWaterPolygon:

    def is_inside(self, x, y, tide_m_mllw=None):
        ...

def _traj(workers: int) -> TrajectoryConfig:
    ...

@pytest.fixture(scope='module')
def deployment():
    """Free-space truth + a synthetic tide-driven current field over it.

    The centerline is a straight synthetic polyline through the truth track's
    own frame, so no gitignored geospatial fixture is needed and the decay
    profile above is the only spatial structure in play.
    """
    ...

def _run(deployment, workers: int) -> dict:
    ...

def test_a_current_field_no_longer_forces_the_grid_sequential(deployment):
    """The regression: with the temporal driver as a closure this run reported
    ``workers == 1`` and a "cannot be pickled" note on every deployment that
    had a current field — which is every real one."""
    ...

def test_pooled_and_sequential_grids_agree_on_every_node(deployment):
    """The pool is a scheduling detail. A node is a pure function of
    ``(node, seed)``, so the marginals — and the posterior built from them —
    must match bit for bit, not merely to tolerance."""
    ...
