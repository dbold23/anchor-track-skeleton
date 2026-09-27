"""The wet mask's threshold: where the water starts, and how a run moves it.

The tidal stack bakes ``(bed(MLLW) + eta) > threshold`` at 0.05 m — five
centimetres of water is water — and every mask in it stands on that number. A
0.47 m disc-width bat ray cannot swim in five centimetres, and
``docs/regen_2026-09.md`` section 22.6 leaves "a genuine exclusion from the
flats that the polygon does not encode — a minimum swimmable depth" as one of
four untested candidates for the corrected reconstruction's kilometre-scale
endpoint error. These tests pin the knob that runs that candidate: the rebuilt
stack is the shipped stack bit for bit at the baked threshold, a higher
threshold is a subset of it at every level, the knob reaches the effective
config hash, and the run says which threshold it stood on.

The current-free control is pinned here too, for the same section's third
candidate: it is the switch a current arm would be run against.
"""
from __future__ import annotations
import json
from pathlib import Path
from types import SimpleNamespace
import numpy as np
import pyproj
import pytest
import rasterio
from anchor.trajectory import run_deployment as RD
from anchor.trajectory.polygon_constraint import TidalPolygonConstraint, rebuild_wet_masks
from anchor.trajectory.sites.elkhorn import ELKHORN_BATHY_TIF, ELKHORN_OUTLINE_GEOJSON, ELKHORN_TIDE_POLYGON_STACK
NODATA = -9999.0

def _synthetic_site(tmp_path, *, shape=(6, 8), covered=slice(1, 7)):
    """Write a small GeoTIFF and an outline over part of it.

    The bed ramps from 1.0 m above MLLW to 2.0 m below it across the columns,
    so a level sweep crosses the waterline inside the raster rather than at
    its edge. One cell carries the raster's nodata.
    """
    ...

def _constraint(tmp_path, levels, threshold, **kw):
    ...

def test_the_rebuilt_predicate_is_bed_plus_eta_over_the_threshold(tmp_path):
    ...

def test_a_nodata_cell_is_dry_at_every_level_and_every_threshold(tmp_path):
    """NaN fails the comparison, so an unsurveyed cell is never water. It
    would otherwise read as a bed 9999 m below MLLW — the deepest water on
    the raster — which is the opposite of what "not surveyed" means."""
    ...

def test_raising_the_threshold_shrinks_every_level(tmp_path):
    ...

def test_with_threshold_keeps_the_levels_the_grid_and_the_crs(tmp_path):
    ...

def test_with_threshold_at_the_value_already_in_force_is_the_same_object(tmp_path):
    ...

def test_with_threshold_refuses_a_raster_of_another_shape(tmp_path):
    ...

@skipif_no_site
def test_the_rebuild_reproduces_the_shipped_stack_bit_for_bit():
    """The builder's predicate has a second implementation now, and this is
    what keeps the two honest: at the baked threshold, on the baked levels,
    the in-memory rebuild is the npz on disk, cell for cell."""
    ...

@skipif_no_site
def test_a_swimmable_depth_is_a_subset_of_the_shipped_mask_at_every_level():
    ...

@skipif_no_site
def test_one_level_step_of_threshold_is_one_level_step_of_tide():
    """Raising the threshold by the level spacing shifts the stack by a level.

    ``(bed + eta) > 0.05 + 0.25`` and ``(bed + (eta - 0.25)) > 0.05`` are the
    same set, and the shipped axis is spaced at exactly 0.25 m, so the mask at
    0.30 m and level *i* must be the shipped mask at level *i-1* — elementwise,
    on the real raster. It is the sharpest available check that the rebuilt
    predicate is the arithmetic it claims to be rather than something that
    merely produces plausible counts.
    """
    ...

def _traj(**kw):
    ...

def test_an_unset_threshold_is_dropped_from_the_dump_so_old_hashes_hold():
    ...

