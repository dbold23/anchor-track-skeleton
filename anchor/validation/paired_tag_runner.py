"""End-to-end paired CATS+AXY validation orchestrator.

Builds the §C3 cross-tag credibility figure for the paper. Given the
two feature parquets from a paired deployment (same animal carrying
both a CATS housing and a clip-on AXY-5) plus a saved AXY-trained HMM
classifier (and optionally a separately-trained CATS-anchored
supervised classifier), this runner:

  1. Cross-correlates a shared signal (default ``vedba_mean``) across
     the two feature streams to recover the unknown clock offset
     between the free-running tags.
  2. Shifts the CATS time axis by the recovered offset so both streams
     share a common physical time.
  3. Predicts per-window states on each stream by re-applying the
     fitted model(s) via :func:`anchor.behavior.predict_from_features`.
  4. Nearest-neighbour matches windows in time (drop windows with no
     partner within a tolerance).
  5. Computes Cohen's κ + accuracy + per-state confusion matrix
     (the headline §5.4 paper-figure number).

When ``fitted_cats`` is omitted, the same model is applied to both
streams. This is the HMM-consistency mode: it tells you whether the
HMM trained on one tag's features generalises to the other tag's
features when both observe the same animal. For full cross-modal
credibility you supply ``fitted_cats`` (the CATS-video-anchored
supervised classifier produced by the §4.4 W3 labeling workflow).

The species-level §C6 number aggregates per-deployment κ across the
2-3 paired deployments planned for the paper; see
:func:`aggregate_paired_tag_results` and the ``paired-tag aggregate``
CLI subcommand.
"""
from __future__ import annotations
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
import numpy as np
import pandas as pd
from anchor.behavior._base import FittedClassifier, predict_from_features
from anchor.validation.paired_tag import align_clocks_xcorr, cross_tag_agreement

@dataclass
class PairedTagResult:
    clock_offset_s: float
    peak_correlation: float
    n_paired_windows: int
    accuracy: float
    kappa: float
    confusion: pd.DataFrame
    axy_states: pd.DataFrame
    cats_states: pd.DataFrame
    matched_axy_idx: np.ndarray
    matched_cats_idx: np.ndarray

def _match_windows_in_time(axy_t: np.ndarray, cats_t: np.ndarray, max_dt_s: float) -> tuple[np.ndarray, np.ndarray]:
    """Greedy nearest-neighbour match in time. Returns matched index arrays."""
    ...

def run_paired_tag_validation(axy_features: pd.DataFrame, cats_features: pd.DataFrame, fitted_axy: FittedClassifier, fitted_cats: Optional[FittedClassifier]=None, align_signal_col: str='vedba_mean', common_align_fs: float=1.0, max_offset_s: float=600.0, time_col: str='center_t', window_match_dt_s: float=2.0) -> PairedTagResult:
    """Orchestrate a paired-tag validation end-to-end.

    Both feature DataFrames must carry ``time_col`` (default ``center_t``)
    and ``align_signal_col`` (default ``vedba_mean``). Returns a
    :class:`PairedTagResult` ready for paper-figure rendering.
    """
    ...

@dataclass
class DeploymentRound:
    """One paired-deployment round loaded from a saved report directory."""
    deployment_id: str
    n_paired_windows: int
    accuracy: float
    kappa: float
    confusion: pd.DataFrame
    axy_states: pd.DataFrame
    cats_states: pd.DataFrame
    matched_axy_idx: np.ndarray
    matched_cats_idx: np.ndarray
    clock_offset_s: float
    peak_correlation: float

def load_paired_tag_round(report_dir: str | Path, deployment_id: Optional[str]=None) -> DeploymentRound:
    """Load a paired-tag report directory written by ``run_paired_tag_validation``.

    Expects the layout produced by ``anchor validation paired-tag run``:
      - summary.json
      - confusion.parquet
      - axy_states.parquet
      - cats_states.parquet
    """
    ...

def aggregate_paired_tag_results(rounds: list, n_bootstrap: int=1000, ci: float=0.95, rng: Optional[np.random.Generator]=None) -> dict:
    """Pool paired-tag rounds across deployments → species-level κ + bootstrap CI.

    Two complementary κ estimates:

    - **Pooled κ**: concatenate all matched (cats_state, axy_state) pairs across
      deployments, compute one Cohen's κ. Tighter CI when total n is large but
      lets one long deployment dominate.
    - **Per-deployment-bootstrap κ**: bootstrap over deployments (resample with
      replacement and average the per-deployment κs). Conservative when n
      varies wildly between deployments. This is the recommended species-level
      number for the §C6 paper figure.

    Returns dict with: ``per_deployment`` (DataFrame), ``pooled_kappa``,
    ``pooled_accuracy``, ``pooled_n``, ``bootstrap_kappa`` (median + CI),
    ``confusion`` (summed across deployments).
    """
    ...
