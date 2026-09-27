"""In-flight magnetometer calibration, validated by the dip-angle test.

Why this module exists
----------------------
Every magnetometer in this archive ships either uncalibrated or through a
dry-spin ellipsoid fit made on a few hundred samples covering a two-degree cap
of the sphere. Both routes produce a "heading" that is a function of the tag's
posture rather than of its azimuth: on ``BR_260318_S3`` the shipped heading
regresses on pitch and roll with R^2 = 0.9391, and dead-reckoning it walks the
animal out of the estuary and over land within the first kilometre
(``docs/regen_2026-09.md`` sections 14 and 16).

Two things are needed to fix that, and only the first is a fit.

**The fit.** An ellipsoid fitted to the magnetometer samples *taken on the
animal*, which cover the sphere because the animal rolls: 48 of 48 equal-area
cells on the flagship, against 1 of 48 for the dry spin.

**The validation.** A fit statistic cannot tell a sound calibration from a
degenerate one — on the flagship the refused dry-spin fit scores a *better*
``||A b|| / target`` than the sound in-flight fit, and its reported cost is
flattering because a runaway bias makes the residual flat in every direction.
What separates them is an external truth that needs no heading:

    For a correctly calibrated magnetometer whose axes coincide with the
    accelerometer's, the angle between the field vector and the gravity
    vector is the same at every attitude, and equals ``90 - dip``.

That is the **dip-angle test**. Its per-sample scatter (reported as a median
absolute deviation) measures calibration and axis-alignment quality directly.
On ``BR_260318_S3`` it is 2.44 deg for the in-flight fit, 39.38 deg for the raw
record and 38.93 deg for the dry-spin fit: a factor of 16, measured against the
geomagnetic field rather than against the filter, the polygon or the map.

Conventions, fixed here and nowhere else
----------------------------------------
**DOWN is the low-passed accelerometer vector itself, not its negation.**
``anchor.kinematics.mount`` declares "X forward, Y right, Z down, +1 g on accZ
at rest", ``sim/axy5_export.py`` writes that convention explicitly
(``g_dir = [0, 0, 1]``), and ``imu.tilt_compensated_heading``'s formulas
require it. The choice matters: flipping it maps every candidate axis
permutation ``P`` to ``-P``, which turns the measured angle into its supplement
and moves the winner of the search by exactly that reflection. It is stated as
a convention rather than measured, because no reflection-invariant statistic
can measure it (``docs/regen_2026-09.md`` section 16.6).

**The axis mapping is folded into A on the left.** ``P`` maps the
magnetometer's own axes into the accelerometer's frame, so the calibrated
field in the body frame is ``P @ A_fit @ (m_raw - b)`` and the calibration
written to disk carries ``A = P @ A_fit``. Downstream nothing changes:
``anchor.ingest.calibrate.apply_calibration`` computes ``(raw - b) @ A.T``,
which is exactly that product. **The mapping is therefore already applied by
the stored A and must not be applied a second time**; it is recorded in the
validation block for the reader, not for the pipeline.

**The symmetric square root is used, not the upper-triangular one.**
``|A(m - b)| = target`` identifies ``A^T A``, not ``A``: any ``R A`` with ``R``
orthogonal has the same residual, and the two roots differ by a rotation
applied to the field *relative to the accelerometer frame* — the polar factor
of the flagship's upper-triangular root is 5.39 deg, and the two routes'
calibrated directions differ by a median 6.67 deg because they also fit
different ellipsoids. ``anchor.trajectory.imu.fit_hard_soft_iron`` returns the
symmetric root, which is the one that introduces no rotation, so it is the
fitter used here. Since 2026-09-06 ``anchor.ingest.calibrate.fit_ellipsoid``
returns the symmetric root too, so the two routes no longer disagree about the
frame; cards written before that date still carry the rotation, and
``anchor.ingest.calibrate.is_symmetric_root`` is the diagnostic that tells them
apart (reported by :func:`validation_block`).

**Two fitters, and a stated rule for choosing between them.** The
nine-parameter ellipsoid needs the cloud to cover the sphere; on a cap it is
rank-deficient, and a rank-deficient soft-iron matrix buys a flat residual by
collapsing an axis. So a four-parameter hard-iron-only sphere fit
(:func:`fit_sphere_hard_iron`, ``A = I / r``) is carried as a fallback and is
selected by :data:`FITTER_RULE`. It is the honest model when the coverage will
not support six more parameters: it rescues ``LS_260311_S1`` outright, where
the ellipsoid fit is rank-deficient at cond(A) = 5852
(``docs/regen_2026-09.md`` section 16.13.4). Which fitter ran is recorded as
``fitter`` in the validation block.

**The 48 mappings are ranked on the MAD first, not on the dip offset.** The
site inclination is a *model* number; putting it inside the ranking objective
lets an error in it choose the frame, and section 16.13.5 measured that biting —
``APT_240702_S2``'s winner is one mapping at Elkhorn's dip and another at the
Galapagos dip, on identical data. The MAD does not contain the dip at all. But
a mapping and its negation have identical MADs and supplementary medians, so
the MAD alone cannot separate a mirror pair; the offset from the expected dip
breaks that tie, and only within :data:`RANK_MAD_MARGIN_DEG` of the best MAD.
The rule is recorded as ``ranking_rule`` in the validation block.
"""
from __future__ import annotations
import itertools
from dataclasses import dataclass
from typing import Optional, Sequence
import numpy as np
from anchor.ingest.calibrate import is_symmetric_root
from anchor.trajectory.imu import fit_hard_soft_iron
__all__ = ['AxisMapping', 'COVERAGE_CELLS', 'DipResult', 'FITTER_RULE', 'GRAVITY_LOWPASS_S', 'RANKING_RULE', 'RANK_MAD_MARGIN_DEG', 'SPHERE_FALLBACK_COND', 'SPHERE_FALLBACK_COVERAGE_MIN', 'SPIKE_ROBUST_Z', 'VALIDATION_VERSION', 'coverage_stats', 'dip_axis_search', 'dip_statistics', 'down_from_accel', 'expected_field_to_down_deg', 'fit_inflight_mag', 'fit_sphere_hard_iron', 'hard_iron_ratio', 'mapping_margin_deg', 'rank_key', 'reject_spikes', 'signed_permutations']
VALIDATION_VERSION = 2
GRAVITY_LOWPASS_S = 2.0
SPIKE_ROBUST_Z = 8.0
COVERAGE_CELLS = 48
SPHERE_FALLBACK_COND = 100.0
SPHERE_FALLBACK_COVERAGE_MIN = 0.25
RANK_MAD_MARGIN_DEG = 0.5

