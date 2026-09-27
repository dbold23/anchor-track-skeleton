"""Polygon constraint for the particle filter.

Rasterizes a slough/water polygon to a binary inside-mask aligned with the
bathymetry raster grid. Particles outside get ``-inf`` log-weight (=
weight 0 after exponentiation), so they're effectively rejected at the next
resampling pass.

Why hard rather than soft: we have no observed depth at this site, so the
polygon is the only spatial constraint. A soft Gaussian penalty would let
particles drift onto land while assigning them low (but nonzero) weight;
that creates a long tail of non-physical states. Hard rejection is honest
and matches the underlying truth (the shark is in water).

**2026-09-08, the soft option.** That paragraph is still the shipped default
and nothing below changes it. What is added is :meth:`distance_to_water_m` —
the Euclidean distance from a point to the nearest wet cell of the mask that
applies at its tide level — so that
``FilterConfig.polygon_mode="soft"`` can price a particle by *how far* out of
the water it is instead of by the bare fact that it is out. That is a model
change and it is argued where it is switched on
(:meth:`anchor.trajectory.particle_filter.ParticleFilter.apply_polygon_constraint`)
and in the dated design amendment it requires; here it is only measured.

Usage
-----
    from anchor.trajectory.polygon_constraint import PolygonConstraint
    poly = PolygonConstraint.from_geojson(
        "data/raw/elkhorn_outline.geojson",
        raster_path="data/external/elkhorn_bathy.tif",
    )
    inside = poly.is_inside(particles[:, 0], particles[:, 1])  # (N,) bool
"""
from __future__ import annotations
import json
from dataclasses import dataclass
from pathlib import Path
import numpy as np
import pyproj
import rasterio
import shapely.geometry
import shapely.ops
from rasterio.features import rasterize

def _pixel_size_m(transform: rasterio.Affine) -> tuple[float, float]:
    """``(row spacing, column spacing)`` in CRS units, for an axis-aligned grid.

    The distance transform below works on the raster lattice and scales the
    result by the pixel size, which is only a distance if the grid is not
    rotated or sheared. Elkhorn's raster is north-up (``b = d = 0``); a rotated
    one has to be resampled before any of this means metres, so it raises
    rather than returning a number that reads like metres and is not.
    """
    ...

def distance_to_wet_m(mask: np.ndarray, transform: rasterio.Affine) -> np.ndarray:
    """Metres from every cell of ``mask`` to the nearest wet (non-zero) cell.

    Zero on the wet cells themselves. ``scipy.ndimage.distance_transform_edt``
    measures, for each non-zero element of its input, the distance to the
    nearest zero element — so the input is the *dry* mask and the zeros it
    measures to are the wet cells. ``sampling`` carries the pixel size, so the
    result is in the raster's CRS units (metres, on a UTM grid) and not in
    cells.

    Returned as ``float32``: on Elkhorn's 1670 x 1351 raster one level is
    **9.0 MB** at that width against 18.0 at float64, and the quantity is a
    distance in metres compared against a soft width of order 10 m, so single
    precision is four significant figures more than the comparison can use.
    An all-dry level returns ``inf`` everywhere — there is no wet cell to
    measure to, and a large finite number would read as one.
    """
    ...

