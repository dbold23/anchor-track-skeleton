"""The two optional water-constraint modes (TASK C1, A and B).

``FilterConfig.polygon_mode`` has three values and only one of them is the
shipped model:

``indicator``
    The default. Unchanged, and the reference every test here measures against.
``in_water_proposal``
    A *sampler* change with the same target: the position innovation is redrawn
    until it lands in water and the weight carries the redraw's normaliser
    ``log Z``. The tests below check the two properties that make it worth
    having — the estimator is quieter across seeds, and it does not move the
    posterior — and the one that makes it safe: with nothing ever rejected the
    correction is exactly zero, so the mode degenerates to the bootstrap
    proposal rather than to something near it.
``soft``
    A *model* change: the charge becomes a smooth function of the distance to
    the nearest wet cell. The tests check the distance transform against
    hand-computed distances, the likelihood against its own formula, and the
    width -> 0 limit against the indicator's partition, weight for weight.

The channel fixture is analytic on purpose: a band ``|y| <= HALF_WIDTH_M`` has
an exact indicator *and* an exact distance to water, so a disagreement here is
the filter's and never the raster's. The rasterised distance transform is
tested separately on a hand-built mask.
"""
from __future__ import annotations
import numpy as np
import pytest
import rasterio
from anchor.trajectory.animate_filter import _log_sum_exp
from anchor.trajectory.particle_filter import SX, SY, FilterConfig, ParticleFilter
from anchor.trajectory.polygon_constraint import PolygonConstraint, distance_to_wet_m
HALF_WIDTH_M = 10.0
NOISE_M = 15.0
SPEED_MPS = 1.0
N_STEPS = 150
N_PARTICLES = 300

class ChannelPolygon:
    """An east-west band of water, ``|y| <= half_width``.

    Exact in both quantities the filter can ask of a polygon, so the tests
    below compare the filter against arithmetic rather than against a raster.
    """

    def __init__(self, half_width_m: float=HALF_WIDTH_M):
        ...

    def is_inside(self, x, y, tide_m_mllw=None):
        ...

    def distance_to_water_m(self, x, y, tide_m_mllw=None):
        ...

class AllWater:
    """A polygon that never rejects anything."""

    def is_inside(self, x, y, tide_m_mllw=None):
        ...

    def distance_to_water_m(self, x, y, tide_m_mllw=None):
        ...

def _config(mode: str, seed: int, **kw) -> FilterConfig:
    ...

def run_channel(mode: str, seed: int, *, n_steps: int=N_STEPS, polygon=None):
    """One filter down the channel; returns its log marginal and terminal mean.

    The marginal is accumulated by the driver's own recurrence — ``lse_prev``
    resets to ``log N`` after a resample and is the step's own log-sum-exp
    otherwise — so the number is comparable with
    ``run_filter_with_snapshots``'s and with every number in
    ``docs/regen_2026-09.md`` sections 12-19.
    """
    ...

@pytest.fixture(scope='module')
def channel_replicates():
    """Twenty seeds of each mode down the same channel."""
    ...

def test_the_in_water_proposal_is_quieter_across_seeds(channel_replicates):
    """The whole point: the same target, estimated with less seed noise.

    The indicator throws away whatever fraction of the cloud left the water at
    each step, so its per-step increment is the log of a binomial fraction and
    the seeds diverge; the proposal averages that fraction over M trials per
    particle before taking the log. Measured on this fixture the two sds are
    about 0.74 and 0.18 nats over 150 steps, a ratio of 0.24; the assertion is
    the conservative half of that, because the measurement is that the noise
    falls and not how far it falls on one synthetic channel.
    """
    ...

def test_the_in_water_proposal_targets_the_same_distribution(channel_replicates):
    """Same posterior mean, within the Monte Carlo error of the two estimates.

    A sampler change that moved the posterior would be a model change wearing a
    sampler's clothes, which is exactly what the weight correction exists to
    prevent. Both modes are compared against each other's own seed spread — the
    tolerance is the data's, not a number chosen to pass.
    """
    ...

