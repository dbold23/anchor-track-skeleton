"""Pose-detection wrapper tests: keypoint loading + kinematic feature math."""
from __future__ import annotations
import numpy as np
import pandas as pd
import pytest
from anchor.validation import pose as P

def _synthetic_keypoints(n_frames: int=300, fps: float=30.0, tbf: float=1.5) -> P.Keypoints:
    """Two keypoints (snout, tail_tip) with tail oscillating laterally at ``tbf`` Hz."""
    ...

def test_keypoints_dataclass_validates_shape():
    """Mismatched shapes must error at construction time."""
    ...

def test_body_length_pix_constant_along_axis():
    """Static body axis → constant body length."""
    ...

def test_tailbeat_recovers_synthetic_freq():
    """Pose-derived TBF on a 1.5 Hz sine should land within 0.1 Hz."""
    ...

def test_keypoints_to_kinematics_schema():
    """Per-cycle output must carry the documented columns."""
    ...

def test_keypoints_to_kinematics_uses_species_defaults():
    """Default species mappings cover the four paper species."""
    ...

def test_dlc_csv_loader_roundtrip(tmp_path):
    """Write a minimal DLC-style CSV and parse it back."""
    ...

def test_tailbeat_detected_while_fish_translates():
    """A fish drifting across the frame must still yield its tailbeat."""
    ...

def test_tailbeat_survives_keypoint_dropout():
    ...

def test_metric_at_time_uses_positions_not_labels():
    ...
