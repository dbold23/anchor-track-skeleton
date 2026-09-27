"""Tests for the confidence-ellipse helpers."""
from __future__ import annotations
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pytest
from anchor.trajectory.viz_uncertainty import _radius_for_confidence, add_ellipse_track, confidence_ellipse

def test_radius_for_confidence_known_values():
    ...

def test_radius_for_confidence_invalid():
    ...

def test_axis_aligned_ellipse_matches_analytical():
    """For a diagonal cov [[a, 0], [0, b]] at 1σ (df=2), the ellipse
    semi-axes should be sqrt(a) * 1.515 and sqrt(b) * 1.515."""
    ...

def test_singular_cov_does_not_raise():
    """Grounded particle clouds collapse one eigenvalue. The +1e-6 I
    regularization should keep this from blowing up."""
    ...

def test_high_correlation_ellipse_is_finite():
    """rho ≈ 1 should still produce a valid ellipse via the Schelp
    construction (we clip rho to (-1+ε, 1-ε))."""
    ...

def test_add_ellipse_track_thins_correctly():
    ...

def test_add_ellipse_track_skips_nan_steps():
    ...

def test_add_ellipse_track_validates_shape():
    ...

def test_ellipse_renders_in_data_coordinates():
    """Added to an axes, the ellipse must sit on the map at its UTM mean,
    not at pixel (easting, northing)."""
    ...
