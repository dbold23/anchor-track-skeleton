"""Magnetometer + accelerometer processing for AXY-tag dead-reckoning.

Two functions are the workhorses (per design doc §5.3):

  1. fit_hard_soft_iron(mx, my, mz)
     Ellipsoid fit to recover hard-iron offset b (3,) and soft-iron matrix
     A (3x3) from magnetometer samples on the animal. Application:
         m_calibrated = A @ (m_raw - b)
     Reference: NXP AN4246 (eCompass calibration).

  2. tilt_compensated_heading(ax, ay, az, mx, my, mz, declination_deg=0.0)
     Compute heading (true north, radians, [-pi, pi]) from gravity-derived
     roll/pitch + tilt-compensated magnetometer. Apply IGRF declination for
     the deployment location/date. Reference: Bidder et al. 2015 §2.3.

Geomagnetic constants: fetched, not remembered
-----------------------------------------------
The declinations and inclinations below were **quoted from memory of WMM2025**
until 2026-09-06 and are now taken from the model itself. Every value in this
module comes from the British Geological Survey's geomagnetic model web
service,

    https://geomag.bgs.ac.uk/web_service/GMModels/wmm/2025
        ?latitude=<deg N>&longitude=<deg E>&altitude=0&date=YYYY-MM-DD&format=json

fetched 2026-09-06, one JSON per point, saved with the request that produced it
under ``reports/regen_2026-09/section17/wmm/`` (``PROVENANCE.txt``,
``FETCHLOG.txt``). Each constant names its file, its coordinates, its date and
the model revision. The service was cross-checked offline against ``pygeomag``
1.1.0's bundled ``.COF`` coefficients and agrees to 0.001 deg and 1 nT.

What changed, and what it moves: ``ELKHORN_DECLINATION_DEG_2026`` was 12.7 from
memory and is 12.580 from the model, a **-0.120 deg** rotation of every heading
computed through it: ``anchor.trajectory.axy_ingest`` and
``run_deployment``'s ``--declination-deg`` default both take it, so the
flagship's heading rotates by exactly that and no other quantity moves.
``PUERTO_GRANDE_INCLINATION_DEG_2026`` was 22.0 +/- 2 and is 18.168, an error
of 3.83 deg — larger than the tolerance it declared.

Recompute per deployment date rather than reusing a constant whose name carries
an epoch: the secular variation at Elkhorn is -5.2 arcmin/y in declination, so
these figures are good for about a year at the 0.1 deg level.
"""
from __future__ import annotations
import numpy as np
PUERTO_GRANDE_DECLINATION_DEG_2026 = 2.223
ELKHORN_DECLINATION_DEG_2026 = 12.58
ELKHORN_INCLINATION_DEG_2026 = 60.402
PUERTO_GRANDE_INCLINATION_DEG_2026 = 18.168

def inclination_for_site(site: str | None) -> float | None:
    """Magnetic inclination for a ``DeploymentConfig.site`` string, or ``None``.

    ``None`` for a null site and for one the map does not name. Callers that
    need a number must take it from the operator (``--dip-deg``) rather than
    falling back to a default: see :data:`SITE_INCLINATION_DEG_2026`.
    """
    ...

def inclination_tolerance_for_site(site: str | None) -> float:
    """The +/- carried on :func:`inclination_for_site`; 2.0 deg when unnamed.

    The unnamed-site default stays at 2.0 deg deliberately. It is not a model
    uncertainty — :func:`inclination_for_site` returns ``None`` for a site the
    map does not name, so no dip is available at all — and a caller that passes
    ``--dip-deg`` for an unrecorded site has taken the number off a map by
    hand, which is worth several times the model's own 0.4 deg.
    """
    ...

def fit_hard_soft_iron(mx: np.ndarray, my: np.ndarray, mz: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Fit a tri-axial magnetometer to a sphere-to-ellipsoid mapping.

    Solves for hard-iron offset b (3,) and soft-iron matrix A (3x3) such
    that for calibrated samples m_c = A @ (m - b), |m_c| is approximately
    constant (= local field magnitude).

    Implementation: least-squares fit to the implicit ellipsoid
        (m - b)^T M (m - b) = 1
    then decompose M = A^T A via Cholesky to recover A. This is the
    standard NXP/ST eCompass calibration.

    Returns
    -------
    b : (3,)   hard-iron offset, in input units
    A : (3, 3) soft-iron transform; m_calibrated = A @ (m - b)
    """
    ...

def apply_calibration(mx: np.ndarray, my: np.ndarray, mz: np.ndarray, b: np.ndarray, A: np.ndarray) -> np.ndarray:
    ...

def tilt_compensated_heading(ax: np.ndarray, ay: np.ndarray, az: np.ndarray, mx: np.ndarray, my: np.ndarray, mz: np.ndarray, declination_deg: float=0.0) -> np.ndarray:
    """Tilt-compensated magnetic heading -> true heading.

    Convention (NED-like, but sensor-axis dependent):
      ax, ay, az: accelerometer in body frame (gravity dominant). The
        channel reads +1 g along the body DOWN axis at rest, so a
        body-aligned, dorsal-side-up tag reads az = +1 -- the convention
        anchor.kinematics.mount declares and sim/axy5_export.py writes
        (g_dir = [0, 0, 1]). The formulas below require it: roll =
        atan2(ay, az) is zero at az = +1, and the tilt compensation recovers
        the bearing of +X only when the static vector is DOWN. (An earlier
        version of this docstring said "gravity along -z body"; that
        parenthetical contradicted both the formulas and the record, and was
        measured wrong on BR_260318_S3 -- the static accelerometer vector is
        within 26 deg of +Z on 32.2 % of the attached span against 0.06 % for
        -Z. See docs/regen_2026-09.md section 16.3.)
      mx, my, mz: calibrated magnetometer in body frame.
    Output: heading in radians, [-pi, pi], 0 = magnetic north (or true if
    declination_deg is provided), increasing clockwise (east positive).

    Standard tilt compensation per NXP AN4248 / Bidder 2015 eq. (2-5).
    """
    ...
