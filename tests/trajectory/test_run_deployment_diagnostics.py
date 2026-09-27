"""Diagnostics the driver has to surface: the detector's own note, the
G-degeneracy banner, the anchor a distance is measured to, and the gate
verdict travelling with the track parquet.

Every item here was a case of a number reaching the reader with no way to
tell what produced it — ``docs/regen_2026-09.md`` §4.1(c), §4.1(d) and §6.
"""
from __future__ import annotations
import json
from pathlib import Path
from types import SimpleNamespace
import numpy as np
import pytest
from anchor.trajectory import report
from anchor.trajectory import run_deployment as RD
from anchor.trajectory.axy_ingest import IngestedTrack
from anchor.trajectory.detachment import DetachmentResult
from anchor.trajectory.end_anchor import EndAnchor
from anchor.trajectory.particle_filter import evaluate_degeneracy
from anchor.trajectory.release_anchor import ReleaseAnchor
from anchor.trajectory.sites.elkhorn import ELKHORN_DECLINATION_DEG_2026
N_ATTACHED = 7500
N_SURFACE = 1200

class _StopAfterFilter(Exception):
    ...

def _synthetic_track() -> IngestedTrack:
    ...

@pytest.fixture
def stubbed_driver(monkeypatch):
    """Stub every stage before the filter; stop the driver at the filter call."""
    ...

def _run(monkeypatch, tmp_path, method='depth'):
    ...

@pytest.mark.skipif(not CFG_PATH.exists(), reason='needs the repo deployment config')
def test_detector_note_reaches_the_console_on_a_successful_detection(stubbed_driver, monkeypatch, tmp_path, capsys):
    """The note is where a multichannel→depth-only fallback is disclosed. It
    used to print only when *no* detachment was found — i.e. never on a run
    that produced a number.

    The line it accompanies used to read "detected tag detachment at t=…". It
    now names the rule that cut the track ("detach-rule=surface: attached span
    ends at t=…"), because two rules can cut it and the moment alone no longer
    says which one did (``docs/regen_2026-09.md`` §17.4). The assertion moved
    with the wording; what the test is for did not change."""
    ...

@pytest.mark.skipif(not CFG_PATH.exists(), reason='needs the repo deployment config')
def test_channels_line_says_available_not_used(stubbed_driver, monkeypatch, tmp_path, capsys):
    """``channels=`` read as "the channels the rule used"; it lists the
    channels that *have data*. The multichannel rule can fall back to depth
    alone with all three populated."""
    ...

def _detach_panel_body(note: str) -> str:
    ...

def test_detector_note_is_html_escaped_in_the_report():
    """Unescaped, the browser reads "<0.50" as a tag and eats everything up to
    the closing ``</i>`` — threshold, duration and sample index all vanish,
    and the fallback the note exists to disclose is what disappears."""
    ...

def test_detector_note_escaping_does_not_mangle_a_plain_note():
    ...

def _state(n=40, x0=0.0):
    ...

@pytest.mark.parametrize('label', ['detachment anchor', 'recovery anchor'])
def test_smoothed_endpoint_distance_is_labelled_by_the_anchor_it_uses(label):
    """``end_anchor`` is the back-propagated *detachment* anchor once a
    detachment is detected — 1509 m from the recovery point on the flagship
    run — so the panel must not call it "recovery anchor" unconditionally."""
    ...

def _filter_state(degeneracy=None, binding=None, n=40, n_particles=100):
    ...

def _args(n_particles=100):
    ...

def _degeneracy(n_founders, n_steps=40, n_particles=100):
    ...

def test_diagnostics_section_banners_a_failed_gate_and_marks_the_intervals():
    ...

def test_diagnostics_section_leaves_intervals_alone_when_the_gate_passes():
    ...

def test_diagnostics_section_still_renders_without_a_degeneracy_record():
    ...

def _binding(**over):
    ...

def test_diagnostics_section_reports_the_end_anchor_binding():
    ...

def _cube_diag(**over):
    ...

