"""Derive a slough water-body polygon from topobathy via tide-conditional
flood-fill.

The bathymetry raster is the authoritative geometry — depth values encode
exactly where water can sit at any given tide level. The wet predicate
``bathy + η > threshold`` defines a binary mask; connected-component
labeling extracts the topological water-bodies; selecting the component
containing a known channel seed gives the slough-proper outline,
distinguishing it from adjacent water (Monterey Bay, Moro Cojo Slough,
Salinas River).

Pipeline:
    1. Read topobathy raster (NCEI NCEI/USGS Watt 2009 etc.)
    2. Optionally clip to a coarse bounding box (excludes open ocean).
    3. Build wet mask at the chosen tide level + threshold.
    4. Apply optional morphological closing to fill micro-holes from
       interpolation artefacts (1-2 px wide).
    5. Connected-component label.
    6. Pick the component containing the seed point in raster coords.
    7. Vectorize via rasterio.features.shapes; merge into a single
       (Multi)Polygon.
    8. Optional simplification (Douglas-Peucker) to reduce vertex count
       for downstream rasterization performance — kept off by default.
    9. Reproject from raster CRS to output CRS (WGS84 by default).

The output is provenance-tagged: the resulting GeoJSON Feature includes
the tide level, threshold, seed coordinates, source raster path,
component cell count, and a SHA1 of the input raster — so reproduction
is deterministic.

References
----------
- Hall et al. 2018 (CalCOFI) — tide-conditional masking of estuarine
  bathymetry for habitat delineation.
- Friedrichs 2010 — tidal-prism geometry derivations rely on identical
  flood-fill methodology applied at MHW.
"""
from __future__ import annotations
import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
import numpy as np
import pyproj
import rasterio
import shapely.geometry
import shapely.ops
from rasterio.features import shapes as rasterio_shapes
from scipy import ndimage as ndi

@dataclass
class BathyOutlineResult:
    """Provenance-tagged outline derivation result."""
    geometry_wgs84: shapely.geometry.MultiPolygon
    tide_level_m: float
    threshold_m: float
    seed_lonlat: tuple[float, float]
    seed_in_raster_rc: tuple[int, int]
    component_label: int
    component_n_cells: int
    bathy_path: Path
    bathy_sha1: str
    n_components_total: int
    raster_crs: str
    extracted_at_utc: str
    bbox_lonlat: Optional[tuple[float, float, float, float]] = None
    morph_close_iters: int = 0
    simplify_tolerance_m: float = 0.0

def _file_sha1(path: Path, block_size: int=1 << 16) -> str:
    ...

def _wgs_bbox_to_raster_window(bbox_lonlat: tuple[float, float, float, float], raster_transform: rasterio.Affine, raster_crs, raster_shape: tuple[int, int]) -> tuple[int, int, int, int]:
    """Convert a WGS84 lon/lat bbox to integer (row_min, row_max, col_min, col_max)
    indices into the raster, clamped to the raster bounds. Returns rows in
    [row_min, row_max) and cols in [col_min, col_max) (numpy-slice convention)."""
    ...

def _lonlat_to_raster_rc(lon: float, lat: float, raster_transform: rasterio.Affine, raster_crs) -> tuple[int, int]:
    ...

def _vectorize_mask_to_geom(mask_local: np.ndarray, transform_local: rasterio.Affine, raster_crs, output_crs: str=WGS84) -> shapely.geometry.MultiPolygon:
    ...

def derive_outline_from_bathy(bathy_path: str | Path, *, seed_lonlat: tuple[float, float], tide_level_m: float=1.5, threshold_m: float=0.0, bbox_lonlat: Optional[tuple[float, float, float, float]]=None, morph_close_iters: int=1, simplify_tolerance_m: float=0.0, output_crs: str=WGS84) -> BathyOutlineResult:
    """Run the flood-fill outline derivation. See module docstring."""
    ...

def write_outline_geojson(result: BathyOutlineResult, out_path: str | Path, *, name: str='auto-derived bathymetric outline') -> Path:
    """Write a GeoJSON Feature with full provenance in the properties block."""
    ...

def derive_outline_nhd_consensus(bathy_path: str | Path, nhd_polygon_wgs84: shapely.geometry.base.BaseGeometry, *, tide_level_m: float=1.5, threshold_m: float=0.0, bbox_lonlat: Optional[tuple[float, float, float, float]]=None, morph_close_iters: int=1, output_crs: str=WGS84) -> BathyOutlineResult:
    """Derive the outline by NHD-consensus connectivity.

    Why this exists: surface bathymetry alone cannot resolve culvert,
    tide-gate, and tunnel connectivity. Two physically-distinct
    surface-DEM components may be hydraulically the same waterbody if a
    subsurface culvert connects them — Elkhorn Slough has multiple such
    cases (Highway 1 culverts, Salinas River diversion gates, marsh
    mosquito-control flap gates).

    NHD captures this connectivity authoritatively because it's
    surveyed from hydrographic surveys + USGS field validation, not
    from a DEM. So:

        1. Take NHD's polygon for Elkhorn Slough as the authoritative
           "this is hydraulically one waterbody" footprint.
        2. Compute the bathy wet mask at the chosen tide level.
        3. Connected-component label the wet mask.
        4. KEEP any component whose centroid is inside NHD's polygon —
           regardless of whether it's surface-connected to the others.

    Result: an outline that respects subsurface culvert topology while
    using bathymetric depth resolution within each surface component.

    The trade-off is that NHD's polygon is larger than the bathy
    footprint (it includes marsh outside the multibeam coverage), so
    components in NHD-but-not-in-bathy aren't recovered — but they
    couldn't be evaluated by the filter anyway.
    """
    ...

def sweep_tide_levels(bathy_path: str | Path, *, seed_lonlat: tuple[float, float], tide_levels_m: tuple[float, ...]=(-0.5, 0.0, 0.5, 1.0, 1.5, 2.0), threshold_m: float=0.0, bbox_lonlat: Optional[tuple[float, float, float, float]]=None, morph_close_iters: int=1) -> list[BathyOutlineResult]:
    """Sweep the flood-fill across tide levels for sensitivity analysis.

    Returns one BathyOutlineResult per level; the caller can produce an
    overlay figure or compute Jaccard between adjacent levels to quantify
    the outline's tide-sensitivity.
    """
    ...
