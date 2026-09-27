"""Stream-kinematics tests on a synthetic clip with a known tail-beat frequency.

The clip is rendered here rather than fixtured so the ground truth is exact: a
textured static background plus an ellipse "fish" that translates at a constant
speed while its tail tip swings sinusoidally at ``TAIL_HZ``. Every estimator in
``anchor.validation.stream_kinematics`` is then asked to recover a number the
renderer already knows.
"""
from __future__ import annotations
import json
import numpy as np
import pytest
from anchor.validation import stream_kinematics as SK
FPS = 15.0
WARMUP_FRAMES = 15
FISH_FRAMES = 105
WIDTH, HEIGHT = (900, 300)
TAIL_HZ = 1.6
BODY_SEMI_MAJOR = 100
BODY_SEMI_MINOR = 22
TAIL_SPAN = 34
TAIL_SWING_PX = 26
SPEED_PX_S = 75.0
X_START, Y_MID = (150.0, 150.0)

def _background(rng: np.random.Generator) -> np.ndarray:
    """A static, textured seafloor: smoothed noise, so MOG2 has something to model."""
    ...

def _fish_mask(cx: float, tail_offset: float) -> np.ndarray:
    """Body ellipse plus a caudal fin whose tip is displaced laterally."""
    ...

def render_synthetic_clip() -> tuple[SK.Clip, list[np.ndarray]]:
    """``(clip, per-frame binary masks)`` for a fish beating its tail at ``TAIL_HZ``.

    The first ``WARMUP_FRAMES`` frames are background only. A background model
    built while the animal is already in shot leaves a ghost at its starting
    position that stays connected to the animal for the first few seconds; real
    captures pay that cold-start cost too, and the cure there is to discard the
    opening frames rather than to complicate the estimator.
    """
    ...

@pytest.fixture(scope='module')
def synthetic():
    ...

def test_grade_for_px_uses_the_fixed_resolution_rules():
    ...

def test_implied_tailbeat_folds_only_above_the_biological_band():
    ...

def test_band_peak_recovers_a_pure_tone_below_the_bin_width():
    ...

def test_true_runs_finds_contiguous_blocks():
    ...

def test_strouhal_k_is_stride_length_and_guards_bad_frequency():
    ...

def test_clip_from_array_reports_geometry_and_replays(synthetic):
    ...

def test_clip_rejects_a_source_free_construction():
    ...

def test_track_blobs_finds_one_translating_fish(synthetic):
    ...

def test_track_blobs_default_learning_rate_stops_silhouette_absorption(synthetic):
    """The July auto rate lets MOG2 eat the animal it is tracking; the fixed one does not.

    A 242 px silhouette that dwells ~85 frames over each pixel it crosses is
    absorbed into MOG2's background model under the automatic rate
    (``1/min(2n, history)``), punching the middle out of the blob. The default
    fixed rate keeps the whole animal in the foreground.
    """
    ...

def test_mine_close_passes_finds_the_amplitude_grade_pass(synthetic):
    ...

def _pulse_clip(n_animal_frames: int, fps: float=10.0) -> SK.Clip:
    """A static background, then an ellipse rendered on exactly ``n_animal_frames`` frames.

    The clip *ends* on the animal's last frame on purpose: uncovering the
    background it was sitting on hands MOG2 a trailing ghost blob, which the
    tracker would associate with the same track and the sample count would no
    longer be exactly the number of frames the animal was drawn on.
    """
    ...

def test_track_blobs_min_duration_s_is_a_span_not_a_sample_count():
    """``min_duration_s`` is a span, and a run of ``n`` samples spans ``n - 1`` frames.

    Filtering on ``len(track) >= round(min_duration_s * fps)`` keeps a track one
    frame short of the floor the caller asked for, and ``Track.duration_s`` then
    reports the shortfall — 2.9 s for a requested 3.0 s at 30 fps.
    """
    ...

def test_mine_close_passes_min_duration_s_is_a_span_not_a_sample_count(synthetic):
    """Same off-by-one in the miner: every returned pass must meet its own floor.

    The run below is exactly ``round(min_duration_s * fps)`` samples long, which
    spans one frame less than requested — the boundary the sample-count filter
    cannot see, and the case that writes a curated segment stating 2.93 s under a
    3.0 s floor.
    """
    ...

def _run_track(n_total: int, n_big: int, start: int=10, frames=None) -> SK.Track:
    """A hand-built track carrying one maximal run of ``n_big`` amplitude-grade samples."""
    ...

def test_min_duration_s_floor_is_reached_by_ceiling_not_rounding(synthetic):
    """A floor that is not a whole number of frames still has to be met.

    ``round(min_duration_s * fps)`` rounds *down* by up to half a frame, so both
    filters admit a window shorter than the caller asked for — a 3.01 s floor at
    30 fps becomes 90 frames and returns a 3.0 s pass. Only a ceiling makes
    "every returned window meets its floor" true. The floors here are exact
    products; the epsilon that keeps *inexact* ones reachable is pinned by
    :func:`test_min_duration_s_floor_survives_an_inexact_frame_product`.
    """
    ...

