"""Video-label ingest for the supervised WS classifier (W3).

Ground-truth behavior labels for the white-shark deployments come from
hand-annotation of onboard video in BORIS (Behavioral Observation Research
Interactive Software) or VIA (VGG Image Annotator). Both tools export
time-coded behavior intervals; this module:

1. Parses their exports into a common ``labels`` DataFrame.
2. Aligns video timestamps to the deployment's accelerometer time axis via
   a single scalar offset (video_start_datetime − accel_start_datetime).
3. Projects interval labels onto sliding feature windows via majority-vote
   coverage, returning per-window label strings and a confidence fraction.

Minimum viable BORIS CSV columns: ``Behavior``, ``Start (s)``, ``Stop (s)``
(optionally ``Subject``, ``Modifier``).
Minimum viable VIA JSON: top-level ``metadata`` dict with temporal segments
each carrying ``vid``, ``z: [start_s, stop_s]``, ``av: {<attr_id>: <label>}``.

All times inside the BORIS/VIA export are relative to **video start**. The
``align_to_accel`` step converts them to seconds elapsed on the accel time
axis.
"""
from __future__ import annotations
import json
from pathlib import Path
from typing import Optional
import numpy as np
import pandas as pd

def _empty_labels() -> pd.DataFrame:
    ...

def load_boris_export(csv_path: str | Path) -> pd.DataFrame:
    """Parse a BORIS observation CSV into the common labels schema.

    BORIS aggregated-events export lists one row per behavior interval with
    columns including ``Behavior``, ``Start (s)``, ``Stop (s)``, ``Subject``,
    ``Modifier``. Empty stops (point events) get a zero-duration interval.
    """
    ...

def load_via_export(json_path: str | Path) -> pd.DataFrame:
    """Parse a VGG Image Annotator JSON export (temporal project) into the
    common labels schema.

    VIA temporal projects store per-segment entries under ``metadata`` keyed
    by a string id. Each entry has ``z: [start_s, stop_s]`` and ``av`` with
    attribute values keyed by the numeric attribute id.
    """
    ...

def align_to_accel(labels: pd.DataFrame, video_offset_s: float, accel_duration_s: Optional[float]=None) -> pd.DataFrame:
    """Shift video-frame-time labels onto the accel elapsed-seconds axis.

    ``video_offset_s`` is ``(video_start_datetime − accel_start_datetime)``
    in seconds — positive if the video started after the accel. A label at
    ``start_video_s=10`` with offset 30 lands at ``start_t=40`` on the accel
    clock.

    If ``accel_duration_s`` is provided, labels that fall entirely outside
    the accel record are dropped and labels that straddle the edge are
    clipped to it.
    """
    ...

def labels_to_windows(labels_aligned: pd.DataFrame, features: pd.DataFrame) -> pd.DataFrame:
    """Majority-vote label assignment across each feature window.

    For each window ``(start_t, end_t)`` in ``features``, compute the fraction
    of the window's time covered by each behavior, pick the dominant one, and
    attach ``label`` and ``label_confidence`` columns.

    A window with zero coverage gets ``label=NaN`` and ``label_confidence=0``.
    """
    ...

def select_uncertain_windows(states_with_probs: pd.DataFrame, n_queries: int, method: str='entropy') -> pd.DataFrame:
    """Pick the top-``n_queries`` windows by posterior uncertainty.

    Drives Phase B of the W3 labeling protocol: run the Phase A classifier on
    unlabeled windows and ask the annotator to label those the model is
    *least* sure about. Expects the ``state_prob_0..k-1`` columns that the
    upgraded pipeline persists.

    ``method``:
      - ``"entropy"`` — Shannon entropy of the posterior (default; most
        principled, handles any k).
      - ``"margin"`` — 1 − (p_top1 − p_top2); largest when top two are close.
      - ``"least_confident"`` — 1 − p_top1; penalizes low top-class prob.
    """
    ...

def _first_present(df: pd.DataFrame, candidates: list[str], required: bool=True) -> Optional[str]:
    ...
