"""Locomotion-mode dispatch + size-aware DBA correction.

Synthetic-signal tests for W2:
- axial_undulator and pectoral_oscillator produce expected columns.
- pectoral_oscillator stroke-frequency convention = 2 × cycle frequency.
- add_rotation_corrected_dba agrees with uncorrected VeDBA on a pure-translation
  signal (no rotation → no correction) and diverges when strong rotation is
  present.
"""
from __future__ import annotations
import numpy as np
import pandas as pd
import pytest
from anchor.kinematics import core as K, locomotion as L

def _make_oscillation(fs: float, duration_s: float, freq_hz: float, amplitude: float=1.0, axis: str='accY') -> pd.DataFrame:
    """Single-axis sinusoid with other axes quiet. Dynamic/static split is
    trivially the sine wave itself (lowpass near DC for a well above-cutoff
    signal)."""
    ...

def test_axial_undulator_recovers_frequency():
    ...

def test_pectoral_oscillator_emits_stroke_frequency():
    ...

def test_dispatch_rejects_unknown_mode():
    ...

def test_dispatch_routes_both_modes():
    ...

def _full_pipeline_fixture(fs: float, duration_s: float, translation_amp: float, rotation_rate_hz: float):
    """Construct static/dynamic/vedba/pitch/roll directly so the rotation
    correction is tested in isolation from the lowpass filter's leakage
    behavior."""
    ...

def test_rotation_corrected_dba_agrees_on_pure_translation():
    """With zero rotation, vedba_corrected should be ~vedba (no correction)."""
    ...

def test_rotation_corrected_dba_diverges_on_heavy_rotation():
    """With strong rotation, vedba_corrected should fall noticeably below vedba
    (body-length lever arm injects substantial vedba_rot)."""
    ...

def test_rotation_corrected_dba_requires_prerequisites():
    ...

def test_rotation_corrected_dba_requires_vedba():
    ...

def _noisy_rotation_fixture(fs: float, duration_s: float, seed: int=0):
    """The ``scripts/repro_dba_noise.py`` synthetic, in fixture form.

    3.5 m body, 0.5 Hz tail beat at 0.05 g, a slow 0.1 Hz / 0.2 rad body roll
    and sigma = 0.01 g of white accelerometer noise on every axis.
    """
    ...

def test_rotation_correction_survives_sensor_noise():
    """The rotational term must stay bounded by the total DBA under real noise.

    Two chained bare ``np.gradient`` calls amplify white noise by roughly
    ``fs**4``; on this synthetic the pre-N5 code returned a ``vedba_rot`` mean
    2.54x the ``vedba`` mean and clipped ``vedba_trans`` to zero on 88.3% of
    samples. The band-limited derivative brings that to 0.80x and 35%. The
    noise-free tests above pass either way, which is why they missed it.
    """
    ...

def test_rotation_correction_records_the_clip():
    """The zero-clip is recorded, not silent."""
    ...

def _rotation_bias(fs: float, roll_hz: float, split_cutoff_hz: float, deriv_cutoff_hz: float, body_length_m: float, beat_hz: float, duration_s: float=600.0, roll_amp_rad: float=0.2, noise_sigma_g: float=0.01, seed: int=0) -> float:
    """Relative error of ``vedba_rot`` against the closed-form rotational term.

    Mirrors ``scripts/repro_dba_noise.py``. The yardstick is built from the roll
    amplitude the pipeline *recovered*, not the amplitude injected, so the
    static/dynamic lowpass carries none of the blame and what is left is the
    Savitzky-Golay band limit alone.
    """
    ...

@pytest.mark.parametrize('ratio, lo, hi', [(0.2, -0.1, 0.0), (0.5, -0.48, -0.34), (1.0, -0.95, -0.86)])
def test_rotation_derivative_bias_across_the_retained_band(ratio, lo, hi):
    """``vedba_rot`` is biased low, increasingly so towards the cutoff.

    ``test_rotation_correction_survives_sensor_noise`` and the headline table of
    ``scripts/repro_dba_noise.py`` both probe roll = 0.1 Hz against a 0.5 Hz
    cutoff — 0.2x, the single point in the retained band where the polyorder-2
    Savitzky-Golay differentiator is nearly flat. It is not flat elsewhere: its
    gain relative to the ideal differentiator falls to 0.30 at the cutoff and
    ``vedba_rot`` carries that gain *squared* (centripetal goes as ``omega**2``,
    tangential differentiates twice). These bounds pin the resulting bias so
    that a change of window rule or polyorder cannot move it silently.
    """
    ...

@pytest.mark.parametrize('flap, lo, hi', [(0.5, -0.46, -0.34), (1.0, -0.95, -0.85)])
def test_bat_ray_flap_is_lost_at_the_species_static_dynamic_split(flap, lo, hi):
    """The batoid case: at ``lowpass_cutoff_hz = 1.0`` the flap band is gutted.

    bat_ray.yaml's static/dynamic split is 1.0 Hz and the documented pectoral
    flap band is 0.5-2 Hz, so passing that split as the derivative cutoff puts
    the whole flap band at 0.5x the cutoff and above, where the rotational term
    is under-estimated by 40-91%. This is the configuration the
    rotation-corrected-DBA-on-a-batoid claim rests on, so the defect is pinned
    here rather than described in prose.
    """
    ...

@pytest.mark.parametrize('flap', [0.5, 1.0])
def test_bat_ray_flap_is_recovered_when_the_derivative_cutoff_is_5x(flap):
    """...and the fix is a cutoff choice, not a change of differentiator.

    ``lowpass_cutoff_hz`` on ``add_rotation_corrected_dba`` is the derivative's
    band limit and need not equal the static/dynamic split. At 5x the rotation
    frequency the polyorder-2 gain is 0.99, so the squared bias is within ~10%.
    """
    ...
