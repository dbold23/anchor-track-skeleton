"""Tests for the wind math layer."""
from __future__ import annotations
from pathlib import Path
import numpy as np
import pandas as pd
import pytest
from anchor.trajectory.wind import WindSeries, get_wind_series, wind_at

def _two_point_series() -> WindSeries:
    ...

def test_wind_series_dataclass_basic():
    ...

def test_wind_series_rejects_mismatched_shapes():
    ...

def test_wind_at_interpolates_linearly():
    ...

def test_wind_at_clamps_out_of_range():
    ...

def test_get_wind_series_falls_back_to_none_when_offline(tmp_path, monkeypatch):
    """With allow_network=False and an empty cache dir, the dispatcher
    must not raise — it should return None so the leeway model can
    fall back to its Gaussian σ-budget."""
    ...

def test_wind_at_converts_aware_times_to_utc():
    ...
