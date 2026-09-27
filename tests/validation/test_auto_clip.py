"""Auto-clip tests: ffmpeg invocation + manifest output.

Skips if ffmpeg is not on PATH, since the clipping is a pure ffmpeg-shell
wrapper. We test the manifest CSV plumbing and the missing-binary error.
"""
from __future__ import annotations
import shutil
import pandas as pd
import pytest
from anchor.validation import auto_clip as AC

def test_check_ffmpeg_raises_when_missing():
    ...

@pytest.mark.skipif(not HAS_FFMPEG, reason='ffmpeg not on PATH')
def test_clip_uncertain_windows_creates_manifest(tmp_path):
    """Generate a 5 s synthetic mp4, clip 2 windows, check manifest exists."""
    ...

def test_clip_uncertain_windows_preserves_uncertainty(tmp_path):
    """``_uncertainty`` must survive the row iteration (regression: itertuples
    renames leading-underscore columns to positional ``_N``, yielding NaN)."""
    ...

def test_clip_uncertain_windows_video_t_fallback(tmp_path):
    """When video_t is missing, fall back to start_t - video_offset_s."""
    ...
