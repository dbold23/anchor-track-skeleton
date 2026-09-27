"""Integration test: estimate_detachment_position with a synthetic
WindSeries vs without (Gaussian fallback)."""
from __future__ import annotations
import numpy as np
import pandas as pd
import pytest
from anchor.trajectory.detachment import LeewayParams, estimate_detachment_position
from anchor.trajectory.end_anchor import EndAnchor
from anchor.trajectory.wind import WindSeries

class _FakeTrack:
    """Minimal track shape consumed by estimate_detachment_position.

    Needs: depth_m / pitch_rad / etc are NOT touched by the function;
    only t_s, base_hz, t0_utc, utc_at(), __len__ are read.
    """

    def __init__(self, n_steps, dt_s, t0_utc):
        ...

    def __len__(self):
        ...

    def utc_at(self, t_idx):
        ...

def _uniform_wind(t0_utc, t1_utc, u_east, v_north, n_hours=8) -> WindSeries:
    """Constant wind series spanning a comfortable margin around the test
    window so wind_at always interpolates rather than clamps."""
    ...

def test_estimate_detachment_with_wind_shifts_the_anchor_not_the_sigma():
    """5-hour synthetic float window. Compare the back-propagated detach
    anchor under (a) no wind series → Gaussian σ-budget fallback, vs
    (b) constant 5 m/s eastward wind. With wind, the detach anchor must be
    shifted *west* of the recovery point (backward-in-time reversal of
    forward eastward drift), and σ must be **unchanged**: a wind series
    informs the mean drift, never the spread.

    This test used to assert the opposite (``anchor_wind.sigma_m <
    anchor_nowind.sigma_m``), because the wind branch set
    ``sig_total = sig_proc`` and silently dropped the leeway σ budget —
    supplying a wind series made the answer more confident by arithmetic
    rather than by physics. See design §3.5, ``detachment.py:674``.
    """
    ...

def test_zero_wind_series_reproduces_the_no_wind_sigma_budget():
    """A wind series that reads 0 m/s adds no mean drift, so it must
    reproduce the no-wind answer *exactly* — position and σ.

    This is the sharp form of the ``detachment.py:674`` inconsistency: the
    two branches then differ in nothing but ``sig_total``. On the old code
    the wind branch dropped ``sig_wind`` entirely and returned a σ smaller by
    more than an order of magnitude (process noise alone, ~90 m, against the
    ~450 m leeway budget) for a wind field that says the tag was not pushed
    anywhere.
    """
    ...

def test_leeway_params_scalar_reproduces_legacy_path():
    """LeewayParams.scalar(coeff) must produce *identical* results to
    passing the bare float — that's the backward-compat contract."""
    ...

def test_piw_horizontal_inflates_sigma_vs_scalar():
    """The PIW-horizontal default (DWL+CWL+divergence+jibing) should
    inflate σ relative to the scalar-only path. Both run with the same
    seed so the difference is purely the leeway-physics richness."""
    ...

def test_leeway_params_dataclass_immutable():
    """frozen=True so accidental mutation can't sneak in."""
    ...

def test_detach_anchor_sigma_is_per_axis_not_total_spread():
    """``EndAnchor.sigma_m`` is the per-axis σ of an isotropic 2-D Gaussian,
    so ``estimate_detachment_position`` must report sqrt((var_x+var_y)/2),
    not the total 2-D spread sqrt(var_x+var_y).

    Setting ``t_detach_idx = len(track) - 1`` makes the backward advection
    loop empty, so the particle cloud is exactly the recovery prior: an
    isotropic Gaussian with known per-axis σ. The returned anchor's σ must
    equal that per-axis σ; the old convention returned √2 × it.
    """
    ...

def test_detach_anchor_sigma_keeps_20m_floor():
    """The per-axis change must not remove the 20 m floor."""
    ...
