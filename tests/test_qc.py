"""Unit tests for ``anchor.qc`` — the engine behind ``anchor doctor``.

Every check here is exercised on a synthetic CSV built to carry exactly the
defect the check exists to find, so the suite runs without the gitignored
``data/`` drive. The two tests that read real deployment CSVs are marked
``needs_data`` and skip when the file is absent.
"""
from __future__ import annotations
import datetime as dt
import json
from pathlib import Path
import pandas as pd
import pytest
import yaml
from anchor import qc
from anchor.ingest import io as _io
from anchor.ingest.config import load_config

def write_axy_csv(path: Path, *, n: int=400, fs: float=25.0, start: str='2024-07-02 22:16:45', timestamp: str='pair', swap_timestamp: bool=False, gap_at: int | None=None, gap_s: float=0.0, reverse_at: int | None=None, reverse_s: float=0.0, depth: list[float] | None=None) -> Path:
    """Write a small AXY-5-shaped CSV with a precisely controlled time axis.

    ``timestamp="pair"`` writes both ``Date`` + ``Time`` and a ``Timestamp``
    column (the APT export's shape); ``"only"`` writes ``Timestamp`` alone;
    ``"none"`` writes ``Date`` + ``Time`` alone. ``swap_timestamp`` transposes
    month and day in the ``Timestamp`` column only, reproducing the
    ``APT_240702_S2`` defect.
    """
    ...

def make_config(tmp_path: Path, csv: Path, *, fs: float=25.0, **deploy):
    """A minimal but valid DeploymentConfig pointed at ``csv``."""
    ...

def probe(csv: Path, probe_rows: int=5000) -> qc.RawProbe:
    ...

def test_count_csv_rows_excludes_the_header(tmp_path):
    ...

def test_count_csv_rows_counts_an_unterminated_final_line(tmp_path):
    ...

def test_probe_keeps_the_first_and_last_data_row(tmp_path):
    """The head chunk starts exactly one byte past the header's newline.

    Regression: dropping a "partial" first line there loses row 1, which
    silently shifts t_min and breaks ``detect_sampling_rate``'s duplicate
    heuristic by one sample.
    """
    ...

def test_probe_collapses_tail_into_head_when_the_head_covers_the_file(tmp_path):
    """Otherwise every gap and reversal in a short record is counted twice."""
    ...

def test_probe_trims_the_head_tail_overlap(tmp_path):
    """Partially overlapping head/tail blocks must not probe a row twice.

    Regression: collapsing only the exact-cover case left every record with
    ``probe_rows < n_rows < ~2x the block's line capacity`` sharing rows
    between the two chunks, doubling every gap and reversal inside them. At
    the default ``probe_rows`` a 6000-row record reported ``n_gaps == 2`` and
    a missing fraction of 0.0250 for a single 3.04 s gap.
    """
    ...

def test_probe_overlap_trim_does_not_manufacture_a_fail(tmp_path):
    """A gap that loses 0.8% of the record is a WARN, not a FAIL.

    Regression: double-counting pushed the missing fraction over the 1% FAIL
    threshold, so ``anchor doctor`` exited 1 on a healthy-enough record. The
    repo's own ``anchor demo`` writes 7500 rows, inside the affected band.
    """
    ...

def test_probe_reads_a_middle_chunk_on_a_large_file(tmp_path):
    ...

def test_swapped_timestamp_column_is_flagged(tmp_path):
    ...

def test_a_wide_disagreement_says_the_loader_falls_back_to_date_time(tmp_path):
    """Since 3354f0f the pipeline is *not* on Timestamp here.

    ``_reconcile_datetime_columns`` hands a disagreement this wide to Date+Time,
    so the message must name the defective column rather than claim the loaded
    record is built from it.
    """
    ...