def test_the_two_marginals_differ_only_by_the_gap_jensen_predicts(channel_replicates):
    """The same estimand, and the noisier estimator reads lower.

    Both modes are unbiased for the marginal *likelihood*; what is reported is
    its logarithm, and ``E[log X] <= log E[X]`` by concavity, with a gap of
    about ``Var(X) / 2 E[X]^2``. The quieter estimator therefore sits
    **higher**, by less than the noisier one's own seed spread. Anything else —
    the proposal reading lower, or the gap exceeding that spread — would mean
    the two modes are not estimating the same quantity, which is the failure
    the weight correction exists to rule out.
    """
    ...

def test_the_weight_correction_is_exactly_zero_when_nothing_is_rejected():
    """``log Zhat = log(M/M) = 0``, bit for bit, on an all-water polygon.

    Not "small": every trial draw lands in water, ``k = M`` for every particle,
    and the correction is the logarithm of one. A mode that perturbed the
    weights here would be charging for a constraint that is not binding.
    """
    ...

def test_every_particle_the_proposal_accepts_is_in_the_water():
    """The proposal's own contract: an accepted draw is inside, not nearly."""
    ...

def test_the_proposal_records_its_redraws_and_its_mean_acceptance():
    """``n_redraws`` and ``mean_z`` are what the section reads per step."""
    ...

def test_the_kept_draw_is_uniform_among_the_accepted_trials():
    """The pairing itself, replayed from the RNG, not one of its consequences.

    ``propose_in_water``'s docstring makes the uniform choice among the
    accepted trials load-bearing, and every other test in this file measures a
    *consequence* of it — the marginal, the posterior mean, the redraw counts —
    each of which a "keep the first accepted draw, count the rest"
    implementation would also satisfy. What separates the two is the **rank**
    of the kept trial among the accepted ones: uniform on ``{1..k}`` here,
    identically 1 there.

    The trials are recovered by replaying the generator from the state it held
    before the call, so this compares the implementation against its own draws
    rather than against a tolerance.
    """
    ...

def test_the_proposal_pair_is_properly_weighted_against_its_own_draws():
    """``E[Zhat . h(x)] = E[h(x^1) 1_W]`` — the identity the docstring derives.

    Both sides are formed from the *same* replayed trials, so this is a paired
    comparison and its noise is the pairing's own, not the Gaussian's.
    """
    ...

def test_a_second_predict_without_the_polygon_step_raises():
    """The correction cannot be silently dropped.

    ``predict`` computes ``log Zhat`` and ``apply_polygon_constraint`` applies
    it; a loop that skipped the second call would be sampling from a truncated
    proposal and weighting as though it had not.
    """
    ...

def test_the_step_zero_cloud_still_meets_the_indicator():
    """At t=0 the cloud comes from the release prior, not from the transition.

    There is no proposal to correct for, so the polygon applies as it always
    did — which is also what keeps a proposal-mode run's first step comparable
    with the shipped path's.
    """
    ...

def test_the_distance_transform_reports_metres_not_cells():
    """Hand-built 5x5 mask, one wet cell, 2 m pixels: distances by Pythagoras."""
    ...

def test_an_all_dry_level_has_no_distance_to_water():
    """No wet cell means no distance to one; ``inf``, not a large number."""
    ...

def test_a_rotated_raster_is_refused_rather_than_measured_in_pretend_metres():
    ...

def test_the_polygon_constraint_samples_its_own_distance_field():
    """Off the raster is ``inf``; on it, the transform's own value."""
    ...

def test_the_soft_likelihood_is_the_formula_at_known_distances():
    """``-0.5 (d / width)^2`` on the analytic channel, particle by particle."""
    ...

def test_a_particle_in_the_water_pays_nothing_under_the_soft_mode():
    ...

