"""Wrap the SDB depth + sigma rasters as a (lon, lat) -> (depth, sigma) lookup
with bilinear interpolation. Used as a soft Gaussian constraint in the
particle-filter trajectory reconstruction (per design doc §5.2b / §5.3).

Behavior outside the raster (or in nodata cells): returns (nan, +inf) so the
likelihood is uninformative — caller should fall back to GEBCO with σ ≈ 30 m
(:data:`REFERENCE_SIGMA_M`, which is also the reference σ that puts the
in-raster and no-data likelihood branches on one scale).
"""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import numpy as np
import pyproj
import rasterio
REFERENCE_SIGMA_M = 30.0

@dataclass
class BathyLookup:
    depth: np.ndarray
    sigma: np.ndarray
    nodata: float
    transform: rasterio.Affine
    crs: pyproj.CRS
    _to_raster: pyproj.Transformer
    _to_wgs84: pyproj.Transformer

    @classmethod
    def from_paths(cls, depth_path: Path, sigma_path: Path) -> 'BathyLookup':
        ...

    def _xy_to_rc(self, x: np.ndarray, y: np.ndarray):
        ...

    def _bilinear(self, arr: np.ndarray, row: np.ndarray, col: np.ndarray):
        """Bilinear interp with graceful partial-nodata handling.

        If any of the 4 corners are nodata, we renormalize over the valid
        corners' weights. If all 4 are nodata, output nan. This avoids
        ragged holes along the valid-mask boundary which would otherwise
        leave the soft constraint uninformative there.
        """
        ...

    def lookup(self, lon: np.ndarray, lat: np.ndarray):
        """Return (depth_m, sigma_m). Out-of-raster / nodata -> (nan, +inf)."""
        ...

    def lookup_xy(self, x: np.ndarray, y: np.ndarray):
        """Lookup using raster-native CRS (typically UTM, meters).
        Faster than lookup() for particle filter inner loops."""
        ...

    def bathymetry_violation_logpdf(self, observed_depth: np.ndarray, x: np.ndarray, y: np.ndarray, extra_sigma_m: float=1.0, mode: str='one_sided', off_bottom_factor: float=1.0, reference_sigma_m: float=REFERENCE_SIGMA_M, tide_m_mllw: float | None=None) -> np.ndarray:
        """Soft-constraint log-likelihood on animal depth vs seafloor depth.

        Outside the raster (or in an all-nodata neighbourhood) the result is 0.0
        exactly in both modes. Both branches are on a common reference scale, so
        that 0.0 is a *comparable* score and not a free pass: see
        ``reference_sigma_m`` below.

        **The two depths are measured from different data, and ``tide_m_mllw``
        is what puts them on one datum.** The raster gives the bed's depth below
        MLLW, ``bathy``; the tag's pressure record gives ``observed``, a depth
        below the *instantaneous* water surface. The surface at time t stands
        η(t) above MLLW, so the seafloor's depth below that surface is
        ``bathy + η(t)`` and the physical constraint is
        ``observed <= bathy + η(t)``. Every formula below therefore compares
        ``observed`` with ``bed = bathy + η``. ``tide_m_mllw=None`` (or a
        non-finite value, which is what a gap in a tide series looks like) means
        η = 0, i.e. the MLLW comparison this method made before the term
        existed, and it is then bit-for-bit that comparison — the addition is
        skipped, not performed with a zero. On an intertidal record η is not a
        rounding error: at Elkhorn it runs +0.28 to +1.6 m, so a tag at 1.2 m
        over a 0.5 m (MLLW) flat at η = +1.0 m is perfectly legal and was
        charged, with no tide term, as a 0.7 m violation
        (``docs/regen_2026-09.md`` §21.2, §21.7). ``TidalPolygonConstraint``
        already draws its wet mask at ``bathy + η``, so passing η here is also
        what makes the depth likelihood and the water polygon agree about where
        the water is.

        ``mode="one_sided"`` (default, behaviour-agnostic) encodes only the hard
        physical fact that the animal cannot be below the seafloor::

            bed   = bathy + η
            log p = 0                                          if observed <= bed
                  = -0.5 * ((observed - bed) / σ_eff)²          otherwise
                  = 0                                          outside raster

        This is a log-*probability of admissibility*, log P(seafloor >= observed),
        not a density in ``observed``: it is capped at 0 and carries no
        ``-log σ_eff`` normaliser. That is deliberate, and it is a modelling
        argument rather than an empirical one. Every admissible particle must
        score identically, because "the animal is not inside the seabed" is
        equally true in a well-surveyed and a poorly-surveyed cell; a
        ``-log σ_eff`` term here would grade admissible particles by local survey
        quality, which carries no physical content. (The flat branch also makes
        the one-sided form non-normalisable in ``observed``, and its true
        normaliser over depths >= 0 would be ``-log(bathy + σ_eff*sqrt(π/2))``,
        not ``-log σ_eff``.) The σ scaling of the violation branch is the whole
        model: a larger survey uncertainty genuinely makes a given apparent
        violation more plausible.

        ``mode="bottom_following"`` instead assumes the animal tracks the bottom
        at ``off_bottom_factor * bathy``, giving a two-sided Gaussian that also
        penalises positions that are *too deep* for the observed depth. That IS a
        density in ``observed``, so it carries the Gaussian normaliser, expressed
        as a log-density *ratio* against a reference cell of uncertainty
        ``reference_sigma_m``::

            residual = observed - off_bottom_factor * (bathy + η)
            log p    = -0.5*(residual/σ_eff)² - log(σ_eff / σ_ref)

        The factor multiplies the tide term as well as the bed, and that is the
        modelling claim, not an implementation convenience: ``off_bottom_factor``
        is defined as a fraction of the *local water depth* ("swims at 85 % of
        the depth"), and the local water depth is ``bathy + η``. The alternative
        ``off_bottom_factor * bathy + η`` is a fixed distance off the MLLW bed
        wearing a fraction's clothes, and it breaks where the tide matters most:
        over a flat with ``bathy = 0`` it puts the animal at η — on the bed —
        for every factor, while ``f * (bathy + η)`` correctly puts an f = 0.85
        animal at 85 % of the water that is actually there. At f = 1 the two
        agree, which is why the default is unaffected by the choice.

        The ``-log σ_eff`` term is not optional here: σ_eff varies spatially with
        the surveyed-uncertainty raster, so dropping it makes least-surveyed
        (high-σ) cells uniformly cheaper for every particle and quietly attracts
        the cloud to them.

        The ``+log σ_ref`` is what keeps the no-data branch honest. An absolute
        Gaussian log-density peaks at ``-log σ_eff - 0.5*log(2π)``, which is
        negative for every σ_eff above 1/sqrt(2π) ≈ 0.4 m — i.e. always, here. So
        pairing it with a no-data branch pinned at 0.0 would make an unsurveyed
        hole beat *every* in-raster particle — the same "run to the unsurveyed
        cells" failure the normaliser exists to remove, only with the sign
        flipped. Referencing every cell to σ_ref instead makes 0.0 mean "a
        σ_ref-quality cell whose seafloor matches the observation", so a genuinely
        better-surveyed matching cell scores above a hole and a badly mismatched
        one scores below it. Only a per-call additive constant changes; the
        spatial weighting is unaffected.

        This is a BEHAVIOURAL assumption, not a physical one. In low-relief
        estuarine channels it makes depth genuinely informative about position
        (measured ~2-3x lower track RMSE for benthic species when combined with
        the polygon constraint — measured before the normaliser below landed,
        and not yet re-derived), but it is catastrophically wrong for an animal
        swimming mid-water: a shallow-swimming animal is pulled onto shallow
        banks whose seafloor matches its depth (measured ~5-9x WORSE — likewise
        measured before the normaliser landed, and not yet re-derived). Neither
        figure describes current behaviour; treat both as the qualitative
        direction only. Enable this mode only for demonstrably benthic species,
        and never as a global default. Note it is only informative alongside the
        polygon constraint — depth alone is positionally ambiguous.

        σ_eff = sqrt(raster_σ² + extra_sigma_m²) — extra_sigma absorbs animal
        off-bottom swimming + raster vertical error, per design doc §5.1.
        σ_ref = ``reference_sigma_m``, the GEBCO fallback σ (see
        :data:`REFERENCE_SIGMA_M`); it shifts ``bottom_following`` by the
        constant ``+log σ_ref`` and is ignored by ``one_sided``.
        η = ``tide_m_mllw``, the water level above MLLW in metres, positive up —
        the same scalar the caller hands
        :meth:`ParticleFilter.apply_polygon_constraint`. **η is treated as
        exact**: it enters the residual and not σ_eff, so no tide error is
        modelled here. One station, linearly interpolated, with no phase lag to
        the animal's reach of the slough — 20 minutes at 0.32 m/h is 0.11 m of
        unmodelled bias in every residual — and ``extra_sigma_m`` is the only
        slack absorbing it (``docs/regen_2026-09.md`` §22.6).

        Precision note: σ_eff is evaluated in float64, where it used to inherit
        the raster's float32. ``one_sided`` is therefore unchanged in *form* but
        not bit-identical: with ``extra_sigma_m=0.0`` it is exact, and at the
        production defaults (1.0 / 1.5 m) the returned log-pdf moves by up to
        ~6e-06, which propagates to ~1e-08 m on a 240-step two-filter endpoint.
        Golden-value tests must use a tolerance rather than exact equality.
        The tide branch is on the same footing: with ``tide_m_mllw`` supplied
        the corrected bed is formed in float64, and with it absent the raster's
        own float32 value is used unaltered, so a no-tide call is exactly the
        call this method served before the term existed.
        """
        ...

    def log_likelihood(self, lon: np.ndarray, lat: np.ndarray, observed_depth: np.ndarray, tide_m_mllw: float | None=None) -> np.ndarray:
        """Gaussian log-likelihood log p(observed_depth | bathy(lon, lat)).

        Thin lon/lat convenience wrapper over
        :meth:`bathymetry_violation_logpdf` with ``mode="bottom_following"``,
        ``off_bottom_factor=1.0`` and no extra σ, i.e. the two-sided Gaussian
        on ``observed - bathy`` with the raster σ alone, on that method's
        reference scale (an additive ``+log σ_ref + 0.5*log(2π)`` away from an
        absolute Gaussian log-density, constant across cells and so irrelevant
        to weighting). ``tide_m_mllw`` is forwarded unchanged, so the two public
        depth entry points cannot drift apart; its default of ``None`` leaves
        this wrapper comparing ``observed`` with the MLLW bed exactly as it did
        before the term existed. Out-of-raster -> 0.0. Depth below the seafloor
        is *not* hard-rejected here;
        per design doc we use a soft Gaussian with the spatially-varying σ.
        """
        ...
