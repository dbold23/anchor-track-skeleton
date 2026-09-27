"""Sequential Monte Carlo particle filter for shark trajectory reconstruction.

State (per design doc §5.3):
    x_t = (x, y, ψ_bias, k_speed)
    - x, y       : position in raster-native CRS (UTM 16S meters)
    - ψ_bias     : magnetometer heading bias (rad). Slow random walk;
                   absorbs animal-mounted mag distortion + residual declination.
    - k_speed    : multiplicative speed scale. Slow random walk;
                   absorbs TBF→U calibration error.

Inputs at each timestep (treated as observations of *raw* heading/speed):
    heading_rad : tilt-compensated mag heading (rad). Effective heading
                  used in dynamics is heading_rad + ψ_bias.
    speed_mps   : raw speed proxy (m/s). Effective speed is k_speed * speed_mps.
    depth_m     : observed depth from pressure tag.

Optional observations:
    vps_xy      : (x, y) acoustic fix in raster CRS, when available
    vps_sigma_m : 1σ horizontal uncertainty (1 + 0.2·HPE per Smith 2013)

Likelihoods:
    VPS:        bivariate Gaussian on (x, y).
    Bathymetry: penalty when observed depth > bathy(x, y) (BathyLookup helper).

If you don't want to estimate bias/scale, set the corresponding _walk_std and
_init_std to 0.0 — particles stay frozen at (0, 1) and the filter degenerates
to the (x, y)-only case.

Smoother is a separate pass on the saved history (see ffbs_smoother below).
"""
from __future__ import annotations
import logging
from dataclasses import dataclass
from typing import Optional
import numpy as np
from anchor.trajectory.bathymetry import BathyLookup
from anchor.trajectory.polygon_constraint import PolygonConstraint
from anchor.trajectory.release_anchor import ReleaseAnchor
SX, SY, SBIAS, SSCALE = (0, 1, 2, 3)
STATE_DIM = 4
POLYGON_PENALTY_NATS = 800.0
DEFAULT_POLYGON_PROPOSAL_DRAWS = 8
DEFAULT_POLYGON_SOFT_WIDTH_M = 20.0

@dataclass
class FilterConfig:
    n_particles: int = 5000
    process_noise_xy_m: float = 5.0
    bathymetry_extra_sigma_m: float = 1.0
    bathymetry_off_bottom_factor: float = 1.0
    bathymetry_tide_term: bool = True
    resample_threshold: float = 0.5
    rng_seed: int = 0
    init_speed_std: float = 0.2
    bias_walk_std_rad_per_s: float = 0.0
    speed_walk_std_per_s: float = 0.0
    speed_min: float = 0.5
    speed_max: float = 1.8
    enable_bathymetry_constraint: bool = True
    enable_polygon_constraint: bool = False

