"""High-activity event detection via VeDBA + jerk thresholds.

Grouping (:func:`extract_events`) and the joint-exceedance rule
(:func:`flag_candidate_events`) come from the notebook prototype (Dylan Moran).
Threshold *derivation* does not.

The pre-N5 rule was a within-deployment percentile, which fixes the event
**rate** by construction: a 99.5th-percentile VeDBA rule flags 0.5% of samples
on every animal, so an "event" meant nothing beyond "unusual for this record"
and counts could not be compared at all. :func:`robust_scale_thresholds` is the
default replacement and :func:`percentile_thresholds` keeps the old rule as an
explicit opt-in.

What the replacement does and does not buy, stated plainly because the first
version of this module overclaimed it:

* it frees the rate — measured on the shipped fixtures at
  ``VEDBA_SCALE_FACTOR = 8``, the VeDBA channel flags 0.44% (``ls_slice``),
  3.16% (``br_slice``) and 0.30% (``ws_axy_slice``) of samples, and the joint
  rule 0.06% / 2.18% / 0.06%. A percentile rule would flag the same fraction on
  all three by definition;
* it is **not** an absolute threshold and **not** a noise floor. ``median +
  k * MAD`` is a robust *scale* statistic of the record itself. On ``ls_slice``
  the VeDBA median is 0.1246 g and the resulting threshold 1.1936 g, against a
  measured ``accY_dyn`` sensor floor of 0.0097 g: the statistic is dominated by
  locomotion, not by sensor noise. It therefore still scales with how variable
  the animal's own cruising is — on a synthetic holding ten identical 0.9 g
  bursts, raising the cruising VeDBA sigma through 0.01 / 0.03 / 0.10 / 0.30 g
  moves the threshold to 0.054 / 0.161 / 0.538 / 1.613 g and the event count to
  10 / 10 / 10 / 0.

So counts are comparable between records of similar baseline variability, and
are not comparable between a placid and a restless animal. A genuinely absolute
per-axis threshold in g needs a bench-measured tag noise floor and a
biomechanical burst criterion; that is N4 work and is not available here.
"""
from __future__ import annotations
from typing import Literal
import numpy as np
import pandas as pd
VEDBA_SCALE_FACTOR = 8.0
JERK_SCALE_FACTOR = 8.0

def _robust_baseline(x: np.ndarray) -> tuple[float, float]:
    """``(median, 1.4826 * MAD)`` over the finite samples of ``x``."""
    ...

def robust_scale_thresholds(df: pd.DataFrame, vedba_col: str='vedba', jerk_col: str='jerk_mag', vedba_factor: float=VEDBA_SCALE_FACTOR, jerk_factor: float=JERK_SCALE_FACTOR) -> tuple[float, float]:
    """``median + factor * (1.4826 * MAD)`` on each channel.

    A robust scale rule, not a noise floor and not an absolute threshold — see
    the module docstring for the measured flagged fractions and for the way the
    threshold tracks the animal's own cruising level. Its one guarantee over
    :func:`percentile_thresholds` is that the flagged fraction is free rather
    than fixed by construction, so an animal that bursts more can register more
    events than one that does not.
    """
    ...

def percentile_thresholds(df: pd.DataFrame, vedba_pct: float, jerk_pct: float, vedba_col: str='vedba', jerk_col: str='jerk_mag') -> tuple[float, float]:
    """Legacy within-deployment percentile thresholds — opt-in only.

    Retained for reproducing pre-N5 outputs and for the rare case where "the
    top x% of *this* record" is genuinely the question. It fixes the flagged
    fraction by construction, so it cannot register that one animal bursts more
    than another; see the module docstring.
    """
    ...

def flag_candidate_events(df: pd.DataFrame, vedba_thresh: float, jerk_thresh: float) -> pd.DataFrame:
    """Mark rows where VeDBA **and** jerk both exceed their thresholds.

    The conjunction is deliberate: VeDBA alone rises during sustained cruising,
    jerk alone rises on a single-sample tag knock, and only their coincidence
    indicates a short high-power manoeuvre.
    """
    ...

def extract_events(df: pd.DataFrame, fs: float, min_gap_s: float=1.0, time_col: str='t') -> pd.DataFrame:
    """Group flagged samples into events separated by at least ``min_gap_s``."""
    ...
