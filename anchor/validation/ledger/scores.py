"""The ledger's scoring functions.

Five families, all of them proper or diagnostic in the sense section 3.3 of the
design document requires, and all of them computed in channel coordinates:

``rmse_*``
    Accuracy of the ensemble mean. Not a proper score; reported because a
    reader expects it and because it is the only number comparable with the
    published pre-twin figures.
``crps_*``
    Continuous ranked probability score, ensemble form. Proper, in metres,
    reduces to the absolute error for a deterministic forecast. This is the
    scalar every gate in section 3.7 that says "CRPS" means.
``variogram_score``
    Scheuerer & Hamill (2015) variogram score of order ``p``. Proper for the
    *joint* distribution over a path: unlike a sum of per-step CRPS values it
    is sensitive to the correlation structure, which is exactly what a
    degenerate particle filter destroys. Order 0.5 is their recommendation,
    and section 3.7 fixes it.
``rank_histogram``
    Calibration of the ensemble for a scalar functional of the whole path.
    Flat means calibrated; U-shaped means under-dispersed; dome-shaped means
    over-dispersed; sloped means biased.
``credible_containment``
    Empirical coverage of the central ``level`` credible interval, per step.
    G-field's floor is stated on this number.

References
----------
- Gneiting & Raftery 2007, *JASA* 102:359-378 (CRPS, propriety).
- Scheuerer & Hamill 2015, *Mon. Weather Rev.* 143:1321-1334 (variogram score).
- Hamill 2001, *Mon. Weather Rev.* 129:550-560 (rank histograms).
"""
from __future__ import annotations
from typing import Callable, Iterable, Mapping, Optional, Sequence
import numpy as np
from anchor.validation.ledger.channel import CenterlineLike, to_channel
__all__ = ['PATH_FUNCTIONALS', 'QUANTILE_METHOD', 'credible_containment', 'credible_interval', 'crps_ensemble', 'crps_gaussian', 'ensemble_rank', 'functional_ranks', 'max_up_slough_excursion_m', 'net_displacement_m', 'rank_histogram', 'rmse', 'score_paths', 'total_path_length_m', 'variogram_score']

def rmse(error: np.ndarray) -> float:
    """Root mean square of an error field, ignoring non-finite entries."""
    ...

def crps_ensemble(ensemble: np.ndarray, observation: np.ndarray, *, fair: bool=False) -> np.ndarray:
    """Empirical CRPS of an ``(m, ...)`` ensemble against an ``(...)`` observation.

    ``CRPS = E|X - y| - 0.5 E|X - X'|``, both expectations estimated from the
    ``m`` members. With ``fair=True`` the spread term uses the unbiased
    ``1 / (m (m - 1))`` normaliser (Ferro 2014), which removes the
    ``O(1 / m)`` optimism of the plain estimator; with ``fair=False`` it uses
    ``1 / m**2``, the textbook form. Units are the units of the input.

    Returns an array shaped like ``observation`` (a 0-d array for a scalar
    observation), so callers keep control of how they pool over steps.
    """
    ...

def crps_gaussian(mu: np.ndarray, sigma: np.ndarray, observation: np.ndarray) -> np.ndarray:
    """Closed-form CRPS of ``N(mu, sigma**2)``, for the correctness cross-check."""
    ...