def test_a_narrow_disagreement_says_the_loader_is_still_on_timestamp(tmp_path):
    """Below ``io.TIMESTAMP_DISAGREEMENT_FRAC`` the loader keeps Timestamp.

    One row in 300 is under the 1 % reconciliation threshold, so those rows do
    reach the pipeline from the disagreeing column — the message has to say
    which of the two regimes the record is in.
    """
    ...

def test_consistent_timestamp_column_passes(tmp_path):
    ...

def test_timestamp_consistency_is_skipped_without_a_redundant_pair(tmp_path):
    ...

def test_time_axis_uses_date_time_not_the_swapped_timestamp(tmp_path):
    """The check must not inherit ``io.parse_datetime``'s Timestamp preference.

    The record spans days (0.01 Hz keeps the fixture small), so transposing
    month and day in the Timestamp column stretches the apparent span by ~30x —
    the ``APT_240702_S2`` failure in miniature. The Date+Time columns are
    intact, so a check that reads them lands on a zero residual anyway.
    """
    ...

def test_time_axis_fails_when_span_and_row_count_disagree(tmp_path):
    """A 25 Hz record declared as 50 Hz: span x fs is twice the row count."""
    ...

def test_time_axis_passes_on_a_self_consistent_record(tmp_path):
    ...

def test_sampling_rate_flags_25_hz_data_under_a_50_hz_default(tmp_path):
    ...

def test_sampling_rate_passes_when_config_matches(tmp_path):
    ...

def test_time_continuity_reports_gap_boundaries(tmp_path):
    ...

def test_time_continuity_warns_on_a_gap_that_loses_little(tmp_path):
    ...

def test_time_continuity_fails_on_a_time_reversal(tmp_path):
    ...

def test_time_continuity_passes_on_a_regular_record(tmp_path):
    ...

def test_depth_check_is_absent_without_a_depth_column(tmp_path):
    ...

def test_depth_check_flags_a_zero_offset(tmp_path):
    ...

def test_depth_check_flags_drift(tmp_path):
    """Head and tail must be probed separately for drift to be visible."""
    ...

def test_depth_check_passes_on_a_surface_referenced_record(tmp_path):
    ...

def _by_check(findings) -> dict[str, qc.Finding]:
    ...

def test_config_sanity_fails_on_a_species_default_body_length(tmp_path):
    ...

def test_config_sanity_fails_when_length_cm_is_null(tmp_path):
    ...

def test_config_sanity_reports_the_default_over_measured_ratio(tmp_path):
    """A measured length carried alongside ``species_default`` is still a FAIL,
    and the finding quantifies how far off the default is."""
    ...

def test_config_sanity_passes_on_a_measured_length(tmp_path):
    ...

def test_config_sanity_warns_when_length_source_is_unrecorded(tmp_path):
    ...

def test_config_sanity_fails_on_missing_endpoints(tmp_path):
    ...

def test_config_sanity_passes_with_both_endpoints(tmp_path):
    ...

def test_config_sanity_warns_on_a_null_timezone(tmp_path):
    ...

def test_config_sanity_passes_on_a_set_timezone(tmp_path):
    ...

def _write_cal(path: Path, A, b, target=1.0, cost=1.0, n=1000, validation=None) -> Path:
    ...
FLAGSHIP_INFLIGHT_TARGET = 1.0019414391587782

def _validation(occupied_cells=48, n_cells=48, min_eig=0.0967, **extra):
    """A ``validation`` block in the shape ``calibrate mag --in-flight`` writes."""
    ...

def test_calibration_gate_fails_on_a_collapsed_axis(tmp_path):
    """``LS_250326/mag.json`` shape: ``A[2][2] = 1.35e-08``, cost 21039."""
    ...

def _mag_finding(tmp_path, cal):
    ...

def test_calibration_gate_passes_a_real_hard_iron(tmp_path):
    """The 2026-09-06 repair, stated as a test.

    The validated in-flight fit of ``BR_260318_S3`` carries ``||A b|| / target
    = 1.7405`` -- a hard iron of 1.49 field radii, which is the physics of the
    mount and not a defect (docs/regen_2026-09.md section 16.13.3) -- and the
    old 0.5 floor FAILed it. It must now PASS, and the message must say what
    the verdict rests on.
    """
    ...

