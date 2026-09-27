"""Zero-data demo: synthesize a deployment and run the full pipeline.

The real deployments are private, which makes anchor hard to try. This module
fabricates a physically-plausible AXY-5 accelerometer record — a swimming animal
cycling through rest / cruise / active / burst regimes with a tail-beat
oscillation — and drives it through the *actual* ingest → kinematics → behaviour
pipeline, then through the flagship energy-seascape analysis. Nothing here is
private; ``anchor demo`` lets a new user see every stage run end-to-end on their
own machine in seconds.

The synthetic record is for demonstration only — it is generated from a known
generative model, so behaviour clusters are clean by construction and must not be
read as biological results.
"""
from __future__ import annotations
import os
from pathlib import Path
import numpy as np
import pandas as pd

def synthesize_axy5_csv(path: str | Path, minutes: float=5.0, fs: float=25.0, seed: int=0, tag_id: str='DEMO_AXY5', start: str='2026/03/18 10:00:00.000', mag_stride: int=25) -> Path:
    """Write a synthetic AXY-5 CSV (gravity + tail-beat sway + regime structure).

    Gravity sits on ``accZ`` (~1 g); the axial sway rides on ``accY`` so
    ``accY_dyn`` carries the tail-beat. Magnetometer rows are logged every
    ``mag_stride`` samples (as on the real tag), blank otherwise.
    """
    ...

def write_demo_config(config_path: str | Path, raw_csv: str | Path, deployment_id: str='DEMO') -> Path:
    """Write a self-contained deployment YAML (no inheritance) for the demo CSV."""
    ...

def synth_track_samples(n_steps: int=600, k: int=80, seed: int=0, origin=(606000.0, 4076000.0)):
    """A synthetic (T, K, 2) FFBS-style sample ensemble for the spaceuse demo.

    A smooth meandering mean path with K perturbed realizations whose spread
    grows then contracts (mimicking dead-reckoning drift pinned by an endpoint).
    Coordinates are UTM 10N metres near Elkhorn Slough.
    """
    ...

def run_demo(out_dir: str | Path, minutes: float=5.0, seed: int=0, with_spaceuse: bool=True) -> dict:
    """Generate synthetic data and run the full pipeline under ``out_dir``.

    Returns a dict of output paths. Runs ingest → kinematics → behaviour via the
    real pipeline, then (optionally) the energy-seascape analysis on a synthetic
    trajectory-sample ensemble weighted by the demo's own window VeDBA.
    """
    ...
