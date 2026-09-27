"""Uncertainty-propagated utilization distributions and energy seascapes.

Most space-use analyses build a home range from a *single* reconstructed track,
silently treating the path as exact. anchor's FFBS smoother instead produces K
*joint* trajectory samples (shape ``(T, K, state)``) — a multiple-imputation
ensemble of plausible paths consistent with all data, the physics constraints,
and the endpoint / Verified-Position anchors. Aggregating occupancy over all
K×T sample points yields a utilization distribution (UD) that **propagates
reconstruction uncertainty into the space-use estimate** — the gap momentuHMM
addresses for location measurement error via multiple imputation, here applied
to dead-reckoned IMU tracks.

Weighting each sample point by an instantaneous **energy proxy** (VeDBA/ODBA —
ODBA tracks metabolic rate at R²≈0.90 in lemon sharks, Bouyoucos et al. 2017)
turns the UD into an *energy seascape*: not just where the animal was, but where
it spent its metabolic budget. Both are emitted as a GeoTIFF density raster and
GeoJSON isopleth polygons via the standard :mod:`anchor.export` reprojection.

Core entry points:
  - :func:`kde_occupancy` — weighted KDE density grid from points.
  - :func:`utilization_distribution` — UD + isopleth areas from FFBS samples.
  - :func:`isopleth_mask` / :func:`home_range_area_m2` — volume-contour home range.
  - :func:`write_geotiff`, :func:`isopleth_polygons` — raster / vector output.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
import numpy as np

@dataclass
class UtilizationDistribution:
    """A normalized occupancy density on a regular grid.

    ``grid[i, j]`` is the probability mass in cell (row i = y, col j = x);
    ``grid`` sums to 1. ``extent`` is ``(xmin, ymin, xmax, ymax)`` in ``crs``
    units; ``cell_size_m`` is the square cell edge. Rows are ordered south→north
    (``grid[0]`` is the ``ymin`` row); writers flip as needed.
    """
    grid: np.ndarray
    extent: tuple
    cell_size_m: float
    crs: str
    energy_weighted: bool = False

def points_from_samples(samples: np.ndarray, energy_per_t=None):
    """Flatten FFBS ``(T, K, >=2)`` samples to ``(M, 2)`` xy points + weights.

    ``energy_per_t`` (length T) is broadcast across the K samples so every
    imputed path shares the per-timestep energy proxy. Returns ``(xy, weights)``
    where ``weights`` is None when no energy is supplied.
    """
    ...

def kde_occupancy(points_xy: np.ndarray, weights=None, cell_size_m: float=10.0, bandwidth_m: float=30.0, bounds: Optional[tuple]=None, pad_m: Optional[float]=None):
    """Weighted Gaussian-KDE occupancy density on a regular grid.

    Bins points into ``cell_size_m`` cells (weighted), smooths with a Gaussian
    of σ = ``bandwidth_m`` and normalizes to unit total mass. Returns
    ``(grid, extent)`` with ``grid`` summing to 1 and rows ordered south→north.
    """
    ...

def isopleth_mask(grid: np.ndarray, level: float) -> np.ndarray:
    """Boolean mask of the smallest cell set holding ``level`` of total mass.

    The standard volume-contour home-range rule: sort cells by density
    descending, accumulate mass, and include cells until the cumulative mass
    first reaches ``level`` (e.g. 0.95 → 95% UD).
    """
    ...

def home_range_area_m2(grid: np.ndarray, cell_size_m: float, level: float) -> float:
    """Area (m²) of the ``level`` isopleth = (#cells in mask) × cell area."""
    ...

def utilization_distribution(samples: np.ndarray, crs: str, energy_per_t=None, cell_size_m: float=10.0, bandwidth_m: float=30.0, levels=(0.5, 0.95), bounds: Optional[tuple]=None) -> UtilizationDistribution:
    """Build a (optionally energy-weighted) UD from FFBS trajectory samples.

    ``samples`` is the smoother's ``(T, K, >=2)`` array. With ``energy_per_t``
    (per-timestep VeDBA/ODBA), the density becomes an energy seascape. Returns a
    :class:`UtilizationDistribution` with isopleth areas (m²) per requested level.
    """
    ...

def _affine(extent, cell_size_m, n_rows):
    """North-up affine transform for writers (row 0 = north edge)."""
    ...

def write_geotiff(ud: UtilizationDistribution, path: str | Path) -> Path:
    """Write the UD density as a single-band float32 GeoTIFF (north-up)."""
    ...

def isopleth_polygons(ud: UtilizationDistribution, level: float) -> list:
    """Vectorize the ``level`` isopleth into polygons, reprojected to lon/lat.

    Returns a list of GeoJSON-style polygon coordinate lists (rings of
    ``[lon, lat]``) — directly embeddable in a FeatureCollection.
    """
    ...

def isopleths_geojson(ud: UtilizationDistribution, levels=(0.5, 0.95)) -> dict:
    """A GeoJSON FeatureCollection of isopleth polygons for each level."""
    ...
