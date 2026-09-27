"""Online corpus end-to-end tests: manifest I/O, swim-speed-from-pose,
and species K calibration on synthetic keypoints with a known target K.
"""
from __future__ import annotations
import json
import numpy as np
import pandas as pd
import pytest
from anchor.validation import corpus as C
from anchor.validation import pose as P

def test_clip_id_sequential():
    ...

def test_corpus_save_load_roundtrip(tmp_path):
    ...

def test_corpus_load_missing_returns_empty(tmp_path):
    ...

def test_corpus_add_rejects_species_mismatch():
    ...

def test_corpus_add_rejects_duplicate_id():
    ...

def test_corpus_remove_returns_clip():
    ...

def test_corpus_get_raises_on_unknown():
    ...

def _synthetic_drift_keypoints(n_frames: int=600, fps: float=30.0, body_length_pix: float=200.0, drift_pix_per_frame: float=2.5, tbf_hz: float=1.5, tail_amplitude_pix: float=30.0) -> P.Keypoints:
    """A 'bat ray' translating left-to-right with a known body length, swim
    speed, and tail-flap frequency. Used for K-calibration round-tripping.

    Layout: rostrum at (x_drift, 240), tail_base 200 px behind rostrum
    oscillating laterally at ``tbf_hz``, a left_pectoral_tip co-located with
    the tail_base for the bat-ray species mapping
    (``SPECIES_TAILBEAT_KP['bat_ray'] = 'left_pectoral_tip'``), and a
    centroid at the geometric midpoint.
    """
    ...

def test_metres_per_pixel_from_pose_recovers_scale():
    """Known body length + median pose body-length-pixels should give true mpp.

    Lateral tail oscillation makes the rostrum-to-tail Euclidean distance
    fluctuate slightly above the static body length (perspective wobble),
    so we assert within 1 % of the static reference.
    """
    ...

def test_swim_speed_from_pose_recovers_drift():
    """A 2.5 px/frame drift at 30 fps and 0.0045 m/px = 0.3375 m/s.

    Tracks the rostrum keypoint, which has no lateral oscillation in the
    synthetic. Real DLC labels should pick an analogous stable body-centre
    keypoint (rostrum, dorsal-fin base, pectoral-base) rather than a
    midpoint that inherits tail oscillation.
    """
    ...

def test_cycle_swim_speed_interpolation():
    """Cycle midpoints get the per-frame speed interpolated correctly."""
    ...

def test_calibrate_clip_recovers_known_k():
    """Synthetic clip designed for K_target = 0.25 should round-trip to ~0.25.

    L = 0.9 m, TBF = 1.5 Hz, U = 0.25 · 0.9 · 1.5 = 0.3375 m/s.
    With 200 px body → 0.0045 m/px and 2.5 px/frame at 30 fps → U_pix = 0.3375 m/s. ✓
    """
    ...

def test_calibrate_clip_uses_external_swim_speed_if_given():
    """When clip.swim_speed_m_s is set, it overrides pose-derived speed."""
    ...

def test_calibrate_corpus_skips_missing_keypoints(tmp_path):
    """Clips without a keypoints.csv must be skipped, not fail."""
    ...

def test_calibrate_corpus_aggregates_one_real_clip(tmp_path):
    """With one synthetic-keypoints clip, aggregate K should match per-clip K."""
    ...

def _write_dlc_csv(path, kp: P.Keypoints) -> None:
    """Write a Keypoints object to a DLC-format multi-index CSV."""
    ...
