"""The outer latent grid (design §3.5): (psi_bias, k_speed) off the particle state.

In the shipped 4-state path the two static latents are particle-state
dimensions with near-zero random walks, so resampling can only ever kill
latent atoms: the flagship run ended with one surviving ``k_speed`` value out
of 4000 founders and a reported posterior sd of exactly 0. Grid mode fixes that
structurally — one conditional filter per ``(psi_bias, k_speed)`` node, and a
posterior over nodes formed from their log marginal likelihoods, which
resampling cannot touch because resampling never crosses nodes.

These tests pin the four properties the mode is worth having for:

1. it is **additive** — a one-node grid reproduces the particle mode with its
   latents frozen, bit for bit, on every array in ``filter_state``;
2. the grid **learns** — on the free-space synthetic with a known injected
   ``k_speed`` the posterior concentrates near the truth, and the ``psi_bias``
   marginal is unimodal;
3. the §3.7 degeneracy gate evaluates **per node**, and the exported verdict is
   the worst node's;
4. the report renders the posterior.
"""
from __future__ import annotations
import numpy as np
import pytest
from anchor.ingest.config import TrajectoryConfig
from anchor.trajectory.animate_filter import _run_grid_nodes, run_filter_with_snapshots
from anchor.trajectory.particle_filter import SBIAS, SSCALE, LatentNode, build_latent_grid, default_latent_axis, ffbs_smoother_over_grid, integrate_snapshot_intervals, latent_axis_marginal, latent_axis_values, latent_posterior, worst_degeneracy_node
from anchor.trajectory.release_anchor import ReleaseAnchor
from anchor.trajectory.synthetic import simulate_observations, simulate_truth_free_space
from anchor.trajectory.verified_positions import VerifiedPosition, VerifiedPositionSet
DT = 1.0
N_STEPS = 181
TRUE_BIAS_DEG = 7.0
TRUE_SCALE = 1.1
VP_PERIOD = 15
VP_SIGMA_M = 3.0
N_PARTICLES = 400

class _AllWaterPolygon:

    def is_inside(self, x, y, tide_m_mllw=None):
        ...

def _track(truth, obs):
    ...

@pytest.fixture(scope='module')
def synthetic():
    """Free-space truth with a known bias/scale, plus periodic position fixes.

    The fixes are what make the latents identifiable at all: with no positional
    observation every node has the same marginal likelihood and the grid is
    just its prior.
    """
    ...

def _traj(**kw):
    ...

def _run(synthetic, traj, seed=0):
    ...

def test_particle_mode_still_exports_a_log_marginal_likelihood(synthetic):
    """The marginal is accumulated in both modes — grid mode needs it, and it
    is the one number that says whether the data preferred this run at all."""
    ...

def test_single_node_grid_reproduces_frozen_particle_mode_bit_for_bit(synthetic):
    """A one-node grid at (0°, 1.0) is the frozen-latent 4-state run.

    This is what "additive" has to mean: the conditional filter must consume
    the RNG in exactly the same order as the unconditional one, so a zero-sigma
    latent draw is still *drawn*. Anything looser and grid mode would be a
    second, subtly different pipeline rather than a restructuring of the one.
    """
    ...

def test_grid_freezes_the_latents_at_the_node_value(synthetic):
    """Within a node the particle state is (x, y): the two latent columns are
    the node's constants at every snapshot, for every particle."""
    ...

def test_a_node_outside_the_speed_clip_is_not_dragged_back_inside():
    """``predict`` clips k_speed into [speed_min, speed_max]; a grid node
    outside that interval must still be the value the node claims, or the
    posterior would be reported against latents the filter never ran."""
    ...

@pytest.fixture(scope='module')
def grid_run(synthetic):
    ...

def test_the_k_speed_posterior_concentrates_near_the_injected_truth(grid_run):
    ...

def test_the_psi_bias_marginal_is_unimodal(grid_run):
    ...

def test_every_node_carries_a_marginal_a_prior_and_a_posterior(grid_run):
    ...

def test_the_reported_spread_is_the_exact_mixture_over_nodes(synthetic):
    """``mean = Σ p_j m_j``, ``cov = Σ p_j (C_j + d_j d_jᵀ)``, checked against
    the two nodes run separately.

    The between-node term ``d_j d_jᵀ`` is the whole point: it is uncertainty
    about the latents expressed as uncertainty about position, which the
    4-state path could only express through a particle cloud that resampling
    had already collapsed onto one latent atom.
    """
    ...

def test_degeneracy_is_scored_per_node_and_the_worst_is_exported(grid_run):
    ...

def test_worst_degeneracy_node_prefers_more_breaches_then_fewer_founders():
    ...

