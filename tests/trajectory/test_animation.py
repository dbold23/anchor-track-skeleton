"""Ancestry tracking sanity tests for the anchor ParticleFilter.

The animation in ``anchor.track.animate_filter`` plots `n_unique_founders`
per snapshot. Resampling can only kill founder lineages — never create them —
so the unique-founder count must be monotonically non-increasing across all
snapshots. If it ever goes up, ancestry tracking is buggy.
"""
from __future__ import annotations
import numpy as np
import pandas as pd
import pyproj
import rasterio
from anchor.trajectory.bathymetry import BathyLookup
from anchor.trajectory.particle_filter import FilterConfig, ParticleFilter

def _trivial_bathy() -> BathyLookup:
    ...

def test_ancestry_initialized_to_arange():
    ...

def test_ancestry_monotonic_non_increasing_across_snapshots():
    ...

def test_ancestry_unchanged_when_no_resample():
    ...

class _AllWaterPolygon:
    """Polygon constraint that accepts everything."""

    def is_inside(self, x, y, tide_m_mllw=None):
        ...

class _NoWaterPolygon:
    """Polygon constraint that rejects everything — forces weight collapse."""

    def is_inside(self, x, y, tide_m_mllw=None):
        ...

def _stub_track(n: int=24, t0_utc=None):
    ...

def _run_stub_filter(polygon, traj=None, n_particles=100, current_field=None):
    ...

def test_filter_state_exports_collapse_diagnostics():
    ...

def test_filter_state_exports_the_degeneracy_record():
    """The §3.7 G-degeneracy scalars ride out with the filter state: without
    them the report could quote a credible interval from a one-founder cloud,
    which is what the flagship run did."""
    ...

def test_degeneracy_fails_and_warns_when_the_cloud_collapses(caplog):
    """A polygon that rejects everything drives every floor through the
    floor; the gate must say so rather than leave it to a figure caption.

    ``ess_min`` is deliberately *not* asserted here. Under the finite
    ``polygon_penalty_nats`` the penalty is a constant added to every
    log-weight, so the normalised weights — and the ESS — are the ones the
    cloud already had; the floor is silent and rightly so. The all-outside
    signal it used to carry now travels as ``n_polygon_all_rejected``, which
    is asserted below. The hard mode keeps the old ESS behaviour and is
    pinned in ``test_the_hard_polygon_mode_still_breaches_the_ess_floor``.
    """
    ...

def test_the_hard_polygon_mode_still_breaches_the_ess_floor(caplog):
    """``polygon_penalty_nats=None`` is the pre-2026-09 constraint, and the
    -inf path keeps its coverage: every weight is -inf, the filter resets to
    uniform, ESS is recorded as 0 and the §3.7 floor breaches."""
    ...

def test_step_zero_weights_are_scored_before_the_release_anchor_is_resampled():
    """Step 0 carries the release anchor and the polygon, then is resampled
    flat. Scoring after that resample would record a vacuous ESS = N on the
    one step whose weights are most informative."""
    ...

def test_a_polygon_that_rejects_everything_is_charged_not_reset(caplog):
    """Under the default finite penalty there is no collapse to recover from.

    Every log-weight is shifted by the same constant, so the cloud keeps its
    weighting, the uniform reset does not fire and the step is *scored*: the
    marginal moves by one penalty instead of contributing 0
    (``docs/regen_2026-09.md`` §12.4). The trace the reset used to leave is
    replaced by the penalised-step record, which is what the report reads.
    """
    ...

def test_collapsed_steps_flags_a_polygon_that_rejects_everything(caplog):
    """The reset-to-uniform recovery used to leave no trace at all.

    Reachable now only in the hard mode, which is where the reset belongs:
    ``-inf`` really is unrecoverable. Keeping the coverage keeps
    ``collapsed_steps`` and ``n_collapses`` honest for it.
    """
    ...

def test_bathymetry_mode_and_off_bottom_factor_flow_from_trajectory_config(monkeypatch):
    """The two fields reach FilterConfig via the ``_t`` shim, defaults intact."""
    ...

class _GradientCurrentField:
    """Stub current field whose uv varies across the particle cloud.

    A constant field would let a wrong reduction (first particle, median,
    whatever) pass by accident, so ``u`` carries an x-gradient. Every call
    records the cloud mean of exactly the array handed to ``predict``, which is
    what ``current_uv_at_step`` is supposed to hold.
    """

    def __init__(self):
        ...

    def uv_at(self, x, y, t_utc):
        ...

def test_current_uv_at_step_is_the_cloud_mean_actually_applied():
    """``current_uv_at_step`` is the sole input to the smoother's current
    integration, so it must equal the mean of the per-particle uv that
    ``predict`` consumed — not a constant, not the field sampled elsewhere."""
    ...
