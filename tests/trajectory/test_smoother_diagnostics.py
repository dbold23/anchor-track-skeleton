"""The smoother's own degeneracy diagnostic (TASK C1, C).

``docs/regen_2026-09.md`` section 19.6.3 lists three ways to make the section
3.7 founder floor mean something, and the third is to stop measuring the
forward filter: ``n_founders_final`` counts distinct time-zero ancestors in the
*forward* cloud, while every positional number the report prints — the track,
``sigma_along``/``sigma_cross``, ``along_span_m`` — is read off the FFBS
smoother's sample cube. This module tests the measurement of the cube.

It is a **diagnostic**. ``GATE_TABLE`` is unchanged, no floor is scored from
any number here, and the tests assert that too: choosing a floor is a dated
amendment to the design document, not a code change.
"""
from __future__ import annotations
import numpy as np
import pytest
from anchor.trajectory.particle_filter import SBIAS, SSCALE, SX, SY, SMOOTHER_CUBE_FRACTIONS, STATE_DIM, ffbs_smoother, ffbs_smoother_over_grid, smoother_cube_diagnostics
from anchor.validation.ledger.gates import GATE_TABLE, GATE_TABLE_VERSION
T_SNAP = 9
N = 40
K = 12

def _history(seed: int=0, n_particles: int=N):
    """A tiny forward history: a straight drift east with spread weights."""
    ...

def _smooth(seed=0, diagnostics=None, n_smooth=K, history=None):
    ...

def test_the_cube_diagnostic_counts_distinct_ancestries_through_the_record():
    ...

def test_a_cube_of_identical_paths_reports_one_ancestry_everywhere():
    """The degenerate case the diagnostic exists to name."""
    ...

def test_the_cube_diagnostic_counts_the_latent_pairs_the_ensemble_spans():
    """Section 19.6.3's own number: the flagship's cube carried 2 of 25."""
    ...

def test_a_cube_that_is_not_a_cube_is_refused():
    ...

def test_the_backward_ess_is_recorded_only_when_a_dict_is_passed():
    ...

def test_recording_the_backward_ess_does_not_move_a_single_sample():
    """The diagnostic reads the weights; it must not touch them or the RNG."""
    ...

def test_the_backward_ess_folds_into_the_cube_block_under_its_own_prefix():
    ...

def test_the_grid_smoother_reports_one_backward_record_per_drawn_node():
    """Two nodes, separate forward histories, separate backward sweeps.

    Pooling them into one dict would report the last node's ESS as the
    ensemble's, so each node keeps its own record and the ensemble's mean is
    weighted by the paths each node actually supplied.
    """
    ...

def test_the_grid_smoother_is_unchanged_when_no_diagnostics_are_asked_for():
    ...

def test_no_gate_scores_the_smoothed_cube():
    """The section 3.7 rows are pre-registered; this adds none of them."""
    ...
