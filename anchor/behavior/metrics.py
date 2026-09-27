"""Per-class classification metrics for behavior evaluation.

Cohen's κ and overall accuracy summarise agreement but hide the failure mode that
matters most for elasmobranch ethograms: rare behaviours. Brewster et al. 2018
(*Mar Biol*) classified five lemon-shark behaviours at macro-F=0.88 yet the rarest
classes (headshaking, burst swimming) had 0.26–0.30 class error while common
swimming scored F=0.999. Reviewers expect per-class precision/recall/F1, a
confusion matrix, and balanced accuracy — not a single pooled scalar.

This module is the shared metrics core used by both the supervised LOSO evaluation
(:func:`anchor.behavior.cv.evaluate_supervised_loso`) and paired-tag agreement
(:func:`anchor.validation.paired_tag.cross_tag_agreement`).
"""
from __future__ import annotations
from typing import Optional, Sequence
import numpy as np
import pandas as pd

def classification_metrics(y_true: Sequence, y_pred: Sequence, labels: Optional[Sequence]=None, label_names: Optional[dict]=None) -> dict:
    """Overall + per-class metrics for a single (y_true, y_pred) comparison.

    Parameters
    ----------
    y_true, y_pred
        Equal-length arrays of class labels (int or str).
    labels
        Explicit label ordering. Defaults to the sorted union of both arrays so
        classes present only in the test fold (common under LOSO) still appear.
    label_names
        Optional ``{label: human_name}`` map applied to per-class keys and the
        confusion-matrix axes.

    Returns
    -------
    dict with keys:
        ``n`` (int), ``accuracy``, ``balanced_accuracy``, ``kappa``,
        ``macro_f1``, ``weighted_f1`` (floats),
        ``per_class`` ({name: {precision, recall, f1, support}}),
        ``confusion`` (DataFrame, true=rows, pred=cols),
        ``labels`` (the resolved label ordering).
    """
    ...

def flatten_metrics(metrics: dict) -> dict:
    """Collapse a :func:`classification_metrics` dict to scalar-only keys.

    Produces a flat ``{name: float}`` dict suitable for per-fold aggregation by
    :func:`anchor.behavior.cv.aggregate_fold_metrics`. Per-class metrics become
    ``f1__<name>`` / ``recall__<name>`` / ``precision__<name>`` keys; the
    confusion matrix and label list are dropped (non-scalar).
    """
    ...
