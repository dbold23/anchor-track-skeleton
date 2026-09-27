"""Zero-data demo: synthetic AXY-5 generation + full-pipeline run."""
from __future__ import annotations
import numpy as np
import pandas as pd
from typer.testing import CliRunner
from anchor import demo as DEMO
from anchor.cli import app

def test_synthesize_axy5_csv_format(tmp_path):
    ...

def test_synthesize_regimes_have_distinct_activity(tmp_path):
    ...

def test_synth_track_samples_shape_and_spread():
    ...

def test_run_demo_end_to_end(tmp_path):
    ...

def test_run_demo_relative_out_dir(tmp_path, monkeypatch):
    ...

def test_cli_demo(tmp_path):
    ...