def test_a_vanishing_width_reproduces_the_indicators_partition():
    """The limit, weight for weight — not merely the same sign.

    As the width goes to zero every outside particle saturates at
    ``polygon_penalty_nats`` and every inside particle stays at exactly zero,
    which is the shipped indicator's own log-weight vector.
    """
    ...

def test_the_soft_mode_still_reports_a_cloud_that_left_the_water():
    """``n_polygon_all_rejected`` keeps its meaning under every mode."""
    ...

def test_the_default_mode_is_the_indicator_and_draws_the_same_numbers():
    """A default-configured filter is the one section 19 ran.

    Same two ``rng.normal`` calls, in the same order, at the same sizes: the
    positions after a predict are identical to a filter built before
    ``polygon_mode`` existed, which is reproduced here by driving the same
    generator by hand.
    """
    ...

@pytest.mark.parametrize('mode', ['in_water_proposal', 'soft'])
def test_a_non_default_mode_without_a_polygon_is_refused(mode):
    ...

def test_an_unknown_mode_is_refused_by_name():
    ...

def test_the_soft_mode_needs_a_polygon_that_can_measure_a_distance():
    ...

@pytest.mark.parametrize('kw,match', [({'polygon_proposal_draws': 0}, 'at least 1'), ({'polygon_soft_width_m': 0.0}, 'must be positive')])
def test_an_out_of_range_knob_is_refused_where_it_is_used(kw, match):
    ...

def _synthetic_track(n_steps: int=120):
    """A free-space track that drifts east down the channel."""
    ...

def _run_driver(mode, **traj_kw):
    ...

def test_the_config_field_reaches_the_filter_loop_and_the_run_record():
    """``trajectory.polygon_mode`` is what the loop builds its FilterConfig from.

    The per-step block is the section's own instrument: ``mean_z`` is the
    cloud-mean estimated probability that a proposed innovation lands in water,
    and ``n_redraws`` is how many particles needed more than their first trial.
    """
    ...

def test_the_default_run_record_says_the_indicator_and_measures_no_redraws():
    ...

def test_the_soft_mode_reaches_the_loop_and_keeps_more_of_the_cloud():
    """A soft shoreline should retain weight the indicator throws away."""
    ...

def test_a_soft_all_rejected_step_is_recorded_but_not_charged_the_penalty():
    """The mode's own charge, not the indicator's flat rate.

    ``_apply_soft_shoreline`` returns "all rejected" on exactly the indicator's
    condition — no particle inside the wet mask — but its consequence is a
    per-particle distance cost, not ``polygon_penalty_nats``. The report and
    the console read ``marginal_penalised_steps`` as "n x penalty nats", so a
    soft step must not appear there; the raw fact still travels in
    ``polygon_all_rejected_steps``.
    """
    ...

def test_the_soft_mode_leaves_the_penalised_step_list_empty():
    """The driver's bookkeeping follows the charge, not the condition."""
    ...

def test_the_run_records_export_the_mode_and_the_proposal_totals():
    """A completed non-default run leaves a trace of the mode it ran in.

    ``polygon_mode`` and the proposal's totals used to stop at
    ``filter_state``: the parquet footer, the report and the latent-grid JSON
    carried none of it, so a soft-shoreline reconstruction was indistinguishable
    from a shipped-indicator one except through a 16-hex ``config_hash``.
    """
    ...

def test_the_proposal_has_no_backward_form_and_says_so():
    """``direction=-1`` under the proposal is refused, not silently corrected.

    ``propose_in_water``'s derivation is for the forward transition kernel. The
    two-filter smoother's backward leg runs a different one, and applying the
    forward ``log Zhat`` inside it would be wrong without being loud — so the
    filter refuses. Nothing in ``run_deployment`` reaches this (it smooths with
    FFBS), and ``two_filter`` builds its own indicator-mode config; the guard
    is here so that stays a decision rather than an accident.
    """
    ...