class ParticleFilter:

    def __init__(self, bathy: Optional[BathyLookup], config: FilterConfig, polygon: Optional[PolygonConstraint]=None):
        ...

    def initialize(self, x0: tuple[float, float], x0_std: tuple[float, float]=(20.0, 20.0)) -> None:
        ...

    def predict(self, dt_s: float, heading_rad: float, speed_mps: float, current_uv: tuple[float, float]=(0.0, 0.0), process_noise_xy_m: Optional[float]=None, direction: int=1, tide_m_mllw: float | None=None) -> None:
        """Step dynamics.

        ``direction = 1`` runs forward in time (default).
        ``direction = -1`` runs in reverse — used by the backward leg of
        the two-filter smoother. The animal's velocity at observation
        time t propelled it from x_{t-1} to x_t; running backward, we
        subtract the same displacement to recover x_{t-1} from x_t.
        Process-noise variance is unaffected (random walk magnitude is
        symmetric in time).

        ``tide_m_mllw`` is used only under
        ``polygon_mode="in_water_proposal"``, where the position innovation is
        drawn from the transition kernel restricted to the wet mask at that
        tide level (:meth:`propose_in_water`). Under the default
        ``"indicator"`` mode it is ignored and this method draws exactly the
        random numbers, in exactly the order, that it always did.
        """
        ...

    def propose_in_water(self, dx: np.ndarray, dy: np.ndarray, sig_xy: float, *, tide_m_mllw: float | None=None) -> dict:
        """Draw the position innovation from the transition restricted to water.

        **The proposal.** The bootstrap filter proposes from the transition
        density itself, ``q_i(x) = f(x | x_i) = N(x; mu_i, sigma^2 I)`` with
        ``mu_i = x_i + (drift)``, and the incremental weight is then the
        likelihood alone. Here the proposal is that density *conditioned on the
        water*::

            q'_i(x) = q_i(x) . 1[x in W] / Z_i,
            Z_i     = integral over W of q_i = P_q(x in W | particle i),

        so the incremental weight has to carry the normaliser back::

            f(x | x_i) . 1[x in W] . g(x) / q'_i(x) = Z_i . g(x),

        i.e. **log w += log Z_i**, and the indicator is no longer evaluated at
        the drawn point — it has been absorbed into where the point was drawn
        from. The target is unchanged: what the indicator model integrates at a
        step is ``integral of q_i(x) 1[x in W] g(x) dx``, and that is exactly
        what ``Z_i . g(x)`` estimates.

        **The estimator, and why it is exact rather than approximate.** ``Z_i``
        is not available in closed form (it is a Gaussian integral over a
        rasterised, tide-dependent mask), so it is estimated from ``M =
        polygon_proposal_draws`` trial innovations: ``Zhat_i = k_i / M`` with
        ``k_i`` the number of trials that landed in water. The particle keeps
        one draw chosen **uniformly among the accepted trials**. That pairing —
        and not the obvious "first accepted draw, count the rest" — is what
        makes the scheme exact. For any test function ``h``, writing the choice
        as uniform over the ``k`` accepted trials,

            E[ Zhat . h(x) ] = E[ (k/M) . (1/k) . sum over accepted h(x^m) ]
                             = (1/M) . E[ sum over all m of h(x^m) 1[x^m in W] ]
                             = E[ h(x^1) 1[x^1 in W] ]
                             = Z_i . E_{q'}[h],

        with the ``k = 0`` event contributing zero to both sides. So the pair
        ``(Zhat_i, x_i)`` is a *properly weighted* sample for ``q'_i`` with
        normaliser ``Z_i``, and taking ``h = g`` (this step's remaining
        likelihood, the depth term included) gives an incremental weight whose
        expectation is the indicator model's own incremental weight, exactly.
        No Jensen correction is needed and none is applied: the correction
        enters the weight multiplicatively as ``Zhat``, and it is ``Zhat`` and
        not ``log Zhat`` that has to be unbiased for the SMC marginal to be —
        this is the standard random-weight / pseudo-marginal argument (Fearnhead,
        Papaspiliopoulos & Roberts 2008; Andrieu & Roberts 2009), used here in
        the one case where it is available in closed form.

        Two honest caveats, both stated rather than buried:

        * **``k = 0``.** A particle none of whose ``M`` trials found water
          keeps its first trial draw and is charged ``polygon_penalty_nats``,
          per the exactness argument's own ``Zhat = 0``. At the shipped 800
          nats ``exp(-800)`` is exactly 0.0 in IEEE double, so the fallback is
          bit-for-bit the zero weight the argument requires; it exists only so
          the log marginal stays finite, for the reason
          ``docs/regen_2026-09.md`` section 12.4 gives.
        * **Variance, not bias, is what M buys.** ``Zhat`` has relative
          variance ``(1 - Z) / (M Z)``, so a particle deep in the channel
          (``Z = 1``) carries no estimator noise at all and one on a shoreline
          carries the most. Small ``M`` costs precision, never correctness.

        Returns the per-step statistics it also stores on
        ``self._pending_proposal``; the weight correction is applied by the
        :meth:`apply_polygon_constraint` call that must follow.
        """
        ...

    def update_vps(self, vps_xy: tuple[float, float], vps_sigma_m: float) -> None:
        ...

    def update_bathymetry(self, observed_depth_m: float, tide_m_mllw: float | None=None) -> None:
        """Reweight by the depth likelihood at this step.

        ``tide_m_mllw`` is the water level above MLLW, the same scalar
        :meth:`apply_polygon_constraint` takes, and it is what puts the tag's
        pressure depth (below the instantaneous surface) and the raster's bed
        depth (below MLLW) on one datum: see
        :meth:`BathyLookup.bathymetry_violation_logpdf`. ``None`` — the default,
        and what a deployment with no tide series supplies — means η = 0, the
        MLLW comparison. ``FilterConfig.bathymetry_tide_term=False`` discards a
        tide that *is* supplied, which reproduces the pre-2026-09-07 arithmetic
        bit for bit.
        """
        ...

    def apply_polygon_constraint(self, tide_m_mllw: float | None=None) -> bool:
        """Penalise out-of-polygon particles. Returns True if *all* were.

        ``tide_m_mllw`` is forwarded to ``polygon.is_inside``. For a static
        ``PolygonConstraint`` it's ignored; for a ``TidalPolygonConstraint``
        it picks the nearest precomputed wet-mask level.

        **Why a finite penalty and not -inf.** A hard rejection is the right
        model — the animal is in water — but it is not a number. When the whole
        cloud is outside, every log-weight is ``-inf``, the log mean weight is
        ``-inf``, and the accumulated log marginal likelihood is destroyed; the
        filter's standing fallback then reset the weights to uniform and the
        marginal simply *skipped* the step, contributing 0. Zero is larger than
        the negative number an honest likelihood would supply, so the omission
        credited whichever grid node leaned on the fallback hardest
        (``docs/regen_2026-09.md`` §12.4). Subtracting a large finite
        ``polygon_penalty_nats`` instead keeps the step scored: the cloud pays
        one penalty and the marginal moves by that much.

        **Why 800 nats.** ``exp(-745.2)`` is already exactly 0.0 in IEEE
        double, so a penalised particle's *normalised* weight is exactly zero —
        bit for bit what ``-inf`` gave — unless it was more than ~55 nats
        better than every unpenalised particle before the penalty. The
        posterior mean, the resampling indices, the ESS, ``var(log w)`` and the
        §3.7 diagnostics are therefore the hard constraint's, while the
        marginal becomes finite. It is a modelling choice (a soft polygon with
        penalty ``c``) and it is applied identically at every grid node, which
        is what makes the nodes' marginals comparable.

        **Effect on the ESS.** When only some particles are outside, nothing
        changes: their normalised weight underflows to zero exactly as before.
        When *all* are outside, the penalty is a constant added to every
        log-weight, so the relative weights — and hence the ESS — are the ones
        the cloud already had, instead of being reset to a spurious ``ESS = N``
        by the uniform fallback. That is strictly more informative: the step
        no longer erases the cloud's weighting.

        **The two non-default modes.** ``polygon_mode="in_water_proposal"``
        replaces the indicator evaluated at the drawn point by the proposal
        normaliser ``log Zhat`` computed in :meth:`propose_in_water`, which
        targets the same distribution and bounds the per-step charge at
        ``-log M``; this method then only *applies* the correction the predict
        step computed, so the two must be called in that order — a second
        ``predict`` with a correction still outstanding raises rather than
        dropping it. ``polygon_mode="soft"`` replaces the indicator
        by a smooth function of the distance to water and is a **model change**
        — the animal may be within a cell width of the shoreline as the raster
        sees it, and under the soft mode the posterior says so. Neither is the
        shipped path and neither is reachable without asking for it.
        """
        ...

    def _polygon_penalty_log(self) -> float:
        """The log-weight an out-of-water particle is charged: finite, or -inf."""
        ...

    def _apply_in_water_proposal_weight(self) -> bool:
        """Charge the pending proposal's ``log Zhat`` and clear it.

        The correction is bounded below by ``-log M`` for every particle that
        found water at all, which is 2.08 nats at the default ``M = 8`` — the
        whole point of the mode. Particles that found none are charged the
        indicator's penalty (:meth:`propose_in_water` says why that is exactly
        the estimator's own zero weight).
        """
        ...

    def _apply_soft_shoreline(self, tide_m_mllw: float | None) -> bool:
        """Charge ``0.5 (d / width)^2`` nats, capped at the indicator's penalty.

        ``d`` is the distance from the particle to the nearest wet cell of the
        mask at this tide level, so a particle in the water pays nothing and
        one a metre outside pays almost nothing. The cap is what makes the
        width -> 0 limit *exactly* the indicator: as the width shrinks every
        outside particle saturates at ``polygon_penalty_nats`` and every inside
        particle stays at zero, which is the shipped partition, weight for
        weight. A point off the raster has no measured distance and is charged
        the cap directly.
        """
        ...

    def update_release_anchor(self, anchor: ReleaseAnchor) -> None:
        """Single-fix Gaussian likelihood at the release point. Call once at t=0."""
        ...

    def effective_sample_size(self) -> float:
        ...

    def _record_collapse(self, step: Optional[int], reason: str, *, hard_rejection: bool=False) -> None:
        """Count and log a total-weight collapse recovered from by reset.

        Resetting to uniform weights is a survival hack, not an inference
        step: the posterior at such a step is the *prior* propagated by the
        dynamics, with every observation at that step silently discarded. It
        used to happen without a trace; it is now counted, logged and exported
        per step so a run that leans on the hack is visible in diagnostics.

        ``hard_rejection`` separates the two ways it can happen. Under the
        default finite ``polygon_penalty_nats`` the constraint can no longer
        produce one, so what is left here is genuine numerical underflow — and
        the counts are kept apart so that is checkable rather than assumed.
        """
        ...

    def resample(self, step: Optional[int]=None) -> None:
        ...

    def maybe_resample(self, step: Optional[int]=None) -> bool:
        """Resample if ESS has fallen below the threshold.

        ``step`` is only used to name the step in the collapse warning; it
        does not affect the dynamics.
        """
        ...

    def snapshot(self) -> None:
        ...

    def normalized_weights(self) -> np.ndarray:
        ...

    def posterior_mean_cov(self) -> tuple[np.ndarray, np.ndarray]:
        ...

    def posterior_xy_mean_cov(self) -> tuple[np.ndarray, np.ndarray]:
        ...

    def posterior_bias_scale(self) -> tuple[float, float, float, float]:
        """Return (bias_mean, bias_std, scale_mean, scale_std)."""
        ...