def test_log_marginal_is_the_sum_of_per_step_log_mean_weights(synthetic):
    """Hand-computed against the definition on a two-node grid.

    ``log p(y) = Σ_t log Σ_i W_{t-1,i} g_t(x_t^i)``. The filter accumulates it
    as the difference of log-sum-exps across each step's updates, which is the
    same quantity and is what makes it invariant to when resampling fires.
    """
    ...

def test_latent_posterior_normalises_and_zeroes_a_refuted_node():
    ...

def test_latent_posterior_is_uniform_when_every_node_underflows():
    ...

def test_latent_posterior_includes_the_prior():
    ...

def test_default_axis_is_the_particle_priors_two_sigma_span():
    ...

def test_axis_values_accept_a_list_a_spec_and_a_mapping():
    ...

def test_the_grid_prior_is_the_particle_modes_gaussian():
    ...

def test_axis_marginal_sums_duplicates():
    ...

def test_process_workers_produce_the_same_results_as_running_inline(synthetic):
    """The pool is a scheduling detail: a node is a pure function of
    ``(node, seed)``, so the parallel and inline paths must agree exactly."""
    ...

def test_keep_history_false_skips_the_snapshots_but_not_their_steps(synthetic):
    ...

def test_ffbs_over_the_grid_draws_each_column_from_its_own_node(grid_run, synthetic):
    ...

def test_ffbs_over_the_grid_refuses_an_empty_draw():
    ...

def test_report_renders_the_latent_posterior_as_a_table(grid_run):
    ...

def test_report_marks_the_latent_posterior_sd_when_the_gate_fails(grid_run):
    """The banner promises every credible interval in the report is marked;
    the grid's posterior sd is one, because the marginal likelihoods behind it
    are estimated by the same clouds the gate scored."""
    ...

def test_report_latent_table_is_empty_in_particle_mode():
    ...

def test_report_latent_table_caps_its_rows_and_says_so(grid_run):
    ...

def test_diagnostics_section_embeds_the_latent_grid(grid_run):
    ...

def test_console_prints_the_latent_marginals(grid_run, capsys):
    ...

def test_config_rejects_a_degenerate_axis_span():
    ...

def test_config_accepts_both_axis_shapes_and_defaults_to_particle_mode():
    ...

def test_cli_axis_flag_parses_a_list_and_an_n_min_max():
    ...

def test_cli_overrides_reach_the_effective_trajectory_config():
    ...

def test_a_bad_cli_axis_exits_naming_the_flag():
    ...

def test_an_unpicklable_input_drops_to_sequential_with_a_reason():
    """``ProcessPoolExecutor`` spawns on macOS, so every input is pickled.
    ``CurrentField.from_tide_series`` builds a closure and cannot cross that
    boundary; the run has to say so and keep going, not die inside
    ``Process.start`` after the filter is already set up."""
    ...

def test_the_grid_records_the_workers_it_actually_used(grid_run):
    ...

def test_without_resampling_the_marginal_is_the_final_log_sum_exp(synthetic):
    """An exact identity, independent of any model.

    With ``resample_threshold=0`` the weights are never flattened, so the
    telescoping sum the filter accumulates must collapse to
    ``logsumexp(final log-weights) − log N``. If the accumulation ever
    double-counted a step, or missed the release-anchor step, this breaks.
    """
    ...

def test_the_marginal_matches_the_kalman_log_likelihood(synthetic):
    """With the latents fixed the conditional model is linear-Gaussian, so
    ``log p(y_{0:T} | node)`` has a closed form — and that is the number the
    grid posterior is built out of, so it is worth checking against something
    other than itself.

    Everything is isotropic here (an isotropic prior, isotropic process noise
    and isotropic fixes), so the 2×2 covariance stays a multiple of the
    identity and the Kalman recursion is scalar.
    """
    ...

def test_a_node_whose_every_particle_is_rejected_is_scored_not_excused():
    """A grid node can be so wrong that the constraint rejects every particle.

    That step is not information-free: it is the loudest thing the data ever
    says about the node. It used to be handed to the filter's uniform-reset
    fallback and to contribute **0** to the log marginal, which *credits* a
    refuted node with evidence it did not earn and favours whichever node
    leans on the fallback hardest (docs/regen_2026-09.md §12.4). It now costs
    the node ``polygon_penalty_nats`` and the reset does not fire; the count
    is still exported per node, beside the reset count, because a grid whose
    nodes are scored on different subsets of the record is still worth
    seeing.
    """
    ...

def test_the_latent_grid_serialises_to_strict_json_without_the_per_step_arrays(grid_run):
    """The sidecar and the parquet footer are the only machine-readable record
    of which latents produced a track, so they have to be strict JSON — the
    same rule the ledger applies — and must not carry the five per-node,
    per-step arrays, which on the flagship would be 25 × 5 × 61 000 numbers."""
    ...

