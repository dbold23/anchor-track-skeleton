"""Tests for anchor.track.wind_fetch — parsing + cache, no network."""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import pandas as pd
import pytest
from anchor.trajectory.wind_fetch import fetch_ndbc_wind, parse_ndbc_text

def test_parse_ndbc_realtime2_text():
    """3 data rows, three cardinal wind directions:
       WDIR=270 (from west) → +u_east, 0 v
       WDIR=000 (from north) → 0 u, -v_north
       WDIR=090 (from east)  → -u_east, 0 v
    """
    ...

def test_parse_skips_missing_data_sentinels():
    ...

def test_cache_roundtrip(tmp_path):
    """Pre-seed the cache with a synthetic payload, then fetch with
    allow_network=False. Verifies the cache key + parse path work."""
    ...

def test_month_digit():
    ...

def test_url_templates():
    """Verify the closed-year + current-year monthly URLs format correctly."""
    ...

def test_gzip_decode_in_http_helper(tmp_path, monkeypatch):
    """_http_get_text_with_backoff auto-decodes gzip when URL ends in .gz."""
    ...

def test_fetch_raises_when_no_cache_and_no_network(tmp_path):
    ...