def test_min_duration_s_floor_survives_an_inexact_frame_product(synthetic):
    """A floor derived from a frame count must not be pushed up by float error.

    A caller that measures a floor as ``frames / fps`` — the CLI's own
    ``--min-duration-s`` is typically written that way, and so is every test
    above — hands back a float whose product with ``fps`` can land just *above*
    the frame count it came from. ``31 / 15 * 15`` is ``31.000000000000004``, so
    a bare ceiling asks for 32 frames and rejects the very window the floor was
    measured from. This is the one behaviour the epsilon in
    :func:`~anchor.validation.stream_kinematics._min_span_frames` buys; the
    ceiling tests either side of it use exact products and cannot see it.
    """
    ...

def test_track_blobs_min_duration_s_floor_is_reached_by_ceiling_not_rounding():
    """The tracker's own filter has the same half-frame slack, and the same fix."""
    ...

def test_mine_close_passes_needs_samples_and_not_only_a_span(synthetic):
    """A two-sample run spanning 1000 frames is not a 33 s close pass.

    Every statistic a :class:`ClosePass` reports is an aggregate over the run's
    samples, so gating on the span alone would let a sparse track hand downstream
    a long extraction window summarised from two points.
    """
    ...

def test_mine_close_passes_raises_a_static_flag_for_a_swaying_oscillator(synthetic):
    """The E1 kelp failure: a periodic blob that never goes anywhere."""
    ...

def test_mine_close_passes_flags_edge_clipping_and_blob_merges(synthetic):
    ...

def test_mine_close_passes_rejects_tracker_options_when_tracks_are_supplied(synthetic):
    ...

def test_motion_energy_frequency_recovers_the_rendered_tailbeat(synthetic):
    ...

def test_motion_energy_frequency_needs_five_seconds(synthetic):
    ...

def test_motion_energy_frequency_measures_a_close_pass_off_the_frame_centre():
    """The default ROI must not reject the very passes the miner selects.

    ``0.6 * body length`` with a hard whole-ROI-inside-frame test is unusable at
    close-pass framing: the July flagship 592 px shark on a 720 px frame needs a
    710 px square, so its centroid must sit within ~5 px of the vertical centre.
    Rendered here at half that scale (296 px animal, 360 px frame — the same
    0.82 ratio) with the animal well off centre. July used a fixed 70 px ROI, so
    this is a port regression; the cure is to cap the half-size by what the frame
    and the track's centroid excursion can hold.
    """
    ...

def test_body_frame_tail_excursion_from_masks_recovers_f_and_amplitude(synthetic):
    ...

def test_body_frame_tail_excursion_survives_segmentation_dropout(synthetic):
    """Dropped masks must cost signal, not shift the peak.

    ``segment_animal`` returns ``None`` for frames it cannot resolve and E5's own
    run resolved 112/120 (6.7%), so dropout is the operating point. FFT-ing the
    surviving samples as if consecutive compresses the time axis: on this clip
    that reads 1.75 Hz against a true 1.6 Hz, and ``n_frames`` (hence
    ``n_cycles`` and ``gliding``) counts samples instead of the window span.
    """
    ...

def test_body_frame_tail_excursion_refuses_a_mostly_missing_window(synthetic):
    ...

def test_body_frame_tail_excursion_flags_a_glide():
    """One slow undulation across the window is a coast, as in E5's K~0.75 shark."""
    ...

def test_body_frame_tail_excursion_from_keypoints_matches_the_rendered_beat():
    ...

def test_body_frame_tail_excursion_requires_exactly_one_input():
    ...

def test_speed_bl_per_s_uses_the_body_as_its_own_ruler(synthetic):
    ...

def _translating_ellipse_masks(n, step_px, body_px):
    """``n`` masks of one ellipse sliding ``step_px`` per frame — an exact ruler."""
    ...

@pytest.mark.parametrize('n', [8, 12, 16, 24, 60])
def test_speed_bl_per_s_is_unbiased_across_window_lengths(n):
    """Path smoothing must not eat the endpoints of a short window.

    A ``convolve(..., "same")`` moving average zero-pads, so the first and last
    ``w // 2`` points are dragged toward the origin. ``speed_bl_per_s`` takes the
    *median* per-frame step, and for 9 <= N <= 17 the corrupted steps are the
    majority — the median lands on one and the answer (and therefore K) comes
    back 5.5x high, silently. N = 12 and 16 fail on that code; 8, 24 and 60 pass
    either way, and are here so the fix is shown to be continuous in N.
    """
    ...

def _drop_frames(masks, fraction, seed):
    """Replace a pinned random ``fraction`` of the interior masks with ``None``."""
    ...

