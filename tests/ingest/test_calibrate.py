"""Calibration tests: synthetic ellipsoid → identity, real spin CSV fit."""
from __future__ import annotations
import numpy as np
from anchor.ingest import calibrate as C, io

def _sample_unit_sphere(n: int=2000, seed: int=0) -> np.ndarray:
    ...

def test_ellipsoid_fit_recovers_identity():
    """Unit-sphere samples should recover ``A ≈ I``, ``b ≈ 0``, cost ≈ 0."""
    ...

def test_ellipsoid_fit_recovers_known_transform():
    """If we push unit-sphere through known A,b, fit should invert it."""
    ...

def test_save_load_roundtrip(tmp_path):
    ...

def test_apply_calibration_matches_manual(calib_spin_csv):
    ...

def test_calibration_from_spins(tmp_path, calib_spin_csv):
    """End-to-end helper: read spin CSV(s), fit, save."""
    ...

def _symmetric_ellipsoid_cloud(n: int=4000, seed: int=4):
    """``(raw, true_unit_directions, A_true, b_true)`` from a symmetric truth.

    The generating soft-iron tensor is symmetric on purpose. "No net rotation"
    is only a well-posed claim against a truth that has none, and a genuine
    induced-field soft-iron tensor *is* symmetric — which is the physical
    argument for preferring the symmetric root in the first place.
    """
    ...

def test_fit_ellipsoid_returns_a_symmetric_root_that_adds_no_rotation():
    ...

def test_the_upper_triangular_root_of_the_same_fit_would_have_rotated_it():
    """Why the change was needed, measured on the same synthetic cloud.

    The Cholesky root of the fit's own ``A^T A`` has an identical residual and
    is what this function returned before 2026-09-06. Its polar factor is a
    real rotation, and it moves every calibrated direction off the truth.
    """
    ...

def test_is_symmetric_root_is_total_over_anything_a_caller_holds():
    ...

def test_load_calibration_keeps_a_pre_2026_09_06_card_exactly_as_written(tmp_path):
    """The loader diagnoses; it does not repair. Silently symmetrising a stored
    matrix would change what every archived run means."""
    ...

def _z_only_spin(n: int=3000, seed: int=4) -> np.ndarray:
    """A spin about Z only: the field sweeps a circle and Z never changes."""
    ...

def test_full_sphere_fit_passes_the_gate():
    ...

def test_z_only_spin_is_refused():
    ...

def test_calibration_from_spins_withholds_a_degenerate_mag_card(tmp_path, monkeypatch):
    ...
