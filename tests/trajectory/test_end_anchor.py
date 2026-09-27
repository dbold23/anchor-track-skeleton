"""Contract tests for the position-anchor log-likelihoods.

``sigma_m`` on ``EndAnchor`` / ``ReleaseAnchor`` is the PER-AXIS σ of an
isotropic 2-D Gaussian, and the log-likelihood carries the 2-D normaliser
``-log(2*pi*sigma**2)``. Both matter when anchors with different σ are
compared against each other.
"""
from __future__ import annotations
import numpy as np
import pytest
from anchor.trajectory.end_anchor import EndAnchor
from anchor.trajectory.release_anchor import ReleaseAnchor

@pytest.mark.parametrize('cls', ANCHORS)
def test_one_sigma_per_axis_offset_costs_half(cls):
    """A 1σ offset on a single axis must cost exactly 0.5 nats relative to
    the peak — that is what "per-axis σ" means."""
    ...

@pytest.mark.parametrize('cls', ANCHORS)
def test_normaliser_is_two_dimensional(cls):
    """Peak log-density must be ``-log(2*pi*sigma**2)``, the 2-D isotropic
    Gaussian normaliser — not the 1-D ``-log(sigma*sqrt(2*pi))``."""
    ...

@pytest.mark.parametrize('cls', ANCHORS)
def test_density_integrates_to_one(cls):
    """Riemann-integrating exp(log_likelihood) over the plane gives 1."""
    ...
from anchor.trajectory.end_anchor import AUTO_MAX_SURFACE_MINUTES, DEFAULT_BOTTOM_CREEP_SIGMA_M, grounded_end_anchor, resolve_end_anchor_model

def _table(*, stationary=7.617, surface=0.008, dry=3.791, dry_basis='depth+temperature'):
    """A regime table shaped like ``BR_260318_S3``'s, with the three hours
    that decide the model free to vary."""
    ...

def test_auto_picks_grounded_on_a_record_that_stopped_and_was_lifted_out():
    """The flagship's shape: 7.617 h motionless in the water, 28 s of
    depth-channel disagreement, then 3.791 h out of the water."""
    ...

def test_auto_picks_leeway_when_a_surface_float_separates_the_two_spans():
    """A ``surface`` row of half an hour is a drift the model must run.

    Note what this does and does not establish: the regime table here is
    hand-built. ``test_a_float_inside_the_closing_dry_span_is_not_separated``
    below pins the fact that the shipped pipeline cannot *produce* such a row
    for a float that reads zero depth.
    """
    ...

def test_a_float_inside_the_closing_dry_span_is_not_separated():
    """The named limit of ``auto``'s third condition, pinned end to end.

    A genuine surface float reads depth ≈ 0, so it falls inside the terminal
    dry run rather than becoming a ``surface`` row of its own, and
    ``classify_terminal_dry_span`` then classifies float-plus-deck by the
    median over both. Two hours of real drift followed by four hours of warm
    deck therefore yields **no surface row at all** and ``auto`` returns
    ``grounded``; swapping the two durations returns ``leeway``. The verdict
    turns on which half is longer, not on whether a float occurred.

    This test exists so the limitation cannot be quietly repaired without
    someone noticing, and so the docstrings that describe it stay honest.
    """
    ...

def test_the_surface_tolerance_is_the_water_exit_detectors_own_sustain_floor():
    """One minute either side of ``AUTO_MAX_SURFACE_MINUTES`` flips the model,
    and the constant is 10 min — ``detect_tag_detachment``'s ``sustained_min``,
    below which no water exit is called at all."""
    ...

def test_auto_picks_leeway_without_a_stationary_span():
    ...

def test_auto_picks_leeway_when_the_record_does_not_end_out_of_the_water():
    ...

def test_auto_will_not_read_a_depth_only_out_of_water_row_as_evidence():
    """Zero metres is what a boat and a wave crest both read.

    Without the temperature test the row is the depth channel's opinion, and
    the conservative model — the shipped one — stands.
    """
    ...

def test_an_explicit_model_is_returned_unchanged_whatever_the_table_says():
    ...

def test_an_unknown_model_is_refused_by_name():
    ...

def test_resolve_reads_regime_objects_as_well_as_dicts():
    """The driver holds ``RecordRegime`` objects and the card holds dicts."""
    ...

def test_the_grounded_anchor_is_the_recovery_point_widened_by_the_creep_term():
    ...

def test_the_creep_allowance_is_overridable_and_validated():
    ...