@dataclass
class PolygonConstraint:
    mask: np.ndarray
    transform: rasterio.Affine
    crs: pyproj.CRS

    @classmethod
    def from_geojson(cls, geojson_path: str | Path, raster_path: str | Path) -> 'PolygonConstraint':
        ...

    def _xy_to_rc(self, x: np.ndarray, y: np.ndarray):
        ...

    def is_inside(self, x: np.ndarray, y: np.ndarray, tide_m_mllw: float | None=None) -> np.ndarray:
        """Vectorized point-in-polygon. ``tide_m_mllw`` is accepted but
        ignored — kept for signature compatibility with TidalPolygonConstraint
        so the filter loop can call either polymorphically."""
        ...

    def distance_to_water_m(self, x: np.ndarray, y: np.ndarray, tide_m_mllw: float | None=None) -> np.ndarray:
        """Metres from the centre of each point's raster cell to the nearest wet
        cell; 0 anywhere inside a wet cell.

        The lookup is ``field[row, col]``, so the value is quantised to the
        cell the point falls in: a particle half a metre outside the waterline
        is charged a full pixel (4.36 m on Elkhorn) and one anywhere inside a
        wet cell is charged exactly zero. The quantisation is +/- half a pixel,
        small against the 20 m default softening width but not against the
        cell of boundary error design 3.5's amendment cites as the scale it
        is modelling.

        ``tide_m_mllw`` is accepted and ignored, for the same signature
        compatibility :meth:`is_inside` keeps. A point off the raster returns
        ``inf``: the distance transform is defined on the lattice and nothing
        outside it has a measured distance to water. The caller decides what an
        unmeasurable distance costs — see
        :meth:`anchor.trajectory.particle_filter.ParticleFilter.apply_polygon_constraint`,
        which charges it the full polygon penalty, exactly as the indicator does.

        The transform is computed once and cached (one ``float32`` array the
        size of the raster).
        """
        ...

def _sample_distance(field: np.ndarray, xy_to_rc, x, y) -> np.ndarray:
    """Look ``(x, y)`` up in a per-cell distance field; ``inf`` off the raster."""
    ...

def rebuild_wet_masks(bathy_path: str | Path, outline_path: str | Path, levels_m: np.ndarray, threshold_m: float) -> np.ndarray:
    """The tidal wet-mask stack, recomputed in memory at ``threshold_m``.

    The predicate is the one ``scripts/build_tide_polygon_stack.build_stack``
    bakes into ``data/external/elkhorn_tide_polygon_stack.npz`` —
    ``(bathy_at_mllw + η) > threshold ∩ static_outline`` — evaluated on the same
    raster, the same outline and whatever ``levels_m`` the caller passes, which
    is the loaded stack's own level axis wherever the driver calls this. The
    arithmetic is deliberately identical, down to the raster's ``float32`` and
    the ``nodata → NaN`` substitution (NaN fails the comparison, so a nodata
    cell is dry at every level and every threshold), so that at the baked
    threshold this function reproduces the shipped stack **bit for bit** —
    ``tests/trajectory/test_wet_threshold.py`` asserts exactly that against the
    npz on disk, which is the only thing that keeps a second copy of a
    predicate honest.

    The outline is rasterized by :meth:`PolygonConstraint.from_geojson` rather
    than by a second rasterizer written here, so the two classes cannot disagree
    about which cells the drawn outline covers.

    **Why a threshold is worth moving.** The baked value is 0.05 m: a cell with
    5 cm of water over it is water. A 0.47 m disc-width bat ray cannot swim in
    5 cm, so the shipped mask admits intertidal flats the animal is physically
    excluded from, and ``docs/regen_2026-09.md`` §22.6 leaves "a genuine
    exclusion from the flats that the polygon does not encode — a minimum
    swimmable depth" as one of four untested candidates for the corrected
    reconstruction's kilometre-scale endpoint error. This function is how that
    candidate is run without rewriting the npz.

    **Cost.** On Elkhorn's 1670 x 1351 raster and the shipped 15-level axis:
    **0.104 s** (median of three warm rebuilds) and a **58.8 MB** peak
    (``tracemalloc``) — the raster at ``float32`` (9.0 MB), the rasterized
    outline, one ``bool`` scratch per level and the ``uint8`` stack itself
    (33.8 MB), which is the same 33.8 MB the loaded stack already occupies.
    It is paid once per run, in the driver, before the filter starts.

    Returns the ``(L, H, W) uint8`` stack. Raises if the raster and the outline
    do not land on one grid, which cannot happen for the shipped pair.
    """
    ...