def test_the_diagnostics_section_reports_the_smoothed_cube():
    """§19.6.3 option 3, on the page — beside the founder count, not inside it."""
    ...

def test_the_diagnostics_section_reports_the_backward_ess_when_it_was_measured():
    ...

def test_a_run_without_a_smoother_says_nothing_about_a_cube():
    ...

def test_the_card_carries_the_smoothed_cube_as_a_diagnostic_and_not_as_a_gate():
    ...

def test_the_degeneracy_metadata_drops_the_cube_and_the_per_step_arrays():
    ...

def test_the_console_line_names_the_cube_and_disclaims_the_gate(capsys):
    ...

def test_diagnostics_section_reports_weak_binding():
    """The flagship case: not a no-op, but 0.06% of a 4 km gap closed."""
    ...

def test_track_parquet_carries_the_gate_verdict(tmp_path):
    """A parquet handed to ``anchor export`` / ``anchor spaceuse`` carries no
    report, so its σ columns arrive with nothing saying whether they are
    reportable."""
    ...

def _header_kwargs(filter_state):
    ...

def _header_state(degeneracy=None, n=40, n_particles=100):
    ...

def _header_row(rows, label):
    ...

def test_header_2sigma_spread_is_marked_when_the_gate_fails():
    """The header table quotes the same ``filter_state["stds"][-1]`` spread
    that §8 marks, and build_html emits it *above* the banner — leaving it
    raw made the banner's "every credible interval is suppressed" false about
    the most prominent σ number in the report."""
    ...

def test_header_2sigma_spread_is_plain_when_the_gate_passes():
    ...

def test_header_2sigma_spread_is_plain_without_a_degeneracy_record():
    ...

def test_only_the_credible_interval_row_is_marked():
    """Drift, founder counts and the release σ are inputs or point estimates,
    not credible intervals produced by this run."""
    ...

def test_built_html_marks_the_header_row_above_the_banner(tmp_path):
    """End to end: the mark has to survive into the file, and the header row
    is the one the reader meets first."""
    ...

def test_binding_cloud_sigma_is_marked_when_the_gate_fails():
    """The cloud σ quoted in the binding paragraph is a posterior-spread
    figure like any other, and the banner promises it is marked."""
    ...

def test_binding_cloud_sigma_is_plain_when_the_gate_passes():
    ...

def _write_qc_json(cfg, findings, stamp):
    ...

def _doctor_returning(monkeypatch, findings, calls):
    ...

@pytest.mark.skipif(not CFG_PATH.exists(), reason='needs the repo deployment config')
def test_a_stale_qc_json_is_re_run_not_embedded(tmp_path, monkeypatch, capsys):
    """The §10 defect: the config promoted ``length_cm``, the cached JSON was
    written before it, and the report shipped the superseded FAIL."""
    ...

@pytest.mark.skipif(not CFG_PATH.exists(), reason='needs the repo deployment config')
def test_a_matching_qc_json_is_reused(tmp_path, monkeypatch, capsys):
    ...

@pytest.mark.skipif(not CFG_PATH.exists(), reason='needs the repo deployment config')
def test_an_unstamped_qc_json_is_re_run(tmp_path, monkeypatch, capsys):
    """Every ``_qc.json`` written before this gate carries no stamp, and
    nothing ties it to the config the report is being built from."""
    ...

@pytest.mark.skipif(not CFG_PATH.exists(), reason='needs the repo deployment config')
def test_a_stale_qc_json_is_dropped_when_the_doctor_cannot_re_run(tmp_path, monkeypatch, capsys):
    """No section beats a wrong section: if the recompute fails there is
    nothing to fall back on."""
    ...

def _override_args(**over):
    """An argparse namespace with every trajectory override flag unset."""
    ...

def _sweep_card(speed_min):
    ...

def test_a_speed_min_override_moves_the_effective_hash_only():
    ...

def test_an_override_free_run_cards_the_same_hash_twice():
    """With nothing overridden the run *is* the file, and both fields say so."""
    ...