def variogram_score(ensemble: np.ndarray, observation: np.ndarray, *, order: float=0.5, weights: 'np.ndarray | str | None'=None, stride: int=1) -> float:
    """Variogram score of order ``order`` for a path.

    Parameters
    ----------
    ensemble
        ``(m, d)`` scalar paths, or ``(m, d, k)`` vector paths — for a vector
        path the pairwise difference is the Euclidean norm, so a 2-D track can
        be scored without picking a component.
    observation
        ``(d,)`` or ``(d, k)``, the verifying path.
    order
        ``p`` in ``|y_i - y_j|**p``. Section 3.7 fixes 0.5.
    weights
        ``None`` for uniform weights, ``"inverse_lag"`` for the ``1 / |i - j|``
        weighting Scheuerer & Hamill recommend for time series, or an explicit
        ``(d, d)`` array.
    stride
        Thin the path before scoring. The score is a double sum over the
        ``d**2`` step pairs, so a 2880-step track at ``stride=1`` costs
        ``m * 8.3e6`` operations; thinning is the supported way to bound that
        *cost in time*. Peak memory is bounded independently, by tiling the
        pair grid (see :data:`_VARIOGRAM_TILE_BYTES`), so a long path is slow
        rather than unallocatable. Scores are only comparable between runs
        that used the same stride.

    Returns
    -------
    float
        Lower is better. Zero only for an ensemble whose pairwise-difference
        structure reproduces the observation's exactly.

    Notes
    -----
    An explicit ``weights`` array is the one ``(d, d)`` allocation this
    function cannot bound, because the caller has already made it; it is read
    a tile at a time and never modified.
    """
    ...
_VARIOGRAM_MEMBER_BLOCK = 64

def _variogram_tiling(m: int, d: int, k: int) -> 'tuple[int, int]':
    """``(rows, members)`` pair tile whose working arrays fit the byte budget.

    Peak live bytes per ``(member, row, column)`` entry, counting the
    temporaries numpy keeps alive at once. A scalar path holds the difference,
    its absolute value and the ``p``-th power: 24 B. A ``k``-vector path holds
    the ``(..., k)`` component difference and its square (``16k`` B) while
    ``linalg.norm`` reduces them, then the norm and its power (16 B). Short
    paths get a single tile, i.e. exactly the untiled computation.
    """
    ...

def _pair_distance(paths: np.ndarray, i0: int, i1: int) -> np.ndarray:
    """``(b, i1 - i0, d)`` distances from rows ``i0:i1`` to every step.

    ``paths`` is ``(b, d)`` or ``(b, d, k)``; a vector path uses the Euclidean
    norm of the component difference, so a 2-D track needs no component choice.
    """
    ...

def _variogram_weight_spec(weights: 'np.ndarray | str | None', d: int) -> 'np.ndarray | str | None':
    """Validate a weights argument up front, before any pair work is done."""
    ...

def _variogram_weight_tile(spec: 'np.ndarray | str | None', d: int, i0: int, i1: int) -> np.ndarray:
    """Rows ``i0:i1`` of the ``(d, d)`` weight matrix, diagonal zeroed.

    Always a fresh array: an explicit caller-supplied matrix is read, never
    written, so zeroing the diagonal cannot reach back into the caller's copy.
    """
    ...

def total_path_length_m(path: np.ndarray, centerline: Optional[CenterlineLike]=None) -> float:
    """Sum of step lengths along an ``(n, 2)`` path."""
    ...

def net_displacement_m(path: np.ndarray, centerline: Optional[CenterlineLike]=None) -> float:
    """Straight-line distance from the first to the last position of a path."""
    ...

def max_up_slough_excursion_m(path: np.ndarray, centerline: Optional[CenterlineLike]=None) -> float:
    """Furthest the path ever gets up-slough of where it started, in arc length.

    ``max_{t > 0} (s(t) - s(0))`` with ``s`` the centreline arc length. The
    maximum runs over the steps *after* the first: including ``t = 0``, where
    the summand is identically zero, would floor the functional at zero and
    collapse every never-up-slough path onto the same value. "Never went
    up-slough of the release point" is a finding, not a floor, so the sign is
    genuinely kept and a purely down-slough path returns a negative number.

    A path with fewer than two positions has no excursion to measure and
    returns ``nan``.
    """
    ...

def ensemble_rank(ensemble_values: np.ndarray, truth_value: float, rng: Optional[np.random.Generator]=None) -> int:
    """Rank of ``truth_value`` among ``m`` members, in ``1 .. m + 1``.

    Ties are broken uniformly at random (Hamill 2001): without that, a
    discrete or clipped functional piles mass on one bin and the histogram
    looks miscalibrated when it is not.
    """
    ...

