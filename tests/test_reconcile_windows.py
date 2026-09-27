"""``scripts/reconcile_windows.py``'s row logic, unit-tested without parquet.

``docs/window_reconciliation.md`` is a generated document that makes concrete
remediation recommendations, so the functions that decide *which* recommendation
a deployment gets are the part that has to be pinned. All of them are pure
functions of a row dict or of ``(cfg, t_start, t_end)`` and need no data on
disk; the parquet-reading half (`_block_means`, `reconcile_one`) is exercised by
running the script, which needs `data/interim` and so cannot run in CI.

Three behaviours are guarded, all of them corrections to earlier drafts of the
document that stated the wrong thing:

* an operator clip that the configured export has *already* applied must not be
  used as the operator reference, marked as pending, or recommended for
  promotion into ``clip:`` — promoting it would clip an already-clipped record;
* ``deploy_window`` must be reported against the record it actually selects
  from, as disjoint / partial / covers, not merely quoted;
* the ``clip (prose)`` cell must say which of the two cases a row is.
"""
from __future__ import annotations
import importlib.util
import warnings
import sys
from pathlib import Path
from types import SimpleNamespace
import pandas as pd
import pytest

def _load_module():
    ...

@pytest.fixture(scope='module')
def rw():
    ...

def _cfg(**kw):
    """Minimal stand-in for a DeploymentConfig: only these fields are read."""
    ...

def test_operator_end_prefers_the_declared_clip_field(rw):
    ...

def test_operator_end_uses_a_prose_clip_the_export_has_not_applied(rw):
    """`BR_260318_S3`: full-length raw export, clip recorded only in prose."""
    ...

def test_operator_end_skips_an_already_applied_prose_clip(rw):
    """`LS_250326_S8`: sample 680000 is off the end of the clipped export.

    Using it as the reference compares the detector against a sample index that
    does not exist in the record on disk, so the `agree?` column would be a
    comparison with a fictional operator statement.
    """
    ...

def test_operator_end_falls_back_to_the_window_when_the_prose_clip_is_applied(rw):
    ...

def test_operator_end_is_none_without_any_operator_statement(rw):
    ...

def test_window_vs_record_reports_a_disjoint_window(rw):
    """`LS_260311_S1`: the window sits a whole day off the record."""
    ...

def test_window_vs_record_reports_a_partial_window_with_the_fraction_dropped(rw):
    """Hand-computed: a 10 h record, a window that keeps its first 6 h."""
    ...

def test_window_vs_record_reports_a_covering_window(rw):
    ...

def test_window_vs_record_is_none_without_a_window(rw):
    ...

def test_window_cell_renders_each_status(rw):
    ...

def _row(**kw):
    ...

def test_build_table_marks_an_already_applied_prose_clip(rw):
    """`n_rows == end - start` is the evidence; the cell must show it."""
    ...

def test_build_table_leaves_an_unapplied_prose_clip_unmarked(rw):
    ...

def test_findings_recommend_promoting_only_the_unapplied_clip(rw):
    ...

def test_notes_tell_an_already_applied_clip_not_to_be_promoted(rw):
    ...

def _synthetic_document(tail: str=SYNTHETIC_TAIL) -> str:
    ...

def test_hand_written_tail_starts_at_the_first_hand_maintained_heading(rw):
    ...

def test_hand_written_tail_round_trips_the_whole_document(rw):
    """Split then rejoin must be the identity — that is the whole guarantee."""
    ...

def test_hand_written_tail_is_empty_when_the_document_has_none(rw):
    ...

def test_hand_written_tail_keeps_a_dated_section_without_an_appendix(rw):
    ...

def test_render_document_re_emits_the_tail_verbatim(rw):
    """The regression: `build_document` alone destroyed the appendix."""
    ...

def test_render_document_without_an_existing_document(rw):
    ...

def _require_openpyxl():
    """`openpyxl` reads and writes .xlsx for pandas, and nothing in the project's
    dependency graph requires it: `pyproject.toml`'s `dev` extra is
    `pytest`/`pytest-cov`/`ruff` and CI installs `.[dev,trajectory]`. Without
    this guard every workbook test errors on a clean CI checkout."""
    ...

def _write_workbook(path: Path, records: list[dict]) -> Path:
    """A stand-in for `AXY_DeploymentMetadata.xlsx` with the real column names."""
    ...

@pytest.fixture()
def workbook(tmp_path):
    ...

def test_the_join_finds_the_row_the_yaml_comment_never_reached(rw, workbook):
    """`LS_260311_S1`: in the sheet all along, blank in the table."""
    ...

def test_the_join_reproduces_every_clip_the_hardcoded_table_carried(rw, workbook):
    ...

def test_the_join_records_that_a_clip_was_written_as_approximate(rw, workbook):
    """`LS_25032608`'s cells read `5000 about` / `680000 about`."""
    ...

def test_the_join_does_not_borrow_a_sibling_deployments_clip(rw, workbook):
    """`LS_250326_S2` is `LS_25032603`, whose clip cells are blank.

    Both 2025-03-26 rows share the `LS_250326` prefix, so a date-only match
    would hand S2 the S8 range. The `raw_csv` path names the row.
    """
    ...

def test_the_join_declines_an_ambiguous_prefix(rw, workbook):
    """Two `APT240702` rows and no path match: no clip rather than a guess."""
    ...

def test_the_join_returns_nothing_for_a_deployment_absent_from_the_sheet(rw, workbook):
    ...

def test_a_missing_workbook_is_not_an_error(rw, tmp_path):
    ...

def test_a_workbook_without_the_clip_columns_is_an_error(rw, tmp_path):
    ...

