"""Kinematic derivations on accelerometer + magnetometer time series.

Static/dynamic split, VeDBA, ODBA, jerk, pitch/roll, and tailbeat peak picking.
The lowpass filter, dynamic-acceleration split, VeDBA, jerk, and tailbeat
helpers are lifted from ``notebooks/AXY_Kinematics.ipynb`` with no semantic
change. ODBA and pitch/roll are new.
"""
from __future__ import annotations
import logging
from functools import lru_cache
from typing import Optional
import numpy as np
import pandas as pd
from scipy.signal import butter, filtfilt, find_peaks, savgol_filter, sosfiltfilt, sosfreqz
from scipy.ndimage import gaussian_filter1d
DEFAULT_MIN_PERIOD_S = 0.3
NOISE_FLOOR_QUANTILE = 0.05
NOISE_FLOOR_WINDOW_S = 2.0
MIN_BLOCK_FINITE_SAMPLES = 8
NOISE_BAND_MARGIN = 2.0
PROMINENCE_NOISE_FACTOR = 12.0
TB_STALE_PERIODS = 3.0
TB_STALE_FLOOR_S = 10.0
DEFAULT_ROTATION_CUTOFF_HZ = 1.0

def lowpass_filter(x: np.ndarray, cutoff: float, fs: float, order: int=2) -> np.ndarray:
    """Zero-phase Butterworth lowpass.

    Parameters mirror the notebook — ``cutoff`` in Hz, ``fs`` sampling rate in Hz.
    """
    ...
DYN_BEAT_FRACTION_WARN = 0.8
DYN_BEAT_FRACTION_FAIL = 0.5

def dynamic_fraction(f_hz: float, cutoff_hz: float, order: int=2) -> float:
    """Share of a sinusoid at ``f_hz`` that :func:`add_dynamic_acceleration` keeps.

    ``lowpass_filter`` runs a Butterworth of ``order`` forwards and backwards,
    so the static part has gain ``|H|^2 = 1 / (1 + (f/fc)^(2 order))`` and the
    dynamic part, ``x - static``, keeps ``1 - |H|^2``. At the bat ray's 1.0 Hz
    cutoff a 0.5 Hz flap keeps 6 %.
    """
    ...

def add_dynamic_acceleration(df: pd.DataFrame, cutoff: float, fs: float) -> pd.DataFrame:
    """Split each of accX/Y/Z into ``{ch}_static`` (lowpass) and ``{ch}_dyn``."""
    ...

def add_vedba(df: pd.DataFrame) -> pd.DataFrame:
    """VeDBA = sqrt(x_dyn^2 + y_dyn^2 + z_dyn^2)."""
    ...

def add_odba(df: pd.DataFrame) -> pd.DataFrame:
    """ODBA = |x_dyn| + |y_dyn| + |z_dyn| (Wilson et al. 2006)."""
    ...

def add_jerk(df: pd.DataFrame, fs: float) -> pd.DataFrame:
    """Jerk magnitude = ||d(accel_dyn)/dt||."""
    ...
_G = 9.80665
CLIP_WARN_FRACTION = 0.1

def _savgol_window(fs: float, cutoff_hz: float, n: int, polyorder: int=2) -> int:
    """Odd Savitzky-Golay window spanning one period of ``cutoff_hz``.

    ``W = fs / cutoff_hz`` ties the derivative's bandwidth to the same cutoff
    that produced the static/dynamic split. It is a *band-limiter*, not a
    pass-through. The gain of a polyorder-2 SG differentiator relative to the
    ideal ``2*pi*f`` differentiator, measured on unit sinusoids at this window
    length, is

        f / cutoff       0.1    0.2    0.4    0.6    0.8    1.0
        gain (order 2)   0.990  0.960  0.848  0.682  0.488  0.295
        gain (order 4)   1.000  0.999  0.995  0.977  0.933  0.852

    (fs = 50, cutoff = 0.5, W = 101; the amplitude of the differentiated
    sinusoid over the ideal ``2*pi*f``, edge samples excluded. The response
    depends on the window only through ``f * W / fs``, so fs = 25 /
    cutoff = 1.0 gives 0.990 / 0.961 / 0.851 / 0.688 / 0.497 / 0.305 at
    polyorder 2 — the same curve to within 0.01, the residual difference being
    that rounding ``W`` up to an odd integer makes it 101 rather than 100 at
    fs = 50, i.e. ``f * W / fs`` = 1.01 against 1.00 at the cutoff.)
    An earlier version of this docstring claimed unit gain below ``fs / W``;
    that is wrong by a factor of three at the cutoff itself. What the
    attenuation does to ``vedba_rot``, and why polyorder stays at 2 anyway, is
    documented in :func:`add_rotation_corrected_dba`.

    The window is clamped to the array length and to the smallest odd length
    SciPy accepts for ``polyorder``.
    """
    ...

