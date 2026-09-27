"""R0: the versioned score card, the section 3.7 gate table, and the ledger's scores.

Phase 0's first deliverable (``docs/design/leopard_shark_digital_twin.md``,
section 4). One import gives you everything needed to score a reconstruction
and write the record that a reader is meant to judge it by:

>>> import numpy as np
>>> from anchor.validation.ledger import (
...     ScoreCard, Provenance, StraightCenterline, evaluate_degeneracy_gate, score_paths)
>>> rng = np.random.default_rng(0)
>>> truth = 50.0 * np.cumsum(rng.normal(size=(50, 2)), axis=0)   # metres
>>> ens = truth[None] + rng.normal(scale=25.0, size=(64, 50, 2))

The centreline must **span** the track. ``project`` clamps to the polyline, so
any position off either end is given the terminal arc length; a centreline that
the track runs off collapses the along-channel errors to zero and reports
perfect coverage. ``StraightCenterline()``'s default runs from ``(0, 0)``
up-slough, which the walk above leaves within its first step — hence the origin
that brackets it, and the ``fraction_at_centerline_end`` check that proves it.

Coverage is a many-case statistic. ``containment_*_90`` on one 50-step path is
0 or 1 in long blocks because consecutive steps are strongly correlated; judge
calibration from a replicate study (the control arm in
``tests/validation/test_ledger.py``), never from a single card.

>>> line = StraightCenterline(origin=(-5_000.0, 0.0), length_m=10_000.0)
>>> scores = score_paths(ens, truth, line, variogram_stride=5)
>>> scores["fraction_at_centerline_end"]
0.0
>>> gate = evaluate_degeneracy_gate({
...     "n_founders_final": 120, "min_unique_ancestor_fraction": 0.11,
...     "max_norm_weight": 0.01, "ess_min": 900.0, "var_log_w": 1.4,
...     "n_particles": 4000})
>>> card = ScoreCard(run_id="demo", provenance=Provenance.stamp("2026-09-04T00:00:00Z"),
...                  scores=scores, gates=[gate])
>>> card.suppressed
False

Nothing in this package reads ``data/``, the network, or any optional
dependency: it is importable and fully testable from a bare checkout.

Module map
----------
``channel``
    Along/cross decomposition of a position error field against a centreline.
``scores``
    RMSE, ensemble CRPS, variogram score, rank histograms on path
    functionals, credible-region containment.
``gates``
    Section 3.7's table as data, and the standing G-degeneracy evaluation.
``card``
    ``ScoreCard``, the provenance stamp, and the JSON writer.
``linear_gaussian``
    Kalman/RTS/FFBS on a Gaussian random walk — the correctness cross-check
    the scores are calibrated against.
"""
from __future__ import annotations
from anchor.validation.ledger.card import SCORECARD_VERSION, Provenance, ScoreCard, config_hash, git_sha, jsonable, package_version, write_json
from anchor.validation.ledger.channel import CenterlineLike, ChannelCoords, StraightCenterline, channel_error, to_channel
from anchor.validation.ledger.gates import DEGENERACY_FLOORS, DEGENERACY_KEYS, GATE_TABLE, GATE_TABLE_VERSION, GateCheck, GateResult, GateSpec, evaluate_degeneracy_gate, evaluate_heading_gate, evaluate_gates, gate_by_name, gate_suppressed_score_prefixes, gate_suppresses_calibration
from anchor.validation.ledger.linear_gaussian import LinearGaussianModel, ffbs_sample, kalman_filter, rts_smoother
from anchor.validation.ledger.scores import PATH_FUNCTIONALS, QUANTILE_METHOD, aggregate_functional_ranks, credible_containment, credible_interval, crps_ensemble, crps_gaussian, ensemble_rank, functional_ranks, max_up_slough_excursion_m, net_displacement_m, rank_histogram, rmse, score_paths, total_path_length_m, variogram_score
__all__ = ['CenterlineLike', 'ChannelCoords', 'DEGENERACY_FLOORS', 'DEGENERACY_KEYS', 'GATE_TABLE', 'GATE_TABLE_VERSION', 'GateCheck', 'GateResult', 'GateSpec', 'LinearGaussianModel', 'PATH_FUNCTIONALS', 'Provenance', 'QUANTILE_METHOD', 'SCORECARD_VERSION', 'ScoreCard', 'StraightCenterline', 'aggregate_functional_ranks', 'channel_error', 'config_hash', 'credible_containment', 'credible_interval', 'crps_ensemble', 'crps_gaussian', 'ensemble_rank', 'evaluate_degeneracy_gate', 'evaluate_heading_gate', 'evaluate_gates', 'ffbs_sample', 'functional_ranks', 'gate_by_name', 'gate_suppressed_score_prefixes', 'gate_suppresses_calibration', 'git_sha', 'jsonable', 'kalman_filter', 'max_up_slough_excursion_m', 'net_displacement_m', 'package_version', 'rank_histogram', 'rmse', 'rts_smoother', 'score_paths', 'to_channel', 'total_path_length_m', 'variogram_score', 'write_json']
