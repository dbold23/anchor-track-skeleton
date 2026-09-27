"""Generate synthetic shark trajectories + observations for filter validation.

Pattern:
    1. Random-walk path inside the bay polygon, with smoothed heading and
       constrained step size.
    2. Animal swims close to the bottom (depth = bathy * fraction + noise).
    3. Observations:
         - heading_obs = true heading + Gaussian noise (default σ = 5°)
         - speed_obs   = true speed + Gaussian noise (default σ = 0.05 m/s)
         - depth_obs   = animal depth + Gaussian noise (default σ = 0.5 m)
         - vps_obs     = (x, y) every K steps + 2D Gaussian noise (σ = HPE-derived)

This is the "known-truth" generator the particle filter is validated against.
"""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np
from anchor.trajectory.bathymetry import BathyLookup

@dataclass
class TrackTruth:
    t: np.ndarray
    x: np.ndarray
    y: np.ndarray
    heading: np.ndarray
    speed: np.ndarray
    depth: np.ndarray

@dataclass
class TrackObservations:
    t: np.ndarray
    heading_obs: np.ndarray
    speed_obs: np.ndarray
    depth_obs: np.ndarray
    vps_t: np.ndarray
    vps_x: np.ndarray
    vps_y: np.ndarray
    vps_sigma: np.ndarray

def _step_inside_polygon(x, y, dx, dy, in_poly_fn):
    """Take the step if it lands inside; otherwise try the reversed step.

    Returns ``(x_new, y_new, reversed, moved)``. The truth must stay
    self-consistent -- every recorded displacement equals
    ``speed * (sin heading, cos heading) * dt`` -- because the observations
    are generated from ``heading`` and ``speed``, not from positions. The
    earlier version left the animal in place while keeping its heading and
    speed (its "reverse" was a no-op re-wrap), so dead reckoning the true
    heading and speed walked through the boundary the positions stopped at.
    """
    ...

def simulate_truth(bathy: BathyLookup, in_poly_fn, start_xy: tuple[float, float], n_steps: int=600, dt_s: float=5.0, speed_mean_mps: float=0.6, speed_std_mps: float=0.15, heading_step_std_rad: float=0.15, bottom_fraction: float=0.85, bottom_jitter_m: float=0.5, initial_heading_rad: float=0.0, seed: int=0) -> TrackTruth:
    ...

def simulate_truth_free_space(start_xy: tuple[float, float]=(0.0, 0.0), n_steps: int=601, dt_s: float=1.0, speed_mean_mps: float=0.6, speed_std_mps: float=0.15, heading_step_std_rad: float=0.05, depth_m: float=5.0, initial_heading_rad: float=0.0, seed: int=0, current_uv_mps: tuple[float, float]=(0.0, 0.0)) -> TrackTruth:
    """Known-truth track with no raster and no polygon.

    :func:`simulate_truth` needs a :class:`BathyLookup` and a polygon test, so
    every test built on it skips on a machine without the gitignored geospatial
    fixtures. This variant integrates the same dead-reckoning kinematics in free
    space — identical heading/speed model, constant depth, no reflection at a
    boundary — so filter and smoother arithmetic can be pinned by tests that run
    anywhere.

    Conventions match :meth:`ParticleFilter.predict`: heading is measured
    clockwise from grid north, so ``dx = (u·sin ψ + c_u)·dt`` and
    ``dy = (u·cos ψ + c_v)·dt``. ``heading`` and ``speed`` are relative to the
    water; a non-zero ``current_uv_mps`` (east, north) drifts the ground track
    and is exactly what ``predict(..., current_uv=...)`` adds back, so a filter
    that is not told about it shows the error an unmodelled current causes.

    Speed model note: the per-step innovation is ``N(0, 0.05) * speed_std_mps``,
    i.e. 0.0075 m/s at the default, and with the 0.1 mean reversion the
    stationary spread is about 0.017 m/s -- speed is close to constant, not the
    0.15 m/s the parameter name suggests. It is left as is because the golden
    numbers in ``tests/trajectory/test_golden.py`` are pinned on it.
    """
    ...

def simulate_observations(truth: TrackTruth, heading_sigma_rad: float=np.deg2rad(5.0), speed_sigma_mps: float=0.05, depth_sigma_m: float=0.5, vps_period_steps: int=6, vps_sigma_m: float=4.0, true_bias_rad: float=0.0, true_scale: float=1.0, seed: int=1) -> TrackObservations:
    """Generate observations from truth.

    The filter's effective dynamics are:
        eff_heading = heading_obs + ψ_bias
        eff_speed   = speed_obs * k_speed
    so to inject "true" bias/scale into the synthetic data we run the inverse:
        heading_obs = truth_heading - true_bias_rad   + noise
        speed_obs   = truth_speed   / true_scale       + noise
    A correctly-tuned filter will then recover ψ_bias ≈ true_bias_rad and
    k_speed ≈ true_scale.
    """
    ...
