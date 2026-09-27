"""Animated 4-panel particle-filter visualization for the bat ray
BR_260318_S3 deployment — "chains dying" on real benthic data.

Same SMC chain that ``bat_ray_demo.py`` runs (release anchor + slough polygon
hard constraint + Gaussian bathymetry penalty using observed depth + DR
dynamics), but with per-step snapshots rendered as a `FuncAnimation`:

  - Slough bathymetry underlay + polygon outline
  - 1k particles drawn each frame, colored by normalized weight (viridis)
  - Posterior-mean trail in red as it accumulates
  - Release point as a star
  - Ancestry collapse panel: # unique founder particles vs time (chains dying)
  - Particles-inside-polygon panel: how often the hard constraint fires
  - Drift-envelope panel: distance from release ± 2σ posterior spread

To keep memory bounded the filter runs at full 1 Hz but only snapshots every
``--snapshot-stride`` steps. Animation then further downsamples via
``--frame-stride``.

Outputs ``<out>.gif`` (Pillow) and ``<out>.mp4`` (ffmpeg, when available).
"""
from __future__ import annotations
import argparse
import concurrent.futures as _futures
import json
import logging
import pickle
from dataclasses import replace
from pathlib import Path
import matplotlib.animation as mpl_anim
import matplotlib.pyplot as plt
import numpy as np
import pyproj
import rasterio
import shapely.geometry
from shapely.ops import transform as shapely_transform
from anchor.ingest.config import load_config
from anchor.trajectory.axy_ingest import align_behavior_states, behavior_to_process_noise, ingest_deployment
from anchor.trajectory.bathymetry import BathyLookup
from anchor.trajectory.particle_filter import DEFAULT_POLYGON_PROPOSAL_DRAWS, DEFAULT_POLYGON_SOFT_WIDTH_M, POLYGON_PENALTY_NATS, SBIAS, SSCALE, FilterConfig, LatentNode, ParticleFilter, build_latent_grid, default_latent_axis, draw_latent_node_counts, evaluate_degeneracy, latent_axis_marginal, latent_axis_values, latent_posterior, unique_founder_count, weight_diagnostics, worst_degeneracy_node
from anchor.trajectory.polygon_constraint import PolygonConstraint
from anchor.trajectory.release_anchor import ReleaseAnchor
from anchor.trajectory.sites.elkhorn import ELKHORN_BATHY_SIGMA_TIF, ELKHORN_BATHY_TIF, ELKHORN_DECLINATION_DEG_2026, ELKHORN_NOAA_WL_STATION, ELKHORN_OUTLINE_GEOJSON, ELKHORN_TIDAL_PRISM_K_M

def _load_polygon_geometries(geojson_path: Path, raster_crs):
    ...

def normalize_weights(log_w: np.ndarray) -> np.ndarray:
    ...

def resolve_n_steps(n_steps: int | None, n_track: int, *, has_end_anchor: bool=False, allow_truncation: bool=False) -> int:
    """How many filter steps to run, given a request and the track length.

    ``n_steps=None`` means the whole track. An explicit request longer than the
    track is clipped, as it always was. An explicit request *shorter* than the
    track used to be honoured silently, which reconstructs only the head of the
    record; when a recovery anchor is in play that also pins the recovery fix to
    the wrong moment, so that case now raises unless ``allow_truncation`` says
    the caller means it (sensitivity runs).
    """
    ...

def _log_sum_exp(log_weights: np.ndarray) -> float:
    """``log Σ_i exp(lw_i)``, returning ``-inf`` when every term underflows.

    Used only to accumulate the filter's log marginal likelihood, so it must
    not clamp: a step whose total weight really is zero has to be reported as
    such rather than smoothed into a finite number.
    """
    ...

def run_filter_with_snapshots(track, bathy: BathyLookup, polygon, release: ReleaseAnchor, n_steps: int | None, n_particles: int, snapshot_stride: int, process_noise_per_step: np.ndarray | None, enable_bathymetry: bool, bathymetry_extra_sigma_m: float, tide_series=None, current_field=None, verified_positions=None, traj=None, seed: int=0, has_end_anchor: bool=False, allow_truncation: bool=False, latent_node: LatentNode | None=None, keep_history: bool=True):
    """One forward bootstrap filter, snapshotting every ``snapshot_stride`` steps.

    ``latent_node`` is the outer-grid hook (design §3.5). ``None`` — the default
    and the only thing any existing caller passes — runs the shipped 4-state
    path verbatim: ``psi_bias`` and ``k_speed`` stay particle-state dimensions
    with their configured init and walk sigmas. A :class:`LatentNode` instead
    *conditions* on that node: both latents are frozen at the node's values for
    every particle, their init and walk sigmas are forced to zero, and what is
    left free in the state is ``(x, y)``. The RNG is consumed identically in
    both cases (a zero-sigma normal is still drawn), which is what makes a
    single-node grid reproduce the frozen-latent particle run bit for bit.

    ``keep_history=False`` skips the snapshot copies. ``snapshot_steps`` is
    still recorded, so the grid driver can run a node purely for its marginal
    likelihood without paying ``T_snap × N × 4`` floats for a history it will
    not smooth.
    """
    ...

def _grid_worker_init(payload: dict) -> None:
    ...

def _run_grid_node(payload: dict, node: LatentNode, keep_history: bool) -> dict:
    """One node's conditional filter. Deterministic in ``(node, seed)`` alone."""
    ...

def _grid_worker_run(job):
    ...

class _Sink:
    """A write-only sink, so the picklability probe below allocates nothing."""

    def write(self, _b):
        ...

