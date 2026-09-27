"""Unit tests for multi-source outline comparison."""
from __future__ import annotations
import shapely.geometry as sg
from anchor.trajectory.site_geometry.compare import Source, compare_outlines, render_comparison_figure

def _box(lon0, lat0, lon1, lat1):
    ...

def test_jaccard_identical_sources():
    ...

def test_jaccard_disjoint_sources_zero():
    ...

def test_jaccard_uses_largest_component_only():
    """Multi-poly source with one big and several tiny features should
    measure Jaccard on the big one only — that's the whole point of
    largest-component metrics."""
    ...

def test_warning_emitted_when_primary_outside_nhd():
    ...

def test_render_smoke(tmp_path):
    ...
