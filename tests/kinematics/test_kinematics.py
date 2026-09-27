"""Kinematic derivation tests: VeDBA/ODBA identities, tailbeat on a known sine."""
from __future__ import annotations
import inspect
import numpy as np
import pandas as pd
import pytest
from anchor.ingest import io
from anchor.kinematics import core as K

@pytest.fixture(scope='module')
def ls_processed(ls_csv):
    """LS slice parsed + split into static/dynamic at 1 Hz cutoff."""
    ...

def test_vedba_nonneg(ls_processed):
    ...

def test_odba_greater_equal_vedba(ls_processed):
    """ODBA (sum of abs) >= VeDBA (L2 norm of same vector) — algebraic identity."""
    ...

def test_static_plus_dynamic_equals_raw(ls_processed):
    ...

def test_pitch_roll_range(ls_processed):
    ...

def test_lowpass_preserves_dc():
    """Lowpassing a constant should return that constant."""
    ...

def test_tailbeat_recovers_synthetic_sine():
    """A 2 Hz sine at 100 Hz sampling should yield ~2 Hz instantaneous freq."""
    ...

def test_add_tailbeat_columns_adds_expected(ls_processed):
    ...

def _rest_segment(fs: float, seconds: float=120.0, sigma_g: float=0.003, seed: int=0) -> np.ndarray:
    """A rest segment carrying nothing but white sensor noise."""
    ...

def test_rest_segment_yields_no_tailbeat_peaks():
    """Pure sensor noise must not look like swimming.

    The pre-N5 fallback ``prominence = 0.5 * nanstd(smoothed)`` is scale-free,
    so it rescales itself onto whatever the segment contains: on this exact
    synthetic it found 127 peaks at a mean 1.22 Hz.
    """
    ...

def test_noise_floor_recovers_injected_sigma():
    """The estimator must report the sigma it was given, not the signal's."""
    ...

@pytest.mark.parametrize('beat_hz', [1.5, 2.0, 2.5, 3.0])
def test_noise_floor_is_not_contaminated_by_a_fast_tail_beat(beat_hz):
    """The floor must measure the tag, not the animal, anywhere in the band.

    The first N5 implementation high-passed with
    ``x - gaussian_filter1d(x, smooth_sigma)``, whose corner is
    ``fs / (2*pi*smooth_sigma)`` = 1.33 Hz at the leopard shark's fs = 25 and
    smooth_sigma = 3.0 — inside its own documented 1-3 Hz band. On this exact
    synthetic it returned 0.041-0.065 g against a true 0.003 g, a 14-22x
    overestimate, and the gate built on it zeroed 295 of 295 windows of a
    cleanly swimming animal.
    """
    ...

def test_noise_floor_does_not_depend_on_how_much_the_animal_rested():
    """Duty cycle must not move the floor: it is a property of the tag.

    With the corner inside the locomotion band the estimate depended on the
    fraction of the record spent resting, which is the same non-transferability
    N5 exists to remove, merely moved from per-window to per-deployment scale.
    """
    ...

def _dropout_record(kind: str, fs: float=25.0, seconds: float=2000.0, sigma_g: float=0.003) -> np.ndarray:
    """Sigma-``sigma_g`` sensor noise with a flat or missing stretch in it."""
    ...

@pytest.mark.parametrize('kind', ['zeroed', 'nan', 'half_zeroed'])
def test_noise_floor_ignores_dropouts_and_nan_runs(kind):
    """A dropout must not collapse the floor to 0.0 = "unknown".

    The floor is the 5th-percentile block scale, and a dropout, a zero-padded
    gap or a NaN run (median-filled, hence constant) has a high-passed MAD of
    exactly zero — so taking the quantile over *all* blocks returned exactly
    0.0 as soon as 5% of the record was flat. Measured on this record at
    sigma = 0.003 g: 0.00287 clean, 0.0 with 10% zeroed, 0.0 with 10% NaN.
    Downstream 0.0 means "unknown", so that silently disabled the whole SNR
    gate in ``features`` and made the derived-prominence path raise. Blocks
    that are flat before or after the high-pass are now dropped before the
    quantile, and the surviving blocks are measured on their real samples.
    """
    ...

def test_noise_floor_is_zero_only_when_no_block_is_measurable():
    """0.0 stays reserved for "nothing here was measurable"."""
    ...

def test_noise_floor_warns_about_the_blocks_it_dropped(caplog):
    """Dropping blocks is a data-quality fact the log must carry."""
    ...

def test_noise_floor_is_measured_on_each_block_s_real_samples():
    """A half-missing block must report the tag, not the median fill.

    The fill is needed to run the Butterworth (it cannot step over a NaN) but
    it is a constant, so a MAD taken over the *filled* block is pulled towards
    zero in proportion to how much of the block was filled — and the estimator
    then selects the low tail of exactly that statistic. This record NaNs the
    first half of each of blocks 100-199: every one of them is still 50% real
    data, so it is neither flat nor all-NaN and no whole-block rejection rule
    catches it. Measured with a MAD over the filled block, the floor comes back
    0.00090 against a true 0.00287, a 3.2x under-estimate; measured over each
    block's finite samples it is 0.00283.
    """
    ...

