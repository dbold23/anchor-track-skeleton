"""Unit tests for the tide-height layer.

Exercises:
    - Synthetic harmonic determinism (offline path always available).
    - TideSeries interpolation, derivative, and bounds checking.
    - get_tide_series dispatcher behavior on synthetic source.
    - NOAA payload parser against a recorded fixture (no live HTTP).
"""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import pandas as pd
import pytest
from anchor.trajectory.tides import TideSeries, get_tide_series, synthetic_tide_height, synthetic_tide_series
from anchor.trajectory.tide_fetch import _noaa_payload_to_tide_series

def test_synthetic_determinism():
    ...

def test_synthetic_tide_series_construction():
    ...

def test_value_at_returns_exact_value_at_sample_times():
    ...

def test_value_at_interpolates_between_samples():
    ...

def test_value_at_array_input():
    ...

def test_derivative_matches_numerical_gradient():
    ...

def test_get_tide_series_synthetic_dispatcher():
    ...

def test_get_tide_series_unknown_source_raises():
    ...

def test_get_tide_series_bad_window_raises():
    ...

def test_tide_series_rejects_singleton():
    ...

def test_tide_series_rejects_unsorted():
    """The class auto-sorts on construction; the only way to fail strict
    increase is repeated timestamps."""
    ...

def test_noaa_payload_parser_against_recorded_fixture():
    ...

def test_noaa_payload_error_field_is_raised():
    ...

def test_tide_series_survives_a_pickle_round_trip():
    """The grid's worker pool pickles the tide series along with the current
    field built from it, and the derivative cache is warmed lazily — so the
    round trip has to be exercised both cold and warm."""
    ...

def test_synthetic_tide_is_on_mllw_datum():
    """Heights are metres above MLLW: the long-run mean sits at MSL (~0.86 m)
    and lows rarely dip far below zero."""
    ...