def _band_limited_derivative(x: np.ndarray, dt: float, window: int, polyorder: int=2) -> np.ndarray:
    """First derivative of ``x`` — SG when the window fits, ``np.gradient`` else."""
    ...

def add_rotation_corrected_dba(df: pd.DataFrame, body_length_m: float, fs: float, lowpass_cutoff_hz: Optional[float]=None) -> pd.DataFrame:
    """Size-aware DBA decomposition per Martín-López et al. 2022.

    For large-bodied aquatic animals (> ~1.5 m), a substantial fraction of the
    dynamic-acceleration signal at the tag originates from body rotations
    (pitch/roll) rather than translational stroke acceleration, because the
    tag sits at a lever arm from the rotation axis and rotational motion
    injects centripetal (ω²·r) and tangential (α·r) components into the
    accelerometer. ODBA/VeDBA without rotation correction overestimate
    translational activity for large sharks and underestimate it for small
    animals — so they fail to serve as a universal energy-expenditure proxy.

    This helper computes:

    - ``omega_mag``    — body angular velocity magnitude from pitch/roll rates
                        (rad/s). Angular velocity about yaw is not observable
                        from accel alone.
    - ``alpha_mag``    — body angular acceleration magnitude (rad/s²).
    - ``vedba_rot``    — estimated rotational contribution to tag-frame
                        acceleration magnitude, expressed in g:
                        ``body_length * sqrt((ω²)² + α²) / g``.
                        The lever arm is approximated by body length; for
                        caudal tags the effective lever is shorter but this
                        assumption is standard in the large-body DBA
                        literature.
    - ``vedba_trans``  — translational-only VeDBA ≈ max(vedba - vedba_rot, 0).
    - ``vedba_corrected`` — alias for ``vedba_trans`` for downstream use.
    - ``vedba_trans_clipped`` — bool, True where ``vedba - vedba_rot`` was
                        negative and had to be clipped to zero. The clip used
                        to be silent, which hid the fact that the rotational
                        term could exceed the *total* measured DBA; a high
                        clipped fraction means the estimate is not usable.

    ω and α are obtained with a Savitzky-Golay derivative band-limited by
    ``lowpass_cutoff_hz`` (defaults to :data:`DEFAULT_ROTATION_CUTOFF_HZ`).
    Chaining bare ``np.gradient`` calls, as this function did previously,
    differentiates twice with no smoothing and so amplifies white sensor noise
    by roughly ``fs**2`` — 2500 at 50 Hz — which put ``vedba_rot`` about three
    times above the total signal on a realistic synthetic (see
    ``scripts/repro_dba_noise.py``).

    **In-band bias, and the cutoff rule that controls it.** The band limit is
    not flat over the band it retains, and ``vedba_rot`` carries its gain
    *squared*: the centripetal term goes as ``omega**2`` and the tangential
    term applies the same differentiator twice, so both scale as
    ``G(f/cutoff)**2`` with ``G`` the polyorder-2 gain tabulated in
    :func:`_savgol_window`. A rotation at ``f`` is therefore under-estimated by
    roughly ``G**2 - 1``: -2% at 0.1x the cutoff, -8% at 0.2x, -28% at 0.4x,
    -53% at 0.6x, -76% at 0.8x and -91% at the cutoff itself. Measured end to
    end by ``scripts/repro_dba_noise.py`` (tables 2 and 3), with the yardstick
    built from the *recovered* roll amplitude so the static/dynamic lowpass
    carries none of the blame, and the tag's 0.01 g of sensor noise left on:

        white shark (fs 50, cutoff 0.5, L 3.5 m, roll ±0.20 rad)
            roll 0.05 / 0.10 / 0.20 / 0.30 / 0.40 / 0.50 Hz = 0.1-1.0x cutoff
            → +29.9 / -3.8 / -28.5 / -53.9 / -76.5 / -91.3 %
        bat ray (fs 25, cutoff 1.0, L 1.0 m, flap ±0.20 rad)
            flap 0.5 / 0.7 / 1.0 Hz → -40.0 / -64.8 / -90.7 %

    From 0.2x up the measurement tracks ``G**2 - 1``. The 0.1x row does not,
    and is positive rather than -2%, because there the true rotational term is
    only 0.005 g: sensor noise and the tail beat that leaks into the static
    channel dominate it, so *both* ends of the band are untrustworthy, the low
    end from noise and the high end from attenuation.

    So ``lowpass_cutoff_hz`` is not "the band you may analyse"; it is where the
    rotation estimate has lost two thirds of its amplitude, and the species'
    static/dynamic split is the wrong value for it whenever the rotation of
    interest sits near that split — as the bat ray's 0.5-2 Hz pectoral flap does
    against its 1.0 Hz split. **To recover a rotation at frequency ``f`` to
    within about 10%, pass ``lowpass_cutoff_hz >= 5 * f``.** On the bat-ray
    case that turns -40.0% (0.5 Hz), -64.8% (0.7 Hz) and -90.7% (1.0 Hz) into
    -4.2%, -6.2% and -6.6%.

    **Why polyorder stays at 2.** Polyorder 4 flattens the in-band response
    (0.995 at 0.4x the cutoff, 0.852 at the cutoff) and does fix the bat-ray
    0.5 Hz case, -40.0% → +1.0% (1.0 Hz is still -26.3%). It also re-admits
    exactly what the band limit exists to exclude: on the
    ``scripts/repro_dba_noise.py`` synthetic it takes ``vedba_rot`` from 0.80x
    to 1.90x the total VeDBA, the clipped fraction from 35.2% to 78.9% and the
    error against the closed-form truth from -3.3% to +129.3%, and on the
    white-shark sweep above it over-estimates by +128.0% at 0.2x the cutoff and
    +761.5% at 0.1x, because its wider passband lets the sensor noise and the
    leaked tail beat through into the roll derivative. The trade is therefore
    bias against variance, and it is not symmetric in consequence: polyorder 2
    under-estimates a fast rotation, polyorder 4 over-estimates a slow or noisy
    one by an order of magnitude. The asymmetry settles it: ``vedba_rot`` is
    *subtracted*, so an over-estimate clips ``vedba_trans`` to zero and
    destroys the quantity being measured, while an under-estimate degrades
    gracefully back towards uncorrected VeDBA. Polyorder 2 with a cutoff set
    well above the rotation of interest is the shipped configuration, and the
    bias above is its price.

    Original ``vedba`` and ``odba`` are left unmodified for back-compat.
    """
    ...

