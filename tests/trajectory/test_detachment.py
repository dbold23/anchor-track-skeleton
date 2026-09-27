"""Tests for tag-detachment detection.

Synthetic-only — no fixtures, no parquet, no network. Builds a minimal
track-shaped namespace exposing only the attributes the detection
functions actually read (depth_m, tailbeat_freq_hz, roll_rad, base_hz,
__len__).
"""
from __future__ import annotations
from pathlib import Path
import numpy as np
import pytest
from anchor.trajectory.detachment import detect_post_detach_regimes, detect_tag_detachment, detect_tag_detachment_multichannel

class _FakeTrack:

    def __init__(self, depth_m, tailbeat_freq_hz, roll_rad, base_hz=1.0):
        ...

    def __len__(self):
        ...

def _clean_detachment_track(n_attached=1000, n_surface=1000, base_hz=1.0):
    """Attached: depth ~5 m, tailbeat 1 Hz, roll oscillating ±0.3 rad.
    Surface: depth ~0 m, tailbeat ~0, roll near-flat (clamped).

    Note: Whitney's roll-variance signature is *high* variance when
    floating (tumbling) and *low* when clamped. We invert that here for
    the synthetic so the detector should still trigger — wait, the
    detector tests `var > floor` for surfaced. A clamped tag has near-
    zero roll variance, but a tumbling-on-surface tag has high. For a
    simple positively-buoyant float bobbing in waves, roll variance
    *jumps up* at detachment. We model that.
    """
    ...

def test_detect_depth_only_finds_clean_detachment():
    """Depth-only rule: depth = 5 m for 30 min, then 0 m for 30 min →
    detect detachment near the boundary."""
    ...

def test_detect_multichannel_matches_depth_on_clean_signal():
    """When all three channels agree, multichannel should land on the
    same detachment boundary (within a few samples of the depth-only
    rule)."""
    ...

def test_detect_multichannel_handles_calm_grounded_surface_regime():
    """Real-world post-detach periods often include a calm/grounded
    segment where the tag is sheltered, depth = 0, motion = 0, but
    roll variance is *low* (tag is settled, not tumbling). The strict
    AND-of-three rule (Whitney 2016 as written) misses this; the
    refined OR-of-aux rule must catch it because depth + motion both
    confirm.
    """
    ...

def test_detect_multichannel_rejects_brief_surface_excursion():
    """A 30-second dip to surface in the middle of an attached deployment
    should NOT trigger detachment — the sustained-min threshold blocks
    it. Final window must remain near surface for ≥sustained_min min,
    and here it doesn't."""
    ...

def test_post_detach_regimes_without_high_rate_vedba_returns_nothing():
    """No high-rate accel → no VEDBA → no regimes.

    Regression for the unit bug where ``tailbeat_freq_hz`` (Hz) was used
    as a low-rate stand-in for VEDBA and compared against thresholds in
    g (DEFAULT_ACTIVE_VEDBA_G = 0.025). A quiescent post-detach tag
    bobbing at ~0.3 Hz scored far above 0.025, so every bin was labelled
    "active" and the regime-aware leeway narrowing never fired.

    Here the post-detach signal is unambiguously quiescent, and the
    track exposes no ``deployment_id``, so no interim parquet is read.
    """
    ...

def _quiescent_track(deployment_id, n_attached=600, n_surface=600):
    ...

def _seed_regime_parquet(tmp_path, deployment_id, n_rows, sidecar_cfg=None):
    """Write a real high-rate accel parquet for ``deployment_id``, optionally
    keyed to ``sidecar_cfg``."""
    ...

def _regime_cfg(raw_csv, deployment_id, accel_json=None):
    ...

def test_regimes_use_an_interim_parquet_keyed_to_the_config(tmp_path, monkeypatch):
    ...

def test_regimes_refuse_an_interim_parquet_from_a_different_config(tmp_path, monkeypatch):
    """A stale parquet holds another config's calibration; using it would put
    silently wrong VEDBA behind the leeway-σ narrowing. Skipping it lands on
    the documented conservative fallback (no regimes, unmodulated leeway)."""
    ...

def test_regimes_without_a_config_use_the_parquet_and_warn(tmp_path, monkeypatch, caplog):
    """No cfg means the cache cannot be keyed. Silently disabling regimes for
    such callers would be a regression, so it is used with a warning."""
    ...