def _traj_argv(*extra):
    """The parsed args of a run with no flag set but the ones passed."""
    ...

def _traj_from(argv_extra=(), *, base=None):
    ...

def _hash_of(traj, yaml_traj=None):
    ...

def test_the_bathymetry_switch_is_a_config_field_defaulting_to_on():
    """§13.6 keeps the shipped default at True; the field is what carries it."""
    ...

def test_a_yaml_block_can_disable_bathymetry_without_the_flag():
    """The point of the field: the deployment file gets a say, and keeps it
    when no override is on the command line."""
    ...

def test_no_bathymetry_moves_the_effective_hash_and_not_the_file_hash():
    """Arms (a) and (c) of §13 must no longer card identically."""
    ...

def test_the_driver_reads_the_bathymetry_switch_off_the_effective_config(stubbed_driver, monkeypatch, tmp_path):
    """``enable_bathy`` must come from the effective ``TrajectoryConfig``, not
    from ``argparse``: it is the block the card hashes, so a run whose YAML
    turned the depth likelihood off has to reach the filter with it off."""
    ...

def test_the_polygon_penalty_flag_parses_a_number_and_the_hard_mode():
    ...

def test_the_polygon_penalty_flag_moves_the_effective_hash():
    ...

@pytest.mark.parametrize('bad', ['0', '-400', 'inf', 'nan'])
def test_an_illegal_polygon_penalty_exits_with_the_field_validator_message(bad):
    """The rule lives on ``TrajectoryConfig``; the flag reuses it rather than
    restating it, so the operator gets the validator's own sentence with the
    offending flag named."""
    ...

def test_the_new_polygon_and_smoother_knobs_default_to_no_instruction():
    ...

def test_a_run_that_names_none_of_the_new_knobs_cards_the_hash_it_always_did():
    """The golden check, at the level of the fingerprint.

    ``docs/regen_2026-09.md`` §19.5.2's ``G-ship`` cards ``930fb22f941e98a2``
    against a ``TrajectoryConfig`` that predates all four fields; the hash is
    taken over the model dump, so a field that stays out of the dump cannot
    move it. This asserts the mechanism rather than the digest, which depends
    on the whole deployment YAML.
    """
    ...

@pytest.mark.parametrize('flag,value,field,expected', [(['--polygon-mode', 'indicator'], None, 'polygon_mode', 'indicator'), (['--polygon-mode', 'in_water_proposal'], None, 'polygon_mode', 'in_water_proposal'), (['--polygon-mode', 'soft'], None, 'polygon_mode', 'soft'), (['--polygon-proposal-draws', '16'], None, 'polygon_proposal_draws', 16), (['--polygon-soft-width-m', '7.5'], None, 'polygon_soft_width_m', 7.5), (['--smoother-diagnostics'], None, 'smoother_diagnostics', True)])
def test_each_new_flag_reaches_the_effective_trajectory_block(flag, value, field, expected):
    ...

def test_every_new_knob_moves_the_effective_hash_and_not_the_file_hash():
    """All four reach the fingerprint, and none of them touches the YAML's own.

    ``--polygon-mode indicator`` is in the list on purpose: it names the
    shipped model, which is an instruction and must card differently from a
    run that named nothing — the ``declination_deg`` rule (§18.6.1), where two
    runs 5.35 million nats apart shared one hash because the site default was
    indistinguishable from a choice.
    """
    ...

@pytest.mark.parametrize('argv,message', [(['--polygon-proposal-draws', '0'], 'greater than or equal to 1'), (['--polygon-soft-width-m', '0'], 'greater than 0')])
def test_an_out_of_range_new_knob_exits_naming_the_flag(argv, message):
    ...

def test_an_unknown_polygon_mode_is_an_argparse_error():
    ...

def test_unparseable_polygon_penalty_text_is_an_argparse_error():
    ...