def _grid_with_unscored(counts, map_index):
    """A minimal ``latent_grid`` dict carrying one unscored count per node."""
    ...

def test_the_unscored_note_says_which_way_the_bias_points():
    """A step the fallback could not score contributes 0 to that node's log
    marginal instead of a negative number, so the bias *favours* whichever node
    leans on the fallback hardest — it cannot be signed "against concentration".
    The flagship is the counter-example: the node that took 100% of the
    posterior had skipped 25 989 of 60 992 steps while four nodes on the same
    ``k_speed`` axis point skipped none.
    """
    ...

def test_the_unscored_note_exonerates_a_map_node_that_skipped_the_fewest():
    ...

def test_the_unscored_note_is_absent_when_no_node_collapsed():
    ...

def test_the_console_warns_when_the_map_node_skipped_more_steps_than_another(capsys):
    """The same fact the report states has to reach the console, because a
    grid run is watched from the terminal and the number that decides which
    latents the track was drawn under is the log marginal."""
    ...

class _Refuting:
    """An anchor whose likelihood is -inf everywhere (a refuted node)."""
    x = y = 0.0
    sigma_m = 1.0

    def log_likelihood(self, px, py):
        ...

def _anchor(x, y, sigma_m=10.0):
    ...

def test_end_anchor_log_evidence_is_the_weighted_mean_anchor_likelihood():
    """log Σ_i W_i L(x_i) with W the *normalised* terminal forward weights."""
    ...

def test_end_anchor_log_evidence_does_not_underflow_at_twenty_sigma():
    """The flagship's anchor sits 21 σ from the terminal cloud, where every
    term underflows to 0.0 in linear space. Computed by log-sum-exp it stays
    finite, which is the only reason the term can be compared across nodes."""
    ...

def test_end_anchor_log_evidence_is_minus_infinity_for_a_refuted_cloud():
    ...

def _toy_grid(log_marginals, log_priors=None):
    """A minimal ``latent_grid`` dict of the shape the driver produces."""
    ...

def test_the_anchor_term_can_reorder_the_grid():
    """The whole point: p(node | y, anchor) ∝ p(node | y) · p(anchor | y, node),
    and the second factor is decisive when node tracks end kilometres apart."""
    ...

def test_the_anchor_term_zeroes_a_node_it_refutes():
    ...

def test_the_anchor_term_rejects_a_length_mismatch():
    ...

def test_the_filter_returns_every_nodes_terminal_cloud(grid_run):
    """The anchor is scored per node, so every node's terminal cloud has to
    come back — at N x 4 floats each, which the histories are not."""
    ...

def test_the_filters_own_posterior_is_forward_only_and_says_so(grid_run):
    ...

def test_the_driver_materialises_exactly_one_history(grid_run):
    ...

def test_a_uniform_posterior_still_materialises_exactly_one_history(synthetic, monkeypatch):
    """The diffuse case, forced the way ``latent_posterior`` itself produces
    it. Before the fix this drew from every node and built a history for each."""
    ...

def test_a_rerun_node_reproduces_its_pass_one_marginal_bit_for_bit(grid_run):
    """Pass 2 is only sound because a node is a pure function of (node, seed)."""
    ...

def test_ffbs_over_the_grid_holds_one_history_at_a_time(grid_run, synthetic):
    """The contract that bounds the memory: ``node_runs`` is consumed lazily,
    and a caller that re-runs nodes on demand never holds two histories."""
    ...

def _grid_state_for_smoothing(synthetic):
    ...

def test_the_driver_folds_the_anchor_in_before_drawing_the_nodes(synthetic, capsys):
    """End to end over the wiring: an anchor placed on a node the forward
    posterior dislikes takes over the draw. Before the fix the draw was made
    from the forward posterior and this node was never smoothed."""
    ...

def test_the_driver_leaves_the_forward_summaries_on_the_forward_weights(synthetic):
    """``means``/``cov_xy``/``inside_count`` describe a filter that never saw
    the anchor, so they keep the weights they were averaged with."""
    ...

def test_the_console_names_which_weights_it_is_printing(grid_run, capsys):
    ...

def test_the_report_says_what_the_node_weights_condition_on(grid_run):
    ...

def test_the_report_names_the_anchor_term_once_it_is_folded_in():
    ...

def test_an_anchored_grid_still_serialises_to_strict_json():
    """``log_anchor`` is -inf on a node the anchor refutes, and strict JSON has
    no ``-Infinity``; the ledger's coercion has to reach it."""
    ...

