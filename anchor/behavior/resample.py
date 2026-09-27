"""Resample a processed-parquet time series to a target sample rate.

Needed for cross-species SSL pooling: LS and BR log at 25 Hz, WS logs at
50 Hz. Feeding mixed-fs windows into a single DCL encoder would leak the
sampling rate as an informative feature — so we resample everything to a
common rate before pretraining.

Approach: anti-alias with a Butterworth lowpass at the new Nyquist, then
linearly interpolate onto the new time grid. The tailbeat peaks and
`state_prob_*` columns, if present, are preserved through the interp —
booleans are converted to floats-at-each-sample and re-binarized at the
destination rate.

This is *not* the same as re-running the pipeline at a different fs. Use
the resampler for pretraining pool consistency, not for re-deriving
kinematics.
"""
from __future__ import annotations
from pathlib import Path
from typing import Optional, Sequence
import numpy as np
import pandas as pd
from scipy.signal import butter, filtfilt
from anchor.ingest import io

def _antialias(x: np.ndarray, src_fs: float, dst_fs: float, order: int=4) -> np.ndarray:
    """Butterworth lowpass at 0.45 × dst_fs before decimating."""
    ...

def _nearest_index(src_t: np.ndarray, dst_t: np.ndarray) -> np.ndarray:
    """Index of the source sample nearest each destination time."""
    ...

def resample_frame(df: pd.DataFrame, src_fs: float, dst_fs: float, time_col: str='t', antialias: bool=True) -> pd.DataFrame:
    """Return a new DataFrame resampled from ``src_fs`` to ``dst_fs``.

    - Numeric float columns are antialiased then linearly interpolated onto
      the new time grid. Destination samples that touch a NaN in the source
      stay NaN; gaps are never filled with invented values.
    - Integer columns (state codes, labels) are nearest-neighbor sampled so
      they never take fractional values.
    - Boolean columns (e.g. ``tb_peak``) are interpolated as floats and
      re-binarized at threshold 0.5.
    - Non-numeric columns (strings, datetimes) are nearest-neighbor sampled.
    - The ``time_col`` is regenerated on the new grid.
    """
    ...

def resample_parquet(src_path: str | Path, dst_path: str | Path, src_fs: float, dst_fs: float, columns: Optional[Sequence[str]]=None, time_col: str='t') -> int:
    """Load a processed parquet, resample it, write to ``dst_path``.

    ``columns`` optionally selects a subset to emit (keeps files small for
    SSL pretraining — only the 6 accel channels are needed). The ``time_col``
    is always included.
    """
    ...
