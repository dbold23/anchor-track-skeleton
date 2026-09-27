"""Per-class classification metrics."""
from __future__ import annotations
import numpy as np
import pandas as pd
from anchor.behavior import metrics as M

def test_perfect_prediction():
    ...

def test_per_class_surfaces_rare_class_failure():
    ...

def test_labels_union_covers_test_only_classes():
    ...

def test_label_names_applied():
    ...

def test_confusion_matrix_shape_and_orientation():
    ...

def test_empty_input():
    ...

def test_mismatched_lengths_raise():
    ...

def test_flatten_metrics_keys():
    ...

def test_absent_class_does_not_drag_macro_f1():
    """Under LOSO a held-out subject may never show a class; a perfect
    prediction must still score macro-F1 = 1."""
    ...

def test_false_positive_class_still_counts_in_macro_f1():
    ...
