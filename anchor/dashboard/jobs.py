"""One-at-a-time CLI jobs spawned by the dashboard.

A job is the existing ``anchor`` CLI run as ``python -m anchor.cli <cmd> ...``
in the repository root, with an argv built here from a small whitelist — the
browser never supplies a command line. Output is captured line by line into a
bounded buffer the front end polls; cancel sends SIGTERM to the job's process
group, then SIGKILL after a grace period.
"""
from __future__ import annotations
import os
import re
import signal
import subprocess
import sys
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional
from anchor.dashboard.data import PathError, REPORTS_DIR, _raw_yaml, rel, resolve_config, safe_path
MAX_LOG_LINES = 20000

class JobError(ValueError):
    """A job request the dashboard refuses (bad action or option)."""

class JobBusy(JobError):
    """A job is already running; only one runs at a time."""

def _int_opt(options: dict, key: str, lo: int, hi: int) -> Optional[int]:
    ...

def build_command(root: Path, action: str, config: Optional[str], options: Optional[dict]=None, *, stamp: Optional[str]=None) -> tuple[list[str], Optional[Path]]:
    """``(argv, out_dir)`` for a job request; raises on anything off-whitelist.

    ``config`` must resolve inside ``configs/`` (see
    :func:`anchor.dashboard.data.resolve_config`). A ``track`` job writes to a
    fresh ``reports/<id>/runs/<label>`` directory so it never overwrites an
    earlier run's outputs.
    """
    ...

@dataclass
class Job:
    id: int
    action: str
    config: Optional[str]
    argv: list[str]
    out_dir: Optional[str]
    ended: Optional[float] = None
    returncode: Optional[int] = None
    dropped: int = 0
    proc: Optional[subprocess.Popen] = None
    cancel_requested: bool = False

    def public(self) -> dict[str, Any]:
        ...

class JobManager:
    """Runs at most one CLI subprocess at a time."""

    def __init__(self, root: Path, grace_s: float=5.0, builder=build_command):
        ...

    def current(self) -> Optional[dict]:
        ...

    def history(self) -> list[dict]:
        ...

    def log(self, job_id: Optional[int]=None, since: int=0) -> dict:
        ...

    def _find(self, job_id: Optional[int]) -> Optional[Job]:
        ...

    def start(self, action: str, config: Optional[str], options: Optional[dict]=None) -> dict:
        ...

    def _append(self, job: Job, line: str) -> None:
        ...

    def _pump(self, job: Job) -> None:
        ...

    def cancel(self) -> dict:
        ...

    def _reap(self, proc: subprocess.Popen) -> None:
        ...

    def shutdown(self) -> None:
        ...

    def wait(self, timeout: float=30.0) -> Optional[dict]:
        """Block until the current job ends (tests)."""
        ...

def _signal_group(proc: subprocess.Popen, sig: int) -> None:
    ...
__all__ = ['ACTIONS', 'Job', 'JobBusy', 'JobError', 'JobManager', 'PathError', 'build_command']
