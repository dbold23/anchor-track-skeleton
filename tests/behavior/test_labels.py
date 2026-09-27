"""Video-label ingest + alignment + window projection."""
from __future__ import annotations
import json
import pandas as pd
import pytest
from anchor.behavior import labels as LB

def test_load_boris_export_roundtrips(tmp_path):
    ...

def test_load_boris_export_handles_whitespace_columns(tmp_path):
    ...

def test_load_boris_export_requires_behavior_and_start(tmp_path):
    ...

def test_load_via_export_temporal():
    ...

def test_load_via_export_empty_returns_empty_df(tmp_path):
    ...

def test_align_to_accel_applies_offset():
    ...

def test_align_to_accel_drops_out_of_range():
    ...

def test_align_to_accel_clips_edges():
    ...

def test_labels_to_windows_majority_vote():
    ...

def test_labels_to_windows_no_coverage_is_nan():
    ...

def test_labels_to_windows_empty_labels_returns_nan_labels():
    ...

def test_select_uncertain_windows_entropy():
    ...

def test_select_uncertain_windows_margin():
    ...

def test_select_uncertain_requires_probs():
    ...

def test_labels_to_windows_respects_non_contiguous_index():
    ...

def test_select_uncertain_never_returns_rows_without_probs():
    ...