def functional_ranks(ensemble_paths: np.ndarray, truth_path: np.ndarray, centerline: Optional[CenterlineLike]=None, functionals: Optional[Mapping[str, Callable[..., float]]]=None, rng: Optional[np.random.Generator]=None) -> dict[str, int]:
    """One rank per functional for a single verification case.

    ``ensemble_paths`` is ``(m, n, 2)``; ``truth_path`` is ``(n, 2)``. A rank
    histogram needs many cases, so collect these dicts across seeds, blocks or
    deployments and pass the list to :func:`rank_histogram`.
    """
    ...

def rank_histogram(ranks: Sequence[int], n_members: int, n_bins: Optional[int]=None) -> dict:
    """Bin ranks and test them against the uniform.

    Returns ``counts``, ``bin_edges`` (half-integer cut points bracketing the
    1-based integer ranks), ``expected_per_bin``, ``ranks_per_bin``, the
    chi-square statistic and p-value, and the reliability index
    ``RI = sum_k |f_k - e_k|`` where ``e_k`` is the bin's share of the
    ``n_members + 1`` ranks (0 is perfect, 2 is the worst possible).

    ``n_bins`` need not divide ``n_members + 1``. When it does not, the bins
    hold different numbers of integer ranks and the expected counts are
    unequal in exactly that proportion; assuming equal expectations instead
    would declare a perfectly uniform sample miscalibrated (at ``m = 63`` with
    ``n_bins = 10``, one uniform sample of 200000 ranks scores
    ``chi2 = 1199.5``, ``p = 1.6e-252`` under the equal-expectation assumption
    against ``chi2 = 10.4``, ``p = 0.32`` under this one).

    A large p-value is *not* evidence of calibration; a small one is evidence
    against it. The ledger reports the statistic and lets the reader decide.
    """
    ...

def aggregate_functional_ranks(rank_dicts: Iterable[Mapping[str, int]], n_members: int, n_bins: Optional[int]=None) -> dict[str, dict]:
    """Rank histogram per functional across a collection of cases."""
    ...

def credible_interval(ensemble: np.ndarray, level: float=0.9, method: str=QUANTILE_METHOD) -> tuple[np.ndarray, np.ndarray]:
    """Central ``level`` interval of an ``(m, ...)`` ensemble, per trailing cell.

    See :data:`QUANTILE_METHOD` for why the estimator is not numpy's default.
    """
    ...

def credible_containment(ensemble: np.ndarray, truth: np.ndarray, level: float=0.9, method: str=QUANTILE_METHOD) -> float:
    """Fraction of cells where ``truth`` falls inside the central ``level`` interval.

    A calibrated ensemble returns ``level``. This is the number G-field's
    "containment on at least 90 percent of blocks" floor is stated on, applied
    along and across separately.
    """
    ...

def score_paths(ensemble_xy: np.ndarray, truth_xy: np.ndarray, centerline: CenterlineLike, *, level: float=0.9, variogram_order: float=0.5, variogram_stride: int=1, variogram_weights: 'np.ndarray | str | None'=None, crps_fair: bool=False, rng: Optional[np.random.Generator]=None) -> dict[str, float]:
    """Every score in section 3.7, in channel coordinates, for one run.

    ``ensemble_xy`` is ``(m, n, 2)`` posterior sample *paths* (not marginal
    draws: the variogram score and the functional ranks both read the joint
    structure). ``truth_xy`` is ``(n, 2)``.

    Returns a flat ``{name: float}`` mapping, which is what
    :data:`anchor.trajectory.sensitivity.SCORE_REGISTRY` and
    :class:`~anchor.validation.ledger.card.ScoreCard` both consume. Ranks are
    included as floats for one case; feed many cases through
    :func:`aggregate_functional_ranks` to get the histograms.

    Read ``fraction_at_centerline_end`` before reading anything named
    ``*_along_*``: it must be ``0.0``. The centreline has to span the track,
    otherwise ``project`` clamps the off-end positions to a single arc length
    and the along-channel scores measure the clamp.
    """
    ...
