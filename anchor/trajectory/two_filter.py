"""Bidirectional (two-filter) particle smoother.

When a deployment has known endpoint anchors at both t=0 (release) and
t=T (recovery), the trajectory reconstruction becomes a boundary value
problem rather than the standard initial-value problem the forward
filter handles. Briers, Doucet & Maskell 2010 ("Smoothing algorithms
for state-space models") give the two-filter smoother as the
canonical answer:

    p(x_t | y_{1:T}, x_0, x_T)
        ∝ p(x_t | y_{1:t}, x_0)             [forward filter at t]
        · p(y_{t+1:T}, x_T | x_t)           [backward filter at t]

Both terms are particle-approximated. The first comes from the existing
forward filter. The second comes from a backward filter that runs the
dynamics in reverse time (predict with ``direction=-1``), starting at
the recovery anchor at t=T, with observations applied in reverse order
y_T, y_{T-1}, ... y_1.

To combine the two particle clouds at each time step we use
**marginal-particle product reweighting**. For each forward particle,
we estimate the local backward density via a Gaussian KDE on the
backward-particle cloud, multiply, and renormalize. This stays in the
forward particles' support — important because the forward particles
inherit the (x_0, y_{1:t}) information correctly.

The smoothed track is the weighted mean of the reweighted forward
particles at each step. The latent (ψ_bias, k_speed) posteriors come
out tighter because both endpoints constrain the dynamics that connect
them.
"""
from __future__ import annotations
from typing import Optional
import numpy as np
from anchor.trajectory.bathymetry import BathyLookup
from anchor.trajectory.end_anchor import EndAnchor
from anchor.trajectory.particle_filter import SBIAS, SSCALE, SX, SY, FilterConfig, ParticleFilter

def run_backward_filter(track, bathy: BathyLookup, polygon, end_anchor: EndAnchor, *, n_particles: int=4000, n_steps: int | None=None, process_noise_xy_m: float=2.5, process_noise_per_step: np.ndarray | None=None, enable_bathymetry: bool=False, bathymetry_extra_sigma_m: float=1.0, snapshot_stride: int=1, tide_series=None, current_field=None, seed: int=0):
    """Backward particle filter.

    Mirrors ``elkhorn_demo.run_filter`` but runs from t=T to t=0:

    * Initializes particles around the recovery point at t=T.
    * For each step ``t`` going backward, applies the bathymetry +
      polygon + tide / current observations *for that t* to the
      particles' current beliefs (those observations constrain
      x_t regardless of which way we entered the step).
    * Calls ``predict`` with ``direction=-1`` to step from x_t to x_{t-1}.
    * Snapshots particles at each step in *forward-time* order (so
      ``history_particles[t]`` is the backward filter's belief about x_t).

    Returns a dict structurally compatible with the forward
    ``run_filter_with_snapshots`` output but storing the *backward*
    posterior at each step.
    """
    ...

def _normalize_log_weights(log_w: np.ndarray) -> np.ndarray:
    ...

def _gaussian_kde_log_density(eval_pts: np.ndarray, sample_pts: np.ndarray, sample_weights: np.ndarray, bandwidth_m: float) -> np.ndarray:
    """Log of weighted Gaussian KDE evaluated at ``eval_pts``.

    Vectorized: M x N kernel evaluations. Stable but degrades when the
    bandwidth is too tight relative to the cloud spread (the smoother
    used a moment-matched Gaussian approximation by default for this
    reason — see ``_backward_log_density``)."""
    ...

def _backward_log_density(eval_pts: np.ndarray, bp_xy: np.ndarray, bp_weights: np.ndarray, inflation_floor_m2: float=25.0) -> np.ndarray:
    """Log p_b(x_t | future data, x_T) evaluated at each forward particle.

    Approximates the backward marginal as a 2D Gaussian via moment
    matching on the weighted backward cloud. This is the **default and
    recommended** smoother density because:

    * Marginal-particle KDE collapses onto 1-2 particles when
      bandwidth ≪ backward-cloud σ — and the backward cloud at t=T
      starts at the recovery anchor's 10 m σ which is much smaller
      than typical forward-cloud σ at the deployment midpoint.
    * The Gaussian approximation is a valid first-moment match: it
      preserves the backward posterior's mean and covariance, which
      is exactly what's needed to combine with the forward particles
      via importance reweighting.
    * Numerically stable for any cloud shape.

    A small variance floor (``inflation_floor_m2``) prevents numerical
    collapse at the very ends where the backward cloud is tightly
    concentrated at the anchor.
    """
    ...

def two_filter_smoother(forward_state: dict, backward_state: dict, *, method: str='gaussian', bandwidth_m: float | None=None, bandwidth_floor_m: float=8.0, bandwidth_scale: float=0.6, inflation_floor_m2: float=25.0) -> dict:
    """Combine forward + backward marginals into the bidirectional posterior.

    For each time step t with forward particles {x_f^i, w_f^i} and
    backward particles {x_b^j, w_b^j}, the smoothed weight on each
    forward particle is

        w_smooth^i ∝ w_f^i · KDE_b(x_f^i)

    where KDE_b is a weighted Gaussian KDE over the backward cloud.
    The smoothed posterior is then represented by {x_f^i, w_smooth^i}
    — i.e. we stay on the forward support and reweight.

    Bandwidth selection
    -------------------
    Adaptive by default. At each step the bandwidth is

        h_t = max(bandwidth_floor_m, bandwidth_scale * sigma_xy_t)

    where ``sigma_xy_t = sqrt(σ_x_f^2 + σ_y_f^2)`` is the forward cloud's
    weighted spread at that step. The Silverman rule for 2D Gaussian KDE
    gives ``h = (4/3)^(1/5) σ N^(-1/5) ≈ 0.5σ`` at N=2000, so the 0.6
    default is slightly broader than Silverman to avoid degeneracy
    when the forward / backward clouds drift apart in the deployment
    middle.

    A fixed ``bandwidth_m`` overrides the adaptive rule when given.
    Best practice is to leave it None unless you have a calibration
    target — fixed-bandwidth marginal-particle smoothing is unstable
    in high-dimensional state spaces and at deployment midpoints.
    """
    ...