def test_calibration_gate_fails_a_runaway_mag_bias(tmp_path):
    """``LS_260415_S3@native``'s shape: the fitted centre 9.23 radii out.

    The floor is 5.0, so a runaway is still caught and the reason still names
    the statistic. Coverage here is sound, to prove the runaway clause fires on
    its own.
    """
    ...

def test_calibration_gate_fails_a_mag_fit_with_no_coverage_record(tmp_path):
    """``BR_260318/mag.json``: the refused dry-spin fit, which both fit-only
    floors pass.

    ``cond_A`` = 67.68 and ``bias_ratio`` = 0.9997 are *better* than the
    validated in-flight fit's 1.317 and 1.7405 on both counts (section 16.10),
    so nothing computed from the fit alone can refuse it. The file carries no
    ``validation`` block, so its coverage -- 1 of 48 cells, measured in section
    16.14 -- was never recorded, and that is what the check refuses on.
    """
    ...

def test_calibration_gate_fails_a_mag_fit_on_recorded_coverage(tmp_path):
    """A ``validation`` block that records a cap of the sphere is refused on it.

    1 of 48 cells is the refused dry-spin fit's own coverage. The floors are
    the heading family's, read from :mod:`anchor.qc` rather than restated, so
    ``calibration.mag`` and ``heading.coverage`` cannot drift apart.
    """
    ...

def test_calibration_gate_reports_dip_statistics_without_gating_them(tmp_path):
    """A wide dip MAD is reported and deferred, not scored here.

    The heading family scores the dip on the calibration *in use*; a second
    opinion computed from the file alone would print different numbers next to
    it. The finding therefore names the checks that own the verdict.
    """
    ...

def test_calibration_gate_keeps_the_accel_floor_at_half(tmp_path):
    """The accel branch is untouched: no hard iron, so 0.5 still means runaway.

    The magnetometer floor moved to 5.0 and the accelerometer's did not, and an
    accel fit is not asked for a coverage record either.
    """
    ...

def test_calibration_gate_passes_a_sound_accel_fit(tmp_path):
    ...

def test_calibration_gate_fails_on_a_missing_file(tmp_path):
    ...

def test_calibration_gate_warns_when_none_is_referenced(tmp_path):
    ...

def test_run_doctor_assembles_and_writes_a_report(tmp_path, monkeypatch):
    ...

def test_run_doctor_fails_cleanly_on_a_missing_raw_csv(tmp_path):
    ...

def test_run_doctor_fails_cleanly_on_a_header_only_raw_csv(tmp_path):
    """A truncated export must produce a FAIL, not a traceback.

    Regression: ``probe_raw_csv`` returned a ``RawProbe`` whose head frame had
    no ``datetime`` column, and ``check_time_axis`` then raised
    ``KeyError: 'datetime'`` outside ``run_doctor``'s guard.
    """
    ...

def test_report_table_has_one_line_per_finding(tmp_path):
    ...

def test_qc_section_renders_levels_as_tags(tmp_path):
    ...

@pytest.mark.needs_data
def test_apt_240702_s2_reproduces_the_swapped_timestamp_and_25_hz_defects():
    ...

@pytest.mark.needs_data
def test_ls_250326_magnetometer_fit_is_gated_as_degenerate():
    """The 2025 dry-spin fit is refused, asserted against the fit itself.

    Until 2026-09-06 this reached the file through ``LS_250326_S2.yaml``. That
    config now points at a sound in-flight fit of the same record, so gating it
    through a deployment asserted FAIL on a calibration that correctly passes.
    The refusal is a property of the fit and is asserted as one.
    """
    ...

def test_stage_zero_logs_findings_without_raising(tmp_path, monkeypatch, caplog):
    ...

