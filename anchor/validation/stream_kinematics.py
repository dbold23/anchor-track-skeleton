"""Single-camera stream kinematics: tracking, tail-beat frequency, close-pass mining.

This is the productised form of the 2026-07-10 Monterey Bay Aquarium livestream
feasibility programme (AXY+ ``reports/poc_stream_260710/``: ``analyze3.py``,
``viz.py``, ``cotrack.py``, ``e1_bodyframe.py``, ``e5_sam_shark.py``). Section 7b
of ``docs/design/leopard_shark_digital_twin.md`` records what that programme
established; this module is the one place where those five throwaway scripts
live as a tested API.

What the July work proved, and what this module therefore assumes
-----------------------------------------------------------------
* **Capture works.** 1280x720 at exactly 30 fps; the camera holds a static wide
  shot for long stretches (95th-percentile motion 0.88 px/frame), so no
  stabilisation is applied here.
* **Framing is available.** On a 240 s clip a fish of at least 100 px is in
  frame 80.6% of the time and at least 200 px 39.3% of the time. Finding those
  windows is :func:`mine_close_passes` (the E2 miner).
* **Tracking is solved**, training-free (CoTracker3), and **segmentation is
  solved** (MobileSAM prompted on the animal and propagated by mask centroid:
  528 px body length where MOG2 merged shark, sturgeon and kelp into an 89 px
  blob). :func:`segment_animal` is that E5 step.
* **The extraction maths is sound** to a 20 px tail on synthetic ground truth,
  and ``K = U / (L * f)`` is dimensionless, so body-lengths-per-second speed
  needs no scale bar. That is :func:`body_frame_tail_excursion`,
  :func:`speed_bl_per_s` and :func:`strouhal_k`.
* **The one remaining gap** is reliable per-fish keypoints (snout, tail tip,
  body length) on curated *active-swimming* segments — a trained DeepLabCut or
  SLEAP model on 100 to 300 labelled close-pass frames. Nothing in this module
  closes that gap; :func:`write_segment_manifest` exists to produce the curated
  segment list such a model would be trained and run on.

Resolution rules (fixed, from the literature review in the AXY+ plan)
--------------------------------------------------------------------
* body length **>= 100 px** for a trustworthy **frequency**
  (:data:`FREQUENCY_GRADE_MIN_PX`);
* body length **>= 200 px** for a trustworthy **amplitude**
  (:data:`AMPLITUDE_GRADE_MIN_PX`);
* 30 fps is ample for elasmobranch tail-beats (0.4 to 3 Hz) — frame rate was
  never the limiter, spatial resolution of the tail was.

Known failure modes, all flagged rather than silently swallowed
---------------------------------------------------------------
* **kelp** — a swaying, non-translating oscillator reads as a periodic "fish"
  (E1 attempt 1, spurious K = 0.32). Flagged as ``static_flag``.
* **frame edge** — a clipped animal has an underestimated body length, which
  inflates every body-length-normalised quantity (E1 attempt 2, spurious
  K = 2.00). Flagged as ``edge_flag``.
* **merged blob** — background subtraction fuses adjacent animals and kelp into
  one component (E1 retarget, spurious K = 4.11). Flagged as ``merged_flag``;
  the cure is :func:`segment_animal`, not a better blob threshold.
* **gliding** — a coasting animal has no crisp active beat, so its "frequency"
  is one slow undulation and its K is correspondingly high (E5, K about 0.75 on
  a gliding shark). Flagged as ``gliding`` on :class:`TailBeat`; K is
  behaviour-state-conditioned and a single per-species constant is an
  approximation.

Everything heavy is lazy: ``cv2`` is imported inside the functions that need it
(as elsewhere in ``anchor.validation``), and ``torch`` / ``ultralytics`` /
``cotracker`` are imported inside the single function that uses each, with an
install hint. Only ``numpy`` and ``scipy`` are imported at module scope.
"""
from __future__ import annotations
import datetime
import json
import math
import shutil
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterator, NamedTuple, Optional, Sequence
import numpy as np
from scipy.fft import rfft, rfftfreq
from scipy.signal import detrend
__all__ = ['AMPLITUDE_GRADE_MIN_PX', 'FREQUENCY_GRADE_MIN_PX', 'MASK_AREA_TOLERANCE', 'MASK_STABILITY_MIN_FRACTION', 'TAILBEAT_BAND_HZ', 'MOTION_ENERGY_BAND_HZ', 'Clip', 'ClosePass', 'MotionEnergy', 'TailBeat', 'Track', 'body_frame_tail_excursion', 'build_capture_manifest', 'grade_for_px', 'mask_area_stability', 'mine_close_passes', 'motion_energy_frequency', 'render_pass_overlay', 'segment_animal', 'speed_bl_per_s', 'strouhal_k', 'track_blobs', 'tracks_to_dataframe', 'write_segment_manifest']
FREQUENCY_GRADE_MIN_PX = 100.0
AMPLITUDE_GRADE_MIN_PX = 200.0
TAILBEAT_BAND_HZ = (0.4, 2.6)
MOTION_ENERGY_BAND_HZ = (0.4, 6.0)
SNR_CLEAN = 4.0
MIN_CYCLES_ACTIVE = 2.0
MAX_GAP_FRACTION = 0.25
MASK_AREA_TOLERANCE = 0.25
MASK_STABILITY_MIN_FRACTION = 0.8
SEGMENT_REVERSE_CHUNK = 30
ROI_MIN_HALF_PX = 35.0
ROI_MAX_FRAME_FRACTION = 0.45
ROI_FIT_PERCENTILE = 10.0
MOG2_LEARNING_RATE = 0.001
_MANIFEST_SCHEMA = 1