def normalized_weights_from_log(log_weights: np.ndarray) -> np.ndarray:
    """Normalised weights from log-weights by log-sum-exp.

    Particles at ``-inf`` (the polygon's hard rejection) get exactly zero.
    Returns an all-zero array when every weight underflows — callers decide
    what an information-free step means; this function does not invent one.
    """
    ...

def weight_diagnostics(log_weights: np.ndarray) -> tuple[float, float, float]:
    """``(max normalised weight, ESS, var(log w))`` for one step's weights.

    All three are computed by log-sum-exp on the log-weights as they stand; no
    sigma is inflated and no floor is applied anywhere.

    ``var(log w)`` is taken over the particles that carry non-zero weight.
    Including the ``-inf`` ones would make it identically infinite on every
    step at which the polygon constraint rejects a single particle, which is
    essentially every step of a slough run, and would say nothing about
    weight degeneracy. Those particles are counted in ESS and in the maximum,
    which is where a hard rejection actually shows up.

    A step whose weights have collapsed entirely (all ``-inf``, or a total
    that underflows to zero) is reported as maximally degenerate:
    ``(1.0, 0.0, inf)``.
    """
    ...

def unique_founder_count(ancestry: np.ndarray, n_particles: int | None=None) -> int:
    """How many of the initial particles still have a descendant in the cloud.

    ``ancestry`` is the founder index carried by each live particle (see
    :meth:`ParticleFilter.resample`). ``bincount`` rather than ``unique``
    because this runs once per filter step on a 10^4-step record.
    """
    ...