FS_HI = 25.0

def _accel_record(minutes_spec, *, fs=FS_HI, seed=3):
    """Tri-axial accel in g from ``[(minutes, dynamic_amplitude_g), ...]``.

    Gravity sits on +Z and the "motion" is a 1 Hz sway on Y plus white noise,
    so the dynamic norm a quiet minute has to fall below is set by ``amp``
    alone. An ``amp`` of 0 gives a perfectly still tag; the flagship's
    stationary span reads 0.016 g and its moving span 0.053 g.
    """
    ...

def _depth_record(minutes_spec, *, fs=FS_HI):
    """Depth in m from ``[(minutes, depth_m), ...]`` on the same grid."""
    ...

def test_stationary_lowpass_matches_mag_inflight():
    """The 2 s box port is the same filter, not a lookalike.

    ``detect_stationary_onset`` decomposes the accelerometer with a filter
    ported from ``anchor.ingest.mag_inflight``; if the two drift, "the tag is
    quiet" and "the static vector points there" stop being statements about
    one decomposition and §17.4's census and boundary stop being comparable.
    """
    ...

def test_stationary_onset_finds_the_boundary_and_its_length():
    """Nine minutes of motion, ninety of stillness: the onset is at minute 9."""
    ...

def test_a_stationary_run_under_the_floor_is_not_a_span():
    """Fifty-nine quiet minutes is a rest, not a record ending.

    The 60 min floor is what separates a resting animal from a tag that has
    stopped; without it every glide would truncate a track.
    """
    ...

def _rule_track(deployment_id='STATIONARY_RULE_TEST'):
    """A 1 Hz track whose depth surfaces at 200 min and leaves the water at
    230 min, over a 25 Hz record whose accelerometer goes quiet at 100 min."""
    ...

def _onset_of(acc, depth_hi):
    ...

def test_the_stationary_rule_cuts_at_the_onset_and_the_surface_rule_at_the_exit():
    """Both moments are reported whichever rule wins; ``rule`` says which cut.

    This is §17.4's finding in miniature: the depth channel puts the cut at
    200 min and 100 of those minutes are a tag that is not moving.
    """
    ...

def test_the_two_rules_agree_when_nothing_stops_moving():
    """A record that swims until it surfaces is cut in the same place twice."""
    ...

def test_the_regime_table_covers_the_record_without_gaps_or_overlaps():
    ...

def test_a_track_with_no_accelerometer_falls_back_and_says_so():
    """A rule that could not run must not read as a rule that found nothing."""
    ...

def test_the_stationary_span_is_pinned_grounded_for_the_leeway_model(tmp_path, monkeypatch):
    """``grounded_until_idx`` overrides the VEDBA bin labels.

    ``|‖a‖ - 1|`` reads 0.0103 g over BR_260318_S3's stationary span, above
    ``DEFAULT_GROUNDED_VEDBA_G``, so the bin rule calls 446 of its 457 minutes
    "calm" — leeway 0.3 — and 0.3x the tidal current for 7.6 h would carry the
    back-propagated cloud across the slough. Here the accelerometer reads a
    steady 1.02 g, which is "calm" by the same rule, and the pin has to win.
    """
    ...

@pytest.mark.skipif(not FLAGSHIP_PARQUET.exists(), reason='data/interim/BR_260318_S3.parquet is not in this tree')
def test_the_flagship_stops_being_an_animal_record_at_9_333_h():
    """§17.4.2's boundary, to the minute, and its span to the minute.

    9.333 h and 457 min. The one-minute median dynamic norm falls from
    0.0361 g to 0.0078 g across the boundary and does not recover.
    """
    ...

@pytest.mark.skipif(not FLAGSHIP_PARQUET.exists(), reason='data/interim/BR_260318_S3.parquet is not in this tree')
def test_the_flagship_left_the_water_at_16_950_h_and_the_temperature_says_so():
    """§19's premise, on the record itself.

    The last 3.791 h read depth zero, which the depth channel alone cannot
    distinguish from a float. The temperature channel can: the span's median
    is 20.5 °C against 18.4 °C over the 60 wet minutes before it, a +2.1 °C
    contrast against a largest in-water 60-minute swing of +0.5 °C on the same
    record. The tag was on a boat deck.
    """
    ...

