"""Paired CATS + AXY harmonization for cross-tag credibility validation.

Use case: same WS wears both a CATS housing (camera + IMU + depth, ~50 Hz)
and a clip-on AXY-5 (accel + mag, 25 Hz) simultaneously. We want:

  1. Align the two tag clocks (they free-run independently before the
     deployment), via cross-correlation on a shared signal. The most
     reliable shared signal is **dynamic-VeDBA** because both tags
     observe the same animal acceleration after being downsampled to a
     common rate.
  2. Downsample CATS → AXY rate so both streams share a time axis.
  3. Run the same HMM through both streams. Compute per-window
     state-agreement matrix; report `kappa` as the headline cheap-tag
     credibility number for the paper.

This unlocks the §C3 cross-species credibility claim: if AXY-only HMM
agrees with CATS-anchored HMM at >κ on the same animal, we license the
LS/TS AXY-only HMM inferences as credible despite their lack of video.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
import numpy as np
import pandas as pd
from scipy.signal import correlate
from anchor.behavior.resample import resample_frame

@dataclass
class ClockAlignment:
    """Result of paired-tag clock alignment."""
    offset_s: float
    peak_correlation: float

def _downsample_uniform(t: np.ndarray, x: np.ndarray, target_fs: float) -> tuple[np.ndarray, np.ndarray]:
    """Resample (t, x) onto a uniform grid at ``target_fs`` via linear interp."""
    ...

def align_clocks_xcorr(cats_t: np.ndarray, cats_signal: np.ndarray, axy_t: np.ndarray, axy_signal: np.ndarray, common_fs: float=10.0, max_offset_s: float=600.0) -> ClockAlignment:
    """Cross-correlate two free-running tag signals to recover their clock offset.

    Both signals should be the same physical observable (typically
    dynamic-VeDBA), pre-downsampled to ``common_fs``. Positive
    ``offset_s`` means CATS clock is *ahead* of AXY clock by that many
    seconds.
    """
    ...

def harmonize_to_rate(df: pd.DataFrame, src_fs: float, dst_fs: float, time_col: str='t') -> pd.DataFrame:
    """Resample a feature/state DataFrame from ``src_fs`` to ``dst_fs``.

    Wraps :func:`anchor.behavior.resample.resample_frame` for paired-tag use:
    e.g. CATS at 50 Hz → AXY-like 25 Hz so both streams share a time axis
    and the same HMM can be applied to both.
    """
    ...

def cross_tag_agreement(cats_states: pd.Series, axy_states: pd.Series, state_labels: Optional[list[str]]=None) -> dict[str, object]:
    """Per-window confusion matrix + Cohen's κ between paired-tag HMM states.

    Both series must be aligned (same length, same time axis). Returns dict
    with ``confusion`` DataFrame, ``accuracy`` (overall), ``kappa``
    (Cohen's κ; >0.7 is the Wilson-2025 quality bar), ``n``.
    """
    ...
