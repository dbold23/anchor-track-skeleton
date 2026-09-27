"""Tag-detachment detection + post-detachment surface-drift modeling.

When an AXY-5 (or any timed-release biologger) tag pops off the animal,
the time series after detachment isn't biological — it's the tag
floating at the surface, advected by surface currents and wind. Treating
it as bat-ray-dynamics gives nonsense.

Detachment leaves a textbook signature in the depth channel: depth drops
to ~0 m within seconds (tag rises to surface) and stays there for the
remainder of the recording. We exploit that here.

Three groups of functions:

    detect_tag_detachment(track, ...) -> DetachmentResult
        Find the first sample index where depth < threshold and stays
        below threshold for the remainder of the deployment. This is the
        *water-exit* rule: it finds the moment the tag reached the
        surface, which on a negatively-settling record is hours after
        the moment it stopped moving.

    detect_stationary_onset(acc, fs, ...) -> StationaryOnset
        The moment the tag stopped moving, from the accelerometer alone
        (docs/regen_2026-09.md §17.4.2). A tag can detach, sink and lie
        on the bottom for hours before its float works it to the
        surface; the depth channel cannot see that and the water-exit
        rule therefore ships those hours as animal record.

    estimate_detachment_position(track, recovery_anchor, t_detach,
                                 tide_series, current_field, ...)
            -> EndAnchor

        Given a known recovery position and the float duration
        t_recovery - t_detach, propagate the recovery point *backward*
        through the surface drift to estimate where the tag detached
        — i.e., where the bat ray actually ended its trajectory.
        Returns a wide-σ EndAnchor at the detachment time that the
        FFBS smoother can use without overconstraining.

Surface drift = tidal current (subsurface scaled by surface-vs-near-
bottom factor) + (optional) wind drag. Wind drag would be the major
component for hours-long floats but requires NOAA NDBC data to fetch;
this module's default is tide-only and documents wind as a known
unmodeled term in the σ budget.
"""
from __future__ import annotations
import logging
from dataclasses import dataclass, field
from typing import Literal, Optional
import numpy as np
from anchor.trajectory.end_anchor import EndAnchor
from anchor.trajectory.wind import WindSeries, wind_at
STATIONARY_QUIET_VEDBA_G = 0.03
STATIONARY_MIN_SPAN_MIN = 60.0
STATIONARY_BIN_S = 60.0
STATIONARY_GRAVITY_LOWPASS_S = 2.0
OUT_OF_WATER_DEPTH_M = 0.05
OUT_OF_WATER_WARMING_C = 1.0
OUT_OF_WATER_WINDOW_MIN = 60.0
OUT_OF_WATER_MIN_MINUTES = 30.0

@dataclass(frozen=True)
class TerminalDrySpan:
    """The record's closing dry span, and whether it was air or water.

    ``label`` is ``"out_of_water"`` or ``"surface"`` — the two things a depth
    channel reading zero to the end of the record can be. ``basis`` says which
    channels decided it: ``"depth+temperature"`` when the temperature test ran,
    ``"depth"`` when there was no temperature channel to run it on. A
    ``"depth"`` basis is never promoted to a positive out-of-water finding by
    anything downstream — see
    :func:`anchor.trajectory.end_anchor.resolve_end_anchor_model`.

    ``at_water_prefix_min`` is the leading run of the dry span whose running
    median has not yet reached ``pre_wet_median_temp_c + warming_c``. It is
    **measured and reported, never thresholded**: a genuine float has one, and
    so does a tag warming up on a deck (32 min on ``BR_260318_S3``), and
    no record in the repository provides a float to size the separation
    against. It is the quantity a float guard would need, recorded so that a
    later pass with a float in hand has it (§19.3.2).
    """
    label: str
    start_min: int
    minutes: int
    basis: str

    def to_dict(self) -> dict:
        ...