@pytest.mark.parametrize('missing', [0.3, 0.4, 0.5])
def test_noise_floor_survives_scattered_dropout(missing):
    """Uniformly scattered NaN must still yield a usable floor, never 0.0.

    Scattered NaN leaves no block untouched, so a per-block finite-*fraction*
    cutoff rejects the whole record at once and returns 0.0 = "unknown" — which
    disables the SNR gate in ``features`` and makes ``detect_tailbeat_peaks``
    raise, i.e. the very collapse this estimator was repaired to prevent, in a
    record that is 50-70% good data. Taking each block's MAD over its own
    finite samples needs no such cutoff. The residual bias is downward and
    bounded by the ``sqrt(p)`` amplitude loss the constant fill imposes:
    measured against this record's clean 0.00287, 0.00248 / 0.00232 / 0.00219
    at 70 / 60 / 50% finite.
    """
    ...

def test_derived_prominence_survives_a_partial_dropout():
    """``prominence=None`` must still derive a usable threshold through a gap.

    ``anchor/trajectory/axy_ingest.py`` takes this path on every deployment, so
    a flat stretch broke it two ways depending on where the flat blocks fell:
    with the quantile landing on a flat block the floor was exactly 0.0 and
    ``detect_tailbeat_peaks`` raised — blaming a "too short, constant, or
    all-NaN" signal when 90% of it was good — and with the quantile landing on
    a block the high-pass rang into, it was 3.3e-129 g on this record, giving a
    "prominence" of 4e-128 g that would accept sensor noise as swimming. Both
    are the same defect: flat blocks were allowed to set a low-tail statistic.
    """
    ...

def test_explicit_prominence_is_absolute():
    """Scaling the signal must change the peak count for a fixed prominence.

    Under the old scale-free rule the count was invariant to amplitude, which
    is exactly why a rest window and a burst window looked alike.
    """
    ...

def test_default_min_period_matches_config_default():
    """One source of truth: core's fallback mirrors ``TailbeatConfig``.

    Pre-N5 the value was 0.2 in ``core``, 0.25 in ``features``, 0.4 in
    ``locomotion`` and 0.3 in the configs.
    """
    ...

def _species_yaml(name: str) -> dict:
    ...

def _fixture_axis(fixture: str, schema: str, cutoff: float, fs: float, axis: str) -> np.ndarray:
    ...

@pytest.mark.parametrize('name,fixture,schema,cutoff,band_top', SPECIES_CASES)
def test_config_smooth_sigma_puts_the_corner_at_the_band_top(name, fixture, schema, cutoff, band_top):
    """``smooth_sigma`` is in samples, so it must be derived from fs.

    A single shared 3.0 put the Gaussian corner at 1.33 Hz on the 25 Hz tags —
    inside the leopard shark's 1-3 Hz band — and at 2.65 Hz on the 50 Hz ones.
    """
    ...

@pytest.mark.parametrize('name,fixture,schema,cutoff,band_top', SPECIES_CASES)
def test_config_prominence_matches_its_documented_derivation(name, fixture, schema, cutoff, band_top):
    """Each YAML prominence is ``noise_floor_prominence`` on that fixture.

    The comment in every species YAML states this derivation; this test is what
    stops the constant and the comment drifting apart. It also pins the origin:
    the number is a *noise-floor* measurement above the locomotion band, not the
    ADC quantisation step the first N5 pass claimed it was.
    """
    ...

@pytest.mark.parametrize('name,fixture,schema,cutoff,band_top', SPECIES_CASES)
def test_beat_at_the_top_of_the_documented_band_is_detected(name, fixture, schema, cutoff, band_top):
    """A beat at the top of each species' own TBF range must be reported.

    This is the false-negative side of the threshold, and it is the side the
    first N5 pass got wrong: with the corner inside the band, a fixed absolute
    prominence imposed a hard ~1.6 Hz ceiling on reported TBF for a 0.08 g beat,
    truncating the upper two thirds of the leopard shark's documented range and
    feeding that truncation into U = K * L * TBF.
    """
    ...

def _beats_then_silence(fs=25.0, f_beat=2.0, n_beats=20, silence_s=120.0):
    """A clean beat train followed by a long flat stretch."""
    ...

def test_forward_fill_expires_after_the_stale_bound():
    ...

def test_unbounded_forward_fill_is_still_reachable():
    """``max_stale_periods=None`` restores the behaviour the bound replaces."""
    ...

def test_the_stale_floor_keeps_a_slow_beat_alive_between_its_own_peaks():
    """A 0.4 Hz beat has a 2.5 s period; three of them is under the 10 s floor.

    Without the floor, ``3 / f`` alone would be 7.5 s — still enough here, but a
    0.2 Hz beat's peaks are 5 s apart and any species band bottom below
    ``3 / TB_STALE_FLOOR_S`` would expire inside its own cycle. The floor is
    what makes the rule safe for the slowest documented beat in the fleet.
    """
    ...

def test_the_bound_is_measured_from_the_peak_not_from_the_block():
    """Two separated beat trains: the gap goes NaN, the second train recovers."""
    ...
