"""Anchor's signature marks: the pieces every Anchor figure is built from.

* :func:`lens` — the posterior uncertainty along a track, drawn as one
  continuous envelope (the union of per-step confidence ellipses) rather than
  a scatter of outlines. Pinned tracks read as a lens: tight at release and
  recovery, swelling between.
* :func:`behavior_track` — the mean path as a single line coloured by
  behaviour state, with a thin surface halo so it stays legible over bathymetry.
* :func:`pin` — an anchor point (release / recovery / verified fix): the one
  warm highlight in the view, direct-labelled, with its σ ring.
* :func:`lens_profile` — the same lens in one dimension: ±2σ about zero over
  time, forward vs smoothed.
* :func:`state_ribbon` / :func:`state_bands` — the ethogram as a barcode strip,
  or as soft background bands behind a time series.
* :func:`scale_bar`, :func:`north_arrow`, :func:`release_relative_axes` — map
  furniture that replaces raw UTM tick labels.
* :func:`stamp` — the reproducibility receipt in a figure's bottom corner.

All colours come from :mod:`anchor.viz.theme`, so a mark follows the active
light/dark mode.
"""
from __future__ import annotations
from typing import Iterable, Sequence
import matplotlib.patheffects as pe
import matplotlib.transforms as mtransforms
import numpy as np
from matplotlib.collections import LineCollection
from matplotlib.lines import Line2D
from matplotlib.patches import Patch, PathPatch
from matplotlib.path import Path
from matplotlib.ticker import FuncFormatter
from scipy.stats import chi2
from anchor.viz import theme

def _ellipse_union_path(means: np.ndarray, covs: np.ndarray, radius: float) -> Path | None:
    """One compound path of CCW ellipses; nonzero fill renders their union."""
    ...

def lens(ax, means_xy, cov_xy, *, levels: Sequence[float]=(0.5, 0.95), max_ellipses: int=400, color: str | None=None, alphas: Sequence[float] | None=None, zorder: float=3, label: str | None=None) -> list[PathPatch]:
    """Draw the posterior envelope along a track.

    Each confidence level is rendered as a single filled patch — the union of
    that level's ellipses at up to ``max_ellipses`` evenly spaced steps — so
    overlap never darkens the fill and the silhouette reads as one shape.
    ``levels`` go outermost-lightest; the default draws the 50 % core over
    the 95 % envelope.
    """
    ...

def lens_handles(levels: Sequence[float]=(0.5, 0.95), color: str | None=None, alphas: Sequence[float] | None=None) -> list[Patch]:
    """Legend swatches matching :func:`lens` (inner level first)."""
    ...

def _halo(width: float) -> list:
    ...

def behavior_track(ax, means_xy, states=None, *, lw: float=2.0, color: str | None=None, halo: bool=True, zorder: float=6, alpha: float=1.0) -> LineCollection:
    """The mean track as one line, coloured by behaviour state when given."""
    ...

def path_line(ax, means_xy, *, color: str | None=None, lw: float=1.2, ls: str=(0, (4, 2.5)), label: str | None=None, zorder: float=5, halo: bool=False):
    """A plain comparison path (e.g. forward-only), recessive by default."""
    ...

def pin(ax, x: float, y: float, label: str | None=None, *, sigma_m: float | None=None, offset: tuple[float, float]=(8, 8), ha: str='left', size: float=70, zorder: float=12, kind: str='anchor'):
    """An anchor point: warm dot, ink ring, optional σ ring and direct label.

    ``kind="end"`` draws an unfixed endpoint (hollow), for tracks whose end is
    not a recovery fix.
    """
    ...

def pin_handle(label: str='anchor fix') -> Line2D:
    ...

def state_handles(states=None, counts: bool=False, names: Sequence[str] | None=None) -> list[Line2D]:
    """Legend entries for the states present (all four when ``states`` is None)."""
    ...

def release_relative_axes(ax, x0: float, y0: float, unit: str='m') -> None:
    """Relabel UTM axes as metres east/north of the release (data stays UTM)."""
    ...

def map_axes(ax, *, grid: bool=False) -> None:
    """Map styling: equal aspect, all four spines hairline, no grid."""
    ...

def _nice(v: float) -> float:
    ...

def scale_bar(ax, *, loc: str='lower right', frac: float=0.2, zorder: float=20) -> float:
    """A two-tone scale bar sized to ~``frac`` of the x-extent. Returns its length."""
    ...

def north_arrow(ax, *, xy=(0.045, 0.93), zorder: float=20) -> None:
    ...

def bathymetry(ax, depth: np.ndarray, extent, *, vmax: float | None=None, zorder: float=0, contours: bool=True):
    """Water-column raster in the depth ramp, with hairline isobaths."""
    ...

def _runs(states: np.ndarray):
    ...

def state_bands(ax, t, states, *, amount: float=0.8, zorder: float=0) -> None:
    """Behaviour states as soft full-height bands behind a time series."""
    ...

def state_ribbon(ax, t, states, *, label_runs_longer_than: float | None=None, names: Sequence[str] | None=None) -> None:
    """The ethogram as a barcode: one horizontal strip, runs coloured by state.

    Runs longer than ``label_runs_longer_than`` (x units) get their state name
    written inside, so identity is never colour alone.
    """
    ...

def lens_profile(ax, t, sigma_forward=None, sigma_smoothed=None, *, k: float=2.0, anchors: Iterable[float]=()) -> None:
    """Uncertainty as a ±kσ fan about zero: the lens seen side-on.

    The forward filter's fan opens and never closes; the smoothed fan pinches
    shut at every anchor.
    """
    ...

def direct_label(ax, x, y, text, color=None, *, dx: float=4, ha: str='left', va: str='center', **kw):
    """Label a line at its end, in ink (the mark beside it carries the colour)."""
    ...

def header(fig, title: str, subtitle: str | None=None, *, x: float=0.012, y: float=0.995) -> None:
    """Left-aligned figure title with a muted subtitle line (replaces suptitle)."""
    ...

def stamp(fig, text: str | None=None, *, mark: bool=True) -> None:
    """Reproducibility receipt, bottom-left in mono; small Anchor mark bottom-right."""
    ...

def _text_width_pt(text, fig) -> float:
    ...

def receipt(deployment_id: str | None=None, **fields) -> str:
    """Build the text for :func:`stamp`: ``anchor 0.1.0 · <id> · k=v …``."""
    ...
