"""Loader + schema normalization tests across all three CSV schemas."""
from __future__ import annotations
import logging
from pathlib import Path
from types import SimpleNamespace
import numpy as np
import pandas as pd
import pytest
from anchor.ingest import io
from anchor.ingest.config import load_config

def test_read_flexible_csv_axy5(ls_csv):
    ...

def test_read_flexible_csv_ws_axy_depth(ws_axy_csv):
    ...

def test_parse_datetime_timestamp(ls_csv):
    ...

def test_parse_datetime_date_time_pair(ws_axy_csv):
    ...

def test_detect_sampling_rate_ls(ls_csv):
    ...

def test_detect_sampling_rate_ws(ws_axy_csv):
    ...

def test_normalize_schema_axy5(ls_csv):
    ...

def test_normalize_schema_axy_depth(ws_axy_csv):
    ...

def test_normalize_schema_cats(ws_cats_csv):
    ...

def test_parquet_roundtrip(tmp_path, ls_csv):
    ...

def _window_cfg(**fields) -> SimpleNamespace:
    """Minimal duck-typed config for the pure window/rate helpers."""
    ...

@pytest.fixture()
def parsed_ls(ls_csv) -> pd.DataFrame:
    ...

def test_apply_analysis_window_is_a_no_op_when_nothing_is_declared(parsed_ls):
    ...

def test_apply_analysis_window_applies_clip_positionally(parsed_ls):
    ...

def test_apply_analysis_window_clamps_a_clip_past_the_end(parsed_ls, caplog):
    ...

def test_apply_analysis_window_rejects_a_clip_start_past_the_end(parsed_ls):
    ...

def test_apply_analysis_window_applies_deploy_window_inclusively(parsed_ls):
    ...

def test_apply_analysis_window_warns_when_the_timezone_is_unresolved(parsed_ls, caplog):
    ...

def test_apply_analysis_window_refuses_an_offset_endpoint_without_a_timezone(parsed_ls):
    ...

def test_apply_analysis_window_maps_an_offset_endpoint_through_the_timezone(parsed_ls):
    ...

def test_apply_analysis_window_raises_when_clip_and_window_disagree(parsed_ls):
    """An empty intersection is the signature of a clip/window contradiction."""
    ...

def test_apply_analysis_window_skips_a_disjoint_window_under_an_unresolved_clock(parsed_ls, caplog):
    """A window that selects nothing under `timezone: null` diagnoses the clock.

    The shipped `LS_260311_S1` config declares a window a full day away from its
    record in the file's own clock. Raising there would take a working
    deployment to ValueError over an ambiguity the config itself flags as
    unresolved, so the window is skipped and the full record is loaded.
    """
    ...

def test_apply_analysis_window_raises_on_a_disjoint_window_under_a_declared_clock(parsed_ls):
    """Declaring the clock removes the ambiguity, so emptiness is an error again."""
    ...

def test_apply_analysis_window_warns_naming_the_fraction_dropped(parsed_ls, caplog):
    """Partial overlap under an unresolved clock is applied, but not silently."""
    ...

def _ls_260311_label_axis() -> pd.DataFrame:
    """The `LS_260311_S1` vendor `Timestamp` column, reproduced exactly.

    Measured 2026-09-04 over all 1 404 626 rows of
    `data/raw/LeopardShark_260311/AxyD5_3_LS_260311_S1.csv`: the column is
    **not monotonic**. It carries 25 rows per label and advances the label by
    2 s — twice real time at 25 Hz — for 1500 rows, then steps *back* by
    exactly 58 s onto the true start of the next 60 s block. There are 936 such
    backward steps, every one of them −58.0 s, and all 937 block starts sit
    exactly on a 25 Hz ramp from row 0 (`2026-03-12 01:41:22`). The label
    therefore leads the record by 0 to 59 s, +29 s on average, and
    `anchor doctor` FAILs `time.continuity` on it.

    The frame carries a `row` column so a test can assert the *positional*
    range a window selects, which is the property the sawtooth destroys.
    """
    ...

