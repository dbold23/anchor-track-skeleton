"""Online video corpus management: per-species clip manifest + end-to-end K
calibration from pose.

Workflow:

  1. ``anchor validation corpus add --url ... --species bat_ray --body-length-m 0.9``
     registers a clip in the per-species manifest at
     ``data/labels/online_corpus/{species}/manifest.json``.

  2. ``anchor validation corpus prep --clip-id BR_001 --n-frames 100``
     downloads (if needed) and extracts N evenly-spaced frames for hand
     labeling in DeepLabCut. Output:
     ``data/labels/online_corpus/{species}/clips/{id}/frames/``.

  3. The annotator labels the frames in DLC, trains, and runs inference
     to produce a keypoints CSV (DLC's standard export). The expected
     path is ``data/labels/online_corpus/{species}/clips/{id}/keypoints.csv``.

  4. ``anchor validation corpus calibrate --species bat_ray`` walks every
     clip with a keypoints file, derives metres-per-pixel from the known
     body-length-m and the median body-length-pixels in the pose, computes
     per-cycle K = U / (L · TBF) using pose-derived swim speed, and
     bootstraps a species-level K with CI.

The manifest is the single source of truth for clip provenance, scale,
and license. It is JSON-encoded and committable; raw video files and
DLC outputs are gitignored under ``data/``.
"""
from __future__ import annotations
import datetime
import json
import shutil
import subprocess
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Optional
import numpy as np
import pandas as pd
from anchor.validation import pose as P
from anchor.validation import online_corpus as OC

@dataclass
class OnlineClip:
    """One published-video sample in the per-species corpus."""
    id: str
    species: str
    body_length_m: float
    scale_metres_per_pixel: Optional[float] = None
    swim_speed_m_s: Optional[float] = None
    fps: Optional[float] = None
    frame_range: Optional[tuple[int, int]] = None

@dataclass
class Corpus:
    """A per-species collection of online clips."""
    species: str

    def add(self, clip: OnlineClip) -> None:
        ...

    def remove(self, clip_id: str) -> OnlineClip:
        ...

    def get(self, clip_id: str) -> OnlineClip:
        ...

    @classmethod
    def manifest_path(cls, species: str, root: Path=CORPUS_ROOT) -> Path:
        ...

    @classmethod
    def load(cls, species: str, root: Path=CORPUS_ROOT) -> 'Corpus':
        ...

    def save(self, root: Path=CORPUS_ROOT) -> Path:
        ...

def make_clip_id(species: str, n_existing: int) -> str:
    """Generate a sequential clip id like 'BR_001', 'LS_017'."""
    ...

def clip_dir(clip: OnlineClip, root: Path=CORPUS_ROOT) -> Path:
    ...

def keypoints_path(clip: OnlineClip, root: Path=CORPUS_ROOT) -> Path:
    """Expected DLC export path for a clip."""
    ...

def frames_dir(clip: OnlineClip, root: Path=CORPUS_ROOT) -> Path:
    ...

def extract_diverse_frames(video_path: str | Path, n_frames: int, out_dir: str | Path, method: str='uniform', ffmpeg_path: str='ffmpeg') -> list[Path]:
    """Extract N frames from a video for hand-labeling.

    ``method='uniform'`` picks evenly-spaced frames. This is what DLC's
    own ``extract_frames`` does in its uniform mode and is good enough
    for first-pass corpus labeling.

    Returns the list of saved frame paths.
    """
    ...

def metres_per_pixel_from_pose(keypoints: P.Keypoints, species: str, body_length_m: float, body_axis_pair: Optional[tuple[str, str]]=None) -> float:
    """Derive the pixel-to-metre scale from the median body length in the pose.

    We measure body length in pixels at every frame (Euclidean distance
    between the two anchor keypoints), take the median to suppress
    perspective wobble, and divide the known body length in metres by it.
    Robust enough for n = 3-5 clip corpora; fragile for clips with
    extreme camera angle changes (consider per-segment scaling then).
    """
    ...

def swim_speed_from_pose(keypoints: P.Keypoints, body_kp_name: str, metres_per_pixel: float, smooth_window_s: float=0.5) -> pd.DataFrame:
    """Per-frame swim speed from the displacement of a single body keypoint.

    Returns a DataFrame with columns ``t`` (s, midway between frames i and i+1)
    and ``speed_m_s``. Smoothing reduces frame-to-frame jitter from pose
    inference noise; a 0.5 s window is wide enough to remove DLC noise
    but narrow enough to preserve burst events.
    """
    ...

def cycle_swim_speed(cycle_t: np.ndarray, speed_df: pd.DataFrame) -> np.ndarray:
    """Interpolate the per-frame swim-speed time series onto cycle midpoints."""
    ...

def calibrate_clip(clip: OnlineClip, keypoints: P.Keypoints) -> pd.DataFrame:
    """Compute per-cycle K for one clip.

    Returns the kinematics DataFrame with added ``k`` and ``swim_speed_m_s``
    columns. Mutates ``clip.scale_metres_per_pixel`` in-place if it was
    ``None``.
    """
    ...

def calibrate_corpus(corpus: Corpus, root: Path=CORPUS_ROOT, weight_by: str='per_clip') -> dict:
    """Walk the corpus and produce a species-level K calibration.

    For every clip with a ``keypoints.csv`` under
    ``data/labels/online_corpus/{species}/clips/{id}/``, load the keypoints,
    compute per-cycle K, then bootstrap across clips.

    Returns dict with: ``per_clip`` (list of per-clip dataframes),
    ``aggregate`` (bootstrap summary from :func:`online_corpus.aggregate_corpus`),
    ``skipped`` (list of clip ids missing keypoints).
    """
    ...

def today_iso() -> str:
    ...
