"""Drone (UAS) video ingest + pixel→world georeferencing.

For LS drone-from-shore at Elkhorn, TS drone-from-boat in open coastal,
and WS drone overhead at TOPP-coordinated trips. The DiGiacomo, Abraham &
Block 2025 (*Wildlife Research* 52:WR24193) WS drone pose paper is the
proof-of-concept; this module is the lab's implementation.

Coordinate convention:
  - Drone pose: ``lat`` (deg), ``lon`` (deg), ``alt_m`` (above water surface).
  - Camera: nadir (gimbal_pitch_deg = -90) is the simple case. Off-nadir
    requires the full pinhole-projection treatment (not implemented here;
    flag in TODO if a deployment needs it).
  - Output: per-frame ``lat`` / ``lon`` for tracked body keypoint(s).

For a nadir-pointed drone at altitude ``h``, horizontal field-of-view
``fov``, and image width ``w`` pixels, the ground-plane scale is
``2 · h · tan(fov/2) / w`` metres per pixel. We then project pixel
offsets from the image centre to drone-frame east/north and add to
the drone's lat/lon. This is the flat-earth small-area approximation
appropriate for a single estuary or coastal site.
"""
from __future__ import annotations
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
import numpy as np
import pandas as pd

@dataclass
class DroneFrame:
    """One frame's drone-state snapshot."""
    t: float
    lat: float
    lon: float
    alt_m: float
    yaw_deg: float = 0.0
    gimbal_pitch_deg: float = -90.0
    gimbal_yaw_deg: float = 0.0

@dataclass
class DroneMetadata:
    """Per-frame drone metadata indexed by frame number; aligns to video fps."""
    frames: list[DroneFrame]
    fps: float
    image_width_px: int
    image_height_px: int
    horizontal_fov_deg: float

    def to_dataframe(self) -> pd.DataFrame:
        ...

    def metres_per_pixel(self, frame_idx: int) -> float:
        """Ground-sample distance for a given frame (nadir approximation)."""
        ...

def load_dji_srt(path: str | Path, image_width_px: int=3840, image_height_px: int=2160, horizontal_fov_deg: float=84.0) -> DroneMetadata:
    """Parse a DJI SRT subtitle file (per-frame telemetry beside an MP4).

    Field-tested on Mavic 3 Enterprise output. Other DJI firmwares use
    different tag formats; extend the regexes here if/when needed.
    """
    ...

def pixel_to_world(pix_x: float | np.ndarray, pix_y: float | np.ndarray, drone: DroneFrame, metres_per_pixel: float, image_width_px: int, image_height_px: int) -> tuple[np.ndarray, np.ndarray]:
    """Project image-plane pixel(s) to world (lat, lon) under nadir flat-earth.

    The drone's ``yaw_deg`` rotates the image-plane axes onto north/east.
    Pixel y increases downward in image space; we flip to image-up = +y.
    Returns (lat, lon) arrays matching the input shape.
    """
    ...

def world_speed_from_trajectory(traj: pd.DataFrame, smooth_window_s: float=0.5, fps: Optional[float]=None) -> pd.DataFrame:
    """Per-frame swim speed (m/s) from a (t, lat, lon) trajectory.

    Computes great-circle displacement between successive frames using a
    flat-earth approximation valid at the small distances per frame
    that drone overflights produce (cm to m). Returns DataFrame with
    columns ``t`` (cycle midpoint, s) and ``speed_m_s``.

    ``fps`` is read off ``traj`` time-spacing if not supplied; smoothing
    is a centred rolling mean.
    """
    ...

def extract_trajectory_from_keypoints(keypoints: 'anchor.validation.pose.Keypoints', metadata: DroneMetadata, body_kp_name: str='centroid') -> pd.DataFrame:
    """Per-frame world-coord trajectory of one tracked body keypoint.

    Returns DataFrame with columns ``t``, ``lat``, ``lon``, ``mpp``
    (metres-per-pixel at that frame). Length = min(n_frames, n_meta).
    """
    ...
