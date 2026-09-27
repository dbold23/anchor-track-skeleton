"""Drone footage ingest + georeferencing tests."""
from __future__ import annotations
import numpy as np
import pytest
from anchor.validation import drone as D
from anchor.validation import pose as P

def _write_synthetic_dji_srt(path, n_frames: int=30, fps: float=30.0) -> None:
    """Tiny DJI-Mavic-style SRT with constant pose (lat, lon, alt) at 30 Hz."""
    ...

def test_load_dji_srt_parses_metadata(tmp_path):
    ...

def test_metres_per_pixel_nadir():
    """Ground-sample distance for a known altitude + FOV must round-trip."""
    ...

def test_pixel_to_world_centre_roundtrips():
    """A pixel at the image centre maps to the drone's lat/lon."""
    ...

def test_pixel_to_world_offset_applies_yaw():
    """A pixel right of centre with yaw=90° maps north (not east)."""
    ...

def test_pixel_to_world_off_nadir_rejected():
    """Off-nadir gimbal must NotImplementedError until pinhole is wired."""
    ...

def test_extract_trajectory_from_keypoints_smoke():
    """Stitch keypoints + drone metadata → per-frame world coords."""
    ...
