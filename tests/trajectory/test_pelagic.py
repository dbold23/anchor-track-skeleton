"""Pelagic / open-coastal site geometry tests."""
from __future__ import annotations
from anchor.trajectory.sites import pelagic

def test_outer_monterey_bbox_sane():
    """BBox covers Monterey + Año Nuevo and is well-formed."""
    ...

def test_pelagic_disables_polygon_constraint():
    """Open-coastal mode must skip the estuarine polygon constraint."""
    ...

def test_process_noise_states_cover_hmm_labels():
    """All 4 HMM states have a process-noise σ defined for pelagic mode."""
    ...

def test_is_pelagic_site_predicate():
    ...

def test_ndbc_and_coops_stations_listed():
    """Wind + water-level station IDs must be present for the SMC end-anchor pipeline."""
    ...

def test_declination_is_recent_epoch():
    """Declination at outer Monterey @ 2026.3 epoch matches the WMM 2025 value."""
    ...
