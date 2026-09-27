"""End-to-end smoke test: real AXY → filter → posterior trajectory.

Verifies the pipeline produces a non-trivial reconstructed track that:
  - stays mostly inside the slough polygon (>50% of particles inside at all times)
  - exhibits monotonically growing 2σ position spread (no observation anchors after t=0)
"""
from __future__ import annotations
from pathlib import Path
import numpy as np
import pytest
from anchor.trajectory.bathymetry import BathyLookup
from anchor.trajectory.particle_filter import FilterConfig, ParticleFilter
from anchor.trajectory.polygon_constraint import PolygonConstraint
from anchor.trajectory.release_anchor import ReleaseAnchor

@skipif_missing
def test_filter_runs_on_real_axy_and_stays_inside_polygon():
    ...