def _payload_pickle_error(payload) -> Exception | None:
    """``None`` if ``payload`` can cross a process boundary, else why not.

    ``ProcessPoolExecutor`` uses the *spawn* start method on macOS and Windows,
    so every worker input is pickled. Probing here turns an unpicklable input
    into a named, actionable warning and a correct sequential run, instead of
    an ``AttributeError`` raised from deep inside ``Process.start`` after the
    filter has already been set up.
    """
    ...

def resolve_grid_workers(payload, n_jobs: int, workers: int) -> tuple[int, str]:
    """How many worker processes this run can actually use, and why.

    Returns ``(workers, reason)``; ``reason`` is ``""`` when the requested
    count stands and otherwise says in one line why it did not, so the driver
    can print it. A run that quietly falls back to sequential and still reports
    "8 workers" is the kind of thing that makes a wall-clock number a lie.
    """
    ...

def _run_grid_nodes(payload, nodes, *, keep_history: bool, workers: int) -> list[dict]:
    """Run ``nodes``, in this process or across a process pool, in node order.

    Threads would not help: the filter is a long NumPy loop that holds the GIL
    between array calls. A single job is always run inline — spawning a pool to
    run one node costs more than the node. ``workers`` is taken as already
    resolved by :func:`resolve_grid_workers`; the numbers do not depend on it,
    because a node is a pure function of ``(node, seed)``.
    """
    ...

def _polygon_mode_grid_summary(results: list[dict]) -> dict:
    """Grid totals of the water constraint's per-run accounting, scalars only.

    ``run_filter_with_snapshots`` records ``mean_z_at_step``,
    ``n_redraws_at_step`` and ``n_zero_accepted_at_step`` — three arrays of
    ``n_steps`` numbers per node, which on the flagship's 45-node grid is 4.5 M
    numbers. They stay in ``filter_state``; what reaches the latent-grid JSON
    and the parquet footer is this reduction, the same bargain
    ``_degeneracy_metadata`` strikes with ``per_step``.

    ``mean_z`` is averaged over the nodes that measured one (the indicator
    measures none and reports ``nan``); the two counts are summed.
    """
    ...

def run_filter_over_latent_grid(track, bathy: BathyLookup, polygon, release: ReleaseAnchor, *, traj, seed: int=0, **filter_kwargs):
    """Grid mode: a conditional bootstrap filter per latent node (design §3.5).

    The shipped 4-state filter carries ``(psi_bias, k_speed)`` as particle-state
    dimensions with near-zero random walks. Resampling copies whole particles,
    so those two dimensions can only ever *lose* atoms — the flagship run
    finished with one surviving ``k_speed`` value out of 4000 founders and a
    reported posterior sd of exactly zero. No amount of tuning fixes that,
    because it is ancestral degeneracy on a static parameter.

    Here the latents leave the state. Node ``j`` fixes ``(psi_bias, k_speed)``
    and runs its own filter over ``(x, y)``; the node's log marginal likelihood
    — accumulated inside :func:`run_filter_with_snapshots` before any weight
    normalisation — is the evidence for that pair, and

        ``posterior_j ∝ exp(log_prior_j + log_marginal_j)``

    is a posterior over the latents that resampling cannot collapse, because
    resampling never happens *across* nodes. The prior is the same Gaussian the
    particle mode samples its initial cloud from, so the two modes start from
    the same belief; the grid's cell widths are equal and cancel.

    This posterior conditions on the *forward* observations only. On this
    pipeline the end anchor does not exist yet (it is back-propagated from the
    recovery position after the filter runs), so the driver returns every
    node's terminal cloud in ``latent_grid_terminals`` and the caller folds
    ``log p(anchor | y, node)`` in with
    :func:`~anchor.trajectory.particle_filter.apply_end_anchor_to_latent_grid`
    before drawing the smoother's nodes. ``latent_grid["anchor_applied"]``
    says whether that happened.

    Two passes, both exactly reproducible:

    1. every node, ``keep_history=False`` — the marginals, the per-node
       diagnostics and the terminal clouds, at bounded memory (a full history
       is ``T_snap × N × 4`` floats per node, which a 25-node grid cannot
       hold);
    2. the MAP node alone, ``keep_history=True`` — the history the report, the
       animation and the end-anchor binding check read. Every *other* node the
       smoother draws from is re-run on demand through
       ``filter_state["latent_grid_rerun"]`` and dropped again, so peak memory
       is one forward history however diffuse the posterior turns out to be. A
       node's run is a pure function of ``(node, seed)``, so each re-run
       reproduces pass 1 bit for bit.

    Positional summaries are the posterior mixture over nodes, not the MAP
    node: ``mean = Σ p_j m_j`` and ``cov = Σ p_j (C_j + d_j d_jᵀ)`` with
    ``d_j = m_j − mean``, which is the exact mixture covariance and so includes
    the between-node spread that the 4-state path had no way to express.
    ``current_uv_at_step`` is likewise mixed, and the smoother integrates that
    one field per interval; the nodes' current fields differ only through
    particle position, so this is the same cloud-mean approximation the
    single-node path already makes, taken one level up.

    The §3.7 degeneracy gate evaluates **per node**, and the record exported as
    ``filter_state["degeneracy"]`` is the *worst* node's — a node that
    degenerates still contributes its collapsed lineage to the mixture. Every
    node's own record is in ``latent_grid["degeneracy_per_node"]``.
    """
    ...

def _read_depth_extent(depth_path: Path):
    ...

def render_animation(track, state, polys_raster, release, args, polygon=None):
    ...

def main() -> None:
    ...
