"""Plotting helpers lifted from the notebook prototype plus new ethogram/calibration views.

Every function here renders inside the Anchor theme (``anchor.viz.theme``):
set ``ANCHOR_FIG_THEME=dark`` for dark figures.
"""
from __future__ import annotations
from pathlib import Path
from typing import Optional
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from anchor.viz import marks, theme

@theme.styled
def plot_multirate_timeseries(df_accel: pd.DataFrame, df_env: Optional[pd.DataFrame]=None, depth_col: bool=False, save_to: Optional[str | Path]=None):
    """Multi-panel plot: dynamic accel, VeDBA, jerk, temperature, and (optional) depth."""
    ...

@theme.styled
def plot_event(df: pd.DataFrame, peak_t: float, window_s: float=6.0, time_col: str='t', save_to: Optional[str | Path]=None):
    """Zoom around an event's peak time, like the notebook's plot_event."""
    ...

@theme.styled
def plot_tailbeat_peaks(signal: np.ndarray, peaks: np.ndarray, fs: float, start_s: float=0, end_s: float=20, save_to: Optional[str | Path]=None):
    ...

@theme.styled
def plot_tailbeat_metrics(wm: pd.DataFrame, time_col: str='center_t', save_to: Optional[str | Path]=None):
    ...

@theme.styled
def plot_calibration_sphere(acc_raw: np.ndarray, acc_cal: np.ndarray, save_to: Optional[str | Path]=None):
    """Before/after 3-D scatter showing ellipsoid → unit sphere correction."""
    ...

@theme.styled
def plot_ethogram(metrics: pd.DataFrame, states: np.ndarray, label_map: Optional[dict[int, str]]=None, time_col: str='center_t', save_to: Optional[str | Path]=None):
    """Ethogram strip of behaviour states over VeDBA (and tailbeat frequency).

    States 0-3 take the Anchor rest / cruise / active / burst colours; any
    higher state index renders in the neutral "unlabelled" grey.
    """
    ...
