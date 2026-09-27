"""A self-contained demo workspace for ``anchor dashboard --demo``.

The real deployments are private, so a new user who runs ``anchor dashboard``
in a fresh clone sees an empty list. This module writes a small, clearly
labelled *synthetic* workspace instead: three animals in Monterey Bay, one with
a quotable reconstruction, one whose run failed a gate, and one that has not
been reconstructed yet. Together they show every state the dashboard can be in.

What is real and what is not:

* The configs inherit the repository's own species files and validate through
  ``load_config``; the raw CSVs come from :func:`anchor.demo.synthesize_axy5_csv`;
  the QC reports are written by the real ``anchor doctor``.
* The tracks, ledger cards, depth and behaviour series are generated here from a
  known model. They are shaped like ``anchor track`` output (the same parquet
  columns, footer keys and ledger schema) so the dashboard reads them through
  its normal code path, but they are not reconstructions and every ledger card
  says so in ``notes``.
"""
from __future__ import annotations
import json
import os
import shutil
import time
from dataclasses import dataclass
from pathlib import Path
import numpy as np
_M_LAT = 111320.0
_X0, _Y0 = (600000.0, 4070000.0)

@dataclass
class DemoAnimal:
    deployment_id: str
    species_file: str
    animal_id: str
    length_cm: float
    sex: str
    release: tuple[float, float]
    hours: float
    seed: int
    runs: tuple[str, ...]
    recovery_offset: tuple[float, float] = (1800.0, -1400.0)

def _state_sequence(n: int, dt: float, rng: np.random.Generator) -> np.ndarray:
    """Behaviour state per sample: dwell bouts drawn per state, Markov-ish."""
    ...

def _smooth(x: np.ndarray, w: int) -> np.ndarray:
    ...

def synth_track(a: DemoAnimal, dt: float=2.0) -> dict:
    """Mean track, pinned σ and sensor series for one demo animal."""
    ...

def _gate(name: str, passed: bool, key: str, value: float, floor: float, detail: str) -> dict:
    ...

def _ledger(dep_id: str, kind: str, tr: dict, when: float) -> dict:
    ...

def _write_track(path: Path, tr: dict, footer: dict) -> None:
    ...

def _config_yaml(a: DemoAnimal, tr: dict | None) -> str:
    ...

def _run_doctor(root: Path, cfg: Path) -> None:
    """The real ``anchor doctor`` on the synthetic raw CSV (heading checks skipped)."""
    ...

def build_workspace(root: Path | str, *, force: bool=False, doctor: bool=True) -> Path:
    """Write the demo workspace under ``root`` (idempotent unless ``force``)."""
    ...

def default_root() -> Path:
    ...
