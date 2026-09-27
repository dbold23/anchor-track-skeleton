"""Sensor calibration via ellipsoid fit.

Given a point cloud of accelerometer (or magnetometer) samples covering many
orientations, we fit an affine map ``cal: raw -> A @ (raw - b)`` whose output
has unit norm. This corrects bias (``b``) and axis-scale/misalignment (``A``)
jointly — the standard hard+soft iron correction for mag sensors, and an
analogous treatment for accel (where the target norm is 1 g).

We use ``scipy.optimize.least_squares`` on the residual
``||A(raw - b)|| - target``. The *search* is over an upper-triangular ``A``
(6 params) + ``b`` (3 params) → 9 parameters total, enough to represent any
positive-definite ellipsoid without redundancy.

Which square root is returned, and why it changed
-------------------------------------------------
``|A(raw - b)| = target`` identifies ``A^T A``, not ``A``: every ``Q A`` with
``Q`` orthogonal has the same residual to the last digit. The representatives
therefore differ by a rotation (or a reflection) applied to the calibrated
vector **relative to the other sensors' frame**, which rotates every heading
computed through the calibration. On ``BR_260318_S3`` the polar factor of the
upper-triangular root this function used to return is a **5.39 deg** rotation,
moving each calibrated field direction by a median of 5.32 deg
(``docs/regen_2026-09.md`` section 16.5).

Since **2026-09-06** this function returns the **symmetric** (positive
semi-definite) square root of ``A^T A`` instead: the unique representative with
no orthogonal factor of its own, and the one a genuine induced-field soft-iron
tensor actually is. The residual, the cost and ``b`` are unchanged by the
substitution — ``|S x|^2 = x^T S^2 x = x^T A^T A x = |A x|^2`` exactly — so the
on-disk JSON format is unchanged and only the frame of the calibrated vector
moves.

**Calibration JSONs written before 2026-09-06 carry the upper-triangular root
and therefore that rotation.** :func:`load_calibration` does not repair them:
it returns them exactly as written, because silently symmetrising a stored
matrix would change what an archived card means. What ships instead is a
diagnostic, :func:`is_symmetric_root`, used by
:func:`anchor.ingest.mag_inflight.validation_block` and available to
``anchor.qc.calibration_degeneracy``, so a reader can tell an old card from a
new one rather than having to guess from the file's mtime.
"""
from __future__ import annotations
import json
from pathlib import Path
from typing import Optional
import numpy as np
import pandas as pd
from scipy.optimize import least_squares

def _pack(A: np.ndarray, b: np.ndarray) -> np.ndarray:
    """6 upper-triangular entries of A + 3 bias entries."""
    ...

def _unpack(params: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    ...

def _residual(params: np.ndarray, raw: np.ndarray, target: float) -> np.ndarray:
    ...
SYMMETRIC_ROOT_RTOL = 1e-09

def is_symmetric_root(A) -> bool:
    """Is ``A`` the symmetric square root, i.e. does it add no rotation?

    ``True`` for a matrix produced by :func:`fit_ellipsoid` or
    :func:`anchor.trajectory.imu.fit_hard_soft_iron` on or after 2026-09-06,
    and for a signed permutation of one folded in on the left only when that
    permutation is diagonal. ``False`` for the upper-triangular roots written
    before that date, which carry a rotation of the calibrated vector relative
    to the accelerometer frame (module docstring; regen section 16.5).

    Total over anything a caller holds — a list of lists out of JSON, a wrong
    shape, ``None`` — because the doctor and the ledger ask this of files they
    did not write. Anything that is not a 3x3 of finite numbers is ``False``.
    """
    ...

def symmetric_root(A) -> np.ndarray:
    """The symmetric positive semi-definite square root of ``A^T A``.

    The representative of the fit's equivalence class that introduces no
    rotation of its own. ``|symmetric_root(A) x| == |A x|`` for every ``x``, so
    substituting it changes no residual, no cost and no norm — only the
    direction of the calibrated vector, and only by the polar factor the fit
    never identified in the first place.
    """
    ...

def fit_ellipsoid(raw: np.ndarray, target_norm: float=1.0) -> dict:
    """Fit the 9-parameter ellipsoid model. Returns {'A': 3x3, 'b': 3, 'target': float}.

    The search is over an upper-triangular ``A``; the ``A`` **returned** is the
    symmetric square root of that fit's ``A^T A`` (module docstring). The two
    have identical residuals, so ``cost`` is the optimiser's own number and is
    comparable with cards written before 2026-09-06; the matrix is not, and
    :func:`is_symmetric_root` tells the two apart.
    """
    ...

def spin_fit_degeneracy(cal: dict, raw: np.ndarray, *, kind: str) -> list[str]:
    """Reasons a spin fit cannot be trusted; empty when it can.

    A low cost is not evidence of a good fit: a Z-only spin lets the optimiser
    run the bias away along the unexcited axis (``b_z = -7418`` on a real
    card) while the residual stays flat, because ``|A(m - b)|`` is then
    dominated by the constant ``|A b|``. The gate reuses the in-flight fitter's
    criteria (:mod:`anchor.ingest.mag_inflight`) and the doctor's runaway
    floor (:mod:`anchor.qc`), so a spin card and an in-flight card are refused
    for the same reasons:

    - ``cond(A)`` above ``SPHERE_FALLBACK_COND`` (an axis has collapsed),
    - calibrated directions occupying less than
      ``SPHERE_FALLBACK_COVERAGE_MIN`` of the equal-area cells (the spin did
      not turn the tag through enough of the sphere to fit nine parameters),
    - ``||A b|| / target`` above the doctor's runaway floor (the bias left the
      data cloud).
    """
    ...

def fit_accel_ellipsoid(acc_xyz: np.ndarray) -> dict:
    """Accel target is 1 g (data are already in g)."""
    ...

def fit_mag_ellipsoid(mag_xyz: np.ndarray) -> dict:
    """Mag target is the mean radius of the raw cloud — absolute units cancel."""
    ...

def apply_calibration(df: pd.DataFrame, cal_accel: Optional[dict]=None, cal_mag: Optional[dict]=None) -> pd.DataFrame:
    """Overwrite accX/Y/Z and/or magX/Y/Z with calibrated values."""
    ...

def save_calibration(cal: dict, path: str | Path) -> None:
    ...

def load_calibration(path: str | Path) -> dict:
    """Read a calibration card **exactly as written**, old root and all.

    No repair happens here, deliberately. A card written before 2026-09-06
    carries the upper-triangular square root and with it a rotation of the
    calibrated vector relative to the accelerometer frame; symmetrising it on
    load would silently change what every archived run means. Ask
    :func:`is_symmetric_root` of ``cal["A"]`` instead — the diagnostic is
    reported by :func:`anchor.ingest.mag_inflight.validation_block` and is
    available to ``anchor.qc.calibration_degeneracy``.
    """
    ...

def calibration_from_spins(spin_paths: list[str | Path], out_dir: str | Path, source_schema: str='axy5') -> tuple[Optional[Path], Optional[Path]]:
    """End-to-end: read spin CSVs, concat, fit accel + mag (if present), save.

    Returns ``(accel_json_path, mag_json_path)``; either is ``None`` when that
    fit was refused by :func:`spin_fit_degeneracy` (or, for mag, when the spins
    carry no magnetometer). A refused fit is written beside the good ones as
    ``accel.rejected.json`` / ``mag.rejected.json`` with its reasons, so the
    evidence is kept but nothing downstream can load it by the usual name.
    """
    ...
