"""Unit tests for ``anchor.ingest.mag_inflight`` — the dip-angle test.

Everything here runs on a synthetic world with a *known* answer: a known
geomagnetic field at a known inclination, a known hard-iron offset, a known
soft-iron matrix and a known signed axis permutation between the magnetometer's
axes and the accelerometer's. The point of the module is that it recovers all
four from the record alone, with no heading truth, so the tests give it none.
"""
from __future__ import annotations
import numpy as np
import pytest
from anchor.ingest import calibrate as CAL
from anchor.ingest import mag_inflight as MI
FS_HZ = 25.0
DIP_DEG = 60.8

def _smooth_rotations(n: int) -> np.ndarray:
    """``n`` rotations, world <- tag, sweeping the sphere *slowly*.

    Slowly on purpose. The gravity direction is recovered by a 2 s low pass, so
    an attitude that jumps between independent orientations from one 1 Hz block
    to the next would leave the filter averaging unrelated postures and the dip
    angle would scatter for a reason that has nothing to do with the
    magnetometer. A swimming animal rolls over seconds, not milliseconds, and
    these three incommensurate sweeps are that: three yaw turns, a +/-80 deg
    pitch oscillation and a +/-180 deg roll oscillation, which between them put
    the tag through the whole direction sphere.
    """
    ...

def synthetic_record(*, n_mag: int=4000, block: int=25, mapping_label: str='x,y,z', b_true=(140.0, -60.0, 310.0), field_counts: float=400.0, A_true: np.ndarray | None=None):
    """A record with a known field, hard iron, soft iron and axis mapping.

    World frame is NED-like with ``+Z`` pointing DOWN, so the accelerometer
    channel — which reads +1 g along body DOWN at rest — is the tag-frame image
    of the world's ``+Z``.  The field sits ``dip`` degrees below the horizontal,
    i.e. ``90 - dip`` degrees off DOWN, which is exactly what the dip test
    measures.
    """
    ...

def _fit(rec, **kw):
    ...

def test_there_are_exactly_48_mappings_half_proper_and_the_identity_is_first():
    ...

def test_the_negated_identity_is_present_and_improper():
    """The mapping the flagship needs is a reflection, and a search over the 24
    rotations alone could not have found it."""
    ...

def test_a_known_bias_soft_iron_and_identity_mapping_are_recovered():
    ...

def test_a_non_identity_signed_permutation_is_recovered():
    ...

def test_the_dip_test_passes_on_the_truth_and_fails_on_the_identity_when_reflected():
    """The flagship's case, synthesised: the magnetometer's sign convention is
    inverted relative to the accelerometer's."""
    ...

def test_the_mapping_is_folded_into_A_so_apply_calibration_needs_no_knowledge_of_it():
    ...

def test_the_dip_median_tracks_the_site_inclination():
    """A different dip must move the expectation, not the measurement."""
    ...

@pytest.mark.parametrize('label', ['-z,x,-y', 'y,-x,z', '-x,-y,-z'])
def test_remapping_the_calibrated_field_equals_remapping_the_raw_and_refitting(label):
    ...

def test_the_spike_rule_drops_a_single_axis_excursion_and_nothing_else():
    ...

def test_a_non_finite_triple_is_not_counted_as_a_spike():
    ...

def test_down_is_the_low_passed_accelerometer_not_its_negation():
    """The convention the whole search hangs on (module docstring)."""
    ...

def test_coverage_separates_a_cap_from_a_sphere():
    ...

def test_a_degenerate_record_is_refused_rather_than_fitted():
    ...

def test_mismatched_grids_without_an_index_are_refused():
    ...

def test_the_site_inclination_lookup_is_total_and_never_guesses():
    """The values are WMM2025's, fetched 2026-09-06 and saved under
    ``reports/regen_2026-09/section17/wmm/``; before that they were quoted from
    memory at 60.8 and 22.0."""
    ...

def test_the_elkhorn_declination_is_the_fetched_value_not_the_remembered_one():
    """``axy_ingest`` and ``run_deployment`` both default to this constant, so
    the -0.120 deg change moves the flagship's heading by exactly that."""
    ...

def _thin_band_cloud(n: int=6000, half_width: float=0.05, noise: float=3.0, radius: float=400.0, seed: int=11):
    """A cloud on a narrow band about a great circle: pure hard iron, no soft.

    The nine-parameter ellipsoid cannot be identified on it — the scale along
    the band's thin direction is never sampled — so the algebraic fit comes
    back rank-deficient, which is ``LS_260311_S1``'s failure at cond(A) = 5852
    (``docs/regen_2026-09.md`` section 16.13.4). The four-parameter sphere has
    no such parameter to lose.
    """
    ...

def test_the_sphere_fitter_recovers_b_where_the_ellipsoid_fit_is_rank_deficient():
    ...

def test_the_fitter_rule_is_applied_and_recorded():
    """The rule fires on the thin cloud and does not fire on a sound one."""
    ...

def test_the_coverage_guard_catches_a_cap_on_its_own():
    """The second guard, which is the one section 16.5 says separates a sound
    fit from a degenerate one: the calibrated directions occupy a cap.

    A cap trips both guards at once, so the test disables the conditioning one
    (``sphere_cond_max=inf``) to show that coverage alone is sufficient — which
    is the case that matters, because a collapsed axis buys a *flattering*
    residual and a plausible-looking cost.
    """
    ...

def _noisy_directions(seed: int=5):
    """A record noisy enough that the 48 scores are close, which is the regime
    in which the ranking rule is load-bearing."""
    ...

def test_the_winner_is_unchanged_on_the_flagship_like_synthetic():
    """The reflected mapping the flagship needs, under the new rule."""
    ...

def test_a_wrong_expected_dip_no_longer_changes_the_winner():
    """Section 16.13.5's defect, synthesised: under the old rule the site's dip
    sat inside the objective and chose the frame."""
    ...

def test_the_mad_ordering_itself_does_not_contain_the_dip():
    """Why MAD-first works: theta does not move with the expectation, so the
    MAD of every one of the 48 mappings is the same at every dip."""
    ...

def _unit_field(rec):
    """The calibrated field directions of a synthetic record, unmapped."""
    ...

def _down(rec):
    ...

def test_the_offset_tie_break_is_what_separates_a_mirror_pair():
    """A mapping and its negation have identical MADs, so the MAD alone cannot
    tell a field 29 deg from DOWN from one 29 deg from UP."""
    ...

def test_the_reported_margin_is_in_the_statistic_that_decided_the_winner():
    ...

def test_validation_block_reports_whether_a_stored_A_is_symmetric():
    """The loader-side diagnostic: an archived card written before 2026-09-06
    carries the upper-triangular root, and the reader is told so."""
    ...

def test_box_lowpass_is_nan_aware():
    """One NaN sample must not poison the rest of the record (audit 2026-09-25)."""
    ...