def classify_terminal_dry_span(minute_depth_m, minute_temp_c=None, *, first_wet_min: int=0, depth_max_m: float=OUT_OF_WATER_DEPTH_M, warming_c: float=OUT_OF_WATER_WARMING_C, window_min: float=OUT_OF_WATER_WINDOW_MIN, min_minutes: float=OUT_OF_WATER_MIN_MINUTES) -> Optional[TerminalDrySpan]:
    """Air or water, for the run of dry minutes that closes a record.

    Both arguments are per-minute medians on the same grid —
    :attr:`StationaryOnset.minute_depth_median_m` and
    :attr:`StationaryOnset.minute_temp_c`.

    The rule:

    * the closing run of minutes whose median depth is below ``depth_max_m``
      is the **dry span**; a run shorter than ``min_minutes`` is a surface
      excursion and None is returned;
    * the dry span is **out of the water** when its median temperature exceeds
      the median over the ``window_min`` wet minutes immediately before it by
      at least ``warming_c``, and is a **surface** float when it does not;
    * with no temperature channel the span is reported as ``out_of_water`` on
      ``basis="depth"``, which is what the depth channel alone has always said
      and is not evidence that the tag left the water.

    The window is clipped at ``first_wet_min`` so a deck head before the
    release — which is also dry, and also warm — never becomes the water the
    contrast is measured against.
    """
    ...

def _box_lowpass(a: np.ndarray, width: int) -> np.ndarray:
    """Centred moving average along axis 0, edge-clamped, via a cumulative sum.

    Ported from ``anchor.ingest.mag_inflight._box_lowpass`` (and identical to
    ``scripts/attitude_mode.box_mean``) rather than imported, so that a library
    module does not depend on a script and the three cannot drift: the port is
    pinned by ``test_stationary_lowpass_matches_mag_inflight``.

    Edge-clamped rather than zero-padded: a zero-padded mean at the ends would
    pull the gravity direction toward the origin and make the first and last
    seconds of every record look like free fall.
    """
    ...

def dynamic_acceleration_norm(acc: np.ndarray, fs: float, *, lowpass_s: float=STATIONARY_GRAVITY_LOWPASS_S) -> np.ndarray:
    """``‖a - static‖`` per sample, in g, under the 2 s box low pass.

    ``static`` is the low-passed accelerometer resolved back onto its own
    direction — ``unit * ‖static‖`` — which is how ``attitude_mode``
    computes it, so the number this returns is the one §17.4.2's table
    quotes. Rows whose static vector has no direction (a low-passed norm at
    machine zero, i.e. genuine free fall) come back NaN rather than as a
    division by zero.
    """
    ...

@dataclass(frozen=True)
class StationarySpan:
    """One run of quiet minutes long enough to be called stationary."""
    start_min: int
    end_min: int
    minutes: int

    @property
    def start_s(self) -> float:
        ...

    @property
    def end_s(self) -> float:
        ...

    def to_dict(self) -> dict:
        ...

@dataclass
class StationaryOnset:
    """Result of :func:`detect_stationary_onset`.

    ``onset_s`` is the start of the *earliest* qualifying span, in seconds
    from the record start, and is the moment the record stops being an animal
    record under §17.4.2's rule. The per-minute series are carried so a caller
    can plot or re-threshold them without re-reading the accelerometer.
    """
    onset_s: Optional[float]
    end_s: Optional[float]
    minutes: float
    spans: list[StationarySpan]
    n_minutes: int
    fs_hz: float
    bin_seconds: float
    quiet_threshold_g: float
    min_span_minutes: float
    frac_quiet_minutes: float
    minute_vedba_g: np.ndarray
    minute_depth_median_m: np.ndarray
    first_wet_s: Optional[float] = None
    out_of_water_s: Optional[float] = None
    terminal_dry: Optional[TerminalDrySpan] = None

    def __bool__(self) -> bool:
        ...

    def span_before(self, t_s: float, *, not_before_s: Optional[float]=None) -> Optional[StationarySpan]:
        """The earliest qualifying span that begins before ``t_s``.

        Every span in ``spans`` already clears ``min_span_minutes``, so
        "begins before the water exit and lasts at least an hour" is this
        test and nothing more. Earliest rather than longest: the claim being
        made is "the record stops being an animal record here", and the first
        hour of stillness is the first moment that claim is supportable.

        ``not_before_s`` drops spans that begin before it — in practice
        :attr:`first_wet_s`, so an hour of stillness on the deck before the
        release is not read as an animal that stopped. Without that bound a
        deck head longer than the span floor is returned as the earliest span,
        and the caller's "index 0" guard then disables the rule altogether
        while a genuine in-water span later in the record is never considered.
        """
        ...

    def to_dict(self) -> dict:
        """JSON-safe summary. The per-minute series are deliberately absent —
        they are 1 244 floats on the flagship and belong in a figure."""
        ...

