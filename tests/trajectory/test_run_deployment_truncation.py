"""Regression: the driver must run the filter over the *truncated* span.

``run_deployment.main`` detects tag detachment and narrows ``n_steps_for_filter``
to the detachment index, but the value has to actually reach the filter (and the
VPC leave-one-out reconstruction, and the sensitivity sweep) — otherwise the
reconstruction keeps integrating heading/speed from a tag that is bobbing on the
surface, and the FFBS end anchor (back-propagated to the *detachment* moment) is
matched against the wrong terminal step.

Synthetic + monkeypatched: no rasters, no network, no filter run. Every heavy
stage before the filter call is stubbed; the detachment detection itself runs
for real, and the stubbed filter records the ``n_steps`` it was handed.
"""
from __future__ import annotations
import json
from pathlib import Path
from types import SimpleNamespace
import numpy as np
import pytest
from anchor.trajectory import run_deployment as RD
from anchor.trajectory.axy_ingest import IngestedTrack
N_ATTACHED = 7500
N_SURFACE = 1200

class _StopAfterFilter(Exception):
    """Sentinel: unwind out of main() once the filter call is observed."""

def _synthetic_track() -> IngestedTrack:
    ...

@pytest.fixture
def stubbed_driver(monkeypatch):
    """Stub every stage main() touches before the filter; capture the call."""
    ...

def _argv(tmp_path, extra_argv=(), n_steps=str(N_TOTAL), behavior=False, states_parquet=True):
    ...

def _run(monkeypatch, tmp_path, extra_argv=(), n_steps=str(N_TOTAL), **kwargs):
    ...

@pytest.mark.skipif(not CFG_PATH.exists(), reason='needs the repo deployment config')
def test_filter_receives_detachment_truncated_n_steps(stubbed_driver, monkeypatch, tmp_path):
    ...

@pytest.mark.skipif(not CFG_PATH.exists(), reason='needs the repo deployment config')
def test_sensitivity_sweep_uses_the_same_truncated_span(stubbed_driver, monkeypatch, tmp_path):
    ...

@pytest.mark.skipif(not CFG_PATH.exists(), reason='needs the repo deployment config')
def test_no_auto_truncate_keeps_the_full_span(stubbed_driver, monkeypatch, tmp_path):
    ...

@pytest.mark.skipif(not CFG_PATH.exists(), reason='needs the repo deployment config')
def test_omitting_n_steps_runs_the_whole_track(stubbed_driver, monkeypatch, tmp_path):
    """No --n-steps means the full record, not the old 7200-step (2 h) default.

    The synthetic track is 8700 steps, deliberately longer than 7200: below
    that the old default was clipped by ``min(n_steps, len(track))`` to the
    track length anyway and this test could not have seen it. ``--no-auto-truncate`` keeps detachment out of the way; what is under
    test is only the default span.
    """
    ...

@pytest.mark.skipif(not CFG_PATH.exists(), reason='needs the repo deployment config')
def test_explicit_short_n_steps_with_a_recovery_anchor_is_refused(stubbed_driver, monkeypatch, tmp_path):
    """BR_260318_S3 declares `recovery:`, so a partial run misplaces the anchor."""
    ...

@pytest.mark.skipif(not CFG_PATH.exists(), reason='needs the repo deployment config')
def test_allow_truncation_permits_the_partial_run(stubbed_driver, monkeypatch, tmp_path):
    ...

@pytest.mark.skipif(not CFG_PATH.exists(), reason='needs the repo deployment config')
def test_short_n_steps_is_allowed_without_a_recovery_anchor(stubbed_driver, monkeypatch, tmp_path):
    """The guard is about the end anchor, not about partial runs in general."""
    ...

@pytest.fixture
def release_calls(monkeypatch):
    """Record every (lon, lat, sigma_m) the release anchor is built from."""
    ...

@pytest.mark.skipif(not CFG_PATH.exists(), reason='needs the repo deployment config')
def test_release_endpoint_comes_from_the_config(stubbed_driver, release_calls, monkeypatch, tmp_path):
    ...

@pytest.mark.skipif(not CFG_PATH.exists(), reason='needs the repo deployment config')
def test_cli_release_flags_override_the_config(stubbed_driver, release_calls, monkeypatch, tmp_path):
    """Each component overrides independently: σ alone, coordinates alone."""
    ...

@pytest.mark.skipif(not CFG_PATH.exists(), reason='needs the repo deployment config')
def test_a_config_without_a_release_is_a_named_error(stubbed_driver, monkeypatch, tmp_path):
    ...

