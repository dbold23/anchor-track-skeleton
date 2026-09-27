"""Tests for the R0 ledger: channel coordinates, scores, gates, card, cross-check.

Everything here runs with no ``data/``, no network and no optional geospatial
dependency — that is a requirement of the deliverable, not an accident of the
fixtures, so the centreline used throughout is
:class:`anchor.validation.ledger.channel.StraightCenterline`.
"""
from __future__ import annotations
import json
import re
import tracemalloc
from pathlib import Path
import numpy as np
import pytest
from anchor.validation.ledger import scores as _scores
from anchor.validation.ledger import DEGENERACY_FLOORS, GATE_TABLE, GATE_TABLE_VERSION, GateResult, LinearGaussianModel, PATH_FUNCTIONALS, Provenance, QUANTILE_METHOD, ScoreCard, StraightCenterline, aggregate_functional_ranks, channel_error, config_hash, credible_containment, crps_ensemble, crps_gaussian, ensemble_rank, evaluate_degeneracy_gate, evaluate_heading_gate, ffbs_sample, functional_ranks, gate_by_name, gate_suppresses_calibration, git_sha, jsonable, kalman_filter, max_up_slough_excursion_m, net_displacement_m, rank_histogram, rts_smoother, score_paths, to_channel, total_path_length_m, variogram_score

def _passing_degeneracy(**overrides) -> dict:
    ...

def test_to_channel_on_a_straight_line_is_x_and_y():
    ...

def test_cross_offset_is_positive_to_the_left_of_increasing_arc():
    """A centreline heading north puts +cross to the west, not the east."""
    ...

def test_along_error_is_an_arc_length_difference_not_a_tangent_projection():
    """On a right-angle bend the two definitions disagree; we use arc length."""
    ...

def test_channel_error_broadcasts_an_ensemble_against_one_truth():
    ...

class _ElbowCenterline:
    """(0,0) -> (100,0) -> (100,100): a bend with unambiguous arc lengths."""

    def project(self, x, y):
        ...

def test_to_channel_flags_positions_clamped_to_a_centreline_end():
    """``project`` clips to the polyline; ``at_end`` says which points it clipped.

    Without the flag an out-of-range track is indistinguishable from a
    perfectly reconstructed one: every off-end position carries the same
    terminal arc length, so along-channel differences between two of them are
    identically zero.
    """
    ...

def test_score_paths_reports_a_track_that_ran_off_the_centreline():
    """The clamp deflates the along-channel scores, and the bundle says so.

    This is the package docstring's original example: a unit-variance random
    walk about the origin scored against ``StraightCenterline()``, whose
    default runs up-slough from ``(0, 0)``. Nearly two thirds of the projected
    positions clamp, and the along-channel CRPS is under half what the same
    ensemble scores against a centreline that spans the track.
    """
    ...

def test_crps_of_a_point_mass_is_the_absolute_error():
    ...

def test_crps_ensemble_converges_to_the_gaussian_closed_form():
    ...

def test_fair_crps_is_less_biased_than_the_plain_estimator_for_small_ensembles():
    """The 1/m**2 spread term under-counts spread, so plain CRPS reads high.

    A small ensemble's ``E|X - X'|`` is biased low by ``(m-1)/m``; subtracting
    too little spread inflates the score. The fair normaliser removes it, which
    matters because section 3.7 compares CRPS *between arms* that may not share
    an ensemble size.
    """
    ...

def test_crps_rejects_a_one_member_ensemble():
    ...

def test_variogram_score_is_zero_for_an_ensemble_of_copies_of_the_truth():
    ...

def test_variogram_score_penalises_a_lost_correlation_structure():
    """A filter that keeps the marginals but shreds the path is caught here.

    Both ensembles have the same per-step marginal spread; only the second has
    the truth's step-to-step correlation. A sum of per-step CRPS values cannot
    tell them apart, which is why section 3.7 asks for this score.
    """
    ...

def test_variogram_weights_and_stride_are_validated():
    ...

def test_variogram_score_on_a_long_path_stays_within_a_memory_budget():
    """A deployment-length path must be slow, not unallocatable.

    The score is a double sum over the ``d**2`` step pairs of every member, so
    a member block taken over the whole pair grid is quadratic in path length:
    1.5 GB at ``d=1200``, 8.7 GB for a 2880-step track at ``score_paths``'s
    default ``variogram_stride=1``. Tiling the pair grid bounds the peak
    instead, so this is the same number computed inside a fixed budget.
    """
    ...

@pytest.mark.parametrize('shape', [(60, 45), (12, 30, 2)])
def test_variogram_score_does_not_depend_on_the_tile_size(monkeypatch, shape):
    """Tiling re-associates the outer sum only; the score itself is unmoved."""
    ...

def test_variogram_score_does_not_mutate_a_caller_supplied_weight_matrix():
    """The diagonal is dropped from a copy; the caller's array is read-only."""
    ...

def test_jsonable_is_public_and_the_private_alias_still_resolves():
    """``run_deployment`` stamps its parquet footer with the card's own rule."""
    ...