@dataclass(frozen=True)
class AxisMapping:
    """One signed axis permutation of the magnetometer, ``m_acc = P @ m_mag``.

    ``label`` names the *rows* of ``P``: ``"x,-y,z"`` means the accelerometer
    frame's X is the magnetometer's +X, its Y is the magnetometer's -Y, and its
    Z is the magnetometer's +Z. ``proper`` is ``det(P) == +1`` — a rotation; an
    improper mapping is a reflection, which a firmware axis convention is
    perfectly entitled to be and which the flagship turns out to need.
    """
    label: str
    matrix: tuple[tuple[int, int, int], ...]
    proper: bool

    @property
    def array(self) -> np.ndarray:
        ...

    @property
    def is_identity(self) -> bool:
        ...

    def to_dict(self) -> dict:
        ...

def signed_permutations() -> tuple[AxisMapping, ...]:
    """All 48 signed axis permutations: 24 rotations and 24 reflections.

    Both halves are searched because a firmware axis convention can be either.
    The identity is first, so a caller that wants "what the pipeline does
    today" can take element zero without knowing the enumeration order.
    """
    ...

def _box_lowpass(a: np.ndarray, width: int) -> np.ndarray:
    """Centred moving average along axis 0, edge-clamped, via a cumulative sum.

    Edge-clamped rather than zero-padded: a zero-padded mean at the ends would
    pull the gravity direction toward the origin and make the first and last
    seconds of every record look like free fall.

    NaN-aware: each output is the mean of the *finite* samples in its window,
    and is NaN only when the window holds none. A plain cumulative sum carries
    one NaN to every later row, which on a real record turned the gravity
    direction into NaN from the first dropout to the end (audit 2026-09-25).
    """
    ...

def down_from_accel(acc_xyz: np.ndarray, fs_hz: float, lowpass_s: float=GRAVITY_LOWPASS_S) -> np.ndarray:
    """Unit DOWN direction per sample from the low-passed specific force.

    The accelerometer channel reads +1 g along DOWN at rest (see the module
    docstring), so the low-passed vector *is* DOWN and is returned normalised.
    Rows whose low-passed norm is not usable come back as ``nan`` rather than
    as an arbitrary direction.
    """
    ...

def reject_spikes(mag_xyz: np.ndarray, robust_z: float=SPIKE_ROBUST_Z) -> tuple[np.ndarray, dict]:
    """``(keep_mask, info)`` for the per-axis robust-z spike rule.

    A triple is dropped when *any* axis lies more than ``robust_z`` robust
    z-scores (median, 1.4826 x MAD) from that axis's own median. See
    :data:`SPIKE_ROBUST_Z` for why the test is per-axis.
    """
    ...

def _fibonacci_cells(n: int) -> np.ndarray:
    """``n`` approximately equal-area directions on the unit sphere."""
    ...