def _cv2():
    """Import ``cv2`` with an actionable hint. Kept lazy, as in ``pose_overlay``."""
    ...

@dataclass
class Clip:
    """A re-readable frame source: a video file, or frames already in memory.

    Both passes of the motion-energy method (track, then crop a centroid-locked
    ROI) walk the same frames, so the source has to be re-readable. A file-backed
    clip re-opens the video; an array-backed clip is a ``(T, H, W, 3)`` uint8
    BGR stack and is what the tests use, so no codec is in the test path.
    """
    fps: float
    width: int
    height: int
    n_frames: int
    path: Optional[Path] = None
    array: Optional[np.ndarray] = None

    def __post_init__(self) -> None:
        ...

    @classmethod
    def from_video(cls, path: Path | str) -> 'Clip':
        ...

    @classmethod
    def from_array(cls, array: np.ndarray, fps: float, source: str='array') -> 'Clip':
        ...

    def __len__(self) -> int:
        ...

    def frames(self, start: int=0, stop: Optional[int]=None) -> Iterator[tuple[int, np.ndarray]]:
        """Yield ``(frame_index, bgr_frame)`` for ``start <= index < stop``."""
        ...

    def frame_at(self, index: int) -> Optional[np.ndarray]:
        """One BGR frame, or ``None`` past the end."""
        ...

    def seconds(self, frame_index: float) -> float:
        ...

def _as_clip(clip: 'Clip | np.ndarray | Path | str', fps: Optional[float]=None) -> Clip:
    ...

def _min_span_frames(min_duration_s: float, fps: float) -> int:
    """Frames a window must **span** to last at least ``min_duration_s``.

    Two corrections to the obvious ``round(min_duration_s * fps)`` live here, and
    both are needed for the filters that use this to keep their promise.

    Duration is always a span — ``(frames[-1] - frames[0]) / fps`` on both
    :meth:`Track.duration_s` and :attr:`ClosePass.duration_s` — so a window of
    ``n`` samples lasts ``n - 1`` frames, and comparing ``n`` against the floor
    keeps windows one frame short of it (2.97 s under a requested 3.0 s at
    30 fps). Callers compare the span instead.

    The span is then rounded **up**, because rounding to nearest rounds down by
    up to half a frame: a 3.01 s floor at 30 fps would become 90 frames and admit
    a 3.0 s window.

    The epsilon absorbs the float error in the product, so a floor derived from a
    frame count stays reachable. ``31 / 15`` is the shortest such knife edge at
    15 fps: ``31 / 15 * 15`` is ``31.000000000000004``, and a bare ``ceil`` would
    ask for 32 frames and reject the 31-frame window the caller measured the
    floor from. Products that land exactly (``44 / 15 * 15`` is ``44.0``) are
    unaffected either way; the inexact ones are the whole reason it is here.

    The floor is at least one frame, so a window is never fewer than two samples.
    """
    ...

