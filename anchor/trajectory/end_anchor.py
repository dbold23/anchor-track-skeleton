"""Recovery-point anchor for the bidirectional particle smoother.

When a deployment's tag is recovered at a known coordinate (timed-release
+ same-day retrieval, or recapture with GPS) the recovery position is a
second hard observation — a Gaussian likelihood on (x_T, y_T). This is
exactly analogous to ``ReleaseAnchor`` at t=0; we keep them as separate
classes for clarity (different conceptual roles, different σ defaults
since recovery σ may be larger if the tag drifted between detachment
and pickup) but share the log-likelihood implementation.

Combined with ``ReleaseAnchor``, the trajectory is a *boundary value
problem*: dynamics propagate between two known endpoints, with the
animal's actual path constrained to start and end at given coords. The
two-filter smoother in ``anchor.track.two_filter`` exploits this:
forward pass conditions on (x_0, y_{1:t}); backward pass conditions on
(x_T, y_{t+1:T}); the joint posterior multiplies them.

Which anchor the smoother is actually given is a choice of *model*, and this
module owns it (``resolve_end_anchor_model``, ``grounded_end_anchor``):

``leeway``
    The shipped path. The recovery point is back-propagated through surface
    drift over the whole post-detach period by
    ``anchor.trajectory.detachment.estimate_detachment_position``, and the
    anchor is the resulting cloud's mean and per-axis σ. Right for a tag that
    floated; on ``BR_260318_S3`` it puts the anchor 2.7 km from where the tag
    was found, at σ 388 m, over a window in which the tag did not move.

``grounded``
    The recovery position itself, applied at the end of the attached span,
    widened by a bottom-creep allowance. Right for a tag that came to rest and
    was picked up from where it rested.

``auto``
    ``grounded`` when the record's regime table shows a stationary-wet span
    running into a temperature-verified out-of-water span with no separately
    detected surface span between them, ``leeway`` otherwise. The default, and
    the conservative fallback in every ambiguous case is the shipped model.
    It is **not** a float detector: see ``AUTO_MAX_SURFACE_MINUTES`` for what
    the third condition can and cannot see.
"""
from __future__ import annotations
import math
from dataclasses import dataclass
import numpy as np
from anchor.trajectory._gaussian_fix import isotropic_gaussian_logpdf, lonlat_to_xy

@dataclass
class EndAnchor:
    """Gaussian likelihood on the recovery position.

    Parameters
    ----------
    x, y : float
        Recovery coords in ``crs`` (UTM 10N for Elkhorn by default).
    sigma_m : float
        **Per-axis** 1σ of the recovery position, i.e. the σ of an
        isotropic 2-D Gaussian in which each of x and y has standard
        deviation ``sigma_m`` (the total 2-D radial spread is
        ``sqrt(2) * sigma_m``). This is the same convention as
        ``ReleaseAnchor``, ``VerifiedPosition`` and a GPS fix's quoted
        horizontal σ. Defaults to 10 m (GPS + minor tag-detachment
        drift); raise for tags that floated free for hours before
        retrieval.
    crs : str
        EPSG of (x, y).
    """
    x: float
    y: float
    sigma_m: float = 10.0

    @classmethod
    def from_lonlat(cls, lon: float, lat: float, sigma_m: float=10.0, target_crs: str='EPSG:32610') -> 'EndAnchor':
        ...

    def log_likelihood(self, px: np.ndarray, py: np.ndarray) -> np.ndarray:
        ...
DEFAULT_BOTTOM_CREEP_SIGMA_M = 25.0
AUTO_MAX_SURFACE_MINUTES = 10.0

@dataclass(frozen=True)
class EndAnchorChoice:
    """Which end-anchor model a run resolved to, and why.

    ``requested`` is what the configuration asked for (``"auto"``,
    ``"leeway"`` or ``"grounded"``); ``model`` is what ``auto`` resolved to and
    is always ``"leeway"`` or ``"grounded"``. ``reason`` is one sentence naming
    the regime rows the decision was read off, so a run log, a report and a
    ledger card can all quote the same sentence.
    """
    model: str
    requested: str
    reason: str
    stationary_wet_hours: float = 0.0
    surface_hours: float = 0.0
    out_of_water_hours: float = 0.0

    def to_dict(self) -> dict:
        ...

