"""Drone-corpus management: per-species manifest of UAS overflights with
DLC-derived pose, world-coord trajectory, and end-to-end K calibration.

Drone footage gives a stronger K calibration than the online corpus because
swim speed comes from real world coordinates (drone altitude + DJI SRT
telemetry → metres-per-pixel) rather than from a pose-only body-length
scaling. This module is paper §4.5.2 + §5.4 (WS) / §5.2 (LS) / §5.5 (TS)
external-pose validation.

Workflow mirrors :mod:`anchor.validation.corpus`:

  1. ``anchor validation drone-corpus add --species leopard_shark
     --body-length-m 1.2 --video LS_260415_drone.mp4 --srt LS_260415_drone.srt``
  2. ``anchor validation drone-corpus prep --clip-id LS_001 --n-frames 100``
  3. (Manual) hand-label in DLC, train, infer to ``keypoints.csv``.
  4. ``anchor validation drone-corpus calibrate --species leopard_shark``

Paired-deployment mode (drone overhead + AXY tag on same animal) is
flagged via ``deployment_id`` and ``video_offset_s``; this enables the
cross-validation step in §5.4 (drone-derived speed vs accel-derived
speed). The cross-validation runner is on the roadmap; this MVP does
solo drone K calibration only.
"""
from __future__ import annotations
import datetime
import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Optional
import numpy as np
import pandas as pd
from anchor.validation import drone as D
from anchor.validation import online_corpus as OC
from anchor.validation import pose as P

@dataclass
class DroneClip:
    """One drone overflight in the per-species corpus."""
    id: str
    species: str
    body_length_m: float
    video_path: str
    srt_path: str
    image_width_px: int = 3840
    image_height_px: int = 2160
    horizontal_fov_deg: float = 84.0
    fps: Optional[float] = None
    deployment_id: Optional[str] = None
    video_offset_s: Optional[float] = None

@dataclass
class DroneCorpus:
    """A per-species collection of drone clips."""
    species: str

    def add(self, clip: DroneClip) -> None:
        ...

    def remove(self, clip_id: str) -> DroneClip:
        ...

    def get(self, clip_id: str) -> DroneClip:
        ...

    @classmethod
    def manifest_path(cls, species: str, root: Path=DRONE_ROOT) -> Path:
        ...

    @classmethod
    def load(cls, species: str, root: Path=DRONE_ROOT) -> 'DroneCorpus':
        ...

    def save(self, root: Path=DRONE_ROOT) -> Path:
        ...

def make_clip_id(species: str, n_existing: int) -> str:
    ...

def clip_dir(clip: DroneClip, root: Path=DRONE_ROOT) -> Path:
    ...

def keypoints_path(clip: DroneClip, root: Path=DRONE_ROOT) -> Path:
    ...

def frames_dir(clip: DroneClip, root: Path=DRONE_ROOT) -> Path:
    ...

def calibrate_drone_clip(clip: DroneClip, keypoints: P.Keypoints, body_kp_name: Optional[str]=None) -> dict:
    """Drone clip → world-coord trajectory + per-cycle K.

    Returns dict with:
      - ``trajectory``: per-frame DataFrame (t, lat, lon, mpp)
      - ``speed``: per-frame DataFrame (t, speed_m_s) from world-coord deriv
      - ``kinematics``: per-cycle DataFrame (cycle_t, tbf_hz, ...)
      - ``k`` (DataFrame): per-cycle K with U from drone trajectory and
        L from clip.body_length_m
    """
    ...

def calibrate_drone_corpus(corpus: DroneCorpus, root: Path=DRONE_ROOT, weight_by: str='per_clip') -> dict:
    """Walk every clip with DLC keypoints + an SRT and produce species K.

    Returns dict with ``per_clip`` (list of K dataframes), ``aggregate``
    (bootstrap summary), ``trajectories`` (list of per-clip traj dataframes),
    and ``skipped`` (list of clip ids missing keypoints or SRT).
    """
    ...

def cross_validate_drone_axy(clip: DroneClip, keypoints: P.Keypoints, axy_processed: pd.DataFrame, species_k: float, body_kp_name: Optional[str]=None, n_bootstrap: int=1000, ci: float=0.95, rng: Optional[np.random.Generator]=None) -> dict:
    """Paired drone + AXY cross-validation of the Strouhal K speed proxy.

    Compares drone-derived world swim speed (from per-frame lat/lon) against
    the AXY-side Strouhal prediction U_strouhal = K · L · accel_TBF, where
    accel_TBF is interpolated from the AXY processed parquet's
    ``tb_freq_inst`` column at the physical time of each drone cycle.

    The per-cycle ratio drone_U / strouhal_U is the empirical correction
    factor for K. Bootstrap-medianed across cycles, this gives an
    empirically-calibrated K with CI that the paper §4.5.2 K-anchor table
    can compare against the literature default.

    Requires ``clip.video_offset_s`` to be set so AXY-time can be derived
    from drone-time:

        axy_physical_t = drone_local_t - clip.video_offset_s

    ``axy_processed`` is the deployment's processed parquet (output of
    ``anchor process``); only ``t`` and ``tb_freq_inst`` are read.
    """
    ...

def today_iso() -> str:
    ...
