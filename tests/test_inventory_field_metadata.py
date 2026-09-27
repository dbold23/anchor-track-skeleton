"""The second-boundary inventory must *measure* the absence, not assert it.

``scripts/inventory_field_metadata.py`` exists to turn one sentence of
``docs/design/leopard_shark_digital_twin.md`` — a leopard shark has a release
position and nothing at the other end — into a table regenerated from the field
metadata, so the claim stays true *or visibly stops being true* as new
deployments land.

An earlier revision hardcoded ``recovery_position = None``, which made the
"recovery position" column, the "second boundary?" column and the closing
``N/5`` count constants. The table would have printed ``**none**`` and ``0/5``
with full confidence against a workbook that had just gained a recovery-lat/lon
column. These tests exist so that cannot come back: they add a
recovery-position column to a copy of the real sheets and require the scan, the
table and the closing note all to change.
"""
from __future__ import annotations
import importlib.util
import sys
from pathlib import Path
import pandas as pd
import pytest

def _load_script():
    """Import the script; ``scripts/`` is not an importable package."""
    ...

@pytest.fixture(scope='module')
def inv():
    ...

@pytest.fixture
def sheets(inv):
    """Minimal stand-ins with the real workbooks' relevant column names."""
    ...

def test_scan_finds_a_recovery_position_column_when_a_workbook_gains_one(inv, sheets):
    """The claim must be able to stop being true. This is the guard on that.

    Fails against the revision that hardcoded ``recovery_position = None``:
    there, adding this column changed nothing anywhere in the output.
    """
    ...

@pytest.mark.parametrize('column', ['Retrieval GPS', 'pop-off position', 'Recapture Lat/Lon', 'recovery waypoint', 'Tag recovered coordinates'])
def test_scan_recognises_the_ways_a_recovery_position_could_be_spelt(inv, sheets, column):
    ...

def test_a_recovery_TIME_is_not_mistaken_for_a_recovery_POSITION(inv, sheets):
    """``TagRecovered`` and ``TagOFF`` are times; the fleet has those already.

    Counting them as a second *positional* boundary condition would flip the
    design's central claim on evidence that does not support it.
    """
    ...

def test_the_release_site_is_not_mistaken_for_a_recovery_position(inv, sheets):
    """``Location (GPS or Site Name)`` carries both tokens but is the release."""
    ...

def test_an_acoustic_detection_column_is_reported_too(inv, sheets):
    """A detection is the other way a second boundary condition can arrive."""
    ...

def test_release_position_is_reported_as_a_site_constant_when_it_never_varies(inv, sheets):
    ...

def test_release_position_is_reported_as_per_cast_once_it_varies(inv, sheets):
    """`sigma_m: 80.0` on the release blocks was chosen for a site constant."""
    ...

def _rows(inv, recovery_position=None):
    ...

def _provenance(inv, recovery_columns=()):
    ...

def test_table_says_no_second_boundary_on_the_shipped_metadata(inv):
    ...

def test_table_flips_to_yes_once_a_recovery_position_is_present(inv):
    """The "second boundary?" column is derived from the value, not a literal."""
    ...

def test_closing_note_names_the_scan_and_changes_when_the_scan_does(inv):
    ...

@pytest.mark.skipif(not (REPO_ROOT / 'data' / 'raw' / 'data_drop_260502').exists(), reason='data/ symlink does not resolve to the deployment archive')
def test_the_shipped_drop_still_has_no_second_positional_boundary(inv):
    """The design's claim, re-measured. If this fails the design has changed.

    Deliberately not an assertion about a hardcoded ``None``: it re-runs the
    column scan over the real workbooks, so it is a measurement of the drop.
    """
    ...