def test_build_table_marks_a_promoted_clip_as_promoted(rw):
    """`LS_260311_S1`: `n_rows == end - start` because `clip:` did it."""
    ...

def test_notes_do_not_tell_a_promoted_clip_not_to_be_promoted(rw):
    ...

def test_findings_do_not_claim_no_deployment_sets_clip_once_one_does(rw):
    ...

def test_the_generated_half_never_looks_hand_written(rw):
    """The split is by heading, so a generated heading matching the pattern
    would cut the document in half and lose the table."""
    ...

def test_operator_end_measures_a_promoted_clip_from_the_clipped_records_t0(rw):
    """`LS_260311_S1`: `clip: [15000, 635000]` at 25 Hz over a 620,000-row record.

    `apply_analysis_window` slices `out.iloc[start:clipped_end]`, so the interim
    parquet's first row IS raw sample 15000 — the operator's end sample is
    `635000 - 15000` samples into the record, not 635000. Reading it as
    `635000 / fs` puts the reference at 25400 s against a record that ends at
    24800 s: 600 s past its own end, a 10 min bias against a 15 min tolerance.
    """
    ...

def test_operator_end_declines_a_clip_whose_end_was_clamped_off_the_record(rw):
    """A `clip:` end past the raw record is clamped at ingest, so the operator's
    end sample is not in the record at all — the same situation as an
    already-applied prose clip, and there is nothing to compare against."""
    ...

def test_a_thousands_separator_is_not_read_as_a_five_sample_clip(rw):
    """`5,000` search-matched as `5` is a clip index three orders of magnitude
    wrong, published with `000` printed as if it were the operator's word."""
    ...

def test_a_qualifier_before_the_number_is_still_parsed(rw):
    ...

def test_a_cell_that_does_not_parse_cleanly_yields_no_clip_from_the_sheet(rw, tmp_path):
    ...

def test_a_promoted_clip_is_marked_when_the_interim_parquet_is_absent(rw, tmp_path, monkeypatch):
    """`prose_clip_promoted` depends on `clip:` and the sheet, both known before
    `reconcile_one` returns early on a missing parquet — and regenerating an
    interim parquet (a `--force` re-ingest deletes and rewrites one) is the
    routine operation the document's own findings recommend."""
    ...

def test_the_document_does_not_contradict_itself_without_a_parquet(rw, tmp_path, monkeypatch):
    """The table printing `clip (YAML)` while the findings forty lines above say
    no deployment sets it is the exact false statement this pass removes.

    The promoted row is built by `reconcile_one` rather than by `_row`, because
    `_row` would take `prose_clip_promoted` as an argument and pin only the two
    renderers — the defect was in the row builder that feeds them.
    """
    ...

def test_the_promoted_note_claims_a_row_count_only_when_a_record_backs_it(rw):
    """"which is why the record is exactly 620,000 rows" is a claim about a file
    on disk; without the parquet there is no such file to describe."""
    ...

def test_the_promoted_finding_claims_a_row_count_only_when_a_record_backs_it(rw):
    """The finding pairs with the note fixed above and makes the same claim, in
    the more prominent renderer: "the record on disk is exactly its length" is
    a statement about a file, and a `--force` re-ingest deletes that file."""
    ...

def test_the_promoted_finding_scopes_the_row_count_to_the_records_that_back_it(rw):
    """With one promoted clip backed by a parquet and one not, the length claim
    names the backed deployment instead of covering both."""
    ...

def test_an_unreadable_clip_cell_warns_instead_of_vanishing(rw, tmp_path):
    """The module raises on a sheet whose columns moved because "silently
    returning no clips would look exactly like an operator who declared none";
    a cell that will not parse drops one clip end for the same reason."""
    ...

def test_a_blank_clip_cell_does_not_warn(rw, tmp_path):
    """The operator leaving both cells empty is a declaration, not a defect."""
    ...

def test_operator_end_measures_a_prose_clip_from_the_applied_clips_origin(rw):
    """`clip:` clamped off the record falls through to the prose range — but the
    record was still clipped, so its t0 is raw sample `clip[0]` and the prose
    end sample lands `prose[1] - clip[0]` samples in. Reading `prose[1] / fs`
    puts the reference 600 s past a record that is 24,800 s long."""
    ...

def test_operator_end_declines_a_prose_end_past_the_record(rw):
    """No clip applied, so t0 is raw sample 0 — and an end sample beyond the
    last row is not in the record to be compared against."""
    ...

def _unclassifiable(deployment_id):
    """A prose clip, no `clip:`, and no parquet — so `prose_clip_already_applied`
    was never computed and the row cannot be sorted into promote / never-promote.
    """
    ...

def test_findings_do_not_recommend_promoting_a_clip_they_cannot_classify(rw):
    """`prose_clip_already_applied` needs the record's row count, so it is absent
    without a parquet — and `not r.get(...)` read that absence as "safe to
    promote", recommending exactly the operation the same document elsewhere says
    would clip an already-clipped export a second time."""
    ...

def test_findings_classify_only_the_deployments_whose_record_is_on_disk(rw):
    ...

def test_findings_report_an_unclassified_clip_even_when_it_is_the_only_one(rw):
    """The promotion paragraph is gated on there being something to say about a
    clip; an unclassifiable one is something to say."""
    ...

def test_the_note_for_an_unclassified_clip_does_not_describe_the_export(rw):
    """"the pipeline ingests the whole record" reads as "the whole raw record",
    which is untrue of an already-clipped `_CLEAN` export — and whether this is
    one is precisely what the missing parquet leaves undecided."""
    ...