def test_stage_zero_swallows_a_doctor_failure(tmp_path, monkeypatch, caplog):
    """A bug in the health check must never stop a pipeline that used to work."""
    ...

def _promote_length(cfg, length_cm=46.5, source='measured'):
    """``cfg`` with a measured body length — the §10 config edit."""
    ...

def test_run_doctor_stamps_the_report_with_the_config_and_the_raw_file(tmp_path):
    ...

def test_write_report_round_trips_the_stamp(tmp_path, monkeypatch):
    ...

def test_a_length_promotion_invalidates_the_stamp(tmp_path):
    """The §10 defect exactly: ``length_cm`` moves, the doctor's verdict moves
    with it, so the cached report must not be reused."""
    ...

def test_the_ingest_fingerprint_alone_would_miss_the_length_promotion(tmp_path):
    """Why the whole config is hashed rather than ``io.ingest_fingerprint``:
    ``animal`` does not change the interim parquet, so the ingest hash is
    blind to the one edit that moved a doctor finding."""
    ...

def test_a_rewritten_raw_csv_invalidates_the_stamp(tmp_path):
    ...

def test_a_vanished_raw_csv_invalidates_the_stamp(tmp_path):
    """A PASS on a file that is no longer there is a stale PASS."""
    ...

def test_the_mtime_alone_does_not_invalidate_the_stamp(tmp_path):
    """Copying ``data/raw`` rewrites every mtime without changing a byte."""
    ...

def test_an_unstamped_report_is_never_current(tmp_path):
    """Every ``_qc.json`` on disk today predates the stamp."""
    ...

def _cfg_with_accel_cal(tmp_path: Path, cal: Path):
    ...

def test_the_stamp_records_the_contents_of_every_referenced_calibration(tmp_path):
    ...

def test_a_refitted_calibration_invalidates_the_stamp(tmp_path):
    """The re-fit rewrites the same path, so nothing the config hash sees moves."""
    ...

def test_a_vanished_calibration_invalidates_the_stamp(tmp_path):
    ...

def test_touching_a_calibration_file_does_not_invalidate_the_stamp(tmp_path):
    """Contents, not mtime: syncing ``data/`` must not force a doctor re-run."""
    ...
HEADING_DIP_DEG = 60.8

def _heading_rotations(n: int):
    """Slow, sphere-covering attitude — see tests/ingest/test_mag_inflight.py."""
    ...

def heading_record(*, n_mag: int=700, block: int=25, mapping: str='x,y,z', b=(430.0, -260.0, 520.0), field: float=400.0, with_mag: bool=True):
    """``(acc, mag)`` on the full 25 Hz grid; ``mag`` is NaN off the 1 Hz rows.

    The default hard iron is 1.7x the field radius, which is what every raw
    magnetometer cloud in this archive looks like — so the *uncalibrated*
    record fails the dip test and the fit of it passes, which is the pair the
    family exists to tell apart.
    """
    ...

def write_heading_csv(path: Path, acc, mag, *, fs: float=25.0, start: str='2026-03-18 09:00:00') -> Path:
    """An AXY-5-shaped CSV carrying accX/Y/Z and a 1 Hz magX/Y/Z."""
    ...

def heading_deployment(tmp_path: Path, monkeypatch, *, mapping: str='x,y,z', with_mag: bool=True, site: str | None='Elkhorn Slough', ingest: bool=True, **deploy):
    """A synthetic deployment on disk, optionally ingested to an interim parquet."""
    ...

def _heading(findings) -> dict[str, qc.Finding]:
    ...

def test_the_heading_family_fails_a_raw_uncalibrated_magnetometer(tmp_path, monkeypatch):
    """The flagship's state, synthesised: `calibration.mag` null, hard iron 1.7
    field radii, and a "heading" that is a function of posture."""
    ...

def test_the_heading_family_passes_an_in_flight_calibration(tmp_path, monkeypatch):
    ...

