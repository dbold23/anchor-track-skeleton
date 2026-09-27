"""Anchor's figure theme: brand tokens, the behaviour-state palette, colormaps, rcParams.

One place for every colour a figure uses, so a map, a report panel, the
dashboard and an exported PNG all say "rest" in the same blue. The brand
tokens mirror the brand identity's ``docs/brand/brand-tokens.json`` v0.1.0 (its source of truth);
the behaviour-state palette is Anchor's own and was checked for colour-vision
deficiency separation against both surfaces (adjacent-pair CVD ΔE ≥ 10 in
OKLab×100, normal-vision ΔE ≥ 15), so the four states stay distinguishable
under protan / deutan / tritan simulation.

Usage::

    from anchor.viz import theme
    with theme.style():            # light, publication defaults
        fig, ax = plt.subplots()
        ...
    theme.use("dark")              # or set it for the whole process

``ANCHOR_FIG_THEME=dark`` switches every styled figure to the dark theme.
"""
from __future__ import annotations
import functools
import os
from contextlib import contextmanager
from typing import Iterator, Literal
import matplotlib as mpl
import numpy as np
from matplotlib.colors import LinearSegmentedColormap, ListedColormap, to_rgb

def _env_mode() -> Mode:
    ...

def mode() -> Mode:
    """The theme mode currently in force (``use``/``style`` or the env var)."""
    ...

def tokens(m: Mode | None=None) -> dict[str, str]:
    """Surface/ink tokens for ``m`` (default: the active mode)."""
    ...

def status_color(level: str, m: Mode | None=None) -> str:
    """QC colour for ``PASS``/``WARN``/``FAIL``/``UNVERIFIED`` (case-insensitive)."""
    ...

def state_color(state: int | str, m: Mode | None=None) -> str:
    """Colour of one behaviour state, by index (0-3) or name."""
    ...

def state_colors(m: Mode | None=None) -> dict[int, str]:
    """``{0: rest, 1: cruise, 2: active, 3: burst}`` colour map."""
    ...

def state_tint(state: int | str, amount: float=0.82, m: Mode | None=None) -> tuple:
    """A state's colour mixed toward the surface: a background band, not a mark."""
    ...

def state_cmap(m: Mode | None=None) -> ListedColormap:
    """Discrete 4-colour colormap for integer state arrays (``vmin=-0.5, vmax=3.5``)."""
    ...

def _register() -> None:
    ...

def rcparams(m: Mode | None=None) -> dict:
    """matplotlib rcParams for Anchor figures in mode ``m``."""
    ...

def use(m: Mode | None=None) -> None:
    """Apply the Anchor theme process-wide."""
    ...

@contextmanager
def style(m: Mode | None=None) -> Iterator[dict[str, str]]:
    """Scope the theme to a block; yields the surface tokens for that mode."""
    ...

def styled(fn):
    """Decorator: run a figure-building function inside :func:`style`."""
    ...
