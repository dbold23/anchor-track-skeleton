"""Thin orchestration glue driven by the typer CLI (and a planned DVC pipeline).

Each function here is pure enough to be called directly from Python (tests,
notebooks, scripts) without going through the CLI.
"""
from __future__ import annotations
import logging
from pathlib import Path
from typing import Optional
import numpy as np
import pandas as pd
from anchor import qc as QC
from anchor.ingest import io
from anchor.kinematics import core as K
from anchor.kinematics import features as F
from anchor.kinematics import locomotion as L
from anchor import behavior as CL
from anchor import events as EV
from anchor.ingest.config import DeploymentConfig, load_config

def _resolve_body_length_m(cfg: DeploymentConfig) -> float | None:
    """Deployment-level animal length (cm) wins; species default (m) fills in."""
    ...

def process_deployment(cfg: DeploymentConfig) -> pd.DataFrame:
    """Raw CSV → calibrated, dynamic-split, VeDBA/ODBA/jerk/tailbeat parquet."""
    ...

def extract_events_for(cfg: DeploymentConfig, method: Optional[EV.ThresholdMethod]=None) -> pd.DataFrame:
    """Flag and group high-activity events in a processed deployment.

    The rule comes from ``cfg.event_thresholds.method``; ``method`` overrides it
    for a one-off run (the CLI's ``--method``) and ``None`` means "use the
    config". ``"robust_scale"`` (the default) puts each threshold
    ``cfg.event_thresholds.vedba_scale_factor`` / ``.jerk_scale_factor`` robust
    scales above the record's own median, which leaves the flagged fraction free
    to differ between animals instead of fixing it. It is not an absolute
    threshold — see :mod:`anchor.events` for what it does and does not support.
    ``"percentile"`` restores the pre-N5 rule using ``.vedba_pct`` / ``.jerk_pct``,
    kept as an explicit opt-in for reproducing earlier outputs.
    """
    ...

def build_features_for(cfg: DeploymentConfig) -> pd.DataFrame:
    ...

def classify_for(cfg: DeploymentConfig) -> tuple[pd.DataFrame, CL.FittedClassifier]:
    ...

def run_doctor_stage(cfg_path: str | Path) -> QC.QCReport | None:
    """Stage zero of :func:`run_all`: health-check the deployment, never abort.

    Findings are logged at WARNING (FAIL and WARN alike) and the report is
    written to ``data/interim/<id>_qc.json``. This stage deliberately cannot
    fail the run — ``anchor doctor`` is the gate that exits non-zero. Returns
    ``None`` if the check itself could not run, so a doctor bug can never stop
    a pipeline that used to work.
    """
    ...

def run_all(cfg_path: str | Path, doctor: bool=True) -> None:
    """doctor → process → events → features → classify.

    ``doctor=True`` (the default) runs the stage-zero health check, which only
    reports; pass ``doctor=False`` to skip it entirely.
    """
    ...