def test_path_functionals_on_a_known_path():
    ...

def test_max_up_slough_excursion_keeps_a_negative_sign():
    """An animal that only ever goes down-slough reports a negative excursion.

    The maximum runs over ``t > 0``. Including ``t = 0`` would floor the
    functional at zero, because ``s(0) - s(0)`` is identically zero, and every
    never-up-slough path would then tie at exactly 0.0 — which would also make
    :func:`ensemble_rank` tie-break its way to a flat rank histogram that says
    nothing about calibration.
    """
    ...

def test_down_slough_paths_do_not_all_tie_at_zero():
    """The functional separates paths that differ only in how far down they went.

    With the ``t = 0`` term included they were all exactly 0.0, so an ensemble
    of them plus the truth gave ``m + 1`` exact ties and ``ensemble_rank``
    returned a uniform random rank for every case: a flat histogram
    manufactured by the tie-break rather than by calibration.
    """
    ...

def test_ensemble_rank_spans_one_to_m_plus_one():
    ...

def test_rank_histogram_flags_a_uniform_and_a_piled_up_sample():
    ...

@pytest.mark.parametrize('n_bins', [7, 8, 10, 13, 64])
def test_rank_histogram_is_uniform_under_bins_that_do_not_divide_the_ranks(n_bins):
    """Unequal bin widths get unequal expected counts, not an equal-share fiction.

    ``n_members + 1 = 64`` ranks split into 10 bins gives bins of 7 and 6
    ranks. Assuming ``n / k`` per bin instead declared this perfectly uniform
    sample miscalibrated: chi2 1199.5, p 1.6e-252.
    """
    ...

def test_rank_histogram_rejects_out_of_range_ranks():
    ...

def test_credible_containment_is_exact_on_a_constructed_case():
    ...

def test_credible_interval_uses_the_plotting_position_that_makes_coverage_exact():
    """numpy's default quantile under-covers at realistic ensemble sizes.

    For an exchangeable sample of ``m`` members plus one truth, the nominal
    level is attained only at rank ``alpha (m + 1)`` — the Weibull plotting
    position. This is the fix for a 90 percent interval that would otherwise
    contain the truth 87 percent of the time by construction.
    """
    ...

def test_score_paths_returns_every_section_37_score():
    ...

def test_gate_table_carries_all_eleven_section_37_rows_with_their_fixed_floors():
    ...

def test_degeneracy_floors_are_the_numbers_printed_in_section_37():
    ...

def test_degeneracy_gate_passes_a_healthy_run():
    ...

@pytest.mark.parametrize('key,value', [('n_founders_final', 29), ('min_unique_ancestor_fraction', 0.019), ('max_norm_weight', 0.051), ('ess_min', 399.0), ('var_log_w', 5.01)])
def test_each_degeneracy_floor_fails_on_its_own_and_names_itself(key, value):
    ...

@pytest.mark.parametrize('key,value', [('n_founders_final', 30), ('min_unique_ancestor_fraction', 0.02), ('max_norm_weight', 0.05), ('ess_min', 400.0), ('var_log_w', 5.0)])
def test_the_floors_are_inclusive(key, value):
    ...

def test_ess_floor_scales_with_the_particle_count():
    ...

def test_missing_or_unmeasured_diagnostics_do_not_silently_pass():
    ...

def test_config_hash_is_stable_and_key_order_independent():
    ...

def test_provenance_stamp_uses_the_timestamp_it_is_given():
    ...

def test_provenance_records_the_source_config_beside_the_effective_one():
    """``config_hash`` fingerprints what ran; ``source_config_hash`` the file.

    A sweep varies one hyperparameter from the command line, so every card in
    it is built from the same YAML. Carding only one of the two hashes loses
    either which run it was or which file it came from.
    """
    ...

def test_provenance_with_no_source_config_records_no_source_hash():
    """Every caller outside the deployment driver passes one config only."""
    ...

def test_git_sha_never_raises_outside_a_repository(tmp_path):
    ...

def test_a_failed_gate_suppresses_calibration_numbers_but_not_the_banner():
    ...

def test_a_passing_card_reports_its_numbers():
    ...

def test_a_failed_gate_without_a_stop_rule_suppresses_nothing():
    """G-phantom's section 3.7 row reads "diagnostic only, no programme stop rule".

    Generalising G-degeneracy's suppression rule to every gate would contradict
    the table the card exists to encode: a bench-phantom disagreement would
    blank the CRPS of a filter run it says nothing about.
    """
    ...

def test_only_the_three_rows_that_say_so_carry_a_suppression_rule():
    ...

def test_a_gate_result_can_override_the_table_for_one_clause():
    """G-field's row has two clauses; only clause (i) withdraws intervals."""
    ...

def test_card_json_round_trips_and_nan_becomes_null(tmp_path):
    ...