def coverage_stats(unit: np.ndarray, n_cells: int=COVERAGE_CELLS) -> dict:
    """How much of the direction sphere a set of unit vectors occupies.

    Two independent statistics, because each catches a failure the other
    misses. ``occupied_fraction`` is combinatorial and catches a cloud broken
    into disconnected patches; ``min_scatter_eigenvalue`` is the smallest
    eigenvalue of the mean outer product of the unit vectors, which is the mean
    squared projection onto the cloud's thinnest direction and catches a cloud
    that is a thin shell around a great circle — a case the cell count can pass
    with three quarters of the sphere occupied.
    """
    ...

def expected_field_to_down_deg(dip_deg: float) -> float:
    """The field-to-DOWN angle implied by a magnetic inclination."""
    ...

@dataclass(frozen=True)
class DipResult:
    """The dip test for one axis mapping."""
    mapping: AxisMapping
    median_deg: float
    mad_deg: float
    p05_deg: float
    p95_deg: float
    offset_deg: float
    score_deg: float
    n: int

    def to_dict(self) -> dict:
        ...

def dip_statistics(unit_mag: np.ndarray, down_unit: np.ndarray, expected_deg: float) -> dict:
    """Field-to-DOWN angle statistics for one already-mapped field direction.

    ``score_deg`` is ``median |theta_i - expected|``, which penalises a biased
    median and a wide spread together. It was the statistic the 48-mapping
    search minimised until 2026-09-06 and is still reported, but it contains
    the site dip, so the search now ranks on ``mad_deg`` first and uses
    ``offset_deg`` only as a tie-break inside :data:`RANK_MAD_MARGIN_DEG` (see
    :data:`RANKING_RULE`). Spread alone cannot do the whole job: a mapping and
    its negation have identical MADs and supplementary medians, so it cannot
    tell a field 29 deg from DOWN from one 29 deg from UP, and that is exactly
    what the tie-break decides.
    """
    ...

def rank_key(result: 'DipResult', best_mad_deg: float, mad_margin_deg: float=RANK_MAD_MARGIN_DEG) -> tuple:
    """Sort key implementing :data:`RANKING_RULE` for one mapping.

    Mappings whose MAD is within ``mad_margin_deg`` of the best MAD form the
    tie group and come first, ordered by ``|offset|``; everything else follows,
    ordered by MAD. A non-finite MAD sorts last. The label is the final key so
    the ordering is deterministic on exact ties.
    """
    ...

def dip_axis_search(unit_mag: np.ndarray, down_unit: np.ndarray, expected_deg: float, mappings: Optional[Sequence[AxisMapping]]=None, mad_margin_deg: float=RANK_MAD_MARGIN_DEG) -> tuple[DipResult, ...]:
    """The dip test over every signed axis permutation, best mapping first.

    Ranked **MAD-first** (:data:`RANKING_RULE`, :func:`rank_key`): on spread,
    which is independent of the site inclination, with the offset from the
    expected dip breaking ties only inside ``mad_margin_deg``. Before
    2026-09-06 the sort was on ``median |theta - expected|`` alone, which put
    the model's dip figure inside the objective and let an error in it choose
    the frame.

    ``unit_mag`` are the *calibrated* field directions in the magnetometer's
    own axes. Remapping them is exactly equivalent to remapping the raw vectors
    and refitting, for the symmetric square root this module uses: the
    ellipsoid form maps as ``M -> P M P^T``, its symmetric root as
    ``A -> P A P^T``, and ``(P A P^T)(P m - P b) = P A (m - b)``. So the 48
    mappings cost one fit rather than 48; ``tests/ingest/test_mag_inflight.py``
    holds that identity to floating-point tolerance.
    """
    ...