@pytest.mark.skipif(not CFG_PATH.exists(), reason='needs the repo deployment config')
def test_body_length_and_sway_axis_come_from_the_config(stubbed_driver, monkeypatch, tmp_path):
    """L and the flap axis follow the deployment, not a bat-ray CLI default."""
    ...

@pytest.mark.skipif(not CFG_PATH.exists(), reason='needs the repo deployment config')
def test_body_length_falls_back_to_the_species_default(stubbed_driver, monkeypatch, tmp_path):
    """With animal.length_cm null, L is the species default — not a literal 0.9."""
    ...

def test_resolve_n_steps_contract():
    """The guard itself: None = full, longer = clipped, shorter = a decision."""
    ...

@pytest.mark.skipif(not CFG_PATH.exists(), reason='needs the repo deployment config')
def test_states_parquet_is_keyed_off_the_config_not_the_output_stem(stubbed_driver, monkeypatch, tmp_path):
    """``--deployment`` renames outputs; it must not repoint this input.

    ``--config BR_260318_S3.yaml --deployment BR_run_hiK`` names a second run's
    output files. Deriving the states parquet from that stem would look for
    ``BR_run_hiK_states.parquet``, miss, and silently drop the behaviour-state
    -conditioned process noise of §4.5.3.
    """
    ...

@pytest.mark.skipif(not CFG_PATH.exists(), reason='needs the repo deployment config')
def test_missing_behavior_states_is_announced(stubbed_driver, monkeypatch, tmp_path, capsys):
    """Falling back to constant process noise must not be silent."""
    ...

def test_effective_body_length_reports_its_source():
    """L scales every reconstructed metre, so its provenance is not guessable."""
    ...

@pytest.mark.skipif(not CFG_PATH.exists(), reason='needs the repo deployment config')
def test_cli_body_length_is_not_reported_under_the_config_provenance(stubbed_driver, monkeypatch, tmp_path, capsys):
    """``--body-length-m`` must not inherit ``animal.length_cm_source``.

    The provenance the config would otherwise supply is forced to
    ``species_default`` here: the shipped BR_260318_S3.yaml has carried a
    measured 46.5 cm since 2026-09-04, and reading the provenance off it would
    make the assertion below pass for the wrong reason.
    """
    ...

@pytest.mark.skipif(not CFG_PATH.exists(), reason='needs the repo deployment config')
def test_config_body_length_is_reported_under_its_recorded_source(stubbed_driver, monkeypatch, tmp_path, capsys):
    ...

@pytest.mark.skipif(not CFG_PATH.exists(), reason='needs the repo deployment config')
def test_mag_stage_re_ingests_when_the_interim_cache_is_stale(monkeypatch, tmp_path):
    """A parquet with no sidecar predates the keying, so its calibration
    provenance is unknown and it must be regenerated rather than served."""
    ...

def _stop():
    ...

def _traj_args(**over):
    ...

@pytest.mark.skipif(not CFG_PATH.exists(), reason='needs the repo deployment config')
def test_bathymetry_flags_default_to_the_config():
    ...

@pytest.mark.skipif(not CFG_PATH.exists(), reason='needs the repo deployment config')
def test_bathymetry_flags_override_the_config():
    ...

@pytest.mark.skipif(not CFG_PATH.exists(), reason='needs the repo deployment config')
@pytest.mark.parametrize('bad', [85.0, 1.5, 0.0, -0.2])
def test_out_of_range_off_bottom_factor_is_refused_not_silently_applied(bad):
    """The CLI must not slip past the schema bound the YAML enforces.

    ``TrajectoryConfig.bathymetry_off_bottom_factor`` is ``gt=0, le=1``, and
    ``bathymetry.py`` uses it unchecked as ``off_bottom_factor * bathy_d``. An
    operator typing a percentage (85) or an overshoot (1.5) would otherwise
    centre the two-sided depth Gaussian far off the seafloor with no error.
    """
    ...

@pytest.mark.skipif(not CFG_PATH.exists(), reason='needs the repo deployment config')
def test_in_range_off_bottom_factor_edge_values_are_accepted():
    """The bound is inclusive at 1.0 — rejecting it would break the default."""
    ...

def test_bathymetry_mode_flag_is_constrained_to_the_two_real_modes():
    ...

def _qc_cfg(deployment_id='QC_WIRING_TEST'):
    ...

def test_qc_section_is_prepended_from_the_interim_json(tmp_path, monkeypatch):
    """A cached report stamped with *this* config is reused as-is."""
    ...

def test_qc_section_falls_back_to_running_the_doctor(tmp_path, monkeypatch):
    """No cached JSON → probe the raw CSV via the required --config path."""
    ...

def test_qc_section_failure_does_not_stop_the_report(tmp_path, monkeypatch, capsys):
    ...