def test_the_axis_mapping_finding_names_the_permutation_the_data_prefer(tmp_path, monkeypatch):
    """A reflected magnetometer: the pipeline's identity is 180 deg wrong and
    the doctor says which permutation is right."""
    ...

def test_a_deployment_with_no_magnetometer_warns_and_fails_the_gate(tmp_path, monkeypatch):
    """WARN for the doctor, FAIL for the gate: a behaviour-only record is not a
    defective record, but nothing positional may be published from it."""
    ...

def test_a_deployment_with_no_site_cannot_be_dip_tested(tmp_path, monkeypatch):
    ...

def test_an_explicit_dip_override_replaces_the_missing_site(tmp_path, monkeypatch):
    ...

def test_the_heading_check_reads_the_interim_parquet_when_the_cache_is_valid(tmp_path, monkeypatch):
    ...

def test_the_heading_check_falls_back_to_the_csv_and_agrees_with_the_parquet(tmp_path, monkeypatch):
    """The two branches must produce the same numbers, or the verdict depends
    on whether someone happened to have run the ingest."""
    ...

def test_the_magnetometer_rate_finding_reports_the_1_hz_block(tmp_path, monkeypatch):
    ...

def test_every_heading_finding_carries_the_floor_it_was_judged_against(tmp_path, monkeypatch):
    """The ledger scores G-heading from these entries, so the gate's floors are
    the doctor's constants by construction."""
    ...

def test_run_doctor_includes_the_heading_family_and_can_be_asked_not_to(tmp_path, monkeypatch):
    ...

@pytest.mark.needs_data
def test_the_flagship_heading_is_a_measurement_of_posture():
    """``docs/regen_2026-09.md`` sections 14 and 16, as a regression test."""
    ...

def _detach_deployment(tmp_path, monkeypatch, *, quiet_minutes, moving_minutes, surface_minutes, moving_after_minutes=0, fs=25.0, keyed=True):
    """A deployment with an interim parquet: ``moving`` at depth, then
    ``quiet`` at depth, then optionally ``moving`` again, then ``surface`` at
    zero depth.

    ``moving_after_minutes`` is what makes a quiet run *end*. Without it the
    quiet block runs into the surface block, which is quiet too, and the two
    are one run — which is the flagship's own shape and not the case a length
    floor is for.
    """
    ...

def test_the_stationary_span_check_warns_with_the_hours_and_the_fraction(tmp_path, monkeypatch):
    """90 quiet minutes inside a 190-minute attached span is 47 % of it."""
    ...

def test_the_stationary_span_check_passes_when_nothing_stops_moving(tmp_path, monkeypatch):
    ...

def test_a_quiet_run_under_the_floor_does_not_warn(tmp_path, monkeypatch):
    """59 minutes is a rest, not a record ending — the 60 min floor holds."""
    ...

def test_the_stationary_span_check_is_silent_without_a_keyed_parquet(tmp_path, monkeypatch):
    """A check that could not run must not read as a check that passed.

    Calibration is baked into the interim parquet at write time, so one
    written from a different config carries the wrong accelerations on the
    wrong rows; there is no verdict to give from it.
    """
    ...

def test_run_doctor_carries_the_stationary_span_finding(tmp_path, monkeypatch):
    ...

@pytest.mark.needs_data
def test_the_flagship_attached_span_is_44_9_percent_a_motionless_tag():
    """``docs/regen_2026-09.md`` §17.4.2, as a doctor finding."""
    ...

@pytest.mark.parametrize('max_period_s, level', [(None, None), (2.0, 'FAIL'), (1.0, 'WARN'), (0.5, 'PASS')])
def test_config_sanity_checks_lowpass_against_the_slowest_beat(tmp_path, max_period_s, level):
    ...

def test_dynamic_fraction_matches_the_filter():
    """The closed form is what add_dynamic_acceleration actually keeps."""
    ...
