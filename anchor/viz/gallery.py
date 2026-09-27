"""Render Anchor's figure set on the synthetic scene: ``anchor gallery``.

Writes the signature track figure (light and dark) plus the core report and
plot views, all from :func:`anchor.viz.scene.make_scene`, so the look can be
reviewed, shared or dropped into a talk without any field data.
"""
from __future__ import annotations
from pathlib import Path
import matplotlib
from anchor.viz import figures, marks, theme
from anchor.viz.scene import make_scene

def _hero(sc, path: Path) -> None:
    ...

def render(out_dir: str | Path, *, minutes: float=40.0, seed: int=7, dark: bool=True) -> list[Path]:
    """Write the gallery PNGs under ``out_dir``; returns their paths."""
    ...
