"""Sliding-window feature extraction tests."""
from __future__ import annotations
import numpy as np
import pandas as pd
import pytest
from anchor.ingest import io
from anchor.kinematics import core as K
from anchor.kinematics import features as F

@pytest.fixture(scope='module')
def ls_feat(ls_csv):
    ...

def test_window_metrics_non_empty(ls_feat):
    ...

def test_window_metrics_expected_columns(ls_feat):
    ...

def test_build_feature_matrix_shape(ls_feat):
    ...

def test_standardize_zero_mean_unit_std(ls_feat):
    ...

def _synthetic_frame(fs: float, seconds: float, freq_hz: float, amp_g: float, sigma_g: float, seed: int=0) -> pd.DataFrame:
    """Minimal frame with the columns ``summarize_window_metrics`` reads."""
    ...
LS_SMOOTH_SIGMA = 0.99
LS_MIN_PERIOD_S = 0.3
LS_PROMINENCE = 0.0621

def test_rest_windows_report_zero_tailbeat():
    """Rest windows of pure sensor noise must report no tail beat at all.

    Pre-N5 ``summarize_window_metrics`` recomputed a scale-free prominence per
    window, so this exact synthetic reported a mean ``tb_peak_count`` of 5.1 and
    a mean ``tb_freq_mean`` of 1.26 Hz across 58 rest windows.
    """
    ...

@pytest.mark.parametrize('beat_hz', [1.0, 1.5, 2.0, 2.5, 3.0])
def test_swimming_windows_report_the_beat_not_zero(beat_hz):
    """The windowed path must report a swimming animal anywhere in its band.

    This is the failure the first N5 pass shipped: the SNR gate was calibrated
    against a noise floor whose high-pass corner sat at 1.33 Hz, inside the
    leopard shark's own 1-3 Hz band, so the floor measured the animal. On this
    exact synthetic — the shipped LS settings, a clean beat at 0.08 g over
    sigma = 0.003 g — it zeroed 295 of 295 windows at 1.5, 2.0 and 2.5 Hz.
    Trading "rest looks like swimming" for "swimming looks like rest" is the
    worse of the two failures.
    """
    ...

def test_reported_tailbeat_does_not_depend_on_the_rest_duty_cycle():
    """Injecting rest must not change what the swimming windows report.

    The first N5 pass failed this too: because the gate's noise floor was
    contaminated by the tail beat, adding a quiet stretch to a record lowered
    the floor and opened the gate on windows that had been zeroed, so the
    feature depended on how much the animal happened to rest.
    """
    ...

def test_snr_gate_zeroes_a_window_below_the_deployment_noise_floor():
    """The gate must zero a window carrying less in-band power than the tag's noise.

    The gate is keyed to the deployment's measured tail-beat-band noise floor,
    so it holds even when the configured prominence is far too low for the tag
    it is used on: here the record's floor is set by sigma = 0.003 g of sensor
    noise over 98% of its length, the last 20 s are a near-silent stretch
    carrying a 0.0008 g ripple, and ``prominence`` is mis-set to 0.001 g. The
    picker finds that ripple; the gate discards it because the window holds less
    power than sensor noise alone would. The silent stretch is kept to 2% of the
    record so it does not itself set the 5th-percentile floor.
    """
    ...

def test_snr_gate_still_fires_on_a_record_with_a_dropout():
    """A 10% zero-padded gap must not silently switch the gate off.

    The gate is keyed to ``estimate_noise_floor_g``, and that estimator used to
    return exactly 0.0 once 5% of the record was flat after high-passing, which
    a dropout, a zero-padded gap or a NaN run all are. ``summarize_window_metrics``
    reads 0.0 as "floor unknown" and disables the gate, so on the record below
    — the same near-silent 0.0008 g ripple and mis-set 0.001 g prominence as
    the test above, plus a 100 s gap — the three quiet windows reported 7 / 7 /
    6 peaks at 1.50 Hz instead of nothing. Measured with the floor forced to
    0.0; with the floor measured on the good 90% (0.00273 g, identical to the
    gap-free record) they report 0.
    """
    ...

def test_snr_gate_does_not_reject_intermittent_beating():
    """Burst-and-coast must be reported, not zeroed.

    This is the second way the gate produced "swimming looks like rest". Keyed
    to ``P / (2*sqrt(2))`` — the standard deviation of a sinusoid that *fills*
    the window — it demanded ``1/sqrt(d)`` times the amplitude the prominence
    test demands, so at a 30% within-window duty cycle it zeroed 100% of windows
    for beats at 1.29x, 1.61x and 1.93x the configured prominence, all of which
    the picker resolves at 2.03-2.04 Hz with the gate off. Burst-and-coast is
    the canonical elasmobranch gait, so this is not a corner case.
    """
    ...

def test_snr_gate_factor_stays_inside_its_non_binding_bound():
    """The gate constant must stay below the bound its docstring derives.

    A window holding two peaks the prominence test accepted contains at least
    one beat period of amplitude ``P/2``, so its standard deviation is at least
    ``sqrt(band_noise**2 + (P/2)**2 / 2 * min_period_s / window_s)``. With
    ``P = 12 * band_noise`` that is ``sqrt(1 + 18 * min_period_s / window_s)``
    times the floor — 1.13 at the 20 s default window. Above that the gate can
    start rejecting real beating, which is the failure this file exists to pin.
    """
    ...

def test_tailbeat_frequency_is_sampling_rate_invariant():
    """The same swimming animal must yield the same TBF at 25 Hz and 50 Hz.

    Cross-species pooling is only defensible if the feature does not depend on
    the tag's logging rate. ``smooth_sigma`` is in samples, so it has to be
    derived per rate — ``smooth_sigma_for_band`` is the rule the species YAMLs
    are built with, and it is what makes this invariance hold at 2.5 Hz as well
    as at 1.2 Hz.
    """
    ...

def test_no_tailbeat_is_recorded_as_zero_not_dropped(ls_feat):
    """A window with no detectable beat must survive into the feature matrix.

    ``build_feature_matrix`` drops any row with a NaN in ``DEFAULT_FEATURES``,
    so emitting NaN for "fewer than two peaks" silently deleted exactly the
    windows where the animal was not beating its tail — 5 of 110 on the
    leopard-shark fixture and 9 of 98 on the bat-ray one, with the shipped
    configs. Zero and NaN both mean "no tail beat"; only one of them reaches the
    classifier.
    """
    ...