@dataclass
class Track:
    """One nearest-centroid blob track.

    ``length_px`` is the bounding-box diagonal, the July proxy for apparent body
    length. It is an **upper bound**: background subtraction merges touching
    animals and kelp, so a large value can be a merged component rather than a
    large animal. :attr:`merged_flag` on :class:`ClosePass` is the guard.
    """
    track_id: int
    frames: np.ndarray
    xy: np.ndarray
    area_px: np.ndarray
    length_px: np.ndarray
    bbox: np.ndarray

    def __len__(self) -> int:
        ...

    def duration_s(self, fps: float) -> float:
        ...

    @property
    def median_length_px(self) -> float:
        ...

    def net_displacement_px(self) -> float:
        ...

def track_blobs(clip: 'Clip | np.ndarray | Path | str', *, fps: Optional[float]=None, min_area: float=250.0, max_area: float=60000.0, gate_px: float=60.0, min_duration_s: float=3.0, history: int=300, var_threshold: float=36.0, learning_rate: Optional[float]=MOG2_LEARNING_RATE, max_tracks: Optional[int]=None) -> list[Track]:
    """MOG2 background subtraction + greedy nearest-centroid association.

    A port of the July pass-1 tracker, which the July work ran with two different
    parameter sets. Detections are connected components of the foreground mask
    whose area falls in ``[min_area, max_area]``; each active track claims the
    nearest unused detection within ``gate_px``, and any unclaimed detection
    starts a new track. Tracks spanning less than ``min_duration_s`` are dropped
    — a span, rounded up to a whole frame, so a kept track's
    :meth:`Track.duration_s` is never below the floor (see
    :func:`_min_span_frames`); the rest come back sorted longest-first.

    Provenance of each default, since the two July parameter sets disagree and
    these defaults take one from each:

    * ``history=300``, ``var_threshold=36`` and the 3x3 ``MORPH_OPEN`` kernel are
      shared by the only three July scripts that track (``analyze3.py``,
      ``viz.py``, ``e1_bodyframe.py``);
    * ``min_area=250`` and ``gate_px=60`` are ``analyze3.py`` / ``viz.py``
      (``AMIN, AMAX, GATE = 250, 40000, 60``, 7x7 ``MORPH_CLOSE``);
    * ``max_area=60000`` and the 9x9 ``MORPH_CLOSE`` kernel are
      ``e1_bodyframe.py`` (``AMIN, AMAX, GATE = 400, 60000, 70``), the set E1 ran
      on the flagship 592 px broadside shark. It is the more permissive of the
      two on both the area ceiling and the closing kernel, which is what a close
      pass — a large silhouette, the only kind worth measuring — needs;
    * ``min_duration_s=3.0`` is ``e1_bodyframe.py``'s ``len(t) >= int(3 * fps)``,
      restated as a span rather than a sample count;
    * ``learning_rate`` has no July counterpart at all: every July script calls
      ``backsub.apply(frame)`` and so takes MOG2's automatic rate, which absorbs a
      large slow animal into the background model and halves its measured
      silhouette (:data:`MOG2_LEARNING_RATE`).

    So ``learning_rate=None`` restores the July *learning rate* and nothing more:
    no argument setting reproduces a July run exactly, because the area ceiling,
    the closing kernel and the minimum-length rule differ from ``analyze3.py`` as
    listed above, and ``min_area`` / ``gate_px`` differ from ``e1_bodyframe.py``.

    This is deliberately the cheap tracker: it is good enough to *find* candidate
    animals and close passes, and it is exactly what merges objects when asked to
    delineate one. Use :func:`segment_animal` for the delineation.
    """
    ...

def tracks_to_dataframe(tracks: Sequence[Track], fps: float):
    """Long-form per-track, per-frame table: the CSV ``anchor validation stream extract`` writes."""
    ...

def _on_frame_grid(frames: Sequence[int], values: Sequence[float], *, min_samples: int=8) -> Optional[tuple[np.ndarray, float]]:
    """Put an irregularly sampled per-frame series back on its own time base.

    Every spectral estimate here assumes uniform ``1/fps`` spacing, but the
    measurements that feed them are lossy by design: segmentation returns ``None``
    for frames it cannot resolve, and a centroid-locked ROI is dropped when it
    would leave the image. Handing the *surviving* samples to an rFFT as if they
    were consecutive compresses the time axis wherever a gap fell, which biases
    the peak in whichever direction the gaps happened to land (measured on a
    rendered 1.20 Hz sequence: +10.7% for 10% scattered dropout, -11.9% for one
    contiguous 12% gap).

    ``frames`` are integer frame offsets, ``values`` the samples taken at them.
    Returns ``(values_on_the_full_integer_grid, gap_fraction)``, where the grid
    spans ``frames[0] .. frames[-1]`` inclusive and ``gap_fraction`` is the share
    of that span that had to be interpolated. ``None`` if fewer than
    ``min_samples`` samples survive — 8 for a spectrum, lower for the displacement
    statistic in :func:`speed_bl_per_s`, which needs no frequency resolution.
    """
    ...