def fit_sphere_hard_iron(m: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """The four-parameter hard-iron-only fallback: ``(b, A)`` with ``A = I / r``.

    A least-squares sphere through the cloud — three centre coordinates and one
    radius, solved linearly, with no soft-iron term at all. It cannot run away
    the way the Levenberg-Marquardt ellipsoid fitter does and cannot be
    rank-deficient the way the algebraic one can, because it has no degrees of
    freedom left to spend collapsing an axis. That is the point of it: it is
    the honest model when the coverage will not support nine parameters
    (``docs/regen_2026-09.md`` section 16.13.4).

    ``A`` is symmetric by construction, so a calibration written through this
    route introduces no rotation either.
    """
    ...

def _unit_rows(v: np.ndarray) -> np.ndarray:
    """Row-normalised copy of ``v``; zero rows come back as ``nan``."""
    ...

def ranking_best_mad_deg(ranking: Sequence['DipResult']) -> float:
    """The minimum finite MAD over a ranking — :func:`rank_key`'s tie reference.

    Not the same as ``ranking[0].mad_deg``: the winner is chosen on ``|offset|``
    *inside* the tie group, so it can carry a MAD up to ``mad_margin_deg``
    above the minimum. Anything asking "is this mapping in the tie group?" has
    to ask it against this number, exactly as :func:`dip_axis_search` did when
    it sorted.
    """
    ...

def mapping_margin_deg(best: 'DipResult', other: Optional['DipResult'], mad_margin_deg: float=RANK_MAD_MARGIN_DEG, best_mad_deg: Optional[float]=None) -> float:
    """Degrees by which ``best`` beats ``other`` **in the deciding statistic**.

    The MAD when ``other`` is outside the tie margin, ``|offset|`` when it is
    inside — i.e. the same statistic :func:`rank_key` used to put ``best``
    first, so the number is always the one the choice was actually made on.

    ``best_mad_deg`` is the tie group's reference, :func:`ranking_best_mad_deg`
    of the ranking ``best`` came from. Pass it. It defaults to ``best.mad_deg``,
    which is the same number whenever the winner *is* the minimum-MAD mapping —
    the mirror-pair case, and every card in this repository — and is up to
    ``mad_margin_deg`` too generous when it is not, which would score a mapping
    ``rank_key`` placed outside the group as though it were inside and can
    return a negative margin.

    Callers that instead difference ``score_deg`` are measuring a statistic the
    search no longer minimises, and can get a negative margin for a mapping
    that beats the other on spread by a factor of six: on the raw
    ``BR_260318_S3`` record the identity's MAD is 39.56 deg against the
    winner's 6.43 deg, and its ``score_deg`` is nonetheless 1.31 deg smaller.
    """
    ...

def hard_iron_ratio(mag_raw: np.ndarray, b: np.ndarray) -> float:
    """``||b|| / R``, the hard-iron offset in units of the field radius.

    ``R`` is the mean ``|m - b|`` over the samples, i.e. the fitted sphere's
    radius in raw counts. Measured about the *fitted* centre rather than about
    the centroid: a centroid is a biased centre estimate whenever the attitudes
    cover a cap rather than the whole sphere, and that bias is what made the
    ratio look like a universal ~2x across the archive when about the fitted
    centre it runs 0.83 to 1.49 on the sound fits.
    """
    ...

def fit_inflight_mag(mag_raw: np.ndarray, acc_xyz: np.ndarray, *, fs_hz: float, dip_deg: float, dip_tolerance_deg: float=1.0, site: Optional[str]=None, mag_index: Optional[np.ndarray]=None, spike_robust_z: float=SPIKE_ROBUST_Z, lowpass_s: float=GRAVITY_LOWPASS_S, coverage_cells: int=COVERAGE_CELLS, sphere_cond_max: float=SPHERE_FALLBACK_COND, sphere_coverage_min: float=SPHERE_FALLBACK_COVERAGE_MIN, mad_margin_deg: float=RANK_MAD_MARGIN_DEG, source: str='', top_k: int=5) -> dict:
    """Fit and validate an in-flight magnetometer calibration.

    Parameters
    ----------
    mag_raw
        ``(m, 3)`` raw magnetometer counts. NaN rows are dropped.
    acc_xyz
        ``(n, 3)`` calibrated accelerometer, in g, on the *full* sample grid —
        the gravity low pass needs the contiguous record, not the magnetometer
        subset.
    fs_hz
        Accelerometer sample rate, for the gravity low pass.
    dip_deg
        Magnetic inclination at the site, positive downward. See
        :func:`anchor.trajectory.imu.inclination_for_site`.
    mag_index
        Row indices into ``acc_xyz`` at which ``mag_raw`` was sampled. Default
        (``None``) means the two arrays are on the same grid, which requires
        ``len(mag_raw) == len(acc_xyz)``.

    Returns
    -------
    dict
        The on-disk calibration format (``A``, ``b``, ``target``, ``cost``,
        ``n_samples``) with the winning axis mapping already folded into ``A``,
        the fitter chosen by :data:`FITTER_RULE` and the mapping chosen by
        :data:`RANKING_RULE` (both recorded in the ``validation`` block),
        plus a ``validation`` block. Write it with
        :func:`anchor.ingest.calibrate.save_calibration`; apply it with
        :func:`anchor.ingest.calibrate.apply_calibration`, which needs no
        knowledge of the mapping.
    """
    ...

def validation_block(cal: Optional[dict]) -> dict:
    """The ``validation`` block of a calibration dict, or ``{}``.

    Total over anything a caller holds — a calibration with no block, a
    ``None``, a malformed JSON payload — because the doctor and the ledger both
    ask this of files they did not write.
    """
    ...