def evaluate_degeneracy(*, n_particles: int, n_founders_per_step, max_weight_per_step, ess_per_step, var_log_w_per_step, label: str='', floors: dict[str, float] | None=None, n_polygon_all_rejected: int=0, polygon_penalty_nats: Optional[float]=POLYGON_PENALTY_NATS) -> dict:
    """Score a completed filter run against the §3.7 G-degeneracy floors.

    Emits one ``logging.warning`` per breached floor and returns the scalars
    plus a ``breaches`` list. ``passed`` False means *every calibration number
    in that run is suppressed* — the credible intervals stay in the report,
    marked, because deleting them hides which run produced them.

    ``n_polygon_all_rejected`` counts the steps at which the water polygon
    rejected the *entire* cloud. It is carried here, beside the five floors,
    but it is **not** a sixth floor: the §3.7 numbers are pre-registered and
    amending them takes a dated change to the design document. It is carried
    because it used to ride in on ``ess_min``. Under the hard ``-inf``
    constraint an all-rejected step reset the weights to uniform and recorded
    ESS = 0, so that floor breached; under the finite
    ``polygon_penalty_nats`` the penalty is a constant added to every
    log-weight, the normalised weights (and the ESS) are unchanged, and the
    floor is silent — rightly, because a constant says nothing about *which*
    particle, but that would leave "the cloud left the water" unsaid. So it is
    said here, warned about, and printed on the report.

    The returned dict is a superset of
    ``anchor.validation.ledger.gates.DEGENERACY_KEYS``, so the ledger can
    re-score the same numbers for the versioned score card without the filter
    and the ledger having to agree on anything but the names.
    """
    ...

def end_anchor_binding_check(particles: np.ndarray, log_weights: np.ndarray, end_anchor, *, no_op_tv: float=0.001, weak_binding_sigma: float=3.0, weak_binding_gap_closed: float=0.05, label: str='') -> dict:
    """Does the end anchor actually bind the terminal particle cloud?

    :func:`ffbs_smoother` starts its backward sweep from the terminal forward
    cloud reweighted by ``end_anchor.log_likelihood``. It never reports on
    that reweighting, and there are two ways for it to achieve nothing:

    * **A no-op.** The smoother forms the product ``w_fwd * exp(log_anchor -
      max)``; when every term in it underflows to zero its graceful fallback
      fires and backward sampling starts from the *forward* weights, exactly
      as if no anchor had been supplied. The same outcome, minus the
      underflow, is a kernel so flat across the cloud that the reweighted
      weights come back indistinguishable from the forward ones.
    * **Weak binding.** The reweighting does move weight around, but the
      anchor sits many sigma away and the cloud mean barely travels toward
      it: an anchor that cannot close the gap it exists to close. This is the
      flagship failure — a 4215 m, 24.2 sigma anchor that provably could not
      move the endpoint more than a couple of metres (design §2.4).

    The reweighting scored here is done by log-sum-exp, so unlike the
    smoother's product form it cannot underflow; the smoother's own
    arithmetic is reproduced *separately*, only to report whether its
    fallback would fire. No sigma is inflated anywhere.

    Returns the anchor distance in sigma units, the effective number of
    particles the reweighting retains, and the two flags, and warns on each.
    """
    ...