def _run_lengths(mask: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """``(starts, lengths)`` of the True runs in a 1-D boolean mask."""
    ...

def detect_stationary_onset(acc: np.ndarray, fs: float, *, depth: Optional[np.ndarray]=None, temp_c: Optional[np.ndarray]=None, quiet_threshold_g: float=STATIONARY_QUIET_VEDBA_G, min_span_minutes: float=STATIONARY_MIN_SPAN_MIN, bin_seconds: float=STATIONARY_BIN_S, lowpass_s: float=STATIONARY_GRAVITY_LOWPASS_S) -> StationaryOnset:
    """Find where a record stops being an animal record (§17.4.2's rule).

    The rule, and every constant in it, is fixed:

    * a one-minute window whose **median** dynamic-acceleration norm
      ``‖a - lowpass_2s(a)‖`` is below :data:`STATIONARY_QUIET_VEDBA_G`
      (0.030 g) is a **quiet** minute;
    * a run of at least :data:`STATIONARY_MIN_SPAN_MIN` (60) quiet minutes is
      a **stationary span** — a tag that is not on a moving animal;
    * when ``depth`` is supplied, the run of minutes whose per-minute depth
      median is under :data:`OUT_OF_WATER_DEPTH_M` and which closes the record
      is the **terminal dry span**, and its start is reported separately;
    * when ``temp_c`` is supplied too, that span is classified as air or water
      by :func:`classify_terminal_dry_span` — a depth channel reading zero
      cannot tell a tag floating from a tag in a boat, and a tag in a boat is
      not drifting anywhere.

    The median rather than the mean because a single handling transient inside
    an otherwise dead minute would drag a mean over the threshold; the length
    floor because an animal glides. Both constants and the 2 s low pass are
    ``scripts/attitude_mode``'s, declared there before the rule was run on
    anything but ``BR_260318_S3`` and now defined here — that script's
    ``segment_record`` calls this function, so there is one implementation.

    ``acc`` is the raw tri-axial accelerometer in g at ``fs`` Hz, i.e. the
    ``accX``/``accY``/``accZ`` columns of ``data/interim/<id>.parquet``, NOT
    the 1 Hz trajectory track (which carries no accelerometer). ``depth``, if
    given, is on the same grid.

    This function does not decide anything about detachment: a tag that
    stopped moving may have come off the animal or may be riding an animal
    that has stopped, and §17.4.2 records that the channels cannot separate
    the two. What it decides is that the span is not an animal record.
    """
    ...

@dataclass(frozen=True)
class RecordRegime:
    """One row of the record's regime table (§17.4.2's three-records table).

    ``t_start_idx`` / ``t_end_idx`` are indices on the TRACK grid the filter
    runs on, so the driver can slice with them directly.
    """
    label: str
    t_start_idx: int
    t_end_idx: int
    hours: float

    def to_dict(self) -> dict:
        ...

def record_regimes(onset: Optional[StationaryOnset], *, n: int, base_hz: float, surface_idx: Optional[int]=None, stationary_idx: Optional[int]=None) -> list[RecordRegime]:
    """The record's regime table: deck / moving / stationary-wet / surface /
    out-of-water, with hours, on the track's own index grid.

    ``surface_idx`` is where the water-exit rule cut (``detect_tag_detachment``
    and friends); ``stationary_idx`` is where the tag stopped moving, if it
    did. Rows of zero length are dropped, so a record with no stationary span
    yields the three rows it actually has and a record with no depth channel
    yields one ``moving`` row spanning everything.

    Boundaries in seconds are converted at ``base_hz`` and clipped into
    ``[0, n]``, so a table built for a track shorter than the accelerometer it
    was measured on stays inside the track.
    """
    ...

@dataclass
class DetachmentResult:
    """Diagnostic about tag-detachment detection.

    ``t_detach_idx`` is where the track is cut, and which rule put it there is
    ``rule``. The two candidate moments are carried side by side and neither
    is derived from the other: ``surface_idx`` is the water exit, from the
    depth channel; ``stationary_onset_idx`` is where the tag stopped moving,
    from the accelerometer (:func:`detect_stationary_onset`). On
    ``BR_260318_S3`` they are 16.942 h and 9.333 h — 7.617 h apart, which is
    44.9 % of what the water-exit rule calls attached (§17.4.2).
    """
    t_detach_idx: Optional[int]
    t_detach_s: Optional[float]
    sustained_minutes: float
    threshold_m: float
    pct_attached: float
    final_depth_median_m: float
    surface_idx: Optional[int] = None
    stationary_onset_idx: Optional[int] = None
    stationary_minutes: float = 0.0

    def __bool__(self) -> bool:
        ...

    def regime_table(self) -> list[dict]:
        ...

    def to_dict(self) -> dict:
        """JSON-safe summary for the parquet footer and the ledger card."""
        ...

def detect_tag_detachment(track, *, depth_threshold_m: float=0.2, sustained_min: float=10.0) -> DetachmentResult:
    """Detect the moment the tag transitioned to surface-float regime.

    Positively buoyant tags (e.g. AXY-5 with float collar) only have
    one post-detachment state: surface bobbing + leeway drift. The
    detection signature is therefore depth → 0 sustained for the
    remainder of the deployment.

    Walks the depth channel from the END backward; if the last
    ``sustained_min`` minutes are all below ``depth_threshold_m`` we
    have a detachment. Then backs up to find the LAST sample above
    threshold — that's the detachment moment (the next sample is when
    the tag has surfaced).

    For higher-confidence detection on noisy data, see
    ``detect_tag_detachment_multichannel`` which combines depth +
    VEDBA collapse + roll variance per Whitney et al. 2016
    (*Fish. Res.* 183: 210). The single-channel rule here is
    sufficient for the textbook case (clean depth → 0 within seconds).

    Returns ``DetachmentResult`` with ``t_detach_idx = None`` if no
    sustained-near-surface period was detected (e.g. tag stayed
    attached the full deployment).
    """
    ...

def detect_tag_detachment_multichannel(track, *, depth_threshold_m: float=0.5, vedba_quantile: float=0.01, roll_variance_floor: float=0.05, sustained_min: float=10.0) -> DetachmentResult:
    """Multi-channel detachment detection (Whitney et al. 2016) with
    depth-only fallback.

    Combines three signatures, all sustained for ≥ ``sustained_min`` min:

    1. **Depth < ``depth_threshold_m``** — tag has surfaced. The 0.5 m
       default (vs 0.2 m for depth-only) is more lenient because the
       multi-channel rule has redundancy.
    2. **VEDBA below the lower ``vedba_quantile``** of the attached-
       period values — tag is no longer reading biological motion.
    3. **Roll variance > ``roll_variance_floor``** — a clamped tag
       holds stable mean roll; once free + tumbling it doesn't.

    All three must hold sustained from t_detach to deployment end. When
    that strict rule fires, you get a high-precision detection. When it
    doesn't fire — common on deployments where:

      - the tag bobs in surf and the tailbeat-FFT picks up wave-induced
        oscillation that looks like swimming (motion-low never holds),
      - or the post-detach period is mostly calm/grounded so roll
        variance never spikes (roll-high never holds),

    we fall back to ``detect_tag_detachment`` (depth alone). The
    fallback result is annotated in ``notes`` so the caller knows
    multichannel didn't agree but a result was produced.

    Reference
    ---------
    Whitney, N.M. et al. 2016. *A novel method for determining post-
    release mortality, behavior, and recovery period using
    acceleration data loggers.* Fish. Res. 183: 210–221.
    """
    ...

def _interim_accel_and_depth(deployment_id, cfg=None, interim_dir='data/interim'):
    """``(acc, depth, temp_c, fs_hi)`` from ``data/interim/<id>.parquet``, or None.

    Same cache discipline as :func:`detect_post_detach_regimes`: calibration is
    baked into that parquet at write time and the analysis window is applied
    before it, so a parquet written from a different config carries the wrong
    accelerations on the wrong rows. Without ``cfg`` the cache cannot be keyed
    and is used with a warning; a stale one is skipped, and the caller then has
    no accelerometer and falls back to the water-exit rule.

    ``fs_hi`` comes from ``cfg.sampling_rate_hz`` when a config is to hand and
    is otherwise left to the caller to supply: guessing a sampling rate would
    put the 60 s bin at the wrong width and silently move the threshold.
    """
    ...

def stationary_onset_for_track(track, *, cfg=None, fs_hi: Optional[float]=None, interim_dir: str='data/interim', **kwargs) -> Optional[StationaryOnset]:
    """:func:`detect_stationary_onset` on a track's high-rate accelerometer.

    The 1 Hz trajectory track carries no accelerometer, so the rule is run on
    ``data/interim/<track.deployment_id>.parquet`` — the same file
    :func:`detect_post_detach_regimes` reads, under the same cache-validity
    rule. Returns None (never a false negative dressed as a result) when the
    record cannot be read: no ``deployment_id``, no valid parquet, no accel
    columns, or no sampling rate to bin it at.

    The returned onset's times are in seconds from the record start, which is
    the track's own time base, so ``round(onset_s * track.base_hz)`` is a
    track index.
    """
    ...

def detect_detachment(track, *, method: str='multichannel', rule: DetachRule='stationary', cfg=None, onset: Optional[StationaryOnset]=None, depth_threshold_m: Optional[float]=None, sustained_min: float=10.0, vedba_quantile: float=0.01, roll_variance_floor: float=0.05, interim_dir: str='data/interim') -> DetachmentResult:
    """Both rules, reported together; ``rule`` decides which one cuts the track.

    Runs the water-exit detector (``method`` selects
    :func:`detect_tag_detachment_multichannel` or the depth-only
    :func:`detect_tag_detachment`) and, independently,
    :func:`detect_stationary_onset` on the deployment's high-rate
    accelerometer. Both moments are reported on the result whichever rule
    wins, together with the record's regime table.

    ``rule="stationary"`` (the default) cuts the attached span at the earliest
    stationary span that begins before the water exit — the moment the record
    stops being an animal record. ``rule="surface"`` reproduces the shipped
    behaviour exactly: it cuts at the water exit and leaves the stationary
    fields as disclosure. The choice is a
    :class:`~anchor.ingest.config.TrajectoryConfig` field
    (``detach_rule``) so the run's effective config hash sees it.

    When no accelerometer is available the stationary fields come back empty
    and the result is the water-exit rule's, unchanged and so annotated: a
    rule that cannot run must not read as a rule that found nothing.
    """
    ...
DEFAULT_ACTIVE_VEDBA_G = 0.025
DEFAULT_GROUNDED_VEDBA_G = 0.005

@dataclass
class PostDetachRegime:
    """One contiguous post-detachment regime segment."""
    t_start_idx: int
    t_end_idx: int
    label: str
    leeway_factor: float
    median_vedba_g: float

def detect_post_detach_regimes(track, *, detach_idx: int, bin_seconds: float=60.0, active_threshold_g: float=DEFAULT_ACTIVE_VEDBA_G, grounded_threshold_g: float=DEFAULT_GROUNDED_VEDBA_G, grounded_until_idx: Optional[int]=None, cfg=None) -> list[PostDetachRegime]:
    """Segment the post-detachment period into {active, calm, grounded}
    regimes based on VEDBA bins.

    Decision rule per bin:
        VEDBA > active_threshold_g          → "active"   (leeway 1.0)
        grounded_threshold_g < VEDBA ≤ active_threshold_g → "calm" (0.3)
        VEDBA ≤ grounded_threshold_g        → "grounded" (0.0)

    Adjacent same-label bins merge into one segment.

    ``grounded_until_idx`` forces every bin that ends at or before that
    (track-grid) index to "grounded", leeway 0.0, whatever its VEDBA reads.
    It exists for the stationary rule (``detach_rule="stationary"``), which
    cuts the track where the tag stopped moving rather than where it surfaced
    and so hands this function hours of tag-on-the-bottom to segment. The bin
    rule above mislabels exactly that stretch: on ``BR_260318_S3`` it calls
    446 of the 457 stationary minutes "calm" — leeway 0.3 — because
    ``|‖a‖ - 1|`` reads 0.0103 g there, above
    :data:`DEFAULT_GROUNDED_VEDBA_G`, and 0.3 x the tidal current for 7.6 h
    would carry the back-propagated cloud across the slough. The stationary
    rule's own evidence is the stronger statement: the per-window depth
    standard deviation over that span is 4 mm and the depth traces half a
    tide as a smooth arc (§17.4.2), which is a pressure sensor that is not
    being advected anywhere. So the span is pinned, and the pin is recorded
    in the regime list rather than applied silently downstream.

    Requires high-rate tri-axial accel from the *cached interim parquet*
    (``data/interim/<deployment_id>.parquet``) to compute VEDBA. When
    that isn't available the function returns ``[]`` — "no regime
    information" — and callers fall back to an unmodulated leeway σ
    (``leeway_factor`` 1.0 everywhere), which is the conservative
    choice.

    Pass ``cfg`` (the deployment's ``DeploymentConfig``) to have the cache
    checked against it with :func:`anchor.ingest.io.interim_cache_is_valid`:
    calibration is baked into that parquet at write time and the analysis
    window is applied before it, so a parquet written from a different config
    carries the wrong VEDBA on the wrong rows. A stale parquet is skipped, which
    lands on the same conservative "no regimes" fallback. Without ``cfg`` the
    cache cannot be keyed, so it is used with a warning rather than silently
    disabling regime detection for callers that have no config to hand.

    There is deliberately no low-rate substitute. ``tailbeat_freq_hz``
    was previously used as a stand-in, but it is a frequency in Hz and
    the thresholds above are accelerations in g: a quiescent tag bobbing
    at 0.3 Hz scores far above ``active_threshold_g`` = 0.025, so every
    bin read "active" and the regime narrowing never fired. No published
    mapping from tailbeat frequency to a VEDBA-equivalent surface-state
    threshold exists for this tag class, so we report no regimes rather
    than invent one.
    """
    ...

@dataclass(frozen=True)
class LeewayParams:
    """Allen & Plourde 1999 / Breivik et al. 2011 leeway parameters.

    Defaults are PIW-horizontal/face-up class (Allen 2005, MET Norway
    17/2010): a positively-buoyant body half-emergent in water, no sail.
    AXY-5 + float collar fits this category much better than the
    "unmodified buoyant float" class which assumes a near-spherical
    object exposing more freeboard.

    The drift vector is decomposed into a downwind (DWL) component
    along the wind direction and a crosswind (CWL) component
    perpendicular to it, deflected by ``divergence_deg``. CWL is signed
    per particle and stochastically flips sign at the Bernoulli rate
    ``jibing_rate_per_hr`` — capturing the physical "jibing" behavior
    where a buoyant object alternately tracks left and right of the
    downwind axis.
    """
    dwl_slope: float = 0.0165
    cwl_slope: float = 0.0055
    divergence_deg: float = 18.0
    jibing_rate_per_hr: float = 0.04

    @classmethod
    def scalar(cls, coeff: float) -> 'LeewayParams':
        """Backward-compat: collapse to scalar downwind-only.

        Reproduces the legacy ``surface_drift = coeff * W_10`` exactly
        (no CWL, no divergence, no jibing).
        """
        ...

def estimate_detachment_position(track, recovery_anchor: EndAnchor, t_detach_idx: int, *, tide_series=None, current_field=None, surface_current_scale: float=1.5, n_particles: int=5000, process_noise_xy_m_per_sqrt_s: float=1.5, wind_drift_sigma_m_per_hr: float=200.0, wind_series: WindSeries | None=None, wind_drift_coeff: float | LeewayParams=0.025, regimes: list[PostDetachRegime] | None=None, seed: int=0) -> EndAnchor:
    """Back-propagate the recovery point through surface-drift dynamics
    to estimate where the tag detached — i.e., the bat ray's actual
    deployment endpoint.

    Surface drift over the float interval (t_detach, t_recovery) has
    several uncertain components:

      - **Tidal advection** at the surface ≈ ``surface_current_scale``
        × subsurface tidal current (surface currents typically
        exceed near-bottom by ~50 % at Elkhorn channel).
      - **Wind drag** ≈ ``wind_drift_coeff`` × wind speed (Allen 1999
        leeway, default 2.5 % for unmodified buoyant float). When
        ``wind_series`` is supplied the *mean* drift is modelled
        deterministically: the per-step drift is
        ``wind_drift_coeff × W_10(t)``, resolved into downwind and
        crosswind components. When it isn't, the mean drift is zero.
        Either way the ``wind_drift_sigma_m_per_hr × √float_hours``
        Gaussian budget is carried in quadrature with the process
        noise: it is the *uncertainty* in the leeway slopes, which
        knowing ``W_10`` does not remove. Only the mean drift is
        informed by a wind series, never the spread.
      - **Random walk / sub-grid eddies**: standard process-noise term
        with σ growing as ``process_noise_xy_m_per_sqrt_s × √dt``.
      - **Regime-dependent activity**: if ``regimes`` is supplied
        (output of ``detect_post_detach_regimes``), the per-step
        leeway σ is multiplied by the regime's ``leeway_factor`` —
        grounded segments contribute zero σ, calm segments contribute
        reduced σ, active segments contribute full σ. This produces a
        meaningfully tighter detachment-position estimate when the
        tag spent part of the float beached or sheltered.

    We propagate ``n_particles`` from the recovery point, advected
    backward in time over the float duration. The resulting cloud's
    mean and *per-axis* 1σ become the EndAnchor used at t_detach
    (per-axis because that is the convention ``EndAnchor.sigma_m``
    follows; see its docstring).
    """
    ...
