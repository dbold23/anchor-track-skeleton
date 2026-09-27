"""Verified Positions data model + time→step mapping."""
from __future__ import annotations
import numpy as np
import pandas as pd
import pytest
from anchor.trajectory.verified_positions import VerifiedPosition, VerifiedPositionSet

def _vp(t_idx, x=0.0, y=0.0, sigma=10.0, label='fix'):
    ...

def test_log_likelihood_peaks_at_fix():
    ...

def test_normaliser_is_two_dimensional_like_the_anchors():
    """A VP is the same bivariate Gaussian as ``ReleaseAnchor``/``EndAnchor``,
    so its peak log-density is ``-log(2*pi*sigma**2)``. It used to carry the
    1-D ``-log(sigma*sqrt(2*pi))``, left behind when commit ``bb41a0f`` fixed
    the two anchors — wrong by ``log(sqrt(2*pi)/sigma)`` nats, which stops
    cancelling the moment fixes of different σ are compared."""
    ...

def test_density_integrates_to_one():
    ...

def test_update_vps_carries_the_same_two_dimensional_normaliser():
    """``ParticleFilter.update_vps`` is a fourth copy of the same likelihood
    and had the same 1-D normaliser. It has to agree with ``VerifiedPosition``
    exactly, constant or not."""
    ...

def test_from_lonlat_projects_and_scores():
    ...

def test_set_rejects_duplicate_timestep():
    ...

def test_set_lookup_and_sorting():
    ...

def test_interior_excludes_endpoints():
    ...

def test_from_lonlat_fixes_defaults_sigma():
    ...

def test_from_time_fixes_maps_to_steps_and_drops_out_of_range():
    ...

def test_from_time_fixes_collapses_duplicate_steps_keeping_tightest():
    ...