def end_anchor_log_evidence(particles, log_weights, end_anchor) -> float:
    """``log p(anchor | y_{1:T})`` under one terminal forward cloud.

    The forward filter never sees the end anchor: it is applied once, by
    :func:`ffbs_smoother`, to the terminal cloud that starts the backward
    sweep. So the anchor's contribution to the evidence for whatever produced
    that cloud is the particle estimate of

        ``p(anchor | y_{1:T}) = ∫ p(anchor | x_T) p(x_T | y_{1:T}) dx_T
                              ≈ Σ_i W_i · L_anchor(x_T^i)``

    with ``W`` the *normalised* terminal forward weights — the same cloud and
    the same reweighting :func:`end_anchor_binding_check` scores, and the same
    one :func:`ffbs_smoother` starts from. Returned as a log and computed by
    log-sum-exp, because on a real deployment the anchor can sit 20 σ away and
    every term underflows in linear space.

    This is the term that makes the outer grid's node weights comparable with
    the paths drawn inside a node: without it the mixture weight is
    ``p(node | y)`` while the within-node target is ``p(x | y, anchor, node)``,
    which is not the mixture ``Σ_j p(node j | y, anchor) p(x | y, anchor, j)``
    that the smoothed ensemble is claimed to sample.

    ``-inf`` means the anchor refutes this cloud outright (every particle's
    anchor log-likelihood underflowed to ``-inf``), which
    :func:`latent_posterior` turns into exactly zero posterior mass.
    """
    ...