def _band_peak(signal: Sequence[float], fps: float, lo: float, hi: float) -> Optional[tuple[float, float]]:
    """Hann-windowed rFFT peak inside ``[lo, hi]`` -> ``(f_hz, snr)``.

    ``snr`` is the peak-to-median ratio inside the band, the July definition. The
    peak frequency is refined by parabolic interpolation of the three bins around
    the maximum, which removes the bin-quantisation error the July scripts carried
    (a 7 s window has 0.14 Hz bins, comparable to the effect being measured).

    Non-finite samples are interpolated in place rather than dropped: deleting
    them would silently shorten the time axis (see :func:`_on_frame_grid`).
    """
    ...

def _implied_tailbeat(energy_peak_hz: float) -> tuple[float, bool]:
    """Motion energy peaks twice per stroke; fold a super-band peak to its half.

    Frame-differencing measures ``|tail velocity|``, which maxes at both stroke
    extremes, so the energy fundamental is generically ``2 f``. Energy alone
    cannot distinguish ``f`` from ``2 f``; the July rule uses the biological
    prior instead — a peak above the tail-beat band's upper edge
    (:data:`TAILBEAT_BAND_HZ`) can only be the harmonic. Returns
    ``(f_hz, harmonic_flag)``.
    """
    ...

class MotionEnergy(NamedTuple):
    """``(f_hz, snr, harmonic_flag)`` — the implied tail-beat, not the raw peak."""
    f_hz: float
    snr: float
    harmonic_flag: bool

def motion_energy_frequency(clip: 'Clip | np.ndarray | Path | str', track: Track, *, fps: Optional[float]=None, roi_half_px: Optional[float]=None, band: tuple[float, float]=MOTION_ENERGY_BAND_HZ) -> Optional[MotionEnergy]:
    """Centroid-locked ROI motion-energy periodicity for one track.

    Pass 2 of ``analyze3.py``, the method that worked: crop a square ROI centred
    on the track's centroid each frame — which removes bulk translation without
    any stabilisation — and take the mean absolute frame-to-frame difference
    inside it. A beating tail makes that energy oscillate; its spectral peak,
    folded through :func:`_implied_tailbeat`, is the tail-beat.

    The ROI is sampled with ``cv2.getRectSubPix`` rather than the July integer
    crop, so the sub-pixel drift of a translating animal no longer aliases into a
    spurious spectral line. Frames whose ROI would leave the image are dropped
    rather than edge-replicated, and the surviving energy series is put back on
    its frame grid (:func:`_on_frame_grid`) before the transform, so a dropped
    frame costs a little signal instead of shifting the peak.

    The default ROI half-size is ``0.6 * body length``, capped by what the frame
    and the track's own centroid excursion can actually hold — without that cap a
    close pass, which is the only kind worth measuring, is rejected outright (a
    592 px animal on a 720 px frame would need its centroid within 5 px of the
    vertical centre). See :data:`ROI_MAX_FRAME_FRACTION`.

    Returns ``None`` when fewer than 5 s of usable ROI frames survive, or when
    more than :data:`MAX_GAP_FRACTION` of the window was dropped. This is the
    *cheap, shape-free* estimator: it is robust on small silhouettes but
    2x-ambiguous by construction. :func:`body_frame_tail_excursion` on a clean
    mask is the accurate one.
    """
    ...

def grade_for_px(body_length_px: float) -> str:
    """``"amplitude"`` >= 200 px, ``"frequency"`` >= 100 px, else ``"sub"``."""
    ...

