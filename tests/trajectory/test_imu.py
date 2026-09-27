"""Synthetic-data tests for magnetometer calibration and tilt-compensated heading."""
from __future__ import annotations
import numpy as np
from anchor.trajectory.imu import apply_calibration, fit_hard_soft_iron, tilt_compensated_heading

def _sample_unit_sphere(n: int, seed: int=0) -> np.ndarray:
    ...

def test_hard_soft_iron_recovers_known_distortion():
    ...

def test_tilt_compensated_heading_returns_zero_at_north():
    ...

def test_tilt_compensated_heading_handles_roll():
    ...

def test_declination_correction_applied():
    ...
