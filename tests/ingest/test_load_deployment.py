"""End-to-end loader: config → raw CSV → normalized + parsed + cached parquet."""
from __future__ import annotations
import json
import logging
import os
from pathlib import Path
import numpy as np
import pandas as pd
import pytest
from pydantic import ValidationError
from anchor.ingest import io
from anchor.ingest.config import DeploymentConfig

def _make_cfg(raw_csv: Path, deployment_id: str, schema: str, **extra) -> DeploymentConfig:
    ...

def test_load_deployment_ls(tmp_path, monkeypatch, ls_csv):
    ...

def test_load_deployment_ws_axy_depth(tmp_path, monkeypatch, ws_axy_csv):
    ...

def test_load_deployment_ws_cats(tmp_path, monkeypatch, ws_cats_csv):
    ...

def test_load_deployment_applies_clip_and_records_it(tmp_path, monkeypatch, ls_csv):
    ...

def test_load_deployment_applies_deploy_window(tmp_path, monkeypatch, ws_axy_csv):
    ...

def test_load_deployment_warns_when_the_configured_rate_is_wrong(tmp_path, monkeypatch, ls_csv, caplog):
    """APT_240702_S2 runs a 50 Hz species default over a 25 Hz record."""
    ...

def test_load_deployment_writes_a_sidecar_keyed_to_the_window(tmp_path, monkeypatch, ls_csv):
    ...

def test_changed_clip_invalidates_the_interim_cache(tmp_path, monkeypatch, ls_csv):
    """The regression this closes: a re-clipped deployment served a stale parquet."""
    ...

def test_changed_calibration_path_invalidates_the_interim_cache(tmp_path, monkeypatch, ls_csv):
    ...

def test_a_sidecarless_parquet_is_treated_as_stale(tmp_path, monkeypatch, ls_csv, caplog):
    """Every parquet already on disk predates this keying and must regenerate."""
    ...

def _local_raw(tmp_path: Path, source: Path) -> Path:
    """Copy a session-scoped CSV fixture so a test may mutate or delete it."""
    ...

def test_ingest_fingerprint_is_stable_across_the_raw_csv_disappearing(tmp_path, monkeypatch, ls_csv):
    ...

def test_interim_cache_survives_an_absent_raw_csv(tmp_path, monkeypatch, ls_csv, caplog):
    """Interim present, raw absent: accept the cache rather than crash on re-ingest."""
    ...

def test_sidecar_records_the_raw_csv_size_outside_the_hash(tmp_path, monkeypatch, ls_csv):
    ...

def test_a_re_exported_raw_csv_invalidates_the_interim_cache(tmp_path, monkeypatch, ls_csv, caplog):
    ...

def test_touching_the_raw_csv_does_not_invalidate_the_interim_cache(tmp_path, monkeypatch, ls_csv):
    """A cp -r or cloud sync rewrites mtimes; that must not re-parse 605 MB."""
    ...

def _dual_axis_csv(path: Path, *, n: int=2000, step_s: float=0.04, start: str='2024-07-02 22:16:45', swap: bool=False, pair: bool=True) -> Path:
    """``APT_240702_S2``-shaped CSV: ``Date`` + ``Time`` *and* ``Timestamp``.

    ``swap`` transposes month and day in ``Timestamp`` only; ``pair=False``
    writes ``Timestamp`` alone, i.e. a file with nothing to cross-check against.
    """
    ...

def test_load_deployment_uses_date_time_over_a_swapped_timestamp(tmp_path, monkeypatch, caplog):
    """The interim parquet must carry the record's real axis, not the swap's."""
    ...

def test_load_deployment_refuses_an_axis_that_cannot_be_the_record(tmp_path, monkeypatch):
    """No Date+Time to fall back on: refuse rather than cache a 2140 h grid."""
    ...

def test_bumping_the_ingest_schema_version_invalidates_the_interim_cache(tmp_path, monkeypatch, ls_csv, caplog):
    """A parser fix must expire caches it silently changes the contents of."""
    ...

def test_load_deployment_applies_the_declared_mount_rotation(tmp_path, monkeypatch, ls_csv):
    """``tag.axes_rotation_deg`` was read by no code outside ``sim/``; now it is.

    Fails on the old loader, which returned the tag-frame columns unchanged.
    """
    ...

def test_load_deployment_body_alignment_is_the_no_op_default(tmp_path, monkeypatch, ls_csv):
    """Every shipped YAML declares [0, 0, 0]; those records must not move."""
    ...

def test_a_changed_mount_rotation_invalidates_the_interim_cache(tmp_path, monkeypatch, ls_csv):
    """The parquet is body-frame now, so the mount is part of its identity."""
    ...

@pytest.mark.parametrize('bad', [[0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, float('nan'), 0.0], [0.0, 0.0, 350.0]])
def test_config_rejects_an_unusable_axes_rotation(bad, ls_csv):
    """The field is load-bearing now, so a typo must fail at config load."""
    ...