def integrate_snapshot_intervals(snapshot_steps, dt_s: float, headings_rad: np.ndarray, speeds_mps: np.ndarray, current_uv_per_step: Optional[np.ndarray]=None) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Integrate the forward model over each snapshot interval, for FFBS.

    The forward filter runs at every step but only snapshots every
    ``snapshot_stride`` steps. :func:`ffbs_smoother` hops from snapshot ``t``
    to snapshot ``t + 1`` in a single backward-sampling kernel, so that kernel
    has to describe the *whole* interval, not one step of it.

    Over the steps ``k`` in an interval the forward :meth:`ParticleFilter.predict`
    accumulates, for a particle with heading bias ``b`` and speed scale ``s``::

        Δx = Σ_k (s·u_k·sin(ψ_k + b) + cu_k)·dt
        Δy = Σ_k (s·u_k·cos(ψ_k + b) + cv_k)·dt

    Both bias and scale are constant within an interval (their random walks
    are applied by ``predict`` too, but they are slow by construction), so the
    sums factor exactly:

        Δ = s·R(b)·S + C,
        S = Σ_k u_k·dt·(sin ψ_k, cos ψ_k),   C = Σ_k (cu_k, cv_k)·dt
        R(b)·S = (cos b·Sx + sin b·Sy,  cos b·Sy − sin b·Sx)

    which is what this function precomputes: ``S`` and ``C`` per interval, plus
    the interval duration. Process noise accumulates as a random walk, so the
    interval kernel σ is ``process_noise · sqrt(interval duration)``, which is
    exactly what passing the returned ``dts_s`` to :func:`ffbs_smoother` gives.

    Returns ``(dts_s, displacements, current_displacements)``, each indexed so
    that element ``t + 1`` describes the interval from snapshot ``t`` to
    snapshot ``t + 1`` — matching ``ffbs_smoother``'s ``[t + 1]`` indexing.
    Element 0 is unused padding.
    """
    ...

def integrate_snapshot_noise(snapshot_steps, dt_s: float, noise_sigma_per_step: np.ndarray) -> np.ndarray:
    """Accumulated xy process-noise variance over each snapshot interval.

    The forward :meth:`ParticleFilter.predict` draws an independent
    ``N(0, sigma_k^2 * dt)`` per axis at every step ``k``, with ``sigma_k`` the
    behaviour-dependent override when one is supplied. Over an interval the
    variances add, so the backward kernel's variance is ``sum_k sigma_k^2 * dt``,
    not ``sigma_const^2 * duration``. Indexed like
    :func:`integrate_snapshot_intervals`: element ``t + 1`` is the interval
    ``t -> t + 1`` and element 0 is unused padding.
    """
    ...

def ffbs_smoother(history_particles: list[np.ndarray], history_log_weights: list[np.ndarray], headings_obs: np.ndarray, speeds_obs: np.ndarray, dts_s: np.ndarray, process_noise_xy_m: float, n_smooth_samples: int=100, rng_seed: int=0, end_anchor=None, verified_positions=None, snapshot_steps=None, step_displacements: Optional[np.ndarray]=None, current_displacements: Optional[np.ndarray]=None, diagnostics: Optional[dict]=None, interval_noise_var_m2: Optional[np.ndarray]=None, bias_walk_std_rad_per_s: float=0.0, speed_walk_std_per_s: float=0.0) -> np.ndarray:
    """Forward-filter backward-sample smoother (Godsill, Doucet, West 2004).

    Returns smoothed trajectory samples with shape (T, K, STATE_DIM).
    Each k indexes one joint sample of (path, latent params); the per-time
    posterior at t is the empirical distribution over k.

    Why this matters: the forward filter's posterior at time t conditions only
    on data up to t. The smoother conditions on the *whole* sequence, so the
    posterior on heading bias / speed scale concentrates much faster as data
    refines static parameters from both directions.

    ``end_anchor`` (optional): an ``EndAnchor`` instance whose Gaussian
    log-likelihood is multiplied into the t=T particle weights *before*
    backward sampling begins. This is the bidirectional hook — when the
    deployment has a known recovery position, draw all backward samples
    from forward particles weighted toward that point. Robust against
    the marginal-particle KDE degeneracy that plagues two-filter
    smoothers.

    ``verified_positions`` + ``snapshot_steps`` are accepted for backward
    compatibility and deliberately ignored. The forward pass already applies
    every interior Verified Position (``ParticleFilter.update_vps``), so the
    forward weights and resampled positions at a snapshot carry the fix;
    multiplying its likelihood in again here counted it twice (smoothed sigma
    at a fix of 6.8 m where 9.3 m is right) and only at fixes that happened to
    fall on a snapshot step, so the error depended on the stride. The end
    anchor is different: the forward pass never sees it, so it is applied here.

    **Transition density.** The backward weight of ancestor ``i`` for a drawn
    successor ``x'`` is ``w_t^i * f(x' | x_t^i)`` with ``f`` the full forward
    transition, latents included. ``psi_bias`` and ``k_speed`` walk with
    ``bias_walk_std_rad_per_s`` / ``speed_walk_std_per_s`` (both 0 in the
    shipped config), so with zero walk the latent part of ``f`` is a point
    mass: only ancestors with exactly the successor's latents are admissible.
    Ignoring it (the pre-fix kernel used xy only) let a smoothed path swap
    heading bias and speed scale between snapshots. With nonzero walk the
    latent part is the Gaussian random-walk density over the interval.

    ``interval_noise_var_m2`` (optional): the accumulated xy process-noise
    variance per interval from :func:`integrate_snapshot_noise`. Pass it so the
    backward kernel uses the same behaviour-dependent noise the forward pass
    drew; without it the kernel falls back to ``process_noise_xy_m**2 * dt``.

    ``step_displacements`` (optional) + ``current_displacements``: the
    heading/speed and current displacement already integrated over each
    snapshot interval, as built by :func:`integrate_snapshot_intervals`. Both
    are ``(T, 2)`` with row ``t + 1`` describing the interval ``t -> t + 1``.
    Pass them whenever the snapshots are more than one filter step apart —
    without them the kernel treats a stride-``m`` interval as a single step,
    which shrinks the predicted displacement by ``m`` and the kernel variance
    by ``m``. When they are omitted the per-step form is used verbatim, so a
    caller that does not pass them is unaffected. ``dts_s[t + 1]`` must be the
    interval duration, not the per-step dt, whenever the stride is greater than
    one. Note that ``current_displacements`` changes the kernel at *any* stride,
    stride 1 included: the per-step form carries no current term at all, so a
    run with a current field is only reproduced by passing this argument.

    ``diagnostics`` (optional): a dict this function fills in with the
    **backward-sampling effective sample size** — the ESS of the normalised
    backward weights ``w_smooth`` from which each of the ``K`` ancestors is
    drawn, at every backward step. It is the smoother's analogue of the forward
    filter's ``ess``: a backward step at which it collapses to 1 is a step at
    which every one of the ``K`` paths had no choice of ancestor. Recorded, not
    scored — ``docs/regen_2026-09.md`` section 19.6.3 asks for the measurement
    and leaves the floor to a design amendment. Passing the dict costs one
    extra length-``N`` sum of squares per ``(t, k)``, roughly a sixth of the
    inner loop, which is why it is opt-in; omit it and the loop is unchanged.
    Nothing in it touches a weight or the RNG, so a run with diagnostics is
    bit-identical to one without.

    Cost: O(N · K · T). N=4000, K=100, T=600 ≈ 2.4×10⁸ ops, ~10-30 s in Python.
    """
    ...
LATENT_GRID_DEFAULT_N = 5
LATENT_GRID_DEFAULT_HALF_WIDTH_SIGMA = 2.0

@dataclass(frozen=True)
class LatentNode:
    """One node of the outer grid: a fixed ``(psi_bias, k_speed)`` pair.

    ``log_prior`` is the Gaussian prior the *particle* mode places on this
    pair — ``N(0, init_bias_std_rad)`` on the bias and ``N(1, init_speed_std)``
    on the scale — evaluated at the node. On a regular grid the cell widths are
    equal, so they cancel in the normalisation and the prior enters the
    posterior exactly as it should.
    """
    index: int
    psi_bias_rad: float
    k_speed: float
    log_prior: float = 0.0

    @property
    def psi_bias_deg(self) -> float:
        ...

def latent_axis_values(spec, default) -> np.ndarray:
    """Resolve one grid axis to its values.

    ``spec`` is an explicit sequence, an object with a ``values()`` method (the
    config's ``LatentAxisSpec``), a mapping ``{"n", "min", "max"}``, or None —
    in which case ``default`` (itself resolved the same way) is used. Values
    are returned sorted and de-duplicated, because a repeated node would be
    counted twice in the posterior.
    """
    ...

def default_latent_axis(mean: float, std: float, *, lo=None, hi=None) -> dict:
    """The ``{n, min, max}`` axis a config leaves unset: mean ± 2σ on 5 points.

    A non-positive ``std`` means the particle mode holds that latent fixed, so
    the axis collapses to the single point ``mean`` rather than spanning a
    width the prior does not have.
    """
    ...

def _gaussian_log_prior(values: np.ndarray, mean: float, std: float) -> np.ndarray:
    """log N(values; mean, std), or zeros when ``std`` is not positive."""
    ...

def build_latent_grid(psi_bias_deg, k_speed, *, bias_prior_std_deg: float=0.0, speed_prior_std: float=0.0, bias_prior_mean_deg: float=0.0, speed_prior_mean: float=1.0) -> list[LatentNode]:
    """The cartesian product of the two axes, each node carrying its log prior.

    Node order is row-major over ``(psi_bias, k_speed)`` and is the order every
    per-node array in ``filter_state["latent_grid"]`` uses.
    """
    ...

def latent_posterior(log_marginals, log_priors=None) -> np.ndarray:
    """Normalised posterior weights over grid nodes, by log-sum-exp.

    ``log_marginals[j]`` is node ``j``'s accumulated log marginal likelihood
    and ``log_priors[j]`` its log prior; the posterior is proportional to their
    sum. A node whose marginal is ``-inf`` (its likelihood was refuted outright)
    gets exactly zero. If *every* node underflows the weights come back
    uniform — the grid then carries no information, which is a fact about the
    run, not a number to invent a peak from.
    """
    ...

def latent_axis_marginal(values, weights) -> dict:
    """Posterior marginal over one axis: unique values, their mass, mean, sd."""
    ...

def draw_latent_node_counts(posterior, n_smooth: int, *, seed: int) -> np.ndarray:
    """``K_j ~ Multinomial(K, p)`` — how many FFBS paths each node supplies.

    Split out of the driver because the counts are drawn twice on a run with
    an end anchor: once from the forward posterior, and again once
    :func:`apply_end_anchor_to_latent_grid` has folded the anchor evidence in.
    The same ``seed`` gives the same draw for the same weights, so the second
    call is a redraw and not an extra source of randomness.
    """
    ...

def apply_end_anchor_to_latent_grid(grid: dict, log_anchor, *, n_smooth: int, seed: int) -> dict:
    """Fold ``log p(anchor | y, node j)`` into the grid's node weights, in place.

    Why this is not optional. ``run_filter_over_latent_grid`` can only form
    ``p(node j | y) ∝ exp(log prior_j + log marginal_j)`` from the *forward*
    filter — on this pipeline the end anchor does not exist yet when the filter
    runs (it is back-propagated from the recovery position at stage 6b, after
    stage 6). But every path the smoother draws inside a node is conditioned on
    that anchor. Mixing ``p(x | y, anchor, j)`` with weights ``p(node j | y)``
    is not a sample from anything: the correct weight is

        ``p(node j | y, anchor) ∝ p(node j | y) · p(anchor | y, node j)``

    and the second factor is exactly :func:`end_anchor_log_evidence` evaluated
    on node ``j``'s terminal forward cloud. It is not a small correction — on a
    deployment where the anchor sits 20 σ from one node's terminal cloud and
    2 σ from another's, it is hundreds of nats and it reorders the grid.

    The forward weights are kept as ``posterior_forward``: they, not the
    updated ones, are what the forward mixture summaries in ``filter_state``
    (``means``, ``cov_xy``, ``inside_count``, ``current_uv_at_step``) were
    averaged with, and those describe a filter that never saw the anchor.
    Everything the *latent posterior* is read from — ``posterior``, the axis
    marginals, ``map_index``, the node draws — is updated.
    """
    ...

def worst_degeneracy_node(summaries) -> int:
    """Index of the grid node whose §3.7 verdict is worst.

    Ordered by number of breached floors, then by the fewest surviving founder
    lineages. Design §3.5's restructuring note is explicit that the score card
    reports the worst node rather than an average: a node that degenerates
    still contributes its collapsed lineage to the mixture.
    """
    ...
SMOOTHER_CUBE_FRACTIONS = (0.0, 0.25, 0.5, 0.75, 1.0)

def smoother_cube_diagnostics(samples: np.ndarray, *, snapshot_steps=None, node_of_sample=None, backward=None) -> dict:
    """Degeneracy of the **smoothed** cube, which is what the report reads.

    ``docs/regen_2026-09.md`` section 19.6.3, option 3: every positional number
    the flagship reports — the track, ``sigma_along``/``sigma_cross``,
    ``along_span_m`` — comes from the FFBS cube and not from the forward
    filter's stored paths, so ``n_founders_final`` measures an object the
    report does not use. This measures the object it does.

    Three quantities, all read off the returned ``(T, K, STATE_DIM)`` cube:

    * **distinct positions** among the ``K`` draws at each of
      :data:`SMOOTHER_CUBE_FRACTIONS` through the snapshot axis. Backward
      sampling draws each path's ancestor from the whole weighted forward
      cloud, so two draws sharing an ``(x, y)`` at time ``t`` picked the same
      forward particle there; the count is the number of distinct ancestries
      the cube carries at that time.
    * **distinct latent pairs** ``(psi_bias, k_speed)`` over the cube. In grid
      mode these are node constants, so the count is how many latent nodes the
      reported ensemble actually spans; section 19.6.3 notes the flagship's
      cube carries 2 of 25.
    * **distinct nodes**, when ``node_of_sample`` is supplied by
      :func:`ffbs_smoother_over_grid`.

    ``backward`` is :func:`ffbs_smoother`'s optional diagnostics dict; when
    given, its scalars are folded in under ``backward_*`` so one block carries
    both halves of the measurement.

    **A diagnostic, not a gate.** No floor is scored from any of it and
    ``GATE_TABLE`` is untouched: the section 3.7 numbers are pre-registered and
    a new floor is a dated amendment to the design document, not a code change.
    """
    ...

def ffbs_smoother_over_grid(node_runs, *, rng_seed: int=0, diagnostics: Optional[dict]=None, **ffbs_kwargs) -> tuple[np.ndarray, np.ndarray]:
    """FFBS over the latent-grid mixture: sample a node, then a path within it.

    The smoothing distribution is the mixture ``Σ_j p_j · p(x_{0:T} | 𝒟, j)``
    over grid nodes. Drawing ``K`` paths from it is: draw the node counts
    ``K_j ~ Multinomial(K, p)``, then draw ``K_j`` FFBS paths inside node ``j``
    from that node's own forward history. Each node's backward sweep is the
    ordinary :func:`ffbs_smoother` — nothing about the smoother changes, only
    which forward history it is handed.

    **The identity holds only if ``p`` conditions on everything the within-node
    smoother does.** ``ffbs_kwargs`` normally carries an ``end_anchor``, so the
    within-node target is ``p(x | y, anchor, j)`` and the weights must be
    ``p(j | y, anchor)``, not the forward-filter ``p(j | y)`` that
    ``run_filter_over_latent_grid`` can compute on its own. Whoever draws the
    counts is responsible for that: see
    :func:`apply_end_anchor_to_latent_grid`, which folds
    :func:`end_anchor_log_evidence` into the node weights before the draw.
    This function cannot check it and does not try.

    ``node_runs`` is an *iterable* of ``(node_index, n_draws,
    history_particles, history_log_weights)`` and is consumed lazily, one node
    at a time: a forward history is ``T_snap × N × 4`` float64 (1.3 GB on the
    flagship), and the diffuse posterior this mode exists to produce can draw
    from every node on the grid. A caller that re-runs each node on demand
    therefore never holds more than one history. Nodes with zero draws are
    skipped. Each node gets ``rng_seed + node_index`` so a re-run of one node
    reproduces its paths exactly regardless of which other nodes were drawn.

    Returns ``(samples, node_of_sample)`` with ``samples`` shaped
    ``(T, K, STATE_DIM)`` — the same shape :func:`ffbs_smoother` returns, so
    every downstream consumer is unchanged — and ``node_of_sample`` naming the
    grid node each of the ``K`` columns came from.
    """
    ...
