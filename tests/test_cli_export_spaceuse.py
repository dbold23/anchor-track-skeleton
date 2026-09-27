"""CLI smoke tests for `anchor export` and `anchor spaceuse`."""
from __future__ import annotations
import numpy as np
from typer.testing import CliRunner
from anchor import export as EX
from anchor.cli import app

def _write_track_parquet(path, n=12):
    ...

def test_cli_export_geojson(tmp_path):
    ...

def test_cli_export_movebank_and_netcdf(tmp_path):
    ...

def test_cli_spaceuse_plain_and_energy(tmp_path):
    ...