def test_naming_a_threshold_moves_the_effective_config_hash():
    """Including the baked value: naming it is an instruction, on the
    ``polygon_mode`` / ``declination_deg`` rule."""
    ...

def _effective(args):
    ...

def test_the_flag_overrides_the_field():
    ...

def test_no_flag_leaves_the_field_alone():
    ...

def _args(tmp_path, tif, geojson, **kw):
    """The driver's ``args``. ``wet_threshold_m`` is the *flag*: None means the
    operator typed nothing, whatever the deployment file says."""
    ...

def test_the_driver_leaves_the_baked_stack_alone_when_nothing_is_named(tmp_path, capsys):
    ...

def test_the_driver_rebuilds_the_mask_and_stamps_the_override(tmp_path):
    ...

def test_naming_the_baked_value_is_an_instruction_without_a_rebuild(tmp_path, capsys):
    """It moves the hash and the card records where it came from, and no mask
    changes — so the console must not claim a rebuild that did not happen."""
    ...

def test_a_threshold_from_the_deployment_file_is_carded_as_the_files(tmp_path):
    """The stamp names the instruction the run received. A value set in
    ``trajectory.wet_threshold_m`` with no flag on the command line must not
    card as ``--wet-threshold-m``: that is the class of failure §22.5.4 records
    for ``bathymetry_tide_term``, and the reason this stamp exists."""
    ...

def test_the_rebuild_reads_the_pair_the_stack_was_baked_from(tmp_path):
    """``load_tide_aware_polygon()`` takes no arguments and always reads the
    site constants, so the rebuild must too. ``--depth`` / ``--polygon`` agree
    with those constants only by argparse default; here they point at a raster
    of another shape, and the rebuild has to ignore them."""
    ...

def test_a_non_finite_threshold_is_refused_by_the_config():
    """NaN compares False against every cell, so the whole stack goes dry and
    every particle is charged at every step, silently. Negatives stay legal:
    a threshold below the bed is the loosened-mask control."""
    ...

def test_a_threshold_without_a_wet_mask_stack_is_a_cli_error(tmp_path):
    """``--tide-source none`` leaves the static MLLW outline, which has no
    threshold. Ignoring the flag there would run a different model than the
    operator asked for and card it as the one they named."""
    ...

def test_the_header_table_names_the_threshold_and_whose_it_is():
    ...

def _diag_notes(args_kw):
    ...

def test_the_report_notes_an_overridden_threshold_and_is_silent_on_the_baked_one():
    ...

def test_the_card_stamps_the_threshold_that_was_in_force():
    """A null ``wet_threshold_m`` is dropped from the effective config dump,
    so two runs on two masks would otherwise card one fingerprint — the
    failure section 22.5.4 records for ``bathymetry_tide_term``."""
    ...

def _centerline():
    ...

def _sample_points(cl):
    ...

def test_a_zero_prism_constant_gives_exactly_zero_advection():
    """``K = 0`` zeroes the mouth speed, and the whole field scales with it —
    exactly zero, not a small number, because the multiplication is by 0.0."""
    ...

def test_the_zero_field_is_zero_everywhere():
    ...

def test_current_source_none_builds_no_field(monkeypatch):
    """The structural switch: no field is constructed at all, so no advection
    term is formed anywhere in the loop."""
    ...

def test_no_current_field_means_no_advection_in_the_filter():
    """``current_field=None`` is what the switch produces, and the filter's
    own per-step record of the advection it applied is then exactly zero."""
    ...

class _StopAtFilter(Exception):
    ...

@pytest.mark.skipif(not CFG_PATH.exists(), reason='needs the repo deployment config')
def test_the_flag_reaches_the_polygon_the_filter_is_handed(monkeypatch, tmp_path, capsys):
    """``anchor track --wet-threshold-m`` end to end, up to the filter call.

    Everything before the filter is stubbed except the water constraint, which
    is a real (small) tidal stack; the filter is replaced by a trap that
    records what it was given. The knob is worth nothing if the rebuilt mask
    does not reach the object the filter actually queries.
    """
    ...
