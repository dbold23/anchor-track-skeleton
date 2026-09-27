"""Channel-coordinate decomposition of a position error field.

Positional error in a tidal slough is not isotropic and reporting it as a
single scalar RMSE hides the only structure a reader cares about: the
along-channel component is the one the speed scale ``k`` and the current field
control and the one that is weakly identified, while the cross-channel
component is pinned by the polygon and the bathymetry. Section 3.7 of
``docs/design/leopard_shark_digital_twin.md`` scores them separately for
exactly that reason, and every score in :mod:`anchor.validation.ledger.scores`
takes its inputs in these coordinates.

The frame is defined by a centreline polyline (see
:class:`anchor.trajectory.currents.Centerline`):

``along``
    cumulative arc length of the foot point, metres from the centreline's
    first vertex, increasing up-slough;
``cross``
    signed perpendicular offset from the centreline, metres, positive to the
    **left** of the direction of increasing arc length.

The centreline is duck-typed on purpose — anything exposing ``coords_utm``,
``arc_length_m`` and ``project(x, y)`` works — so this module (and therefore
the whole ledger) imports with no geospatial extras installed.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Protocol
import numpy as np
_PROJECT_CHUNK = 20000

class CenterlineLike(Protocol):
    """The three members of ``Centerline`` this module uses."""
    coords_utm: np.ndarray
    arc_length_m: np.ndarray

    def project(self, x: np.ndarray, y: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        ...

@dataclass(frozen=True)
class ChannelCoords:
    """Channel-frame coordinates of a set of positions.

    Attributes
    ----------
    along_m, cross_m
        Arc length and signed lateral offset, same shape as the input's
        leading axes.
    bearing_rad
        Local centreline tangent at each foot point (math convention:
        0 = +East, pi/2 = +North). Carried so a caller can rotate a covariance
        into the same frame without projecting twice.
    at_end
        Boolean, same shape: the position projected onto a *terminal* vertex of
        the centreline, so its arc length was clamped rather than measured.
    """
    along_m: np.ndarray
    cross_m: np.ndarray
    bearing_rad: np.ndarray
    at_end: np.ndarray

    @property
    def fraction_at_end(self) -> float:
        """Fraction of positions whose arc length was clamped, in ``[0, 1]``.

        This is the honesty check on the whole along-channel half of the
        ledger. Both this module's :class:`StraightCenterline` and the real
        :class:`anchor.trajectory.currents.Centerline` clamp ``project`` to the
        polyline, so a track running off either end has *every* off-end
        position mapped to the same arc length. Along-channel errors between
        two clamped points are then identically zero, CRPS collapses, and
        containment goes to 1.0 — a calibration success manufactured by the
        projection rather than by the filter. Any non-zero value invalidates
        the along-channel numbers; the fix is a centreline that spans the
        track, not a wider interval.
        """
        ...

def to_channel(centerline: CenterlineLike, xy: np.ndarray) -> ChannelCoords:
    """Project positions ``xy`` (``(..., 2)``, centreline CRS) into the channel frame.

    ``along`` comes straight from ``Centerline.project``. ``cross`` is
    recovered from the same projection: the foot point is the polyline
    interpolated at the returned arc length, and the offset is the component
    of ``p - foot`` along the left normal of the local tangent.

    ``project`` clamps to the polyline, so positions beyond either end all
    share one arc length. Those are flagged in
    :attr:`ChannelCoords.at_end`; see :attr:`ChannelCoords.fraction_at_end`
    for why a non-zero count voids the along-channel scores.
    """
    ...

def channel_error(centerline: CenterlineLike, estimate_xy: np.ndarray, truth_xy: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Decompose ``estimate - truth`` into ``(along_error_m, cross_error_m)``.

    Both arrays are ``(..., 2)`` in the centreline's CRS and are broadcast
    against each other, so an ``(m, n, 2)`` ensemble against an ``(n, 2)``
    truth returns two ``(m, n)`` error fields.

    The along error is the *arc-length difference*, not the projection of the
    Cartesian error onto the tangent: over a long, curved slough the two
    differ, and the arc-length difference is the quantity the speed scale
    actually controls.
    """
    ...

def _interp_polyline(centerline: CenterlineLike, s: np.ndarray) -> np.ndarray:
    """Point on the polyline at arc length ``s`` (clamped to the ends)."""
    ...

class StraightCenterline:
    """A two-vertex centreline, for tests and for scoring synthetic tracks.

    Constructing a real :class:`~anchor.trajectory.currents.Centerline` needs
    ``pyproj`` and ``shapely`` and a GeoJSON on disk. This gives the same
    duck-typed interface from an origin and a bearing, so the ledger's own
    tests run with no geospatial extras and no ``data/``.
    """

    def __init__(self, origin: tuple[float, float]=(0.0, 0.0), bearing_rad: float=0.0, length_m: float=10000.0, crs: str='EPSG:32610') -> None:
        ...

    @property
    def total_length_m(self) -> float:
        ...

    def project(self, x: np.ndarray, y: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        ...