@pytest.mark.skipif(not CFG_PATH.exists(), reason='needs the repo deployment config')
def test_the_two_grid_arms_of_section_13_now_card_distinct_hashes():
    """The regression this pair of fixes exists for, on the flagship itself.

    Arms (a) and (c) are one ``anchor track`` invocation apart — the second
    adds ``--no-bathymetry`` — and both carded ``b32f742017a25ed7``. Dropping
    the new key from the effective block reproduces that hash exactly, which
    is what makes this an assertion about the fix rather than about the YAML.
    """
    ...

def _sweep(spec, base_traj, *, enable_bathy=True):
    """Run ``_run_sensitivity`` against a stub filter; return what it saw.

    The stub returns the two keys the scorer and the drift column read, so
    the table prints and the only interesting output is the argument trace.
    """
    ...

def test_a_sensitivity_sweep_over_the_bathymetry_switch_reaches_the_filter():
    """Each grid point's own likelihood, not the outer run's.

    ``enable_bathymetry_constraint`` became a ``TrajectoryConfig`` field in
    this pass (§13.7), which made ``--sensitivity
    enable_bathymetry_constraint=0,1`` a legal sweep for the first time. It
    was silently inert: the closure passed the outer ``enable_bathy`` to every
    run, so the table printed one run twice and reported ``range=0.000`` for a
    factor §14.11 measures at ×2.203 on σ_cross.
    """
    ...

def test_a_sensitivity_sweep_survives_a_hard_polygon_base_config():
    """``polygon_penalty_nats: None`` must not make the cast ``NoneType``.

    The hard (``-inf``) polygon is reachable from the command line now, as
    ``--polygon-penalty-nats none``, so a sweep can be launched on top of it.
    ``type(None)(400.0)`` is a bare ``TypeError``; this module reports a sweep
    it cannot build through ``_traj_with``, with the field's own sentence.
    """
    ...

def test_a_sensitivity_grid_point_the_schema_rejects_still_names_the_flag():
    """The guarantee ``_run_sensitivity``'s own comment makes, on the field
    whose cast this pass had to repair."""
    ...

def _heading_gate(passed: bool):
    """A scored G-heading gate, from the shape ``anchor doctor`` emits."""
    ...

def _card_with(heading_gate, degeneracy=None):
    ...

def test_the_card_carries_g_heading_beside_g_degeneracy():
    ...

def test_a_card_built_without_a_heading_gate_carries_no_spurious_verdict():
    """``_build_score_card`` is used by callers that score no heading at all
    (the ledger's own control arms), and a missing gate must not become a
    spurious pass or a spurious failure on the card. The *driver* never gets
    here with ``None``: see the fail-closed test below."""
    ...

def test_an_unscoreable_heading_gate_fails_closed_in_the_driver():
    """"Not scored" is not "no gate".

    ``evaluate_heading_gate`` returns ``None`` when the findings carry no
    ``heading.*`` check — the right answer for a pure ledger function, and the
    state of every QC report cached before the 2026-09-05 amendment, plus every
    run whose doctor was unavailable or raised. The driver's policy is design
    §3.7's: a run that cannot demonstrate its heading is a measurement of
    azimuth may not publish a position, whatever the reason. Treating the
    ``None`` as "no gate" published every metre of exactly those runs.
    """
    ...

def test_the_gate_banner_survives_a_check_whose_numbers_are_null():
    """A FAIL finding with no measurement scores a ``nan``/``nan`` check, and
    ``ScoreCard.to_dict`` writes every non-finite float as ``null``. Formatting
    that with ``:.4g`` raised ``TypeError`` and took the report down after the
    filter had already run."""
    ...

def test_a_failed_heading_gate_banners_and_marks_the_intervals():
    """The particle cloud is healthy; the heading is not. Every interval in the
    report still has to carry the mark the banner promises."""
    ...

def test_a_passing_heading_gate_banners_without_suppressing():
    ...

def test_the_header_table_and_the_bidirectional_panel_honour_the_card():
    """Both sit above or beside the banner and quote credible intervals."""
    ...

def test_the_track_parquet_footer_carries_the_heading_verdict(tmp_path):
    """``anchor export`` reads the parquet and never sees the report."""
    ...

