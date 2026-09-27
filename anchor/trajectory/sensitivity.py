"""Sensitivity analysis for particle-filter hyperparameters.

A reviewer's standard question about any novel filter is: how much does the
result depend on the knobs you chose? This harness varies one
:class:`~anchor.ingest.config.TrajectoryConfig` field over a grid, reruns the
reconstruction for each value, and scores each run — so the answer is a table,
not a hand-wave.

The harness is decoupled from the (heavy) particle-filter driver: the caller
supplies ``reconstruct_fn(value) -> result`` and one or more
``score_fns`` mapping a result to a scalar **or to a ``{name: float}`` dict**,
which is flattened into one column per key. Typical scores are the held-out VPC
drift (:func:`anchor.trajectory.vpc_validation.leave_one_out_drift`), the final
posterior positional σ, and divergence from the baseline track. This keeps the
harness unit-testable without running a 4000-particle filter.

:data:`SCORE_REGISTRY` names the scores a sweep can ask for by string, so a CLI
or a config can select them without importing anything. Alongside the two
original track scores it carries the R0 ledger (design section 3.7): CRPS,
variogram score, credible-region containment and rank histograms in channel
coordinates, and the G-degeneracy scalars. Provenance is not a score — it is
stamped onto the :class:`~anchor.validation.ledger.card.ScoreCard` the caller
writes the sweep into.
"""
from __future__ import annotations
from typing import Any, Callable, Mapping, Optional, Sequence
import numpy as np

def track_divergence(means_a: np.ndarray, means_b: np.ndarray) -> float:
    """RMS per-step displacement (m) between two ``(n, 2)`` mean tracks.

    Truncates to the shorter length if they differ. A direct measure of how far
    the reconstructed path moved when a hyperparameter changed.
    """
    ...

def final_position_sigma_m(filter_state: dict) -> float:
    """Mean of the terminal-step posterior x/y standard deviations (m)."""
    ...

def sweep_parameter(param: str, values: Sequence, reconstruct_fn: Callable, score_fns: dict[str, Callable], baseline_value=None, baseline_means_fn: Optional[Callable]=None) -> dict:
    """Run ``reconstruct_fn`` once per value and score each run.

    Parameters
    ----------
    param
        Name of the swept hyperparameter (for the report only).
    values
        Grid of values to try.
    reconstruct_fn
        ``reconstruct_fn(value) -> result``; the result is passed to each score.
    score_fns
        ``{score_name: callable(result) -> float}``.
    baseline_value
        If given (and present in ``values``), a ``drift_vs_baseline_m`` column is
        added: ``track_divergence`` of each run's track vs the baseline run's.
        Requires ``baseline_means_fn`` to extract an ``(n, 2)`` track from a
        result.
    baseline_means_fn
        ``result -> (n, 2)`` mean track, used only for the divergence column.

    Returns
    -------
    dict with ``param``, ``rows`` (one ``{value, <scores>}`` per value, in input
    order), and ``sensitivity`` (per-score ``{min, max, range, most_value,
    least_value}`` where ``most_value`` is the value giving the max score).
    """
    ...

def parse_sweep_spec(spec: str) -> tuple[str, list[float]]:
    """Parse a CLI sweep spec ``"name=v1,v2,v3"`` into ``(name, [floats])``.

    Example: ``"process_noise_xy_m=1.0,2.5,5.0"`` →
    ``("process_noise_xy_m", [1.0, 2.5, 5.0])``.
    """
    ...

def ledger_scores(result: Mapping[str, Any]) -> dict[str, float]:
    """The full R0 score bundle for a run: CRPS, variogram, containment, ranks.

    Reads ``result["ledger"] = {"ensemble_xy", "truth_xy", "centerline", ...}``
    and returns :func:`anchor.validation.ledger.scores.score_paths`'s mapping.
    Raises ``KeyError`` if the run did not carry the ensemble: a ledger score
    computed from a posterior mean would be a lie about the uncertainty.
    """
    ...

def degeneracy_scores(result: Mapping[str, Any]) -> dict[str, float]:
    """The five G-degeneracy scalars plus the gate verdict as ``0.0``/``1.0``.

    Reads ``result["degeneracy"]``, the dict the particle filter exports with
    exactly the keys in
    :data:`anchor.validation.ledger.gates.DEGENERACY_KEYS`. The verdict is
    carried as a number so it lands in the same sweep table as the scores it
    governs — a sweep arm whose gate failed must be visibly disqualified in
    the same row as its CRPS.
    """
    ...

def register_score(name: str, fn: Callable[[Any], Any], overwrite: bool=False) -> None:
    """Add a scorer to :data:`SCORE_REGISTRY`."""
    ...

def resolve_score_fns(names: Sequence[str]) -> dict[str, Callable[[Any], Any]]:
    """``{name: scorer}`` for the named registry entries, in the order given."""
    ...