def _sensitivity_kwargs(**over):
    """Positional args for ``_run_sensitivity`` — everything heavy is inert.

    Only the spec, the base config and the stubbed filter matter here; the
    track/bathymetry/polygon arguments are passed straight through to
    ``run_filter_with_snapshots``, which the caller monkeypatches out.
    """
    ...

@pytest.mark.skipif(not CFG_PATH.exists(), reason='needs the repo deployment config')
@pytest.mark.parametrize('spec', ['bathymetry_off_bottom_factor=0.5,1.5', 'bathymetry_off_bottom_factor=60,80,100', 'bathymetry_off_bottom_factor=0.0,0.5'])
def test_sensitivity_grid_is_validated_before_any_run(spec, monkeypatch, capsys):
    """An out-of-range grid point must not become a row in the sweep table.

    ``model_copy()`` + ``setattr`` bypassed the ``gt=0, le=1`` bound exactly as
    the override flags once did, so ``--sensitivity
    bathymetry_off_bottom_factor=60,80,100`` ran three reconstructions with the
    two-sided depth Gaussian centred at 60-100x the seafloor depth and printed
    a final-σ / VPC-RMSE table the operator reads as evidence. The whole grid
    is now validated up front, so the failure lands before the sweep starts.
    """
    ...

@pytest.mark.skipif(not CFG_PATH.exists(), reason='needs the repo deployment config')
def test_sensitivity_in_range_grid_still_sweeps(monkeypatch, capsys):
    """The guard must not cost the valid case: every grid point still runs."""
    ...

def test_no_anim_flag_parses_and_defaults_off():
    """``--no-anim`` skips the GIF/MP4 stage; it must default to rendering."""
    ...

def _straight(**over):
    ...

def _degeneracy_record(n_founders, n_steps=40, n_particles=100):
    ...

def test_channel_diagnostics_separates_along_from_cross_on_an_ensemble():
    """Design §2.4: the posterior is anisotropic and a single σ hides it. An
    ensemble 40 m wide along-channel and 4 m wide across must report both."""
    ...

def test_channel_diagnostics_flags_a_centerline_the_track_runs_off():
    """``project`` clamps, so an off-end position gets the terminal arc
    length and along-channel differences collapse to zero. A non-zero
    fraction is what says the along-channel figures measure the clamp."""
    ...

def test_channel_diagnostics_rotates_the_diagonal_sigma_without_an_ensemble():
    """A forward-only run has no path samples; the marginal per-axis σ is
    rotated into the channel frame instead. On a north-running centreline the
    along component is σ_y, not σ_x."""
    ...

def test_score_card_rescoring_matches_the_filters_own_verdict_and_serialises(tmp_path):
    """The card re-scores the five scalars through the ledger rather than
    copying the filter's verdict; the two must agree, and the card has to
    survive ``json`` — a numpy int in the stamp used to raise at write time."""
    ...

def test_score_card_of_a_passing_run_suppresses_nothing():
    ...

def test_diagnostics_section_renders_the_card_under_exactly_one_banner():
    """The card goes at the top of the diagnostics, beneath the banner — and
    it must not add a second verdict of its own."""
    ...

def test_track_parquet_footer_is_strict_json_when_a_diagnostic_is_not_finite(tmp_path):
    """The footer and the ledger JSON are written from the same numbers in the
    same run, so they must be JSON by the same rule. ``var_log_w`` peaks at
    ``inf`` on a collapsed run and Python's lenient writer emitted a bare
    ``Infinity`` literal, which ``JSON.parse``, ``serde_json`` and
    ``encoding/json`` all reject — the flagship parquet already carried one.
    """
    ...

def _bidirectional_states(degeneracy):
    """Forward + smoothed states just rich enough to render the 9b panel.

    The smoothed midpoint spread is deliberately half the forward one, so the
    panel prints a round "50% tighter" and the assertion reads on the figure
    rather than on a formatting accident.
    """
    ...

def _bidirectional_body(degeneracy):
    ...

def test_bidirectional_tightening_ratio_is_suppressed_with_its_endpoints():
    """The "N% tighter" figure is a ratio of the two 2σ spreads printed beside
    it, so it is a credible interval too. Leaving it plain quotes as
    uncertainty exactly what the banner three sections above says has been
    withdrawn — and on a collapsed run the tightening *is* the founder
    collapse. The card already marks a σ ratio
    (``sigma_along_over_cross_median``); this is the same rule."""
    ...

def test_bidirectional_tightening_ratio_is_plain_on_a_passing_run():
    """A run that clears the §3.7 floors quotes all three figures unmarked."""
    ...
