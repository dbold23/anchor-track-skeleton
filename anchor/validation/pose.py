"""Pose-detection wrapper: DeepLabCut + SLEAP keypoints → kinematic features.

Frame-level body keypoints from a video → tailbeat frequency, amplitude,
body-length scale, swim-speed in body lengths. Used by:

- ``anchor.validation.drone`` (drone footage of LS/TS/WS)
- ``anchor.validation.online_corpus`` (published BR video, K calibration)
- future MBA aquarium pipeline (LS + BR side-view filming)

DLC and SLEAP are imported lazily inside functions that need them, so the
rest of `anchor` runs without those heavy ML deps installed. To use the
training/inference paths, install with ``pip install -e ".[validation]"``.
"""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Sequence
import numpy as np
import pandas as pd
from scipy.signal import find_peaks

@dataclass
class Keypoints:
    """A frame x keypoint x (x, y) array with names + confidence + time axis.

    ``xy`` shape: (n_frames, n_keypoints, 2) in pixels. ``t`` is in seconds,
    one entry per frame. ``confidence`` is (n_frames, n_keypoints), in [0, 1].
    """
    xy: np.ndarray
    confidence: np.ndarray
    names: list[str]
    fps: float
    t: np.ndarray

    def __post_init__(self) -> None:
        ...

    def index_of(self, name: str) -> int:
        ...

    def trace(self, name: str) -> np.ndarray:
        """(n_frames, 2) trajectory of one keypoint over time."""
        ...

def load_keypoints_from_dlc_csv(path: str | Path, fps: float) -> Keypoints:
    """Load DeepLabCut export (multi-index CSV: ``scorer/bodypart/coords``).

    DLC v2 multi-animal exports use a 4-level header (scorer, individual,
    bodypart, coords); single-animal exports use 3 levels. Both supported.
    """
    ...

def load_keypoints_from_sleap_h5(path: str | Path) -> Keypoints:
    """Load SLEAP analysis HDF5 export (the .h5 produced by ``sleap-convert``)."""
    ...

def extract_keypoints_dlc(video_path: str | Path, model_path: str | Path, out_dir: Optional[str | Path]=None) -> Keypoints:
    """Run DeepLabCut inference on a video; return Keypoints.

    Heavy: imports deeplabcut at call time. Requires the validation extras.
    """
    ...

def body_length_pix(kp: Keypoints, anchor_pair: Sequence[str]) -> np.ndarray:
    """Per-frame Euclidean body length between two keypoints (pixels)."""
    ...

def tailbeat_from_keypoint(kp: Keypoints, tail_kp_name: str, body_length_pix_arr: np.ndarray, axis: int=0, smooth_sigma: float=2.0, min_period_s: float=0.3, prominence: Optional[float]=None, detrend_window_s: float=6.0) -> dict[str, np.ndarray]:
    """Detect tailbeat peaks on the (high-pass-implicit) lateral coord trace.

    ``detrend_window_s`` is the running-median window used to remove the
    fish's drift across the frame; it should span at least ~1.5 of the
    slowest expected tailbeat periods (the 6 s default covers periods to 4 s).

    Returns dict with ``peak_idx``, ``peak_t``, ``inst_freq_hz``, ``amplitude_pix``.
    Mirrors :func:`anchor.kinematics.core.detect_tailbeat_peaks` so pose-derived
    TBF is comparable to accel-derived TBF (same K = U/(L·TBF) chain).
    """
    ...

def keypoints_to_kinematics(kp: Keypoints, species: str, body_length_m: float, body_axis_pair: Optional[Sequence[str]]=None, tail_kp_name: Optional[str]=None, tailbeat_axis: Optional[int]=None, smooth_sigma: float=2.0, min_period_s: float=0.3) -> pd.DataFrame:
    """Pose → per-tailbeat-cycle kinematic features.

    Returns a DataFrame indexed by tailbeat cycle with columns:

    - ``cycle_t`` (s, mean of two peak times bracketing the cycle)
    - ``tbf_hz`` (instantaneous freq from peak-to-peak period)
    - ``amplitude_pix`` (peak prominence in pixels)
    - ``body_length_pix`` (pixel L at the cycle midpoint)
    - ``amplitude_over_l`` (A / L, dimensionless)
    - ``body_length_m`` (the input L scale, broadcast)

    The output schema is what ``online_corpus.compute_k_from_kinematics``
    consumes to compute ``K = U / (L · TBF)`` once a swim-speed estimate
    is supplied (by drone metadata, scale-bar, or known tank current).
    """
    ...
