"""Unit tests for the tidal-current field.

Exercises:
    - Centerline projection (point-to-line, arc-length, tangent bearing).
    - CurrentField.from_tide_series produces the expected sign + magnitude
      from a synthetic tide.
    - Decay profile interpolation (mouth → Kirby Park → upper marsh).
    - CurrentField.from_csv round-trip on a written CSV.
    - CurrentField.zero is genuinely zero everywhere.
"""
from __future__ import annotations
from pathlib import Path
import numpy as np
import pandas as pd
from anchor.trajectory.currents import Centerline, CurrentField
from anchor.trajectory.tides import synthetic_tide_series
from anchor.trajectory.sites.elkhorn import ELKHORN_CURRENT_DECAY_PROFILE, ELKHORN_TIDAL_PRISM_K_M

def _project_lonlat_to_utm(lon, lat):
    ...

def test_centerline_loads_from_geojson():
    ...

def test_centerline_project_returns_arc_and_bearing():
    ...

def test_centerline_arc_increases_along_axis():
    """Two points along the slough's main axis should produce monotone
    increasing arc lengths."""
    ...

def test_decay_profile_attenuates_upstream():
    """Mouth current must be larger in magnitude than Kirby Park current."""
    ...

def test_zero_field_returns_zero():
    ...

def test_csv_field_round_trip(tmp_path: Path):
    ...

def test_decay_profile_starts_at_one_at_mouth():
    """Real (non-zero) field — the published Elkhorn profile starts at 1.0
    at arc=0 and decays upstream."""
    ...

def _golden_tide_field():
    ...

def test_uv_at_reproduces_the_pinned_pre_refactor_values():
    """Pin on the tide-driven field, so a change to *how* the temporal driver
    is carried cannot quietly change *what* it computes.

    Bitwise until 2026-09-25; the synthetic tide then gained its MSL-over-MLLW
    offset, a constant that the current (driven by dh/dt) cannot see but that
    moves the last bits of the differenced heights. Hence 1e-12, far below any
    change a refactor could make."""
    ...

def test_tide_driven_field_survives_a_pickle_round_trip():
    """``latent_grid_workers > 1`` runs each node in a spawned process, so the
    whole filter payload — the current field included — is pickled. A field
    that cannot cross that boundary silently costs the flagship ~8x wall clock.
    """
    ...

def test_csv_and_zero_fields_survive_a_pickle_round_trip(tmp_path: Path):
    ...
