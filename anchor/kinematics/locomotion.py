"""Locomotion-mode-specific tailbeat extraction.

Elasmobranchs in this project use two distinct locomotor modes:

- **axial undulator** (leopard shark, white shark): sub-/carangiform
  swimming. The body undulates about the sway axis; tailbeat = one full
  lateral excursion. Peak detection on the signed sway-axis signal yields
  one peak per cycle and ``tb_freq_inst`` is the cycle frequency.

- **pectoral oscillator** (bat ray): mobuliform fin oscillation. Pectoral
  fins flap dorsal-ventral; the tag sees a large axial dynamic-accel signal
  on the Z axis. Peak detection still yields one peak per cycle, but the
  batoid literature commonly reports *stroke frequency* (one up-stroke +
  one down-stroke = two strokes per cycle), so this module also emits a
  ``tb_stroke_freq_inst`` column equal to ``2 × tb_freq_inst`` for
  cross-paper comparability.

Routing is driven by ``species.locomotion_mode`` in the YAML configs.
"""
from __future__ import annotations
from typing import Optional
import pandas as pd
from anchor.kinematics.core import DEFAULT_MIN_PERIOD_S, add_tailbeat_columns

def axial_undulator(df: pd.DataFrame, axis_col: str, fs: float, smooth_sigma: float=2.0, min_period_s: float=DEFAULT_MIN_PERIOD_S, prominence: Optional[float]=None) -> pd.DataFrame:
    """Sharks / tuna-like locomotion: peaks on a single sway-axis signal.

    Identity wrapper around ``kinematics.add_tailbeat_columns`` that
    documents its use as the default for axial undulators.
    """
    ...

def pectoral_oscillator(df: pd.DataFrame, axis_col: str, fs: float, smooth_sigma: float=2.0, min_period_s: float=DEFAULT_MIN_PERIOD_S, prominence: Optional[float]=None) -> pd.DataFrame:
    """Batoid pectoral flapping: peaks on the dorsal-ventral axis.

    Adds ``tb_stroke_freq_inst = 2 × tb_freq_inst`` so batoid kinematics
    numbers compare against the stroke-frequency convention common in
    mobuliform-gait literature (Rosenberger 2001, Klausewitz 1964).
    """
    ...

def dispatch(mode: str, df: pd.DataFrame, axis_col: str, fs: float, smooth_sigma: float=2.0, min_period_s: float=DEFAULT_MIN_PERIOD_S, prominence: Optional[float]=None) -> pd.DataFrame:
    """Route to the locomotion-mode-specific tailbeat extractor."""
    ...
