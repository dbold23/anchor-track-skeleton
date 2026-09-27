"""Behavior inference: unsupervised (HMM/GMM) + supervised (RF/XGB).

Paper section 4.4. Public API is re-exported from this `__init__` so callers
can do `from anchor.behavior import fit_hmm, fit_supervised, FittedClassifier`.
"""
from anchor.behavior._base import FittedClassifier, load_model, predict_from_features, save_model
from anchor.behavior.hmm import fit_gmm, fit_hmm, fit_model, label_clusters_post_hoc, predict_proba, predict_states, score_log_likelihood
from anchor.behavior.supervised import fit_supervised
from anchor.behavior.cv import evaluate_supervised_loso, leave_one_subject_out, load_labeled_features, subject_stratified_kfold
from anchor.behavior.metrics import classification_metrics, flatten_metrics
from anchor.behavior.labeling_rounds import LabelingRound, RoundManifest, RoundStatus, bootstrap_round, complete_round, mark_clipped, status_summary
__all__ = ['FittedClassifier', 'fit_gmm', 'fit_hmm', 'fit_model', 'fit_supervised', 'evaluate_supervised_loso', 'leave_one_subject_out', 'subject_stratified_kfold', 'load_labeled_features', 'classification_metrics', 'flatten_metrics', 'label_clusters_post_hoc', 'load_model', 'predict_from_features', 'predict_proba', 'predict_states', 'save_model', 'score_log_likelihood', 'LabelingRound', 'RoundManifest', 'RoundStatus', 'bootstrap_round', 'complete_round', 'mark_clipped', 'status_summary']