@dataclass
class ClosePass:
    """A contiguous window where one track is large enough in frame to measure.

    ``body_length_px`` is the median bounding-box diagonal over the window and is
    an upper bound on the true body length (see :class:`Track`). The three flags
    are the July failure modes; a segment with any of them set is not curated
    material without a human look.

    **Two seed points, not one.** :attr:`seed_xy_start` is the track centroid at
    ``start_frame`` and :attr:`seed_xy_peak` the centroid at :attr:`seed_frame`,
    the frame of maximum apparent length. They are the same point only for a
    stationary animal: on the 2026-09-04 capture they were 807 px apart on a
    1280 px-wide frame (``sharkcam_145759`` segment 9). A segmentation prompt is
    a point *on a particular frame*, so it has to be paired with the frame it
    was measured on — pass ``seed_xy_start`` with the full window, or
    ``seed_xy_peak`` together with ``seed_frame=``.
    """
    track_id: int
    start_frame: int
    end_frame: int
    t0_s: float
    t1_s: float
    duration_s: float
    body_length_px: float
    max_body_length_px: float
    grade: str
    seed_xy_start: tuple[float, float]
    seed_xy_peak: tuple[float, float]
    seed_frame: int
    net_displacement_px: float
    edge_flag: bool
    merged_flag: bool
    static_flag: bool

    @property
    def seed_xy(self) -> tuple[float, float]:
        """Deprecated alias for :attr:`seed_xy_peak`.

        This is what the name always meant, and the ambiguity was the defect:
        callers followed the documented ``segment_animal(clip, p.seed_xy,
        p.t0_s, p.t1_s)`` and prompted at ``t0`` with the animal's *later*
        position, which put every mask of the 2026-09-04 run on background.
        Use :attr:`seed_xy_start`, or pass ``seed_frame=p.seed_frame`` alongside
        this point. Kept so existing callers and manifests keep working.
        """
        ...

    @property
    def clean(self) -> bool:
        """No failure-mode flag raised."""
        ...

def mine_close_passes(clip: 'Clip | np.ndarray | Path | str', min_px: float=AMPLITUDE_GRADE_MIN_PX, *, fps: Optional[float]=None, tracks: Optional[Sequence[Track]]=None, min_duration_s: float=3.0, edge_margin_px: int=4, merge_area_ratio: float=2.5, static_displacement_bl: float=0.5, **track_kwargs) -> list[ClosePass]:
    """The E2 miner: every window where an animal is at least ``min_px`` long.

    E2's finding on a 240 s Shark Cam clip was that framing was never the wall —
    a frequency-grade animal (>= 100 px) is in frame 80.6% of the time and an
    amplitude-grade one (>= 200 px) 39.3%, with a 592 px broadside leopard shark
    passing for about 20 s. This function reproduces that harvest: it tracks (or
    reuses ``tracks``), then cuts each track into maximal runs of frames whose
    apparent length clears ``min_px`` and that *span* at least ``min_duration_s``
    — the same quantity ``ClosePass.duration_s`` reports, so every returned
    segment meets the floor it was mined under (see :func:`_min_span_frames`).

    A run must also *contain* at least as many samples as that span is frames,
    which is automatic for the tracks :func:`track_blobs` builds (their frames are
    consecutive) but not for a ``tracks=`` sequence with gaps in it. Without the
    second guard a two-sample run 1000 frames apart would qualify as a 33 s pass,
    and every statistic below — the median length, the peak area, the net
    displacement, all three flags — would be an aggregate over those two samples.
    A sparse track is therefore rejected rather than summarised from too few
    points.

    Each segment carries its own failure-mode flags:

    * ``edge_flag`` — the bounding box touches the frame border inside
      ``edge_margin_px`` at any point, so body length is truncated;
    * ``merged_flag`` — peak component area exceeds ``merge_area_ratio`` times
      the track's median, the signature of background subtraction fusing
      neighbours;
    * ``static_flag`` — net centroid displacement is under
      ``static_displacement_bl`` body lengths, i.e. a swaying-kelp oscillator
      rather than a swimming animal.

    Each segment also carries **both** seed points — ``seed_xy_start`` at
    ``start_frame`` and ``seed_xy_peak`` at ``seed_frame`` — because a
    segmentation prompt is only meaningful paired with the frame it was measured
    on; see :class:`ClosePass`.

    Segments come back sorted by descending ``body_length_px``.
    """
    ...

def _true_runs(mask: np.ndarray) -> list[tuple[int, int]]:
    """Half-open ``[start, stop)`` index ranges of contiguous ``True``."""
    ...

def _largest_component(mask: np.ndarray) -> Optional[np.ndarray]:
    """Keep only the biggest connected component of a binary mask."""
    ...

