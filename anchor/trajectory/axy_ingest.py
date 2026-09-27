"""AXY ingest for the trajectory pipeline.

Wraps existing anchor infrastructure to produce the time series the particle
filter consumes: ``(t_s, heading_rad, speed_mps, depth_m)``.

Pipeline
--------
1. ``anchor.io.load_deployment(cfg)`` — flexible CSV read + schema
   normalize + accel calibration (and mag calibration when available).
2. ``anchor.kinematics.add_pitch_roll`` — gravity-derived attitude.
3. ``anchor.track.imu.tilt_compensated_heading`` — tilt-compensated mag
   heading + per-site declination correction.
4. ``anchor.kinematics.add_tailbeat_columns`` — sway-axis peak picking for
   instantaneous TBF (Hz), under the species config's own ``tailbeat``
   block (axis, ``smooth_sigma``, ``min_period_s``, ``prominence``).
5. TBF → speed via a Strouhal-style scaling
   ``U = strouhal_k · L · TBF`` (per-species ``cfg.strouhal_k``,
   default ``DEFAULT_STROUHAL_K = 0.4``); see
   Watanabe 2012 (Greenland) / Bouyoucos 2017 (lemon) for sibling-species
   calibrations. The filter's ``k_speed`` latent state absorbs the actual
   per-deployment scale.
6. Downsample to a coarser ``base_hz`` (default 1 Hz) using circular mean
   for heading and ordinary mean for speed.
7. Depth: ``NaN`` for AXY-5 base tags (no pressure sensor) — the filter's
   bathymetry constraint flips off via ``enable_bathymetry_constraint=False``.

Output is a ``pandas.DataFrame`` indexed by ``t_s`` from the deployment
start (or the configured ``deploy_window`` start).
"""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
import numpy as np
import pandas as pd
from anchor.ingest.config import DEFAULT_STROUHAL_K
from anchor.trajectory.imu import ELKHORN_DECLINATION_DEG_2026, tilt_compensated_heading
__all__ = ['DEFAULT_BASE_HZ', 'DEFAULT_BODY_LENGTH_M', 'DEFAULT_STROUHAL_K', 'IngestedTrack', 'align_behavior_states', 'behavior_to_process_noise', 'ingest_deployment']
DEFAULT_BODY_LENGTH_M = 1.2
DEFAULT_BASE_HZ = 1.0

@dataclass
class IngestedTrack:
    """1-Hz observation time series consumed by ParticleFilter."""
    t_s: np.ndarray
    heading_rad: np.ndarray
    speed_mps: np.ndarray
    depth_m: np.ndarray
    pitch_rad: np.ndarray
    roll_rad: np.ndarray
    tailbeat_freq_hz: np.ndarray
    deployment_id: str
    base_hz: float
    declination_deg: float
    t0_utc: Optional[pd.Timestamp] = None

    def __len__(self) -> int:
        ...

    def utc_at(self, t_idx) -> 'pd.Timestamp | np.ndarray':
        """Convert filter-step index → UTC timestamp(s)."""
        ...

    def to_dataframe(self) -> pd.DataFrame:
        ...

def _nanmean_rows(a: np.ndarray) -> np.ndarray:
    """Row-wise mean ignoring NaN, returning NaN for a row with no finite sample.

    ``np.nanmean`` warns (``RuntimeWarning: Mean of empty slice``) on an
    all-NaN row and this project promotes warnings to errors, so a deployment
    whose first block is entirely quiescent would abort the ingest. A block
    with no valid sample genuinely has no mean; return NaN for it quietly and
    match ``np.nanmean`` elsewhere, including letting a non-NaN infinity
    propagate.
    """
    ...

def _circular_mean_blocks(angles_rad: np.ndarray, block: int) -> np.ndarray:
    ...

def _block_mean(values: np.ndarray, block: int) -> np.ndarray:
    ...

def ingest_deployment(cfg, *, base_hz: float=DEFAULT_BASE_HZ, declination_deg: float=ELKHORN_DECLINATION_DEG_2026, body_length_m: float=DEFAULT_BODY_LENGTH_M, strouhal_k: float | None=None, use_cached_parquet: bool=True, sway_axis: str='accY_dyn', lowpass_cutoff_hz: float=1.0) -> IngestedTrack:
    """Load a deployment and return a downsampled trajectory-observation series.

    Parameters
    ----------
    cfg
        ``anchor.ingest.config.DeploymentConfig`` — every call site builds
        one via ``load_config``, and the declared ``strouhal_k`` field is
        read off it directly.
    base_hz
        Output sampling rate (Hz). 50 Hz / base_hz must be an integer
        block size; default 1 Hz averages each second of input.
    declination_deg
        Magnetic declination correction (default = Elkhorn 2026).
    body_length_m, strouhal_k
        For TBF → speed: ``U = strouhal_k · L · TBF``. If ``strouhal_k``
        is None (default) the validated ``cfg.strouhal_k`` field is used
        (set per species in the YAML, defaulting to
        ``DEFAULT_STROUHAL_K``). The filter's ``k_speed`` absorbs
        deployment-specific residual.
    use_cached_parquet
        If True, read the cached interim parquet (``data/interim/<id>.parquet``)
        when it is present *and* was written from this config
        (``io.interim_cache_is_valid``); otherwise re-run the full
        ``load_deployment`` pipeline.
    """
    ...

def align_behavior_states(track: IngestedTrack, states_path: str | Path, state_col: str='state') -> np.ndarray:
    """Align anchor HMM behavior states (window-based) to the 1-Hz track timeline.

    The states parquet has overlapping windows (typically 5 s, stepped every
    2 s). For each track timestamp ``t_s`` we pick the window whose
    ``center_t`` is closest. Returns an int array of state labels with the
    same length as ``track.t_s``; missing values get -1.
    """
    ...

def behavior_to_process_noise(states: np.ndarray, *, rest_noise_m: float=0.3, cruise_noise_m: float=1.5, active_noise_m: float=3.0, burst_noise_m: float=5.0, default_noise_m: float=2.5) -> np.ndarray:
    """Map a per-step HMM state array to per-step process-noise σ.

    Convention: state 0 = rest, 1 = cruise, 2 = active, 3 = burst (matches
    ``configs/species/leopard_shark.yaml`` ``labels_hint``).

    Resting states get tiny noise → particles barely diffuse, posterior
    stays tight. Burst states get inflated noise → reflects high acceleration
    + likely turning. The output array is consumed by ``ParticleFilter.predict``
    via its optional per-step noise override.
    """
    ...

def _detect_fs(df: pd.DataFrame) -> float:
    ...
