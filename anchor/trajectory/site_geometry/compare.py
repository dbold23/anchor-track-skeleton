"""Multi-source slough-outline comparison + consensus selection.

Cross-validates a candidate outline against external authoritative
sources (USGS NHD, OSM, optionally manual) using Jaccard / IoU and
geometric subset metrics. Produces an overlay figure with all sources
visible so a human reviewer can spot disagreements before the canonical
outline is committed.

Decision policy:

    primary:    bathymetric flood-fill (authoritative for what the
                filter can actually evaluate — only bathy-finite cells
                participate in the wet predicate)
    validation: NHD waterbody + OSM natural=water, both clipped to AOI
    consensus:  intersection-bounded acceptance — primary is the
                canonical outline; if Jaccard(primary, NHD) < 0.5 OR
                Jaccard(primary, OSM) < 0.4, raise a warning prompting
                human review

Why these thresholds: NHD is generalized at ~10 m so a bathy-derived
outline at ~4 m won't perfectly match — Jaccard ≥ 0.5 is the empirical
floor below which a structural disagreement is signaled (likely a
different waterbody got picked up). OSM has more variability so the
threshold is laxer at 0.4.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
import matplotlib.pyplot as plt
import numpy as np
import shapely.geometry
import shapely.ops

@dataclass
class Source:
    """A named outline source with provenance."""
    name: str
    polygons: list[shapely.geometry.Polygon]

    @property
    def union(self) -> shapely.geometry.base.BaseGeometry:
        ...

    @property
    def largest_component(self) -> shapely.geometry.Polygon:
        """Return the single largest polygon — the 'main' waterbody.

        Useful when a source includes many small disjoint features
        (small marsh ponds, separate side embayments). The main
        slough body is the largest one."""
        ...

    @property
    def total_area_deg2(self) -> float:
        ...

@dataclass
class ComparisonReport:
    sources: list[Source]

def _pairwise_metrics(a: Source, b: Source) -> tuple[float, float, float]:
    """Return (jaccard, a_contained_in_b, b_contained_in_a) on largest
    component of each.

    Why largest-component-only: every external source returns multiple
    polygons within an AOI bbox — NHD splits Elkhorn Slough, Moss Landing
    Harbor, and Moro Cojo Slough into separate polygons; OSM fragments
    further into individual ponds. The pairwise *full-union* Jaccard
    therefore conflates "are we looking at the same waterbody" with "do
    we agree on the waterbody's exact shape." Comparing largest
    components only — the slough-proper part of each source —
    disentangles those questions.
    """
    ...

def compare_outlines(sources: list[Source], *, primary_name: str='bathy', nhd_jaccard_floor: float=0.5, osm_jaccard_floor: float=0.4) -> ComparisonReport:
    ...

def render_comparison_figure(rep: ComparisonReport, *, bbox_lonlat: Optional[tuple[float, float, float, float]]=None, seed_lonlat: Optional[tuple[float, float]]=None, out_path: Optional[Path]=None) -> plt.Figure:
    ...