def test_the_shipped_ls_260311_s1_window_does_not_break_its_own_record():
    """Regression: the real config against a faithful model of the real record.

    RESOLVED 2026-09-04 (second pass). The operator's own clip — `clip start
    point` 15000, `clip point end` 635000 on row `LS_260311` of
    `AXY_DeploymentMetadata.xlsx` — is now the config's declaration, as
    `clip:`, and `deploy_window` is null. It has to be `clip:` rather than a
    time window: the vendor `Timestamp` column is the 58 s sawtooth
    :func:`_ls_260311_label_axis` reproduces, so no wall-clock window selects a
    contiguous row range on this file at all. The clip does, exactly.

    Only the YAML is read here — the 105 MB raw CSV is not touched.
    """
    ...

def test_no_deploy_window_can_express_the_ls_260311_s1_clip():
    """Why the operator range is `clip:` and not `deploy_window:`.

    The record's label axis is non-monotonic, so a wall-clock window selects a
    *set* of rows rather than a range. The window this config shipped on
    2026-09-04 — `[01:47:00, 17:07:00]`, TagDeployed..TagRecovered converted at
    +7:00 — keeps 1 380 050 rows in three non-contiguous runs; a window written
    to the clip's own labels keeps 620 550 rows in two runs and starts 750 rows
    early. Neither is the operator's 620 000-row range, and no window is.
    """
    ...

def test_check_sampling_rate_warns_naming_both_numbers(parsed_ls, caplog):
    ...

def test_check_sampling_rate_is_quiet_when_the_config_agrees(parsed_ls, caplog):
    ...

def _dual_axis_csv(path: Path, *, n: int=2000, step_s: float=0.04, start: str='2024-07-02 22:16:45', swap: bool=False) -> Path:
    """AXY-family CSV carrying BOTH a ``Timestamp`` column and ``Date``+``Time``.

    This is the ``APT_240702_S2`` export's shape. ``swap=True`` transposes month
    and day in the ``Timestamp`` column only, reproducing that record's defect:
    ``Date=02/07/2024`` (2 July, matching the deployment id) alongside
    ``Timestamp=2024-02-07``.
    """
    ...

def test_parse_datetime_prefers_date_time_when_the_timestamp_column_is_swapped(tmp_path, caplog):
    """APT_240702_S2 in miniature: a day/month-swapped Timestamp must not win."""
    ...

def test_parse_datetime_keeps_timestamp_when_the_two_columns_agree(tmp_path, caplog):
    ...

def test_parse_datetime_records_the_source_for_a_single_column_file(ls_csv, ws_axy_csv):
    """Files carrying only one of the two keep their pre-existing behaviour."""
    ...

def test_check_time_axis_span_rejects_an_axis_that_cannot_be_the_record(tmp_path):
    """The 2140 h grid: a swapped axis is ~32x the record's real length.

    A minute per sample so the 4000 rows straddle 2-5 July, which is what turns
    the transposition into month-long jumps (2 Jul -> 7 Feb, 5 Jul -> 7 May)
    rather than a constant offset.
    """
    ...

def test_check_time_axis_span_accepts_the_repaired_axis(tmp_path):
    ...

def test_check_time_axis_span_tolerates_a_merely_wrong_sampling_rate(parsed_ls):
    """50 Hz configured over a 25 Hz record is 2x — a warning, not a refusal."""
    ...

def test_check_time_axis_span_skips_a_frame_too_short_to_judge():
    ...

def test_parse_datetime_falls_back_when_the_timestamp_column_parses_to_nothing(tmp_path, caplog):
    """An unusable Timestamp column must not empty the frame.

    Some exports write the convenience column blank. There is then nothing to
    cross-check, but preferring it anyway drops every row at ``dropna``.
    """
    ...