@dataclass
class TidalPolygonConstraint:
    """Tide-aware polygon: precomputed stack of wet masks at discrete tide
    levels (m above MLLW). At each filter step, looks up the nearest
    precomputed level and returns its mask.

    Build the stack via ``scripts/build_tide_polygon_stack.py``. The stack
    is a 3D ``uint8`` array of shape ``(L, H, W)`` where ``L`` is the
    tide-level axis. The wet predicate baked into each mask is
    ``(bathy_at_mllw + η) > threshold ∩ static_outline``, so all the
    geometry is correct by construction.

    :attr:`threshold_m` is the wet predicate's own threshold — the depth of
    water below which a cell is not water. It arrives from the npz and is the
    number :meth:`with_threshold` moves.
    """
    masks: np.ndarray
    levels_m: np.ndarray
    threshold_m: float
    transform: rasterio.Affine
    crs: pyproj.CRS

    @classmethod
    def from_stack(cls, stack_path: str | Path, raster_path: str | Path) -> 'TidalPolygonConstraint':
        ...

    def with_threshold(self, threshold_m: float, *, raster_path: str | Path, outline_path: str | Path) -> 'TidalPolygonConstraint':
        """This constraint with its wet masks rebuilt at ``threshold_m``.

        The level axis, the grid, the transform and the CRS are this object's;
        only the masks and :attr:`threshold_m` change, so the nearest-level
        lookup a filter step makes is unchanged and every cached distance field
        is discarded with the object it belonged to. Returns ``self`` unchanged
        when the threshold asked for is the one already in force, so a caller
        that names the baked value pays nothing and gets the shipped arrays.

        The rebuild is :func:`rebuild_wet_masks` — same predicate, same raster,
        same outline — and the result's grid is checked against this stack's:
        a raster of a different shape means the stack and the rebuild are not
        describing one place, and there is no reading of that which the filter
        should be allowed to run on.
        """
        ...

    def _xy_to_rc(self, x: np.ndarray, y: np.ndarray):
        ...

    def _level_index(self, tide_m_mllw: float) -> int:
        """Pick the nearest precomputed tide level. Hard-rejection has no
        fractional semantics — interpolating between two binary masks
        would give a bogus 0.5 weight; nearest is the only honest choice."""
        ...

    @property
    def n_levels(self) -> int:
        ...

    @property
    def grid_shape(self) -> tuple[int, int]:
        ...

    def mask_at_level(self, tide_m_mllw: float) -> np.ndarray:
        """Return the (H, W) bool mask used at this tide level."""
        ...

    def is_inside(self, x: np.ndarray, y: np.ndarray, tide_m_mllw: float | None=None) -> np.ndarray:
        ...

    def distance_field_at_level(self, tide_m_mllw: float) -> np.ndarray:
        """The cached distance-to-wet transform for this tide level, in metres.

        Computed on first use of a level and kept. **Memory.** One level is a
        ``float32`` array the size of the raster — 1670 x 1351 x 4 B = **9.0 MB**
        on Elkhorn — and the stack has ``n_levels`` of them (15 here, eta -1.00
        to +2.50 m in 0.25 m steps), so caching every level a run touches costs
        at most **135 MB**. A nine-hour record sweeps roughly one tidal
        half-cycle and touches a handful of levels, so the realised cost is
        tens of megabytes; the whole stack is only paid for by a run that sees
        the full eta range. The masks themselves are already resident (15 x
        ``uint8`` = 33.8 MB), so this is the same object at four times the width
        and only for the levels asked for.

        The cache is dropped on pickling: a grid worker process receives the
        masks and rebuilds whatever levels it uses, rather than having 135 MB
        of derived array pushed through a pipe. That also means the ceiling is
        **per process**: a latent grid run at ``--latent-grid-workers 8`` has
        eight of these caches, so the worst case is 8 x 135 MB ~ 1.1 GB, not
        135 MB.
        """
        ...

    def distance_to_water_m(self, x: np.ndarray, y: np.ndarray, tide_m_mllw: float | None=None) -> np.ndarray:
        """Metres from each point to the nearest wet cell at this tide level.

        Zero for a point already in the water. ``inf`` for a point off the
        raster, for the reason :meth:`PolygonConstraint.distance_to_water_m`
        gives. The level is chosen by the same nearest-level rule
        :meth:`is_inside` uses, so the distance and the indicator always
        describe the same mask.
        """
        ...

    def __getstate__(self) -> dict:
        """Pickle without the derived distance fields (see
        :meth:`distance_field_at_level`)."""
        ...
