"""Read-only views over what the anchor CLI writes to disk.

Everything here takes a repository ``root`` and returns plain JSON-able dicts.
Nothing in this module runs a reconstruction or writes a file: it reads
``configs/deployments/*.yaml``, ``data/interim/<id>_qc.json`` (``anchor
doctor``), ``data/processed/<id>*.parquet`` and the per-run outputs of
``anchor track`` (``<id>_track.parquet``, ``<id>_ledger.json``, ...).

Honesty rule: every run carries a :func:`verdict`. A run is *quotable* only when
its ledger card exists and no gate failed; a pre-ledger run with no gate record
at all is *unverified*, which the front end treats exactly like a failure.
"""
from __future__ import annotations
import json
import logging
import math
import os
import threading
from pathlib import Path
from typing import Any, Iterable, Optional
import numpy as np

class PathError(ValueError):
    """A client-supplied path that resolves outside what it may name."""

def safe_path(root: Path, rel: str, allowed: Iterable[Path], suffixes: Optional[set[str]]=None) -> Path:
    """Resolve ``rel`` under ``root`` and insist it lands inside one of ``allowed``.

    Containment is checked on the lexically normalised path, so ``..`` segments,
    absolute paths and backslash tricks cannot step out of the allowed trees.
    Symlinks the repository itself contains are followed (``data/interim`` and
    ``data/processed`` hold symlinks into sibling checkouts); a client cannot
    create one. Raises :class:`PathError` on any violation.
    """
    ...

def rel(root: Path, path: Path) -> str:
    """``path`` relative to ``root``, without resolving symlinks."""
    ...

def jsonable(obj: Any) -> Any:
    """Coerce numpy scalars/arrays and non-finite floats into strict JSON."""
    ...

def _file_info(root: Path, path: Path) -> Optional[dict]:
    ...

def _read_json(path: Path) -> Optional[Any]:
    ...

class _MtimeCache:
    """Memoise ``fn(path)`` until the file's mtime/size changes."""

    def __init__(self, maxsize: int=512):
        ...

    def get(self, key: tuple, paths: Iterable[Path], fn):
        ...

def list_config_paths(root: Path) -> list[Path]:
    ...

def resolve_config(root: Path, rel_path: str) -> Path:
    """A deployment YAML the client named; only files under ``configs/``."""
    ...

def _raw_yaml(path: Path) -> dict:
    ...

class _ListHandler(logging.Handler):

    def __init__(self):
        ...

    def emit(self, record: logging.LogRecord) -> None:
        ...

def _captured(fn, *args):
    """``(result, advisories)``: warnings ``anchor`` logs while ``fn`` runs.

    ``load_config`` logs judgement-call advisories (e.g. a low-pass cutoff that
    eats the slowest tail beat); the dashboard shows them beside the config
    instead of letting them scroll past on the server's stderr.
    """
    ...

def _lint_uncached(path: Path) -> dict:
    ...

def lint(root: Path, path: Path) -> dict:
    """``anchor config-lint`` for one YAML (its own validator, reused)."""
    ...

def _load_config(path: Path):
    ...

def qc_report(root: Path, deployment_id: str, cfg=None) -> Optional[dict]:
    """``data/interim/<id>_qc.json`` plus whether its stamp still matches."""
    ...

def _endpoint(raw: Any) -> Optional[dict]:
    ...

def _summary_from(raw: dict, cfg) -> dict:
    """Headline fields, from the validated config when it loads, else the YAML."""
    ...

def deployment_summary(root: Path, path: Path, *, with_qc_freshness: bool=False, all_runs: Optional[list[dict]]=None) -> dict:
    ...

def list_deployments(root: Path) -> list[dict]:
    ...

def deployment_detail(root: Path, rel_path: str) -> dict:
    ...

def _footer(path: Path) -> dict:
    """The ``anchor:*`` keys ``run_deployment`` writes into the parquet footer."""
    ...

def _ledger(path: Path) -> Optional[dict]:
    ...

def verdict(ledger: Optional[dict], footer: Optional[dict]) -> dict:
    """Whether a run's positional numbers may be quoted, and why not.

    Three outcomes:

    * ``quotable`` — a ledger card exists and every gate on it passed;
    * ``not_quotable`` — a gate failed (ledger card, or the parquet footer's
      gate record when no card was written);
    * ``unverified`` — no gate record at all (runs from before the ledger).

    Only ``quotable`` lets the front end show positions and σ as numbers.
    """
    ...

def discover_runs(root: Path, base: Path=REPORTS_DIR) -> list[dict]:
    """Every ``anchor track`` output set under ``reports/``, newest first."""
    ...

def resolve_run(root: Path, run_dir: str, dep_id: str) -> dict[str, Path]:
    """The files of one run; ``run_dir`` must be under ``reports/``."""
    ...

def _tail(path: Path, max_bytes: int=64000) -> str:
    ...

def run_detail(root: Path, run_dir: str, dep_id: str) -> dict:
    ...

def _affine_lonlat(x: np.ndarray, y: np.ndarray, lon: np.ndarray, lat: np.ndarray):
    """Least-squares affine map UTM → lon/lat fitted on the track's own points.

    Used only to place footer-reported anchors (given in the projected CRS) on
    the map without importing pyproj; over a few km of slough the affine
    residual is well below a metre.
    """
    ...

def _stride(n: int, max_points: int) -> int:
    ...

def load_track(root: Path, run_dir: str, dep_id: str, max_points: int=3000, n_ellipses: int=60) -> dict:
    """The reconstructed track, decimated for the browser, plus its anchors.

    Speed and course are derived here from the smoothed mean positions (a
    centred difference over ~10 s), so they are positional numbers and carry
    the run's verdict with them.
    """
    ...

def _clock_origin(root: Path, dep_id: str) -> Optional[dict]:
    ...

def _binned_depth(path: Path, n_bins: int) -> Optional[dict]:
    """Mean Depth per time bin, streamed in record batches (the file is 25 Hz)."""
    ...

def _state_segments(path: Path, max_segments: int=4000) -> Optional[dict]:
    ...

def load_series(root: Path, dep_id: str, n_bins: int=3000) -> dict:
    """Sensor-side series for ``dep_id``: binned depth and behaviour states."""
    ...

def _simplify_ring(ring: list, tol_deg: float) -> list:
    ...

def _simplify(geom: dict, tol_deg: float) -> dict:
    ...

def site_geometry(root: Path, site: Optional[str], tol_m: float=4.0) -> dict:
    """Shoreline outline + channel centreline for a named site, simplified."""
    ...

def claims(root: Path) -> dict:
    ...

def resolve_servable(root: Path, rel_path: str) -> Path:
    ...