@pytest.mark.skipif(not FLAGSHIP_PARQUET.exists(), reason='data/interim/BR_260318_S3.parquet is not in this tree')
def test_the_flagships_regime_table_resolves_the_grounded_end_anchor_model():
    """The three rows §19's rule reads, end to end on the record.

    A 7.617 h stationary-wet span, 28 s of depth-channel disagreement, and a
    temperature-verified out-of-water span. ``auto`` therefore anchors the
    smoother at the recovery position rather than 2.7 km away.
    """
    ...

def test_a_record_that_never_surfaces_is_still_cut_where_it_stops_moving():
    """No water exit is not the same as no end of the animal record.

    A tag whose float fails, or one recovered by hand off the bottom, never
    gives the depth channel its signature. The water-exit rule then reports no
    detachment at all and the whole record is reconstructed as track. The
    stationary rule still has something to say.
    """
    ...

def test_a_quiet_deck_head_does_not_disable_the_stationary_rule():
    """A tag switched on and left on the deck for over an hour before release.

    ``span_before`` used to return that deck head as the earliest qualifying
    span; the caller's "index 0" guard then dropped the stationary rule
    altogether, emitted a note saying the span "does not begin before the
    water exit" (it does), and published a regime table in which the whole
    swimming span was labelled ``stationary_wet``. The release now bounds the
    search from below, so the in-water span is the one that is found.
    """
    ...

def test_the_note_says_which_test_rejected_the_span():
    """The disclosure branch is reached for more than one reason.

    A record whose only quiet hour is on the deck before the release must not
    claim the span "does not begin before the water exit" — it does, and the
    bound that rejected it is the release.
    """
    ...

def _minutes(spec):
    """``[(minutes, value), ...]`` → a per-minute array."""
    ...

def test_a_warm_dry_tail_is_out_of_the_water():
    """The flagship's shape: 18.4 °C in the water, 20.5 °C on the deck."""
    ...

def test_a_dry_tail_at_the_waters_own_temperature_is_a_surface_float():
    """Depth zero and no warming is a tag floating, which is the case the
    leeway model exists for."""
    ...

def test_the_warming_threshold_is_one_degree_and_is_where_the_verdict_flips():
    ...

def test_the_deck_head_is_not_the_water_the_contrast_is_measured_against():
    """A tag switched on warm, cooled by the water, then recovered.

    Without the ``first_wet_min`` bound a short record's pre-window would
    reach back into the deck head — which is dry and warm — and the contrast
    would come out negative on a tag that plainly left the water.
    """
    ...

def test_without_a_temperature_channel_the_span_is_reported_on_depth_alone():
    ...

def test_a_record_that_does_not_end_dry_has_no_terminal_span():
    ...

def test_a_short_dry_tail_is_a_surface_excursion_and_not_a_recovery():
    ...

def test_the_regime_table_carries_the_terminal_spans_basis():
    """The label and the channels that decided it travel together, because
    ``out_of_water`` on depth alone is not evidence the tag left the water.
    """
    ...

def test_the_grounded_leeway_factor_now_suppresses_the_process_noise_too():
    """§18.8's last unrepaired defect in ``estimate_detachment_position``.

    A window every step of which is grounded — leeway 0.0, no advection, no
    wind drift — must add no spread at all. Before this fix each step still
    injected ``process_noise_xy_m_per_sqrt_s``·√dt of random walk, so a σ that
    should have stayed at the recovery fix's grew as √n with the length of the
    window: 7.617 h of motionless tag took the flagship's end anchor from
    395.70 m to 469.33 m for no physical reason.
    """
    ...

def test_the_at_water_prefix_is_measured_and_is_not_a_gate():
    """``at_water_prefix_min`` counts the leading dry minutes still at the
    water's temperature — the quantity a float guard would need.

    It is reported and never thresholded, and the reason is in this test: a
    dry span that warms *gradually* has one too. Here 30 minutes at 18.6 °C
    followed by 170 at 20.5 °C is a deck whose first half hour has not yet
    reached the 1.0 °C flip, and it is still classified out of the water.
    """
    ...

def test_the_dry_span_constants_are_minutes_whatever_the_bin_is():
    """``window_min`` and ``min_minutes`` are element counts on the binned
    grid, so ``detect_stationary_onset`` converts them from minutes at the
    call site. At a 30 s bin the 30-minute floor must still be 30 minutes.
    """
    ...
