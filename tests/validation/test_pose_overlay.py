"""Pose-overlay renderer tests: synthetic video + keypoints → overlaid MP4."""
from __future__ import annotations
import shutil
import subprocess
import numpy as np
import pandas as pd
import pytest
from anchor.validation import pose as P
from anchor.validation import pose_overlay as PO

def test_default_skeleton_for_species():
    ...

def test_default_skeleton_unknown_species_returns_empty():
    ...

def test_conf_to_color_thresholds():
    ...

def test_metric_at_time_picks_nearest_within_tolerance():
    ...

@pytest.mark.skipif(not HAS_FFMPEG, reason='ffmpeg not on PATH')
def test_render_pose_overlay_writes_mp4(tmp_path):
    """Synthetic 2 s blue video + drifting keypoints → MP4 with same frame count."""
    ...

@pytest.mark.skipif(not HAS_FFMPEG, reason='ffmpeg not on PATH')
def test_render_pose_overlay_n_frames_truncates(tmp_path):
    """Only the first N frames are written when n_frames is set."""
    ...

@pytest.mark.skipif(not HAS_FFMPEG, reason='ffmpeg not on PATH')
def test_render_pose_overlay_with_metrics(tmp_path):
    """Per-cycle metrics overlay does not crash and produces a longer file
    than overlay-only."""
    ...
