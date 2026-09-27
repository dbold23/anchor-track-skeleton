"""Render keypoints + skeleton + per-cycle metrics on top of source video.

DLC ships its own ``deeplabcut.create_labeled_video`` which works fine for
raw keypoint visualization. This module adds anchor-pipeline-specific
overlays that DLC doesn't know about: per-cycle TBF, swim-speed-from-pose,
body-length-pixel scale, K when calibrated. Useful for visually
sanity-checking the corpus + drone-corpus K values before they go into
the paper.

OpenCV does the per-frame drawing and writes an MP4 with the mp4v codec.
The full module is gated behind a lazy ``cv2`` import; the rest of
``anchor.validation`` runs without opencv installed.
"""
from __future__ import annotations
from pathlib import Path
from typing import Optional
import numpy as np
import pandas as pd
from anchor.validation.pose import Keypoints

def default_skeleton_for_species(species: str) -> list[tuple[str, str]]:
    ...

def _conf_to_color(conf: float, threshold: float) -> tuple[int, int, int]:
    """BGR colour: green above threshold, yellow at half, red below."""
    ...

def _metric_at_time(metrics: pd.DataFrame, t: float, time_col: str='cycle_t') -> Optional[pd.Series]:
    """Pick the metrics row whose time is closest to ``t`` (within one cycle)."""
    ...

def render_pose_overlay(video_path: str | Path, keypoints: Keypoints, out_path: str | Path, species: Optional[str]=None, skeleton: Optional[list[tuple[str, str]]]=None, metrics_df: Optional[pd.DataFrame]=None, show_kp_names: bool=False, confidence_threshold: float=0.5, point_radius: int=6, skeleton_thickness: int=2, skeleton_color: tuple[int, int, int]=(0, 255, 0), n_frames: Optional[int]=None) -> Path:
    """Write a copy of ``video_path`` with overlaid keypoints, skeleton, and
    per-cycle metrics.

    Parameters
    ----------
    metrics_df
        Optional output of :func:`anchor.validation.pose.keypoints_to_kinematics`
        (carries ``cycle_t``, ``tbf_hz``, ``amplitude_over_l``, optionally
        ``k`` and ``swim_speed_m_s``). When supplied, the nearest-in-time
        cycle's metrics are overlaid on each frame.
    n_frames
        If set, render only the first ``n_frames`` frames; useful for tests
        and quick QC. ``None`` renders the whole video.
    """
    ...