@pytest.mark.parametrize('fraction', [0.067, 0.1, 0.15])
def test_speed_bl_per_s_survives_segmentation_dropout(fraction):
    """A gap inside the smoothing window must not inflate the median step.

    Smoothing the *surviving* centroids and dividing by the real frame spacing
    does not undo a dropout: a difference of moving averages whose 9-sample window
    straddles a one-frame hole spans 10 real frames while the divisor stays 1, so
    the median step reads (9 + g) / 9 high. Because it is a median the error is
    quantised — exactly +11.1% or nothing — and at E5's own 112/120 segmentation
    rate it fires in a minority of windows, which is worse than a steady bias. The
    seed is pinned to one that trips the old code at all three dropout rates
    (0.6597 / 0.6944 / 0.6944 against a true 0.6250).
    """
    ...

def test_speed_bl_per_s_refuses_a_mostly_missing_window():
    """Past ``MAX_GAP_FRACTION`` the path is mostly interpolation, as for f."""
    ...

def test_smooth_path_reproduces_a_constant_velocity_run():
    ...

def test_speed_bl_per_s_returns_nan_without_a_usable_body_length():
    ...

def test_pick_mask_prefers_the_proposal_covering_the_prompt():
    ...

def test_write_segment_manifest_records_flags_and_resolution_rules(synthetic, tmp_path):
    ...

def test_build_capture_manifest_inventories_a_capture_directory(tmp_path):
    ...

def test_build_capture_manifest_preserves_human_judgements(tmp_path):
    ...

def test_build_capture_manifest_rejects_a_missing_directory(tmp_path):
    ...

def test_tracks_to_dataframe_is_long_form_with_grades(synthetic):
    ...

def test_render_pass_overlay_writes_a_png(synthetic, tmp_path):
    ...

def _write_video(clip: SK.Clip, path):
    """Encode the synthetic clip to MP4, or return ``None`` if no encoder is available."""
    ...

def test_cli_stream_manifest_inventories_a_capture_dir(tmp_path):
    ...

def test_cli_stream_extract_writes_tracks_and_manifest(synthetic, tmp_path):
    ...

def _far_translation_track(n: int=60) -> tuple[SK.Clip, SK.Track]:
    """A track crossing the frame, largest at its **last** frame.

    The 2026-09-04 geometry in miniature: the animal is at one side of the frame
    when the window opens and at the other, at maximum apparent length, when it
    closes — 800 px apart on a 1000 px-wide frame, against 807 px on 1280 for
    ``sharkcam_145759`` segment 9.
    """
    ...

def test_close_pass_records_both_the_start_and_the_peak_seed():
    """``seed_xy_start`` is the centroid at ``start_frame``, whatever the peak does."""
    ...

def test_close_pass_seeds_sit_on_the_animal_on_the_real_tracker_path(synthetic):
    ...

def test_write_segment_manifest_carries_both_seeds(synthetic, tmp_path):
    ...

class _FakeMaskData:

    def __init__(self, arr):
        ...

    def cpu(self):
        ...

    def numpy(self):
        ...

class _FakeMasks:

    def __init__(self, arr):
        ...

class _FakeResult:

    def __init__(self, arr):
        ...

class _RecordingSAM:
    """Stand-in for ultralytics' MobileSAM: one disc mask centred on the prompt.

    Records ``(frame_index, prompt_point)`` per call, so a test can assert which
    frame was prompted first and in what order the window was walked. The disc
    radius varies with the frame index, which makes each frame's mask
    identifiable in the returned list.
    """

    def __init__(self):
        ...

    def __call__(self, frame, points=None, labels=None, verbose=False):
        ...

def _install_fake_sam(monkeypatch) -> _RecordingSAM:
    ...

def _indexed_clip(n: int=40, w: int=220, h: int=140, fps: float=10.0) -> SK.Clip:
    """A clip whose frames carry their own index in pixel ``(0, 0)`` channel 0."""
    ...

def test_segment_animal_defaults_to_prompting_at_the_window_start(monkeypatch):
    ...

def test_segment_animal_honours_an_explicit_seed_frame(monkeypatch):
    """Prompt at ``seed_frame``, then propagate forward and backward over the window.

    This is what the capture had to do by hand: seed where the animal actually
    is, without throwing away the frames before it.
    """
    ...

def test_segment_animal_walks_a_long_backward_span_in_chunks(monkeypatch):
    """The reverse walk is buffered, so it must cross chunk boundaries in order."""
    ...

def test_segment_animal_rejects_a_seed_frame_outside_the_window(monkeypatch):
    ...

def _square_mask(side: int, size: int=80) -> np.ndarray:
    ...

def test_mask_area_stability_is_the_fraction_within_a_quarter_of_the_median():
    ...

def test_body_frame_tail_excursion_flags_an_unstable_mask_series(synthetic):
    """A mask that keeps jumping size is the reject signature the humans used.

    Two of the three rejects in the 2026-09-04 capture were masks that had
    locked onto background of roughly the right size for part of the window;
    a per-frame area-stability fraction is what separates them from a mask that
    holds one animal.
    """
    ...

def test_render_pass_overlay_writes_bgr_not_rgb(tmp_path):
    """A pure-red patch must round-trip as red.

    ``Clip`` yields BGR and ``cv2.imwrite`` expects BGR, so nothing on the way
    to disk may swap channels — a swap turns the accepted-pass shark red.
    """
    ...
