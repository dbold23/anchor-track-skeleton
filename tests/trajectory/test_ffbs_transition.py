"""FFBS backward kernel = the forward transition (audit 2026-09-25, findings 1-3).

Hand-built two-snapshot histories, so each check is exact and needs no raster:

1. the latent part of the transition is honoured (a point mass under zero walk),
2. an interior Verified Position already folded in by the forward pass is not
   multiplied in a second time by the smoother,
3. the backward kernel's xy variance is the per-step noise the forward pass
   actually drew, accumulated over the interval.
"""
from __future__ import annotations
import numpy as np
from anchor.trajectory.particle_filter import SBIAS, SSCALE, STATE_DIM, SX, ffbs_smoother, integrate_snapshot_noise
from anchor.trajectory.verified_positions import VerifiedPosition, VerifiedPositionSet

def _cloud(xy, bias, scale=1.0):
    ...

def _smooth(hist, log_w, *, K=64, **kw):
    ...

def test_static_latents_pick_only_matching_ancestors():
    ...

def test_static_speed_scale_also_constrains_ancestors():
    ...

def test_latent_random_walk_admits_nearby_ancestors():
    ...

def test_interior_verified_position_is_not_counted_twice():
    ...

def test_integrate_snapshot_noise_sums_per_step_variance():
    ...

def test_backward_kernel_uses_the_interval_noise_variance():
    ...
