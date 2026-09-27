"""Smoke test for the AXY trajectory-ingest module on real LS_260311 data."""
from __future__ import annotations
from pathlib import Path
import numpy as np
import pytest
from anchor.trajectory.axy_ingest import IngestedTrack, ingest_deployment

@skipif_missing
def test_ingest_real_ls_deployment():
    ...

@skipif_missing
def test_ingest_to_dataframe_columns():
    ...

class _ServedTheCache(Exception):
    """Sentinel: ingest_deployment took the cached-parquet branch."""

class _ReIngested(Exception):
    """Sentinel: ingest_deployment fell through to load_deployment."""

@pytest.fixture
def cache_branch(monkeypatch):
    """Stub both branches so the test observes only *which* one was chosen."""
    ...

def _cache_cfg(raw_csv: Path, accel_json: Path | None=None):
    ...

def _seed_interim(tmp_path: Path, sidecar_cfg) -> Path:
    """A parquet that exists, keyed to ``sidecar_cfg``. Contents are irrelevant:
    ``cache_branch`` stubs read_parquet, so only the gate's verdict is under
    test."""
    ...

def test_cached_parquet_is_served_when_the_sidecar_matches(tmp_path, monkeypatch, cache_branch):
    ...

def test_repointed_calibration_invalidates_the_cached_parquet(tmp_path, monkeypatch, cache_branch):
    """The BR_260318_S3 case: the parquet on disk was written from the shared
    accel fit, the YAML now names the deployment's own. Gating on existence
    alone serves the old calibration forever."""
    ...

def test_changed_clip_invalidates_the_cached_parquet(tmp_path, monkeypatch, cache_branch):
    ...

def test_parquet_without_a_sidecar_is_treated_as_stale(tmp_path, monkeypatch, cache_branch):
    """A parquet predating the keying carries no record of its config, so it
    cannot be trusted."""
    ...

def test_use_cached_parquet_false_still_re_ingests(tmp_path, monkeypatch, cache_branch):
    ...

def _tailbeat_cfg(raw_csv: Path, **tailbeat):
    ...

def _synthetic_axy(fs=25.0, seconds=200.0, f_beat=1.0, amp=0.08, seed=3):
    """A clean beat on accZ over gravity, with a magnetometer that turns."""
    ...

@pytest.fixture
def served_synthetic(tmp_path, monkeypatch):
    """Serve ``_synthetic_axy`` from the cached-parquet branch."""
    ...

def test_species_tailbeat_block_reaches_the_picker(served_synthetic, monkeypatch):
    ...

def test_the_forwarded_prominence_is_load_bearing(served_synthetic):
    """The same record, two thresholds: the beat survives one and not the other.

    Passing the parameter is not enough — this is the test that would have
    caught the defect, because it fails identically whether the block is
    dropped on the floor or forwarded and ignored.
    """
    ...

def test_a_null_configured_prominence_still_falls_back_to_the_noise_floor(served_synthetic):
    """``prominence: null`` is the documented "derive it and warn" branch."""
    ...

def test_the_stale_bound_reaches_the_speed_channel(served_synthetic, monkeypatch):
    """A record that stops beating must stop producing speed.

    Before the bound, the last interval was carried to the end of the record,
    so a tag that went still kept its last tail beat and its last speed for as
    long as the deployment lasted.
    """
    ...
