"""Hyperparameter sensitivity sweep harness."""
from __future__ import annotations
import numpy as np
import pytest
from anchor.trajectory import sensitivity as S

def test_parse_sweep_spec():
    ...

def test_parse_sweep_spec_rejects_malformed():
    ...

def test_track_divergence_zero_and_offset():
    ...

def test_track_divergence_truncates_to_shorter():
    ...

def test_final_position_sigma_m():
    ...

def test_sweep_parameter_scores_and_sensitivity():
    ...

def test_sweep_parameter_runs_each_value_once():
    ...
