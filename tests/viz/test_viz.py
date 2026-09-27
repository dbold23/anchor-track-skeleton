"""Tests for the Anchor figure theme, marks and composed figures."""
from __future__ import annotations
import matplotlib
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pytest
from matplotlib.colors import to_rgb
from anchor.viz import figures, marks, theme
from anchor.viz.scene import make_scene

@pytest.fixture(scope='module')
def scene():
    ...

def test_state_palette_is_four_distinct_colours_per_mode():
    ...

def test_state_color_by_index_and_name_agree():
    ...

def test_status_colours_are_reserved_from_states():
    ...

def test_style_context_restores_rcparams_and_mode():
    ...

def test_env_var_selects_dark(monkeypatch):
    ...

def test_colormaps_registered():
    ...

def test_lens_is_one_patch_per_level_and_covers_the_ellipses():
    ...

def test_lens_skips_non_finite_steps_and_rejects_length_mismatch():
    ...

def test_ellipse_union_rings_all_wind_the_same_way():
    ...

def test_state_ribbon_labels_long_runs_only():
    ...

def test_release_relative_axes_formats_zero_without_sign():
    ...

def test_receipt_carries_id_and_fields():
    ...

@pytest.mark.parametrize('mode', ['light', 'dark'])
def test_track_figure_renders_every_strip(scene, tmp_path, mode):
    ...

def test_track_figure_map_only(scene):
    ...

def test_gallery_writes_pngs(tmp_path):
    ...

def test_ethogram_has_no_twin_axis(scene):
    ...