def test_provenance_extra_is_coerced_like_every_other_payload():
    """``extra`` is where run metadata is stamped, and it arrives as numpy.

    ``remaining`` item 8 of this package tells callers to record the variogram
    stride there. A stride is a numpy integer far more often than a Python
    one, and taking ``extra`` verbatim made ``write_json`` raise ``TypeError``
    at the end of the run the card exists to record.
    """
    ...

def test_a_gate_check_carrying_a_non_finite_value_still_writes_strict_json(tmp_path):
    """An unmeasured diagnostic reaches the JSON through the gate, not the scores."""
    ...

def _dense_posterior(model: LinearGaussianModel, obs_1d: np.ndarray):
    """Brute-force Gaussian posterior for one axis: mean and full covariance."""
    ...

def test_rts_smoother_matches_a_dense_gaussian_solve():
    ...

def test_kalman_filter_final_step_equals_the_smoother_final_step():
    ...

def test_ffbs_draws_reproduce_the_full_joint_posterior_covariance():
    ...

@pytest.mark.slow
def test_exact_gaussian_posterior_samples_are_calibrated_under_the_ledger_scores():
    """The harness's own control arm.

    Truth is drawn from the prior and the ensemble from the *exact* posterior,
    so truth and members are exchangeable: every rank histogram must be flat
    and the nominal-90 percent containment must come out at 0.9. If a score in
    this package has a sign error or an off-by-one in its quantiles, this is
    where it shows.
    """
    ...

@pytest.mark.slow
def test_an_under_dispersed_ensemble_fails_the_same_calibration_checks():
    """Teeth for the test above: shrink the posterior spread and it must break."""
    ...

def test_score_registry_resolves_the_ledger_entries():
    ...

def test_sweep_parameter_flattens_a_bundle_score_into_columns():
    """Registry bundles return a dict; the old sweep did ``float(fn(res))``."""
    ...

def test_sweep_parameter_still_accepts_plain_scalar_scores():
    ...

def sweep_parameter_scalar():
    ...

def test_degeneracy_scores_surface_the_gate_verdict_as_a_number():
    ...

def _heading_finding(check, level, **gates):
    """One ``anchor doctor`` finding, in the dict shape a cached QC JSON has."""
    ...

def _passing_heading_findings():
    ...

def test_the_heading_gate_is_in_the_table_and_withdraws_positional_numbers():
    ...

def test_the_heading_gate_passes_a_validated_calibration():
    ...

def test_the_heading_gate_fails_the_flagship_shipped_chain_and_names_the_floors():
    """``docs/regen_2026-09.md`` §16: MAD 39.6 deg, offset +42.7 deg, and an
    improper axis mapping beating the identity by 30 deg."""
    ...

def test_a_heading_finding_with_no_numeric_floor_still_fails_the_gate():
    """A family that could not run is not a family that passed."""
    ...

def test_no_heading_findings_scores_no_gate_rather_than_a_pass():
    """An older cached QC report says nothing about the heading, and a gate
    scored from an input that does not exist would be a verdict about the
    report's age."""
    ...

def test_the_heading_gate_scores_Finding_objects_and_dicts_identically():
    ...

def test_a_failed_heading_gate_suppresses_the_cards_positional_scores():
    """The scores a trajectory run actually writes, not only the CRPS family.

    ``_build_score_card`` writes ``n_steps``, ``fraction_at_centerline_end``
    and ``n_members``; none of them starts with a calibration prefix, so a
    global prefix tuple left every positional number on a heading-failed card
    printing. §3.7's G-heading row withdraws "every metre, every sigma, every
    endpoint distance" — ``fraction_at_centerline_end`` is one of them, and the
    two shape counts are not.
    """
    ...

def test_a_failed_degeneracy_gate_leaves_the_positional_scores_alone():
    """The two rows withdraw different sets, and the card applies each row's.

    G-degeneracy's row is about calibration numbers: a degenerate cloud makes
    every width a within-lineage spread, but it does not move the track's shape
    statistics, so those keep printing under it and stop printing under
    G-heading.
    """
    ...

def test_a_gate_entry_whose_numbers_did_not_survive_the_round_trip_fails():
    """``jsonable`` writes every non-finite float as ``null``.

    A cached QC report can therefore hand the ledger an entry with no number in
    it. Calling ``float(None)`` there raised ``TypeError`` and took the run
    down; an unscored floor is not a cleared floor, so it fails instead.
    """
    ...

def test_the_gate_table_is_transcribed_from_section_37_not_paraphrased():
    """Every row's three cells, against the design document's own table.

    ``docs/ledger.md`` tells a reader the table is transcribed verbatim, and
    the G-heading row was added by hand and drifted from it in three phrases.
    Markdown emphasis and backticks are stripped, and so is the one source
    citation the design's G-tank row carries inside its floor cell, which the
    code deliberately omits.
    """
    ...

def test_the_gate_floors_are_the_doctors_constants_not_a_second_copy():
    """The ledger reads each floor off the finding that was judged against it,
    so the two cannot drift apart. This holds the wiring, not the numbers."""
    ...
