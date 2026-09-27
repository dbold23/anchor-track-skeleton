"""The depth likelihood's tide term: bed(MLLW) + eta(t), not bed(MLLW).

The raster gives the bed's depth below MLLW; the tag's pressure record gives a
depth below the *instantaneous* water surface. Comparing the two directly is
wrong by eta(t), and at Elkhorn eta runs +0.28 to +1.6 m over the flagship
record, so a legal position over an intertidal flat was charged as a violation
of up to 1.6 m (``docs/regen_2026-09.md`` sections 21.2 and 21.7). The water
polygon has always drawn its wet mask at ``bed + eta``; these tests pin the
depth likelihood to the same datum, and pin the switch that reproduces the old
arithmetic exactly.
"""
from __future__ import annotations
from types import SimpleNamespace
import numpy as np
import pandas as pd
import pyproj
import pytest
import rasterio
from anchor.trajectory import run_deployment as RD
from anchor.trajectory.animate_filter import run_filter_with_snapshots
from anchor.trajectory.bathymetry import BathyLookup
from anchor.trajectory.particle_filter import FilterConfig, ParticleFilter
from anchor.trajectory.release_anchor import ReleaseAnchor

def _logpdf(bathy, observed, **kw):
    ...

@pytest.mark.parametrize('mode', ['one_sided', 'bottom_following'])
def test_no_tide_reproduces_the_mllw_comparison_bit_for_bit(simple_bathy, mode):
    """eta = 0, and None, are the function this method was before the term.

    Bit-for-bit, not to a tolerance: the implementation skips the addition
    rather than adding a zero, which is what lets the ``off`` knob be a golden
    reproduction rather than an approximation of one.
    """
    ...

def test_one_sided_charges_the_residual_against_the_tide_corrected_bed(simple_bathy):
    """Seafloor 10 m below MLLW, sigma 0.3 m, extra sigma 0.0.

    The raster is float32, so the arithmetic is checked to a relative 1e-6
    rather than exactly; the exact claim this file makes is the one in
    :func:`test_no_tide_reproduces_the_mllw_comparison_bit_for_bit`.
    """
    ...

def test_bottom_following_centres_on_a_fraction_of_the_water_column(simple_bathy):
    """The factor multiplies the tide term, because it is a fraction of the
    *local water depth* and the local water depth is bed + eta.

    At f = 0.85 over a 10 m bed under 2 m of tide the model expects the animal
    at 0.85 * 12 = 10.2 m, not at 0.85 * 10 + 2 = 10.5 m.
    """
    ...

def test_the_two_conventions_agree_at_factor_one(simple_bathy):
    """``f * (bed + eta)`` and ``f * bed + eta`` coincide at f = 1, which is
    why the shipped default is unaffected by the choice argued above.

    Both put the density's peak at 11.7 m over a 10 m bed under 1.7 m of tide,
    so the peak's value is the bare normaliser.
    """
    ...

def _flat_bathy(bed_m: float) -> BathyLookup:
    """An intertidal flat: ``bed_m`` below MLLW, well surveyed."""
    ...

def test_a_particle_over_a_flat_at_high_tide_is_no_longer_charged():
    """Section 21.2's case, in miniature: a tag at 1.2 m over a 0.5 m (MLLW)
    flat carrying 1.0 m of tide is legal, and used to be charged 0.7 m."""
    ...

class _SpyBathy:
    """Records the tide the filter hands the likelihood."""

    def __init__(self):
        ...

    def bathymetry_violation_logpdf(self, observed_depth, x, y, **kw):
        ...

def _pf(bathy, **cfg_kw):
    ...

def test_the_tide_term_is_on_by_default_in_the_filter_config():
    ...

def test_update_bathymetry_forwards_the_tide():
    ...

def test_the_knob_off_discards_a_tide_that_is_supplied():
    ...

class _AllWaterPolygon:

    def is_inside(self, x, y, tide_m_mllw=None):
        ...

class _StubTide:
    """A tide that rises 0.1 m per step, so no two steps share an eta."""

    def __init__(self, t0):
        ...

    def value_at(self, t_utc):
        ...

def _stub_track(n=24, depth_m=6.0, t0_utc=None):
    ...

def _run(traj=None, tide=True, seed=0):
    ...

def test_the_driver_hands_the_depth_likelihood_the_step_tide(monkeypatch):
    ...

def test_without_a_tide_series_the_term_is_inert_and_the_state_says_so():
    ...

def _traj(**kw):
    ...

def test_the_knob_off_reproduces_the_mllw_run_and_on_does_not():
    """``off`` is deaf to the tide series; ``on`` is not.

    The likelihood is the only place eta reaches the depth channel, so a run
    that cannot hear the tide is the pre-term run. Doubling the tide series
    leaves ``off`` bit-identical and moves ``on``, which pins the switch from
    both sides. The flagship's golden number is in
    ``reports/regen_2026-09/section22/sections/code_t2.md``.
    """
    ...

def test_an_unset_tide_term_is_dropped_from_the_dump_so_old_hashes_hold():
    ...

@pytest.mark.parametrize('word,expected', [('on', True), ('off', False)])
def test_the_flag_overrides_the_field(word, expected):
    ...

def test_no_flag_leaves_the_field_alone():
    ...

def _effective(cfg, args):
    ...

def _diag_state(**kw):
    ...

def _diag_notes(**kw):
    ...

def test_the_report_names_the_comparison_that_was_used():
    ...

def test_the_card_stamps_which_comparison_ran():
    """The knob's null is dropped from the effective ``config_hash``, so the
    card must say in its own right which comparison the run made.

    Without this stamp a tide-corrected run and an MLLW run of the same
    deployment card an identical fingerprint while differing by ~1230 nats on
    the flagship (``docs/regen_2026-09.md`` sections 14.16, 22.5.4).
    """
    ...

def test_lon_lat_wrapper_forwards_the_tide(simple_bathy):
    """``BathyLookup.log_likelihood`` is public API on the same class; it must
    not be able to drift away from the method the filter calls."""
    ...

def test_the_sibling_filter_loops_pass_the_tide():
    """``two_filter`` and ``elkhorn_demo`` run the same depth likelihood as the
    driver; a backward pass at MLLW under a forward pass at ``bed + eta`` would
    be a silent disagreement inside one smoothed track."""
    ...
