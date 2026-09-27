"""Kinematics: DBA family, jerk, pitch/roll, locomotion-mode dispatch, features.

Paper section 4.3. Exports the public API of `core` (per-sample kinematics),
`locomotion` (axial vs pectoral dispatch), and `features` (window summary).
"""
from anchor.kinematics.core import add_dynamic_acceleration, add_jerk, add_odba, add_pitch_roll, add_rotation_corrected_dba, add_tailbeat_columns, add_vedba, detect_tailbeat_peaks, lowpass_filter, tailbeat_frequency_from_peaks
from anchor.kinematics.locomotion import axial_undulator, dispatch, pectoral_oscillator
from anchor.kinematics.features import build_feature_matrix, standardize, summarize_window_metrics
from anchor.kinematics.stats import detect_change_points, mahalanobis_distance, rotation_test
__all__ = ['add_dynamic_acceleration', 'add_jerk', 'add_odba', 'add_pitch_roll', 'add_rotation_corrected_dba', 'add_tailbeat_columns', 'add_vedba', 'axial_undulator', 'build_feature_matrix', 'detect_change_points', 'detect_tailbeat_peaks', 'mahalanobis_distance', 'rotation_test', 'dispatch', 'lowpass_filter', 'pectoral_oscillator', 'standardize', 'summarize_window_metrics', 'tailbeat_frequency_from_peaks']