def _pick_mask(mask_stack: np.ndarray, point_xy: tuple[float, float]) -> Optional[np.ndarray]:
    """From SAM's ``(k, H, W)`` proposals, the one covering the prompt point.

    Falls back to the largest proposal when no mask covers the point, which is
    the E5 behaviour. Returns ``None`` for an empty stack.
    """
    ...

def _frames_descending(clip: Clip, lo: int, hi: int, chunk: int=SEGMENT_REVERSE_CHUNK) -> Iterator[tuple[int, np.ndarray]]:
    """``(index, frame)`` for ``hi - 1`` down to ``lo``, buffering ``chunk`` at a time.

    Centroid propagation is sequential in the direction it walks, so seeding
    inside a window means walking the frames before the seed *backwards* — and
    :meth:`Clip.frames` only reads forwards. Reading each chunk forwards and
    yielding it reversed keeps the memory bounded by ``chunk`` frames rather
    than by the length of the window.
    """
    ...

def segment_animal(clip: 'Clip | np.ndarray | Path | str', seed_xy: tuple[float, float], t0: float, t1: float, *, seed_frame: Optional[int]=None, fps: Optional[float]=None, model: str='mobile_sam.pt', min_area_px: float=2000.0, max_area_px: float=200000.0) -> list[Optional[np.ndarray]]:
    """MobileSAM on one animal, prompted at ``seed_xy`` and propagated by centroid.

    This is E5, the step that solved the merged-blob failure: background
    subtraction fused a leopard shark, a sturgeon and kelp into an 89 px "body",
    while SAM prompted at a point on the shark returned the shark alone in
    112/120 frames and a correct 528 px body length. The prompt point is moved to
    each frame's mask centroid, which is what carries the segmentation forward
    without a tracker.

    ``t0`` and ``t1`` are seconds. Returns one entry per frame in the window, in
    frame order: a ``uint8`` mask, or ``None`` where segmentation was rejected
    (no mask, or an area outside ``[min_area_px, max_area_px]``, i.e. SAM grabbed
    background or lost the animal). ``ultralytics`` is imported lazily and its
    weights are resolved by ``ultralytics`` itself.

    ``seed_frame`` is the frame ``seed_xy`` was measured on, and defaults to the
    window's first frame. A prompt point is only meaningful together with its
    frame: :attr:`ClosePass.seed_xy_peak` is measured at
    :attr:`ClosePass.seed_frame`, which on the 2026-09-04 capture was up to
    807 px and several seconds from the same track's position at ``t0``, so
    prompting it at ``t0`` — what the documented call did — put every mask of
    that run on kelp and rock. Pass ``seed_xy_start`` with the full window, or
    ``seed_xy_peak`` with ``seed_frame=seed_frame``; with the latter the window
    is segmented forwards from the seed and then backwards to ``t0``, so no
    frames are lost to seeding. A ``seed_frame`` outside ``[t0, t1)`` is an
    error rather than a silent clamp — that is the mis-pairing itself.
    """
    ...

@dataclass
class TailBeat:
    """Body-frame tail-beat result. ``f_hz`` and ``a_over_l`` are the headline pair."""
    f_hz: float
    a_over_l: float
    snr: float
    body_length_px: float
    n_frames: int
    n_cycles: float
    gliding: bool
    amplitude_grade: bool
    gap_fraction: float = 0.0
    mask_area_stability: Optional[float] = None
    mask_unstable: bool = False

    def as_tuple(self) -> tuple[float, float]:
        """``(f_hz, A/L)``, the two quantities the validation plan asks for."""
        ...

def _mask_axis_metrics(mask: np.ndarray, heading: np.ndarray, anterior_pct: float, tail_pct: float) -> Optional[tuple[float, float]]:
    """``(body_length_px, tail_bend_px)`` for one mask, in its own body frame.

    Fits the rigid anterior body axis and measures the tail tip's lateral offset
    from it, so a turning animal does not read as a beating one — the E5 recipe.
    """
    ...

