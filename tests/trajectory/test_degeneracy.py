"""G-degeneracy gate (design §3.7) and the end-anchor binding check.

Five floors, fixed in ``docs/design/leopard_shark_digital_twin.md`` §3.7 and
copied verbatim into :data:`anchor.trajectory.particle_filter.DEGENERACY_FLOORS`:

    n_founders_final >= 30 of N; unique-ancestor fraction >= 0.02 at every t;
    max normalised weight <= 0.05; ESS_min >= 0.1 N; var(log w) <= 5.

Before this, the flagship run ended with 1 founder chain alive out of 4000 and
the report said so in a figure caption; nothing scored it, nothing warned, and
the credible intervals it produced were published as posterior widths. The
tests below pin the scoring, the warning, the export and the banner.
"""
from __future__ import annotations
import logging
import numpy as np
import pytest
from anchor.trajectory.end_anchor import EndAnchor
from anchor.trajectory.particle_filter import DEGENERACY_FLOORS, SBIAS, SSCALE, SX, SY, STATE_DIM, end_anchor_binding_check, evaluate_degeneracy, normalized_weights_from_log, unique_founder_count, weight_diagnostics
from anchor.trajectory.report import Section, build_html, degeneracy_banner
N = 100

def _healthy(n_steps=20, n_particles=N):
    """Per-step arrays that clear all five floors."""
    ...

def test_floors_are_the_section_3_7_numbers_verbatim():
    ...

def test_healthy_run_passes_every_floor():
    ...

@pytest.mark.parametrize('field,value,gate', [('n_founders_per_step', 29, 'n_founders_final'), ('max_weight_per_step', 0.06, 'max_norm_weight'), ('ess_per_step', 9.0, 'ess_min'), ('var_log_w_per_step', 5.1, 'var_log_w')])
def test_each_floor_fires_on_its_own(field, value, gate, caplog):
    ...

def test_unique_ancestor_fraction_is_checked_at_every_t_not_just_the_end():
    """A run that dips to 1 founder mid-track and is resampled back up
    cannot happen — but a run that dips below 0.02 and ends above it can be
    read as healthy from the final step alone. §3.7 says "at every t"."""
    ...

def test_ess_floor_scales_with_n():
    ...

def test_weight_diagnostics_on_uniform_weights():
    ...

def test_weight_diagnostics_on_a_single_surviving_particle():
    ...

def test_var_log_w_ignores_hard_rejected_particles():
    """The polygon's ``-inf`` rejections must not make var(log w) infinite —
    otherwise the gate reads FAIL on every step of every slough run, which
    says nothing about weight degeneracy."""
    ...

def test_weight_diagnostics_reports_a_total_collapse_as_degenerate():
    ...

def test_weight_diagnostics_is_shift_invariant():
    """Log-sum-exp, not exp: a constant offset of 10^4 nats must not
    overflow, underflow or move any of the three scalars."""
    ...

def test_unique_founder_count_matches_np_unique():
    ...

def test_normalized_weights_from_log_returns_zeros_on_collapse():
    ...

def _cloud(n=500, spread=10.0, seed=0):
    ...

def test_binding_check_reports_distance_in_sigma_units():
    ...

def test_a_binding_anchor_is_not_a_no_op_and_costs_ess():
    """Anchor σ comparable to the cloud spread: the reweighting has to bite,
    which shows up as a mean shift and a drop in effective particles."""
    ...

def test_a_far_anchor_with_a_wide_sigma_binds_only_weakly(caplog):
    """The flagship failure mode (design §2.4): a 4215 m / 24 σ anchor against
    an 11.7 m cloud. The reweighting is not literally a no-op — the kernel is
    tilted enough to move weight around — but it closes a few metres of a
    4 km gap, which is the number the report has to state."""
    ...

def test_a_flat_anchor_kernel_is_a_no_op(caplog):
    """σ_anchor enormous against the cloud: the log-likelihood is constant to
    within floating point, so the reweighted weights come back identical."""
    ...

def test_binding_check_detects_the_smoother_underflow_fallback(caplog):
    """``ffbs_smoother`` forms ``w_fwd * exp(log_anchor - max)`` in the product
    space. Put zero forward weight on the one particle the anchor likes and
    the whole product underflows to zero, its fallback fires, and backward
    sampling starts from the *unweighted* forward cloud. Doing the same
    reweighting by log-sum-exp — as this check does — hides that, so the
    smoother's own arithmetic is reproduced to catch it."""
    ...

def test_binding_check_does_not_inflate_the_anchor_sigma():
    ...

def test_banner_is_empty_without_a_degeneracy_record():
    ...

def test_banner_reports_a_pass():
    ...

def test_banner_names_every_failed_floor_and_says_intervals_are_suppressed():
    ...

def test_banner_lands_at_the_top_of_the_section_body(tmp_path):
    ...