def test_the_qc_section_reuses_findings_the_driver_already_built(monkeypatch):
    """The gate is scored before the track parquet is written, so the doctor
    must run once per reconstruction, not twice."""
    ...

def test_the_detach_rule_is_a_config_field_defaulting_to_stationary():
    ...

def test_the_effective_config_hash_sees_the_detach_rule():
    """Two runs of one file that reconstruct different spans must card apart.

    Without the field the only difference between them would be a CLI flag,
    and §13.7's defect — arms differing in what the filter saw and carding one
    hash — would be reproduced on a bigger difference: 33 600 steps against
    60 992.
    """
    ...

def _detachment_dict(rule='stationary'):
    ...

def test_the_track_parquet_footer_carries_the_detach_rule(tmp_path):
    """``anchor export`` reads the parquet and never sees the report, and
    "these coordinates cover 0.333-9.333 h of a 20.7 h record" is part of what
    the coordinates mean."""
    ...

def test_the_score_card_carries_the_regime_table():
    ...

def test_a_card_built_without_a_detachment_carries_an_empty_block():
    """``--no-auto-truncate`` is a run with no detachment, not a run with a
    silently absent one."""
    ...

def test_the_report_section_names_the_rule_and_the_hidden_hours():
    ...

def test_the_truncation_and_the_end_anchor_land_on_the_same_step():
    """The step the filter stops at is the step the end anchor is applied at.

    The driver takes ``min(--n-steps, t_detach_idx)`` and then
    back-propagates the recovery point to ``t_detach_idx``. If the two ever
    disagreed the smoother would be pulled toward a position the forward
    filter never reached; here the stationary rule moves both together.
    """
    ...

@pytest.mark.skipif(not CFG_PATH.exists(), reason='needs the repo deployment config')
def test_the_site_default_declination_stays_out_of_the_effective_config():
    """A run that names no declination has to card the hash it always carded.

    ``--declination-deg`` defaults to the *site's* value rather than to None,
    so "absent" arrives as a number; it is recognised by type and never
    reaches the effective block. Without that, every card in
    ``docs/regen_2026-09.md`` §§10-18 would stop being comparable to a card
    written today for the sake of a field nobody set.
    """
    ...

@pytest.mark.skipif(not CFG_PATH.exists(), reason='needs the repo deployment config')
def test_two_runs_that_differ_only_in_declination_card_different_hashes():
    """§18.6.1's pair. ``S-ship-surface`` and ``D-decl-surface`` differ by a
    −0.120° rotation of every shipped heading — up to 5.35 million nats of
    evidence surface — and shared ``config_hash`` ``c22bdee634b63476``.
    """
    ...

@pytest.mark.skipif(not CFG_PATH.exists(), reason='needs the repo deployment config')
def test_the_effective_hash_sees_the_end_anchor_model_and_the_creep_sigma():
    """Two runs whose smoother gets a different boundary condition are two
    runs, and the card has to say so."""
    ...

@pytest.mark.skipif(not CFG_PATH.exists(), reason='needs the repo deployment config')
def test_a_creep_sigma_the_schema_rejects_exits_naming_the_flag():
    ...

def test_the_end_anchor_metadata_says_which_model_where_and_at_what_sigma():
    """One dict, read by the parquet footer, the ledger card and the report,
    so the three cannot disagree."""
    ...

def test_a_leeway_card_does_not_report_a_creep_allowance_it_does_not_contain():
    """The 25 m creep term is only in the grounded model's σ, so only the
    grounded model's card carries it. A leeway card printing
    ``creep_sigma_m: 25.0`` beside a σ built from back-propagation invites
    exactly the wrong decomposition of that σ."""
    ...

def test_a_states_parquet_older_than_its_species_config_is_flagged(tmp_path, capsys):
    """The ingest fingerprint does not cover the species `tailbeat` block, so a
    behaviour-state file computed under an earlier peak picker is still served
    as valid. Nothing can verify it; the run says what it can see."""
    ...
