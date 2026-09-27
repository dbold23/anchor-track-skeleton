"""End-to-end Elkhorn Slough trajectory demo for the leopard shark
LS_260311_S1 deployment.

Pipeline:
    1. AXY ingest                — observed (heading, speed) at 1 Hz; depth=NaN
    2. Bathymetry + slough polygon
    3. Particle filter            — release anchor + polygon hard constraint
                                    + dead-reckoning dynamics
    4. 4-panel summary figure     — track on bathy, drift envelope, heading,
                                    speed/tailbeat over time
    5. Folium HTML interactive map

No VPS, no observed depth — pure DR + spatial polygon constraint. Track
shape is the deliverable; absolute position drifts unboundedly after the
release anchor. RMSE is meaningless; what matters is that the path stays
in water and matches the behavior segments from the anchor HMM.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import branca.colormap as bcm
import folium
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pyproj
import rasterio
from PIL import Image
from folium.plugins import Fullscreen, MeasureControl
from folium.raster_layers import ImageOverlay
from anchor.ingest.config import load_config
from anchor.viz import marks as _viz_marks
from anchor.viz import theme as _viz_theme
from anchor.trajectory.axy_ingest import align_behavior_states, behavior_to_process_noise, ingest_deployment
from anchor.trajectory.bathymetry import BathyLookup
from anchor.trajectory.particle_filter import FilterConfig, ParticleFilter
from anchor.trajectory.polygon_constraint import PolygonConstraint
from anchor.trajectory.release_anchor import ReleaseAnchor
from anchor.trajectory.sites.elkhorn import ELKHORN_BATHY_SIGMA_TIF, ELKHORN_BATHY_TIF, ELKHORN_DECLINATION_DEG_2026, ELKHORN_OUTLINE_GEOJSON

def build_tide_and_current(track, *, tide_source: str, current_source: str, prism_K: float, n_steps: int, allow_network: bool=True):
    """Factory used by every Elkhorn CLI so tide/current loading is consistent.

    Returns ``(tide_series, current_field)``. Either may be ``None``.
    """
    ...

def load_tide_aware_polygon(*, fall_back_to_static: bool=True):
    """Load TidalPolygonConstraint if the stack file exists; else fall back."""
    ...

def run_filter(track, bathy: BathyLookup, polygon, release: ReleaseAnchor, n_particles: int=4000, n_steps: int | None=None, process_noise_xy_m: float=2.5, process_noise_per_step: np.ndarray | None=None, enable_bathymetry: bool=False, bathymetry_extra_sigma_m: float=1.0, tide_series=None, current_field=None, seed: int=0):
    """Run the forward filter. Returns ``(means, stds, inside_count, bathy_updates)``.

    Tide / current integration:

    * ``tide_series`` — a ``TideSeries``. If supplied AND ``polygon`` is a
      ``TidalPolygonConstraint``, the polygon hard rejection uses the
      tide-conditional wet mask each step. If supplied with a regular
      ``PolygonConstraint`` it's harmless (ignored).
    * ``current_field`` — a ``CurrentField``. If supplied, per-particle
      ``(u, v)`` is fed to ``predict()`` each step.

    Both require ``track.t0_utc`` to be set so the per-step UTC timestamp can
    be computed; raise ``ValueError`` otherwise.
    """
    ...

@_viz_theme.styled
def make_static_figure(track, means, stds, inside_count, bathy_path: Path, polygon_path: Path, release: ReleaseAnchor, out_path: Path, deployment_id: str, states: np.ndarray | None=None, species_label: str='leopard shark, AXY-5', bathy_constrained: bool=False, cov_xy: np.ndarray | None=None):
    ...

def make_html_map(means, release: ReleaseAnchor, bathy_path: Path, polygon_path: Path, out_path: Path, deployment_id: str):
    """Interactive Folium map: bathymetry + reconstructed track + release."""
    ...

def main() -> None:
    ...
