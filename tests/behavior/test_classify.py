"""GMM classifier + post-hoc labeling."""
from __future__ import annotations
import numpy as np
import pytest
from anchor import behavior as CL

def _make_synthetic(k: int=3, n_per: int=120, seed: int=0) -> np.ndarray:
    ...

def test_fit_gmm_predicts_clusters():
    ...

def test_label_clusters_post_hoc_ordering():
    """Higher-activity centroids get later labels (rest → burst)."""
    ...

def test_save_load_roundtrip(tmp_path):
    ...

def test_fit_hmm_predicts_clusters():
    ...

def test_fit_hmm_needs_enough_windows():
    ...

def test_fit_model_dispatches():
    ...

@pytest.mark.parametrize('method', ['gmm', 'hmm'])
def test_predict_proba_shape_and_normalization(method):
    ...

@pytest.mark.parametrize('method', ['gmm', 'hmm'])
def test_score_log_likelihood_is_per_sample(method):
    """Per-sample average should be within a reasonable range for well-fit models."""
    ...

def test_hmm_save_load_roundtrip(tmp_path):
    ...

def test_predict_from_features_supports_string_labels():
    """Supervised models trained on string labels predict string states."""
    ...
