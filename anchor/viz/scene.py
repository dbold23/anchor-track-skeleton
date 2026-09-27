"""A deterministic synthetic deployment for rendering figures without field data.

Everything here is invented: a leopard-shark-like track wandering up a
meandering channel for 40 minutes at 1 Hz, a behaviour-state sequence, the
sensor series the report plots, and a forward / FFBS-smoothed posterior pair
whose smoothed uncertainty is pinned at release and recovery. It exists so
the style gallery (``anchor gallery``) and the figure tests have the same
inputs every time; no number in it is a result.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from types import SimpleNamespace
import numpy as np
import pandas as pd
ORIGIN = (606400.0, 4075800.0)

@dataclass
class Scene:
    n: int
    dt: float
    track: SimpleNamespace
    states: np.ndarray
    forward: dict
    smoothed: dict
    release: SimpleNamespace
    recovery: SimpleNamespace
    centerline: np.ndarray
    metrics: pd.DataFrame | None = None
    accel: pd.DataFrame | None = None
    env: pd.DataFrame | None = None

class _Track(SimpleNamespace):
    """Duck-types the ingest ``Track``: attribute access plus ``len()``."""

    def __len__(self) -> int:
        ...

def _markov_states(n: int, rng) -> np.ndarray:
    ...

def _smooth(x: np.ndarray, w: int) -> np.ndarray:
    ...

def make_scene(minutes: float=40.0, seed: int=7) -> Scene:
    ...

def _channel_bathy(cl: np.ndarray, means: np.ndarray, cell: float=5.0) -> dict:
    ...
