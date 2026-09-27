"""Active-learning loop tracking: round manifest + state across iterations.

The §4.4 W3 supervised-classifier workflow has three primitive steps that
already exist:

  - ``anchor labels query``   → uncertain-window CSV
  - ``anchor validation auto-clip`` → per-window MP4s for BORIS labeling
  - ``anchor labels import``  → BORIS/VIA export → labeled feature parquet

What was missing was state tracking across iterations. After a few rounds
of labeling the annotator easily loses track of which clips have been
labelled, which rounds are pending, and what the cumulative training set
looks like. This module adds a ``LabelingRound`` per-deployment manifest
that ties the three primitives into a single iteration loop.

Round lifecycle:

  PENDING_CLIP   → query CSV exists, MP4 clips not yet cut
  PENDING_LABEL  → MP4s exist, BORIS labels not yet imported
  LABELED        → BORIS export ingested, feature-window labels parquet present
"""
from __future__ import annotations
import datetime
import enum
import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Optional

class RoundStatus(str, enum.Enum):
    ...

@dataclass
class LabelingRound:
    """One active-learning iteration on a single deployment."""
    round_id: int
    deployment_id: str
    n_queries: int = 50
    boris_export: Optional[str] = None
    labels_parquet: Optional[str] = None
    completed_date: Optional[str] = None

@dataclass
class RoundManifest:
    """Per-deployment manifest of all active-learning rounds."""
    deployment_id: str

    def add(self, r: LabelingRound) -> None:
        ...

    def get(self, round_id: int) -> LabelingRound:
        ...

    def next_round_id(self) -> int:
        ...

    @classmethod
    def manifest_path(cls, deployment_id: str, root: Path=ROUNDS_ROOT) -> Path:
        ...

    @classmethod
    def load(cls, deployment_id: str, root: Path=ROUNDS_ROOT) -> 'RoundManifest':
        ...

    def save(self, root: Path=ROUNDS_ROOT) -> Path:
        ...

def round_dir(deployment_id: str, round_id: int, root: Path | str=ROUNDS_ROOT) -> Path:
    ...

def today_iso() -> str:
    ...

def bootstrap_round(deployment_id: str, query_csv: str | Path, method: str='entropy', n_queries: int=50, clips_dir: Optional[str | Path]=None, notes: str='', root: Path=ROUNDS_ROOT) -> LabelingRound:
    """Register a new round with a uncertain-window CSV.

    The MP4 cutting step happens via ``anchor validation auto-clip`` before
    or after this call; this function just records the round in the manifest
    so subsequent ``complete_round`` calls can find it.
    """
    ...

def mark_clipped(deployment_id: str, round_id: int, clips_dir: str | Path, root: Path=ROUNDS_ROOT) -> LabelingRound:
    """Promote round status PENDING_CLIP → PENDING_LABEL after auto-clipping."""
    ...

def complete_round(deployment_id: str, round_id: int, boris_export: str | Path, labels_parquet: Optional[str | Path]=None, root: Path=ROUNDS_ROOT) -> LabelingRound:
    """Promote round status PENDING_LABEL → LABELED after BORIS import."""
    ...

def status_summary(deployment_id: str, root: Path=ROUNDS_ROOT) -> str:
    """Multi-line, human-readable status of all rounds for a deployment."""
    ...