def _regime_rows(regimes) -> list:
    """``[(label, hours, basis), ...]`` from a regime table.

    Accepts ``RecordRegime`` objects or the dicts ``DetachmentResult.
    regime_table()`` produces, so the driver, the report and a test can all
    call the resolver with whatever they have to hand.
    """
    ...

def resolve_end_anchor_model(requested: str, regimes=None, *, max_surface_minutes: float=AUTO_MAX_SURFACE_MINUTES) -> EndAnchorChoice:
    """Resolve ``auto | leeway | grounded`` against the record's regime table.

    ``auto`` chooses **grounded** when all three hold:

    1. the table has a ``stationary_wet`` row — the tag stopped moving while
       still in the water, so there is a moment at which the attached span
       ends and a place the tag came to rest;
    2. the table ends in an ``out_of_water`` row whose ``basis`` is
       ``"depth+temperature"`` — the tag was picked up into air rather than
       left afloat, and a channel that can tell those apart said so. A row
       carrying the depth channel's answer alone does not qualify: zero metres
       is what a boat and a wave crest both read;
    3. any ``surface`` row between the two is shorter than
       ``max_surface_minutes``.

    Otherwise it chooses **leeway**, which is the shipped back-propagation.
    An explicit ``leeway`` or ``grounded`` is returned unchanged, with the
    regime hours recorded so the card still says what the table showed.

    **Condition 3 is not a float detector, and this docstring does not claim
    it is** (measured 2026-09-07; §19.3.2). The ``surface`` row it reads is the
    span between the water-exit index and the start of the terminal dry run —
    28 s on ``BR_260318_S3``. A tag genuinely floating reads depth ≈ 0, so it
    lies *inside* the terminal dry run, and whether the record is called
    ``out_of_water`` or ``surface`` is then decided by
    ``classify_terminal_dry_span``'s median over that whole run: by whether the
    float or the deck after it is the longer half. A record that floated for
    two hours and was then carried on deck for four resolves here to
    ``grounded``, with no surface row anywhere in the table.
    ``TerminalDrySpan.at_water_prefix_min`` measures the leading run of the dry
    span that is still at the water's temperature — the quantity such a guard
    would need — but it is reported and **not** thresholded, because a tag on a
    warming deck has one too (32 min on ``BR_260318_S3``, whose dry span
    reaches +1.0 °C only at minute 32) and no record in the repository provides
    a float to size the separation against.

    The rule is deliberately about the *absence* of a separately detected
    surface span rather than about the presence of a good bathymetric match: it
    contains no positional or bathymetric test at all. On any record satisfying
    the three conditions the recovery coordinate becomes a σ ≈ 27 m anchor with
    no check that it is anywhere near where the tag came to rest. A record whose
    tag floated is a record whose endpoint is not where it was found, however
    well the recovery cell's elevation fits; and a record whose tag never
    floated has an endpoint the recovery position measures directly, at the
    recovery fix's own σ rather than at the σ of hours of modelled drift.
    """
    ...

def grounded_end_anchor(recovery: EndAnchor, *, creep_sigma_m: float=DEFAULT_BOTTOM_CREEP_SIGMA_M) -> EndAnchor:
    """The recovery position itself, widened by a bottom-creep allowance.

    ``σ = sqrt(recovery.sigma_m² + creep_sigma_m²)`` — the recovery fix's own
    uncertainty and an allowance for how far the tag may have crept along the
    bed between the moment it stopped moving and the moment it was picked up.
    On the shipped 10 m recovery σ and the 25 m default that is 26.9 m.

    This is the anchor for a record whose tag never floated: the endpoint is
    *measured*, by whoever picked the tag up, rather than modelled backwards
    through seven hours of drift the tag did not undergo. It is applied at the
    end of the attached span — under the stationary rule, the stationary onset
    — which is where the animal record stops, not where the depth channel
    notices the tag has surfaced.
    """
    ...