def add_pitch_roll(df: pd.DataFrame) -> pd.DataFrame:
    """Pitch and roll (radians) derived from the static-accel vector.

    Convention (tag frame): X forward, Y right, Z down.
      pitch = atan2(-X_static, sqrt(Y^2 + Z^2))
      roll  = atan2( Y_static, Z_static)
    """
    ...

def _gaussian_pass_gain(smooth_sigma: float) -> float:
    """White-noise gain of ``gaussian_filter1d`` at ``smooth_sigma``.

    White noise of standard deviation ``s`` leaves ``gain * s`` in the smoothed
    signal. Read off the actual impulse response, so it tracks SciPy's kernel
    truncation exactly rather than an idealised Gaussian.
    """
    ...

def smooth_sigma_for_band(fs: float, min_period_s: float=DEFAULT_MIN_PERIOD_S) -> float:
    """Gaussian ``smooth_sigma`` (in samples) for a species' tail-beat band.

    ``gaussian_filter1d``'s sigma is in *samples*, so the same YAML value is a
    different filter on a 25 Hz and a 50 Hz tag, and a value chosen without
    reference to ``fs`` can put the corner inside the band it is meant to pass.
    That is not a cosmetic units issue: ``smooth_sigma = 3.0`` at fs = 25 has
    its -3 dB corner at 1.3 Hz, so it attenuates a 3 Hz leopard-shark tail beat
    by 13x. A fixed absolute prominence then imposes a hard ceiling on reported
    tail-beat frequency — the upper two thirds of the species' own documented
    range — and that truncation propagates into ``U = K * L * TBF``.

    ``min_period_s`` already names the top of the resolvable band (the peak
    picker uses ``distance = fs * min_period_s``), so the smoother is placed
    with its corner exactly there: everything the picker can resolve passes at
    >= 1/sqrt(2) gain, everything faster is attenuated. The result depends on
    ``fs`` and ``min_period_s`` only through their product, so a config derived
    from this rule is sampling-rate invariant.
    """
    ...

