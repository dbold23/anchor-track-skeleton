"""Event detection: threshold derivation, the joint rule, and grouping.

N5 replaced within-deployment percentile thresholds with a robust-scale rule.
The point of the change is that the flagged *fraction* must be free to differ
between animals; the percentile rule fixed it by construction, which is what
these tests pin down. They also pin the limit of the replacement — it is a
within-record statistic, so it still tracks the animal's own cruising level and
does not give absolute, cross-animal event counts. That last property is
asserted here rather than left to a docstring, because the first version of
this module claimed it and did not have it.
"""
from __future__ import annotations
from pathlib import Path
import numpy as np
import pandas as pd
import pytest
from anchor import events as EV

def _deployment(fs: float=25.0, seconds: float=200.0, baseline_g: float=0.02, n_bursts: int=3, burst_g: float=1.0, seed: int=0) -> pd.DataFrame:
    """Quiet baseline plus ``n_bursts`` short high-VeDBA, high-jerk events."""
    ...

def test_absolute_threshold_helper_is_not_advertised():
    """No function here promises an absolute or noise-floor-calibrated threshold.

    Naming one that would be a claim the module cannot support until N4 supplies
    a bench-measured tag noise floor.
    """
    ...

def test_get_thresholds_is_gone():
    """The unused 99.5/99.9 helper was removed rather than left to rot."""
    ...

def test_percentile_thresholds_fix_the_event_rate():
    """The legacy rule flags the same fraction of samples on any animal."""
    ...

def test_robust_scale_thresholds_let_the_flagged_fraction_vary():
    """The default rule registers that one animal bursts more than another."""
    ...

def test_robust_scale_threshold_is_not_moved_by_the_bursts_it_detects():
    """Adding bursts must not move the threshold that finds them.

    This is the half of the claim that does hold: median and MAD are robust, so
    a handful of large excursions leaves the threshold where it was.
    """
    ...

def test_robust_scale_thresholds_are_not_absolute_across_animals():
    """Two animals, identical absolute bursts, different cruising levels.

    ``median + k * MAD`` is a within-record scale statistic, so raising the
    cruising level raises the threshold proportionally and the *same* 0.9 g
    burst stops being an event. Measured: cruising VeDBA sigma 0.01 / 0.03 /
    0.10 / 0.30 g gives thresholds 0.054 / 0.161 / 0.538 / 1.613 g and event
    counts 10 / 10 / 10 / 0. The module docstring says so; this test is what
    stops that admission from silently becoming false in either direction — if
    a future rule really is absolute, this test fails and the docstring must be
    rewritten with it.
    """
    ...

def test_robust_scale_thresholds_ignore_nans():
    ...

def test_flag_requires_both_channels():
    """VeDBA alone or jerk alone is not an event; only their coincidence is."""
    ...

def test_flag_is_strict_inequality_on_both():
    """A sample sitting exactly on either threshold does not qualify."""
    ...

def test_extract_events_groups_by_min_gap():
    """Flagged runs closer than ``min_gap_s`` merge into one event."""
    ...

def test_extract_events_empty_when_nothing_flagged():
    ...

def _cfg_with(method, tmp_path, **event_fields):
    """A loadable deployment config carrying the given event settings."""
    ...

@pytest.mark.parametrize('method, n_events', [('robust_scale', 0), ('percentile', 2)])
def test_pipeline_takes_the_event_rule_from_the_config(method, n_events, tmp_path, monkeypatch):
    """``extract_events_for`` must honour ``event_thresholds.method``.

    Before the field existed the rule was a hard-coded default on the function
    and a YAML that tried to set it failed validation outright (``extra=
    "forbid"``), so a deployment could not be reproduced from its config alone.
    The record separates the two rules: on a restless animal (cruising VeDBA
    sigma 0.3 g) with three 1.0 g bursts, ``median + 8 * MAD`` lands at 1.62 g
    and flags none of them, while the 99.5th percentile lands at 1.13 g and
    flags two — so a pipeline that ignored the config could not return both
    counts.
    """
    ...

def test_explicit_method_argument_overrides_the_config(tmp_path, monkeypatch):
    """The CLI's one-off ``--method`` must still win over the YAML."""
    ...

def test_pipeline_takes_the_event_scale_factors_from_the_config(tmp_path, monkeypatch):
    """A retuned ``vedba_scale_factor`` must reach ``robust_scale_thresholds``."""
    ...
