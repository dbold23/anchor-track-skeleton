"""Tests for the bathymetry likelihood modes.

`one_sided` (default) is behaviour-agnostic: it only forbids being below the
seafloor. `bottom_following` adds a two-sided Gaussian around
`off_bottom_factor * seafloor`, which makes depth informative for benthic
species but is wrong for mid-water swimmers. These tests pin the contract and
the default so the behavioural assumption can never be enabled by accident.
"""
import numpy as np
import pytest
from anchor.trajectory.bathymetry import REFERENCE_SIGMA_M
from anchor.trajectory.particle_filter import FilterConfig

def _logpdf(bathy, observed, **kw):
    ...

def test_default_mode_is_one_sided():
    """The behavioural assumption must be opt-in, never the default."""
    ...

def test_the_constraint_itself_is_on_by_default():
    """`enable_bathymetry_constraint` stays True, and this pins the decision.

    Design §3.5 row 6 asks for `default False`, and
    `sim/experiments/RESULTS_2026-09.md` §7 finds `one_sided` harmful against a
    known truth, so the flip is live as a design question. It is not settled by
    the flagship: `docs/regen_2026-09.md` §13 ran the latent grid with and
    without this constraint (arms (a)/(c) at 4000 particles, (b1)/(d1) at
    16000) to test whether the depth likelihood is what pins `k_speed` to its
    `speed_min` floor, and it is not — the `k_speed` posterior is 100 % on
    0.5000 either way. So the ablation came back negative and the default is
    deliberately unchanged; flip it on the sim and §3.5's argument, not on that
    run, and change this test in the same commit.
    """
    ...

def test_one_sided_ignores_shallow_swimming(simple_bathy):
    """Animal well above the seafloor is unpenalised: log p == 0 exactly.

    one_sided is a log-probability of admissibility, not a density, so it is
    capped at 0 and deliberately carries no -log(sigma_eff) normaliser.
    """
    ...

def test_one_sided_is_flat_above_the_seafloor(simple_bathy):
    """No attraction to any particular height off bottom: every depth above the
    seafloor scores identically, and better than any depth below it."""
    ...

def test_one_sided_penalises_below_seafloor(simple_bathy):
    """Being deeper than the seafloor is physically impossible -> penalty."""
    ...

def test_bottom_following_penalises_shallow_swimming(simple_bathy):
    """The two-sided mode also penalises being too far OFF the bottom -
    this is exactly the behavioural assumption, and the reason it is opt-in."""
    ...

def test_off_bottom_factor_shifts_the_optimum(simple_bathy):
    """factor=0.85 expects the animal at 85% of the seafloor depth."""
    ...

def test_unknown_mode_raises(simple_bathy):
    ...

def test_outside_raster_is_uninformative_in_both_modes(simple_bathy):
    """Off-raster must stay log p == 0 so the constraint cannot fabricate
    information where there is no bathymetry."""
    ...

def _bathy_with_sigmas(sigma_left: float, sigma_right: float, nodata_cols: slice | None=None):
    """Flat 10 m seafloor, EPSG:32610, sigma differing between the left and
    right halves so the spatial variation of sigma_eff is exercised."""
    ...
_LOW_SIGMA_XY = (-27.5, 0.0)
_HIGH_SIGMA_XY = (27.5, 0.0)

def test_normaliser_prefers_the_better_surveyed_cell():
    """Zero residual everywhere, sigma varying: the two-sided log-density must be
    HIGHER where the raster is better surveyed.

    Without the -log(sigma_eff) normaliser both cells score identically, so a
    spatially varying sigma silently pulls the particle cloud into the
    least-surveyed cells. Regression test for roadmap N1.
    """
    ...

def test_one_sided_admissible_cells_are_sigma_invariant():
    """The mirror of the test above, and the reason the normaliser is confined to
    the two-sided mode: an admissible particle must score 0 whatever the local
    survey quality, or the physical-only constraint acquires a spurious pull
    toward well-surveyed cells."""
    ...

def test_bottom_following_is_a_normalised_gaussian_log_density(simple_bathy):
    """The absolute scale is a Gaussian log-density referenced to sigma_ref, not
    a bare -0.5 z**2."""
    ...

def test_bottom_following_integrates_to_the_reference_normalisation(simple_bathy):
    """It is a true Gaussian density up to the fixed reference factor: integrating
    exp(log p) over observed depth gives sqrt(2*pi) * sigma_ref for any sigma_eff.
    """
    ...

def test_nodata_does_not_beat_a_matching_surveyed_cell():
    """Regression: the normaliser must not turn the no-data escape hatch into an
    attractor.

    The no-data branch is pinned at 0.0. An *absolute* Gaussian log-density
    (-log(sigma_eff) - 0.5*log(2*pi)) is negative for every realistic sigma_eff,
    so pairing the two would make an unsurveyed hole strictly better than a
    particle sitting exactly on a surveyed seafloor - the very failure roadmap N1
    exists to remove. Referencing to sigma_ref restores the ordering.
    """
    ...

def test_reference_sigma_is_a_pure_additive_constant(simple_bathy):
    """Changing sigma_ref shifts every in-raster cell by the same log-ratio, so it
    cannot alter the spatial weighting the normaliser is there to provide."""
    ...

def test_one_sided_violation_branch_is_unnormalised(simple_bathy):
    """one_sided keeps its pre-N1 shape exactly: -0.5*(residual/sigma_eff)**2."""
    ...

@pytest.mark.parametrize('mode', ['one_sided', 'bottom_following'])
def test_nodata_cell_is_exactly_zero(mode):
    """The non-finite path returns 0.0 exactly - it must not pick up the
    normalising constant, or off-raster particles would be penalised."""
    ...

def test_sigma_eff_is_evaluated_in_float64(simple_bathy):
    """sigma_eff must not inherit the raster's float32 precision.

    The rasters are float32, so before N1 sigma_eff was formed in float32 and
    -log(sigma_eff) would have been computed at that precision. `one_sided` is
    therefore unchanged in *form* but not bit-identical to the pre-N1 code:
    exact at extra_sigma_m=0.0, and up to ~4e-06 different at the production
    defaults. Pinned tightly enough that the float32 sigma_eff (~2e-08
    relative) fails; golden-value tests elsewhere must use a tolerance.
    """
    ...