@lru_cache(maxsize=32)
def _quiet_quantile_bias(block: int, quantile: float) -> float:
    """Expected value of the quiet-quantile MAD statistic on unit Gaussian noise.

    Selecting the ``quantile`` quietest of many noisy per-block MAD estimates is
    biased low — the selection is the point (it is what rejects the parts of the
    record where the animal is moving), but the bias would otherwise propagate
    straight into the prominence, since a per-block MAD over ``block`` samples
    has a relative standard error of order ``1/sqrt(block)``.

    Rather than carry a hand-fitted constant, the bias is measured by running
    the identical statistic on synthetic unit-variance Gaussian noise. It is a
    population quantile of the MAD sampling distribution, so it depends only on
    the block length and the quantile, not on how many blocks the real record
    has; 4096 synthetic blocks estimate it to well under a percent. The seed is
    fixed, so the correction is deterministic and the estimator is reproducible.
    """
    ...

def estimate_noise_floor_g(signal: np.ndarray, fs: float, min_period_s: float=DEFAULT_MIN_PERIOD_S, band_margin: float=NOISE_BAND_MARGIN, window_s: float=NOISE_FLOOR_WINDOW_S, quantile: float=NOISE_FLOOR_QUANTILE) -> float:
    """Broadband sensor-noise standard deviation of a tail-beat axis, in g.

    Two independent contaminations have to be kept out of this number, and the
    estimator addresses them separately:

    * **the tail beat itself** — the signal is high-passed with a 4th-order
      Butterworth at ``band_margin / min_period_s``, an octave above the fastest
      resolvable beat, so no part of the locomotion band reaches the estimate;
    * **flow and manoeuvre noise** — a robust MAD is taken over ``window_s``
      blocks and the ``quantile`` quietest blocks are kept, so a record that is
      swimming most of the time is measured on the part of it that is not.

    The result is de-biased for the quiet-block selection (see
    :func:`_quiet_quantile_bias`) and divided by the high-pass filter's own
    white-noise gain, read off its frequency response, so it is expressed as a
    *broadband* sigma comparable across sampling rates: on white noise it
    returns the sigma it was given to within a few percent, at any sampling
    rate and with any tail beat superimposed.

    **Degenerate blocks are excluded, not averaged in.** A dropout, a
    zero-padded gap or a NaN run (median-filled above, hence constant) has a
    high-passed MAD of exactly zero, and the ``quantile`` is by construction the
    *low* tail — so taking it over all blocks made the estimate collapse to 0.0
    as soon as ``quantile`` of the record was flat, which at the 5% default is
    a 5% dropout. Measured on ``default_rng(0)`` noise, fs = 25, 2000 s,
    sigma = 0.003 g, ``min_period_s = 0.3``: the clean record gave 0.00287, the
    same record with its first 10% zeroed or NaN'd gave exactly 0.0. Because
    0.0 means "unknown" downstream, that silently disabled the SNR gate in
    :mod:`anchor.kinematics.features` and made :func:`detect_tailbeat_peaks`
    raise on the ``prominence=None`` path. Exactly 0.0 was not even the worst
    case: where the quantile landed instead on a block the high-pass rang into
    at the edge of the gap, the same 10% gap over a 2 Hz beat returned
    3.3e-129 g — a "prominence" of 4e-128 g, which accepts sensor noise as
    swimming and warns about neither. Blocks that are flat before *or* after
    the high-pass are therefore dropped before the quantile is taken, and
    dropping any is logged. The same record now returns 0.00287 clean, 0.00286
    with 10% zeroed, 0.00286 with 10% NaN and 0.00288 with 50% zeroed — i.e. a
    record that is 95% good yields the floor its good part supports, unchanged.

    **A block's scale is measured over that block's own finite samples**, not
    over the median fill. The fill is needed to run the filter — a Butterworth
    cannot step over a NaN — but it is a constant, so including it in the MAD
    reports the fill rather than the tag. The effect is not small and it is not
    confined to whole missing blocks: on the same record with the first half of
    each of blocks 100-199 NaN'd (each block still 50% real data, so not
    constant, and the flat-block test does not catch it), a MAD over the filled
    block gives 0.00090 against a true 0.00287 — a 3.2x under-estimate that
    lands squarely on the low tail the quantile selects. Measured over the
    block's finite samples the same record gives 0.00283.

    The residual bias of that choice is **downward and bounded**, because
    filling a fraction ``1 - p`` of a block with a constant attenuates the
    high-passed amplitude at the surviving samples by roughly ``sqrt(p)``.
    Measured on uniformly scattered NaN, as a ratio to the same record's clean
    0.00287: 0.00248 at 70% finite (0.86), 0.00232 at 60% (0.81), 0.00219 at
    50% (0.76). A heavily gapped record therefore *under*-states the tag noise,
    which makes the SNR gate in :mod:`anchor.kinematics.features` more
    permissive — not the failure this estimator exists to prevent, which was
    the gate silently switching off altogether.

    Returns 0.0 only when *no* block survives: an empty, wholly constant, or
    too-short-to-filter signal, or one so sparse that no ``window_s`` block
    retains :data:`MIN_BLOCK_FINITE_SAMPLES` real samples (at the 2 s / 25 Hz
    default, more than ~84% missing). Callers must treat 0.0 as "unknown",
    never as a usable threshold.
    """
    ...

