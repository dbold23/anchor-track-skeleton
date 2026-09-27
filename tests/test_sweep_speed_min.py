"""``scripts/sweep_speed_min.py``'s tabulator, unit-tested on synthetic artefacts.

The sweep's whole point is to distinguish "the floor truncates a mode just below
it" from "the posterior slides down with the floor", so the one number that must
not be wrong is the **fraction of ``k_speed`` samples on the floor** — and that
fraction has to be measured against *each run's own* floor, not against the
shipped 0.5.  A tabulator that hard-codes 0.5 reports 0 % for every widened run
and makes a sliding posterior look like a released one, which is exactly the
wrong answer.

Three behaviours are guarded here:

* the at-floor fraction is taken against the run's own ``speed_min``;
* the attached path length is the summed step-to-step distance of the smoothed
  mean track, and mean speed is that length over the track's own duration;
* weight collapses come from the report banner, and its absence means zero (the
  ledger has no collapse field, so a missing banner must not read as missing
  data).

All three run off files written into a tmp_path, so nothing here needs ``data/``.
"""
from __future__ import annotations
import importlib.util
import json
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import pytest

def _load_module():
    ...

@pytest.fixture(scope='module')
def sweep():
    ...

def _write_run(out_dir: Path, k_values: np.ndarray, xy: np.ndarray, *, deployment_id: str='TEST_1', report_body: str | None=None) -> Path:
    """Write the three artefacts ``read_run`` consumes, plus an optional report."""
    ...

def test_floor_fraction_is_measured_against_the_runs_own_floor(sweep, tmp_path):
    """A widened run's pinned samples must count as pinned, not as released."""
    ...

def test_path_length_and_mean_speed_come_from_the_track(sweep, tmp_path):
    """Path length is summed step-to-step distance; speed is it over the duration."""
    ...

def test_collapse_count_reads_the_banner_and_absence_means_zero(sweep, tmp_path):
    """No banner is zero collapses, not missing data; a banner yields its count."""
    ...

def test_collapsed_value_is_none_when_the_last_snapshot_is_not_collapsed(sweep, tmp_path):
    """`k_speed collapsed` is only meaningful when one lineage survives."""
    ...
SWEEP_N_PARTICLES = 4000
SWEEP_SEED = 0
CUBE_MIN_FREE_ARMS = 0.2803453378128692

def _seed0_speed_cloud(speed_min: float) -> np.ndarray:
    ...

def test_seed0_cloud_has_exactly_one_draw_below_the_0_2_floor():
    """Section 11.1: the 0.2 clip bites exactly one particle of 4000."""
    ...

def test_clipped_arms_are_the_free_cloud_clipped_elementwise():
    """The 0.5/0.3/0.2 clouds differ from the free one only by np.clip."""
    ...