def _smooth_path(xy: np.ndarray, window: int) -> np.ndarray:
    """Moving average over a 2-D path that leaves a straight run straight.

    The obvious ``np.convolve(..., "same")`` zero-pads, so the first and last
    ``window // 2`` points are dragged toward the origin — on a path stepping
    2.5 px/frame from x=400 the first smoothed step comes out at 48.8 px. That is
    invisible in a long window but fatal to :func:`speed_bl_per_s`, which takes
    the *median* per-frame step: for 9 <= N <= 17 the corrupted edge steps are the
    majority and the median lands on one of them (measured: 3.42 BL/s against a
    true 0.625).

    The fix is an odd (antisymmetric) extension, ``2 * x[0] - x[k]``, which
    continues the path's own local trend instead of inventing an endpoint. A
    constant-velocity path is then reproduced exactly, edges included. The window
    is also shrunk to fit a short path rather than skipped, so behaviour is
    continuous in ``N``.
    """
    ...

def mask_area_stability(masks: Sequence[Optional[np.ndarray]]) -> Optional[float]:
    """Fraction of the resolved masks whose area is within 25% of the window median.

    The QC the 2026-09-04 mask review ran by eye, made automatic. A mask that
    tracks one animal keeps roughly one area for the whole window; a mask that
    acquires late, slips onto a kelp column part-way, or swallows a neighbour
    changes size when it moves. Below :data:`MASK_STABILITY_MIN_FRACTION` the
    series is not one object and its ``f``, ``A/L`` and ``U`` are not one
    animal's.

    Denominator is the frames that produced a mask, not the whole window:
    dropout is a different failure and ``TailBeat.gap_fraction`` already reports
    it, so counting missing frames here would charge one fault twice. Empty
    masks count as missing. Returns ``None`` when nothing was resolved.

    It is a necessary check, not a sufficient one, and the capture that
    motivated it says so: a mask parked on the exhibit's window glass for a whole
    window is perfectly stable and still not the animal. Pair it with the
    ``blob``-length agreement and a human look at the mask strip.
    """
    ...

def _mask_centroids(masks: Sequence[Optional[np.ndarray]]) -> tuple[np.ndarray, np.ndarray]:
    """``(frame_offsets, centroids)`` over the masks that survived segmentation."""
    ...

def body_frame_tail_excursion(masks: Optional[Sequence[Optional[np.ndarray]]]=None, *, keypoints: Optional[np.ndarray]=None, fps: float=30.0, head_index: int=0, tail_index: int=-1, band: tuple[float, float]=(0.4, 3.0), anterior_pct: float=40.0, tail_pct: float=8.0) -> Optional[TailBeat]:
    """Tail-beat frequency and amplitude ratio in the animal's own body frame.

    Two inputs, one algorithm. With ``masks`` (E5) the body axis is refitted per
    frame from the silhouette and the tail tip's lateral bend is taken against
    the *rigid anterior* axis. With ``keypoints`` — an ``(T, K, 2)`` array, e.g.
    a DeepLabCut or SLEAP export — the E1 form is used: heading from the head
    path, tail lateral offset from the head along the heading normal, body length
    the median head-to-tail distance.

    Translation is removed by construction, so no camera-motion compensation is
    needed. ``A/L`` is reported as ``2 * p90(|excursion|) / L``, i.e. an
    approximate peak-to-peak ratio, and is only trustworthy when
    ``amplitude_grade`` is set (body length >= 200 px). ``gliding`` is set when
    the window holds fewer than two complete cycles or the spectral peak is below
    :data:`SNR_CLEAN` — a coasting animal, whose K is legitimately high and must
    not be pooled with active swimming.

    Frames that segmentation lost are interpolated back onto the frame grid
    before the transform rather than closed up, and ``n_frames`` is the span of
    the window rather than the count of surviving samples — otherwise a segment
    with dropouts reports a biased frequency and too few cycles, and so trips
    ``gliding`` for the wrong reason. ``gap_fraction`` reports how much was
    filled in.

    With ``masks`` the result also carries the mask-area stability QC —
    ``mask_area_stability`` and ``mask_unstable``, see
    :func:`mask_area_stability` — because nothing else in the pipeline notices a
    mask that changed object part-way through a window.

    Returns ``None`` when there is not enough usable signal, or when more than
    :data:`MAX_GAP_FRACTION` of the window is missing.
    """
    ...