def noise_floor_prominence(signal: np.ndarray, fs: float, smooth_sigma: float=2.0, min_period_s: float=DEFAULT_MIN_PERIOD_S, factor: float=PROMINENCE_NOISE_FACTOR) -> tuple[float, float]:
    """``(prominence_g, band_noise_g)`` derived from the signal's noise floor.

    ``band_noise_g`` is the standard deviation white sensor noise leaves inside
    the smoothed tail-beat band. ``prominence_g`` is ``factor`` times that — an
    absolute threshold in g, not the scale-free ``0.5 * std(smoothed)`` this
    replaces, which tracked whatever the segment happened to contain and so
    found "tail beats" in pure sensor noise.

    This is also the derivation behind the ``tailbeat.prominence`` value in each
    ``configs/species/*.yaml``: evaluate it on that species' fixture with that
    species' axis, ``fs`` and ``min_period_s``.
    ``tests/kinematics/test_kinematics.py`` re-runs it against the YAMLs so the
    configured constants cannot drift away from their stated origin.
    """
    ...

def detect_tailbeat_peaks(signal: np.ndarray, fs: float, smooth_sigma: float=2.0, min_period_s: float=DEFAULT_MIN_PERIOD_S, prominence: Optional[float]=None) -> tuple[np.ndarray, np.ndarray]:
    """Detect peaks in a candidate tailbeat signal.

    ``prominence`` is an absolute threshold in the units of ``signal`` (g).
    Passing ``None`` derives one from the signal's own noise floor via
    :func:`noise_floor_prominence` and warns, because a per-species value
    belongs in ``tailbeat.prominence`` in the config.

    Returns (peak indices, smoothed signal).
    """
    ...

def tailbeat_frequency_from_peaks(peaks: np.ndarray, fs: float) -> pd.DataFrame:
    """Peak indices → inter-peak intervals → instantaneous frequency."""
    ...

def add_tailbeat_columns(df: pd.DataFrame, axis_col: str, fs: float, smooth_sigma: float=2.0, min_period_s: float=DEFAULT_MIN_PERIOD_S, prominence: Optional[float]=None, max_stale_periods: Optional[float]=TB_STALE_PERIODS, stale_floor_s: float=TB_STALE_FLOOR_S) -> pd.DataFrame:
    """Attach ``tb_peak`` (boolean) and ``tb_freq_inst`` (forward-filled Hz).

    The forward fill is **bounded**: a sample more than
    ``max(max_stale_periods / f, stale_floor_s)`` seconds after the peak that
    produced its beat has no beat, and ``tb_freq_inst`` is NaN there rather
    than the last frequency seen. Every consumer already treats NaN as "no
    beat" — ``axy_ingest`` maps it to zero speed — so the bound is what stops a
    single stale interval being integrated indefinitely. Pass
    ``max_stale_periods=None`` for the unbounded fill this replaces; see
    :data:`TB_STALE_PERIODS` for what it cost on the flagship.
    """
    ...