def _yaml_dump(traj):
    """A stand-in for ``cfg.model_dump(mode="json")``: the YAML as written."""
    ...

def _card_for(effective_traj, *, yaml_traj=None):
    ...

def test_the_card_fingerprints_the_effective_trajectory_not_the_yaml():
    """``--latent-mode grid`` has to move ``provenance.config_hash``.

    Both cards below are built from the *same* YAML dump, which is the whole
    point: the only difference is the effective ``TrajectoryConfig`` the run
    used, and that is exactly what a CLI override changes.
    """
    ...

def test_an_override_free_run_keeps_the_hash_the_yaml_alone_would_give():
    """The substitution must not churn every card already written: with no
    override the effective config *is* the YAML, so the hash is unchanged."""
    ...

def test_the_card_config_passes_a_non_model_config_through_untouched():
    """``_build_score_card`` is also called with ``str(cfg)`` when the config
    object is not a pydantic model, and with no effective traj at all;
    substituting a trajectory into a string is not a thing and must not raise."""
    ...

class _NoWater:
    """Rejects every particle at every step."""

    def is_inside(self, x, y, tide_m_mllw=None):
        ...

class _HalfPlane:
    """Rejects the particles east of ``x0`` — some, never all."""

    def __init__(self, x0):
        ...

    def is_inside(self, x, y, tide_m_mllw=None):
        ...
DEAD_STEPS = 25

def _dead_track(n=DEAD_STEPS):
    """A short free-space track with no fixes, for the rejection tests."""
    ...

def _run_with_polygon(track, truth, polygon, traj, n=DEAD_STEPS, seed=0):
    ...

def _one_node(**kw):
    ...

def test_a_node_driven_outside_the_polygon_scores_below_one_kept_inside():
    """§12.4's defect in one assertion.

    Two runs of the same track, the same seed and the same node: one where the
    polygon accepts every particle, one where it rejects every particle. The
    rejected run is the refuted hypothesis, so its log marginal has to be
    *strictly smaller* — under the old hard constraint both scored the same,
    because every rejected step contributed exactly 0 to the sum.
    """
    ...

def test_a_constraint_rejected_step_contributes_the_penalty_and_never_zero():
    """Each rejected step must move the marginal by exactly the penalty.

    The two runs differ only in the constraint, and a uniform shift of every
    log-weight leaves the relative weights (and so the ESS, the resampling
    decisions and the RNG stream) untouched. So the whole difference between
    the two marginals is one penalty per step at which the cloud was outside —
    ``DEAD_STEPS`` of them, none of them contributing 0.
    """
    ...

def test_the_hard_polygon_mode_is_still_reachable_and_still_resets():
    """``polygon_penalty_nats=None`` is the pre-fix behaviour, kept explicit:
    -inf log-weights, the uniform reset on every step, and a marginal that
    scores nothing at all."""
    ...

def test_the_default_penalty_reproduces_the_hard_constraint_run():
    """The default is chosen so ``exp(-penalty)`` underflows to exactly zero
    against any surviving particle, so on a run where the cloud is never
    *entirely* outside the posterior, the resampling and every diagnostic are
    the ones the hard constraint gave."""
    ...

def test_the_grid_reports_penalised_versus_reset_steps_per_node():
    """A grid whose nodes are scored on different subsets of the record is not
    comparing likelihoods on common data (§12.4), so each node has to say how
    many steps it was penalised on and how many it was excused."""
    ...

def _grid_with_penalised(penalised, map_index, penalty=800.0):
    """A minimal ``latent_grid`` carrying a *charged* count per node."""
    ...

def test_the_grid_table_reports_penalised_steps_beside_unscored_ones():
    """Exporting the count into a dict is not reporting it.

    The grid table used to carry one ``unscored steps`` column, which under
    the finite penalty reads 0 for a run whose cloud never left the water
    *and* for one that spent the whole record ashore. The second case has to
    be legible, or the fix for §12.4 makes the report cleaner than the defect
    did.
    """
    ...

def test_the_grid_table_says_nothing_about_penalties_when_none_were_charged():
    ...

def test_the_console_reports_penalised_node_steps(capsys):
    """A grid run is watched from the terminal, and §12.4's disclosure has to
    survive the fix that made the steps scorable."""
    ...

def test_the_console_reports_a_cloud_that_left_the_water_in_either_mode(capsys):
    """The all-rejected signal used to arrive as a weight collapse and a
    breached ESS floor; under the penalty neither fires, so it needs its own
    line — in both modes, said differently."""
    ...

def test_the_diagnostics_note_reports_a_cloud_outside_the_polygon():
    """Section 8's notes are where a reader meets the run's pathologies, and
    the weight-collapse note no longer covers this one."""
    ...
