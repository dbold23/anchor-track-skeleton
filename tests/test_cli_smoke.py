"""CLI surface smoke tests, plus guards for the two CI helper scripts.

Three cheap invariants that used to be untested:

1. Every command and sub-app registered on ``anchor.cli.app`` answers
   ``--help`` with exit code 0.  The command list is walked off the Typer app
   itself, so a newly added command is covered the moment it is registered --
   no test edit required.  This catches the usual regressions: a bad
   ``typer.Option`` default, a sub-app wired with ``add_typer`` but never
   given a name, a module-level import that only fails under the installed
   extras.
2. ``tests/fixtures/geo/*.geojson`` still matches its ``data/raw`` original
   byte-for-byte, so the committed fixture cannot drift away from the working
   file it was copied from.  Skips cleanly when the data drive is absent.
3. ``scripts/check_coverage.py`` still fails when a floor is breached.  A
   coverage gate that silently returns 0 is worse than no gate at all.
"""
from __future__ import annotations
import importlib.util
import json
import sys
from pathlib import Path
import pytest
import typer.main
from typer.testing import CliRunner
from anchor.cli import app

def _command_paths() -> list[list[str]]:
    """Every node of the CLI tree, root first, as argv prefixes.

    Group membership is duck-typed on ``.commands`` rather than tested with
    ``isinstance(cmd, click.Group)``: typer >= 0.16 builds its groups on a
    vendored click base that is not a ``click.Group`` subclass.
    """
    ...

def test_command_tree_is_discovered():
    """Guard the parametrization itself: an empty walk would vacuously pass."""
    ...

@pytest.mark.parametrize('path', COMMAND_PATHS, ids=[' '.join(p) or 'anchor' for p in COMMAND_PATHS])
def test_help_exits_zero(path: list[str]):
    ...

def _load_script(name: str):
    """Import a ``scripts/*.py`` helper; scripts/ is not an importable package."""
    ...

def test_geo_fixtures_match_data_raw():
    """Committed fixtures are byte-identical to their data/raw originals."""
    ...

def test_geo_fixture_drift_is_detected(tmp_path, monkeypatch):
    """The guard above is only useful if a byte difference actually trips it."""
    ...

def _coverage_json(tmp_path: Path, **files: tuple[int, int]) -> Path:
    """Minimal coverage.json: ``path -> (num_statements, covered_lines)``."""
    ...

def test_coverage_floors_are_enforced(tmp_path, monkeypatch):
    ...

def test_coverage_gate_fails_when_a_package_is_unmeasured(tmp_path, monkeypatch):
    """A typo'd package prefix must not pass by measuring nothing."""
    ...

def test_coverage_gate_fails_without_a_report(tmp_path, monkeypatch):
    ...
