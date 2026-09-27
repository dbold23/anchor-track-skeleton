"""End-to-end paired-tag runner tests on synthetic two-stream features."""
from __future__ import annotations
import numpy as np
import pandas as pd
import pytest
from anchor.behavior import _base as B
from anchor.behavior import predict_from_features
from anchor.kinematics import features as F
from anchor.validation import paired_tag_runner as PTR

def _fit_simple_gmm(features_df: pd.DataFrame, k: int=4) -> B.FittedClassifier:
    """Bare-bones FittedClassifier using sklearn GMM on a feature DataFrame."""
    ...

def test_predict_from_features_roundtrip():
    """A model trained on a DataFrame predicts the same states when re-applied."""
    ...

def test_predict_from_features_errors_on_missing_cols():
    ...

def test_match_windows_in_time_basic():
    ...

def test_match_windows_in_time_drops_far_pairs():
    ...

def test_match_windows_in_time_handles_empty():
    ...

def _make_synthetic_features(n_windows: int=200, seed: int=0, state_seed: int=7) -> pd.DataFrame:
    """Generate behavior-feature windows with 4 latent states.

    State means span the full feature space so a 4-component GMM clusters
    cleanly. Used to fit one HMM and then re-apply it to a "second tag's"
    similarly-distributed features.
    """
    ...

def _make_paired_synthetic(n_windows_axy: int, n_windows_cats: int, cats_offset_windows: int, master_seed: int=0, axy_noise_seed: int=1, cats_noise_seed: int=2) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Two tag-feature streams sampling overlapping slices of a master signal.

    Master state sequence covers physical windows [0, total_windows). AXY
    observes physical windows [0, n_windows_axy) and reports local times
    starting at 0. CATS observes physical windows
    [cats_offset_windows, cats_offset_windows + n_windows_cats) and reports
    local times also starting at 0. CATS's clock is therefore "ahead" of
    AXY's by ``cats_offset_windows * 5 s`` because the same physical event
    has CATS_local_t = AXY_local_t - cats_offset_windows * 5.

    Wait, the convention in :func:`align_clocks_xcorr` is "positive offset
    means CATS clock is ahead of AXY". For our setup, CATS_local_t for an
    event at physical-window i is (i - cats_offset_windows) * 5, while
    AXY_local_t for the same event is i * 5. So CATS_local_t < AXY_local_t,
    meaning CATS clock reads SMALLER numbers for the same event, meaning
    CATS clock is BEHIND AXY by cats_offset_windows * 5. The xcorr should
    return a NEGATIVE offset_s in this case.
    """
    ...

def test_run_paired_tag_validation_recovers_clock_offset():
    """Two tags observing the same master state sequence with known offset."""
    ...

def test_run_paired_tag_validation_high_kappa_when_streams_agree():
    """Identical-distribution streams + same model → κ should be high (≥ 0.7)."""
    ...

def test_run_paired_tag_validation_low_kappa_when_streams_disagree():
    """Different latent state sequences → κ should be near zero."""
    ...

def test_run_paired_tag_validation_rejects_missing_align_signal():
    ...

def _build_round(deployment_id: str, n: int, kappa_hint: float, seed: int) -> PTR.DeploymentRound:
    """Synthesize a paired-tag round with target Cohen's κ.

    To get target κ ≈ x with 4 balanced classes (chance = 0.25): set the
    fraction-correct to ``p`` such that κ = (p - 0.25) / 0.75 = x → p = 0.25 + 0.75x.
    """
    ...

def test_aggregate_paired_tag_results_basic():
    """Three deployments with κ ≈ 0.7, 0.8, 0.6 → bootstrap median ~ mean of those."""
    ...

def test_aggregate_paired_tag_results_handles_empty():
    ...

def test_aggregate_paired_tag_results_pooled_matches_single_when_one_round():
    ...

def test_load_paired_tag_round_roundtrip(tmp_path):
    """Write a synthetic report dir → load → fields populate."""
    ...
