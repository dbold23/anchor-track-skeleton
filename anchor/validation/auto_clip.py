"""Active-learning loop closure: clip uncertain windows from source video.

The ``anchor labels query`` CLI (see :func:`anchor.behavior.labels.select_uncertain_windows`)
produces a CSV ranked by HMM posterior uncertainty. Without auto-clipping
the annotator has to manually scrub through hours of source video for each
target window — slow and error-prone. This module cuts the source video
into per-window MP4 clips so the annotator can label them quickly in
BORIS/VIA, then ``anchor labels import`` cycles them back into the
training set.

Requires ``ffmpeg`` on PATH.
"""
from __future__ import annotations
import shutil
import subprocess
from pathlib import Path
import pandas as pd

def _check_ffmpeg(ffmpeg_path: str='ffmpeg') -> str:
    ...

def clip_window(video_path: str | Path, start_s: float, duration_s: float, out_path: str | Path, ffmpeg_path: str='ffmpeg', overwrite: bool=True) -> Path:
    """Cut ``[start_s, start_s + duration_s]`` from ``video_path`` into ``out_path``.

    Uses copy-codec when possible (no re-encode) for speed; falls back to
    H.264 if the source has unusual keyframe spacing that breaks copy-mode
    on small windows. Returns the output path on success.
    """
    ...

def clip_uncertain_windows(query_csv: str | Path, video_path: str | Path, out_dir: str | Path, video_offset_s: float=0.0, duration_pad_s: float=0.0, ffmpeg_path: str='ffmpeg', name_template: str='q{rank:04d}_{video_t:.2f}s_unc{unc:.3f}.mp4') -> pd.DataFrame:
    """Clip every window in a query CSV.

    The query CSV is the output of ``anchor labels query`` — must carry
    columns ``start_t`` (or ``video_t``), ``end_t``, and ``_uncertainty``.
    ``video_offset_s`` is subtracted from accel-time to convert to video-time
    (only used if the CSV has ``start_t`` but not ``video_t``).

    Returns a manifest DataFrame logging where each clip went, suitable for
    handing to the annotator.
    """
    ...