def speed_bl_per_s(masks: Optional[Sequence[Optional[np.ndarray]]]=None, *, keypoints: Optional[np.ndarray]=None, fps: float=30.0, body_length_px: Optional[float]=None, head_index: int=0, tail_index: int=-1, smooth_frames: int=9) -> float:
    """Swim speed in body lengths per second — the animal as its own ruler.

    ``K`` is dimensionless, so a speed in BL/s needs no scale bar and no
    metres-per-pixel: the pixel scale cancels between displacement and body
    length. The estimator is the median per-frame centroid (or head) displacement
    of the smoothed path, divided by body length, times fps. Median rather than
    mean so a single segmentation dropout does not dominate.

    Guard against circularity: this must never be derived from ``f`` or ``A``, or
    K would be calibrating against itself. It is not — only positions enter.

    Like the two frequency estimators, the mask path is put back on its integer
    frame grid (:func:`_on_frame_grid`) before it is smoothed. Smoothing the
    *surviving* centroids and dividing by the real frame spacing does not undo a
    gap: a difference of moving averages whose window straddles a ``g``-frame hole
    spans ``w + g`` real frames while the divisor for the majority of steps is
    still 1, so the median step comes back ``(w + g) / w`` high — exactly +11.1%
    for one dropped frame at ``w = 9``, and quantised, so it is either right or
    wrong by that whole factor. Returns NaN past :data:`MAX_GAP_FRACTION`.
    """
    ...

def strouhal_k(u_bl_s: float, f_hz: float) -> float:
    """``K = U / (L * f)`` with ``U`` already in body lengths per second.

    So ``K = U_BL/s / f``: stride length in body lengths per beat. Non-finite or
    non-positive ``f`` returns NaN rather than an infinity that would propagate
    silently into a speed prior.
    """
    ...

@dataclass
class CaptureEntry:
    """One captured video file in a dated capture directory."""
    file: str
    bytes: int
    fps: Optional[float] = None
    width: Optional[int] = None
    height: Optional[int] = None
    duration_s: Optional[float] = None
    live_verified: Optional[bool] = None

def _ffprobe_stream(path: Path) -> Optional[dict]:
    """First video stream's format info via ffprobe, or ``None`` if unavailable."""
    ...

def _rational(text: Optional[str]) -> Optional[float]:
    ...

def build_capture_manifest(directory: Path | str, *, out: Optional[Path]=None, cam: str='', write: bool=True) -> dict:
    """Inventory a dated capture directory into ``manifest.json``.

    The expected layout is
    ``data/external/media/leopard_shark/mba_stream/<YYYYMMDD>/``, which lives
    under the gitignored ``data/`` symlink — the manifest is the only durable
    record of what was captured, so it is written next to the media and is the
    thing to copy out.

    ``ffprobe`` is used when it is on PATH (it reads the container's real frame
    rate); otherwise OpenCV supplies fps and geometry and ``probe`` records
    which. Existing ``live_verified`` and ``notes`` values in a manifest already
    in the directory are preserved, because those are human judgements the
    Phase 0 gate asks for and no probe can recover them.
    """
    ...

def write_segment_manifest(out_path: Path | str, clip: Clip, passes: Sequence[ClosePass], *, source_credit: str='', notes: str='', min_px: float=AMPLITUDE_GRADE_MIN_PX) -> Path:
    """Write the curated close-pass manifest as JSON.

    Segments are stored flag-annotated and unfiltered: an ``edge_flag`` or
    ``merged_flag`` segment is still worth a human look, and hiding it would
    repeat the July mistake of letting an automatic selection decide which fish
    was measured. ``clean`` is the count that cleared every flag.

    Each segment carries ``seed_xy_start`` and ``seed_xy_peak``, plus
    ``seed_xy`` as the deprecated alias for the peak seed so that manifests
    written before and after the seeding fix read the same way.
    """
    ...

def render_pass_overlay(clip: Clip, tracks: Sequence[Track], close_pass: ClosePass, out_path: Path | str) -> Optional[Path]:
    """One verification PNG per close pass: every track path plus this pass's box.

    The ``viz.py`` figure, reduced to the part that is actually load-bearing —
    a human deciding whether the segment is one animal, broadside and unclipped,
    which no flag can decide for them.

    Drawn at ``close_pass.seed_frame``, where the animal is largest, which is
    what makes the frame worth looking at. Colour stays **BGR** end to end:
    :class:`Clip` yields BGR, the drawing colours are BGR
    (``(60, 255, 60)`` is the green box), and ``cv2.imwrite`` expects BGR — so
    no channel conversion belongs anywhere on this path. A stray
    ``cv2.cvtColor(..., COLOR_RGB2BGR)`` or ``frame[..., ::-1]`` here renders a
    grey-brown leopard shark red, which is a species call, not a cosmetic bug.
    """
    ...
