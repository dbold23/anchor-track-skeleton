"""End-to-end pipeline orchestrator for an anchor deployment.

Single CLI: pick a deployment + release point, get back a self-contained
HTML report bundling every stage's figures, the particle animation (MP4),
and an interactive Folium track map (iframe).

Stages
------
1. Ingest audit            — sample count, coverage, depth distribution
2. Mag calibration cloud   — raw 50 Hz mag → hard/soft-iron fit → before/after
3. Heading + speed series  — derived inputs to the filter
4. Behavior states         — anchor HMM segmentation overlay (if available)
5. Particle filter run     — release + polygon + bathymetry, with snapshots
6. Static track map        — 4-panel summary PNG (reuses elkhorn_demo)
7. Track animation         — MP4 of the chains-dying SMC
8. Folium map              — interactive HTML, embedded as iframe
9. Filter diagnostics      — drift, 2σ growth, particles-in-polygon, ancestry

All stages run in one process. The report HTML is self-contained except for
the Folium map (sibling file).
"""
from __future__ import annotations
import argparse
import json
import time
from html import escape
from pathlib import Path
from typing import get_args
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yaml
from pydantic import ValidationError
from anchor.ingest.config import load_config
from anchor.ingest.io import interim_cache_is_valid, load_deployment, read_parquet
from anchor.trajectory.animate_filter import render_animation, resolve_n_steps, run_filter_with_snapshots
from anchor.trajectory.axy_ingest import align_behavior_states, behavior_to_process_noise, ingest_deployment
from anchor.trajectory.bathymetry import BathyLookup
from anchor.trajectory.elkhorn_demo import build_tide_and_current, load_tide_aware_polygon, make_html_map, make_static_figure
from anchor.trajectory.detachment import DetachmentResult, LeewayParams, PostDetachRegime, detect_detachment, detect_post_detach_regimes, estimate_detachment_position
from anchor.trajectory.end_anchor import DEFAULT_BOTTOM_CREEP_SIGMA_M, EndAnchor, grounded_end_anchor, resolve_end_anchor_model
from anchor.trajectory.particle_filter import SBIAS, SSCALE, apply_end_anchor_to_latent_grid, end_anchor_binding_check, end_anchor_log_evidence, ffbs_smoother, ffbs_smoother_over_grid, integrate_snapshot_intervals, integrate_snapshot_noise, smoother_cube_diagnostics
from anchor.trajectory.imu import apply_calibration, fit_hard_soft_iron
from anchor.trajectory.polygon_constraint import PolygonConstraint
from anchor.trajectory.release_anchor import ReleaseAnchor
from anchor.trajectory.verified_positions import VerifiedPositionSet
from anchor.trajectory import vpc_validation
from anchor import export as EX
from anchor.viz import marks as VM
from anchor.viz import theme as VT
from anchor.trajectory.report import Section, build_html, degeneracy_banner, gate_banner, fig_to_png_b64, latent_grid_table, latent_grid_unscored_bias, qc_section, end_anchor_block, regime_table, score_card_panel, suppressed
from anchor.validation.ledger import GateCheck, GateResult, Provenance, ScoreCard, evaluate_gates, evaluate_heading_gate, to_channel
from anchor.validation.ledger import jsonable as _ledger_jsonable
from anchor.trajectory.wind import get_wind_series
from anchor.trajectory.sites.elkhorn import ELKHORN_BATHY_SIGMA_TIF, ELKHORN_BATHY_TIF, ELKHORN_CENTERLINE_GEOJSON, ELKHORN_DECLINATION_DEG_2026, ELKHORN_NOAA_WL_STATION, ELKHORN_OUTLINE_GEOJSON, ELKHORN_TIDAL_PRISM_K_M

@VT.styled
def stage_ingest_audit(track) -> Section:
    ...

@VT.styled
def stage_mag_calibration(cfg) -> tuple[Section, np.ndarray, np.ndarray]:
    """Fit hard/soft-iron on the raw 50 Hz mag and render before/after cloud.

    Returns the section plus (b_offset, A_inv) so caller can verify the recovery.
    """
    ...

@VT.styled
def stage_heading_speed_timeseries(track, states: np.ndarray | None) -> Section:
    ...

@VT.styled
def stage_tide_overlay(track, tide_series, current_field, filter_state: dict, args) -> Section | None:
    """Render water level + tide-derived current overlaid on observed depth.

    Three panels stacked:

      1. Tide height (m above MLLW) over the deployment window. The
         deployment span is highlighted; ticks are shifted to UTC so
         marine readers can compare with NOAA's published harmonics.
      2. Particles-inside-polygon (bottom y-axis) vs wet-area km²
         (top y-axis from the tide-aware mask stack). When the polygon
         shrinks the inside count should drop in lockstep — that's the
         visual proof the constraint is doing what it says.
      3. Along-channel current speed (m/s). Sign convention: + = flood,
         − = ebb. Marks 0 m/s axis prominently so readers can spot
         slack-water transitions.

    Returns None if no tide_series is available (filter ran tide-blind).
    """
    ...

@VT.styled
def stage_behavior_distribution(track, states: np.ndarray | None) -> Section | None:
    ...

@VT.styled
def stage_filter_diagnostics(filter_state: dict, args, *, card: dict | None=None) -> Section:
    """Section 8, and the one place the run's verdict is rendered.

    ``card`` is an :class:`~anchor.validation.ledger.ScoreCard`'s ``to_dict()``
    — the same payload written to ``<id>_ledger.json`` — rendered directly
    beneath the gate banner, which is where §3.7's verdict, its floors, its
    provenance and the along/cross decomposition all belong. There is still
    exactly **one** banner in the report: the card panel deliberately does not
    restate the verdict, it evidences it.
    """
    ...

@VT.styled
def stage_bidirectional_panel(forward_state: dict, backward_state: dict | None, smoothed_state: dict | None, release, end_anchor, args, end_anchor_label: str='end anchor', card: dict | None=None) -> Section | None:
    """Forward vs FFBS-smoothed comparison panel.

    Three sub-panels:
        1. Map: forward mean (red), smoothed (green), release + recovery anchors.
        2. Posterior k_speed (1D trace ± σ band) for forward vs smoothed.
        3. Posterior ψ_bias (1D trace ± σ band) for forward vs smoothed.

    ``end_anchor_label`` names what ``end_anchor`` actually is on this run —
    the back-propagated *detachment* anchor once a detachment is detected, the
    *recovery* anchor otherwise. The endpoint distance quoted below is to
    ``end_anchor``, so the label has to follow it rather than say "recovery"
    unconditionally.
    """
    ...

def stage_static_track_panel(track, filter_state, release, deployment_id, bathy_constrained, states: np.ndarray | None, species_label: str) -> Section:
    """Re-render the 4-panel static track figure into the report inline."""
    ...

@VT.styled
def stage_detachment_panel(track, detach_result, post_regimes, recovery_anchor, end_anchor, end_anchor_meta: dict | None=None) -> Section | None:
    """3-panel detachment + post-detach regimes + back-prop drift figure.

    Panel 1 — depth + detachment marker + regime bands. Reads at-a-glance
        as "fish swimming → tag pops → bobbing/calm/bobbing → recovery."
    Panel 2 — tailbeat-freq + roll variance with the same time axis,
        overlaid with the regime band colors. Lets readers verify the
        VEDBA segmentation matches the physical signal.
    Panel 3 — UTM map: recovery anchor (X) + dashed line to back-prop
        detach anchor (★) + 1σ circle. Visualizes how the wind+tide+
        regime backward propagation walked the cloud from the recovery
        point to the inferred detachment point.
    """
    ...

def _wet_threshold_label(args) -> str:
    """The header table's wet-mask row: the threshold in force, and whose it is.

    ``(bed(MLLW) + η) > threshold`` is the wet predicate, and the whole water
    constraint stands on the threshold; a report that names the polygon's
    penalty, its mode and its tide levels but not the depth at which a cell
    stops being water is describing the constraint with its scale left out. The
    baked value is quoted alongside an override so a reader can see how far the
    run moved it. ``args`` is stamped by :func:`_apply_wet_threshold`; a caller
    that never ran it — every test that builds a bare namespace — gets the
    em dash.
    """
    ...

def _header_param_table(*, deployment_id: str, species_label: str, body_length_source: str, args, filter_state: dict, release, enable_bathy: bool, tide_source_label: str, current_label: str, wind_series, b_offset, card: dict | None=None) -> list[tuple[str, str]]:
    """The (label, value) rows of the report header table.

    Header values are interpolated into ``<td>`` as raw HTML, so any credible
    interval quoted here has to carry the same ``suppressed()`` mark the
    section bodies use — the header sits *above* the G-degeneracy banner, and
    the banner tells the reader every interval in the report is marked.
    """
    ...

def _intervals_suppressed(state: dict | None) -> bool:
    """Whether the §3.7 G-degeneracy gate suppressed this run's intervals.

    Every credible interval the report quotes — in a section body or in the
    header parameter table — must be marked through :func:`report.suppressed`
    when this is true, because the banner promises the reader that all of
    them are.
    """
    ...

def _card_suppresses(card: dict | None) -> bool:
    """Whether the run's score card carries a failed suppressing gate.

    The card is the authority once it exists, because it is scored against the
    whole of section 3.7 and not only against G-degeneracy. Since the
    2026-09-05 amendment that is a live distinction: **G-heading** can fail on
    a run whose particle cloud is perfectly healthy, and its row withdraws
    every positional number just as G-degeneracy's withdraws every calibration
    number.
    """
    ...

def _scored_heading_gate(qc_findings) -> GateResult:
    """G-heading for this run, or a **failing** gate when it cannot be scored.

    :func:`anchor.validation.ledger.gates.evaluate_heading_gate` returns
    ``None`` when the findings carry no ``heading.*`` check at all, and that is
    the right answer for a pure ledger function: a gate scored from an input
    that does not exist would be a verdict about the report's age rather than
    about the deployment. The *policy* is the driver's, and design §3.7's
    amendment states it: G-heading governs published positions, and a run that
    cannot demonstrate its heading is a measurement of azimuth may not publish
    one, whatever the reason. Treating "not scored" as "no gate" published
    every metre of a run whose doctor was unavailable, whose cached
    ``<id>_qc.json`` predated the amendment, or whose doctor raised — the exact
    opposite of the rule. So it fails closed, and the failure names why.
    """
    ...

def _gate_from_card(card: dict | None, name: str) -> dict | None:
    """One gate's dict out of a card's ``gates`` list, or ``None``."""
    ...

def _load_centerline(current_field):
    """The channel centreline the ledger decomposes against, or ``None``.

    Prefers the one the current field was built on, so the ledger's along/cross
    frame is the same frame the advection was applied in. Falls back to the
    site GeoJSON when the current source is off, and to ``None`` when neither
    is available — a deployment at a site with no centreline gets a card with
    no along/cross block rather than a fabricated one.
    """
    ...

def _median_or_nan(a: np.ndarray) -> float:
    """Median ignoring NaN; ``nan`` for an all-NaN or empty input, no warning.

    ``np.nanmedian`` warns on an all-NaN slice and this project promotes
    warnings to errors.
    """
    ...

def _channel_diagnostics(centerline, means_xy: np.ndarray, *, stds_xy: np.ndarray | None=None, ensemble_xy: np.ndarray | None=None) -> dict:
    """Decompose the reconstruction into channel coordinates (design §2.4).

    The posterior in a tidal slough is anisotropic on two independent routes,
    and a single scalar σ hides the only structure a reader cares about: the
    along-channel width is what ``k_speed`` and the current field control and
    is weakly identified, while the cross-channel width is pinned by the
    polygon and the bathymetry. This reports the two separately.

    ``ensemble_xy`` is ``(m, n, 2)`` FFBS path samples when the smoother ran;
    the widths are then the ensemble's own spread. Without it the marginal
    per-axis σ is rotated into the local channel frame instead, which is the
    same decomposition of a diagonal covariance.

    ``fraction_at_centerline_end`` is the honesty check: ``project`` clamps to
    the polyline, so any non-zero value means the centreline does not span the
    track and the along-channel figures are measuring the clamp.

    ``n_members`` is present only on the ensemble branch. A forward-only run
    has no ensemble to count, and a card renders a null number as "not
    finite" — so an absent count is reported by an absent key, never by a
    ``nan`` that would claim the count was measured and came back non-finite.
    """
    ...

def _card_config_dump(config, traj):
    """The configuration ``provenance.config_hash`` should fingerprint.

    ``config`` is the deployment YAML as loaded; ``traj`` is the
    ``TrajectoryConfig`` the run actually used, which is the YAML's block with
    every ``--n-particles``/``--speed-min``/``--latent-mode`` style override
    applied (:func:`_effective_traj`). Hashing ``config`` alone fingerprints
    the *file*, so two runs that differ only in a CLI override card
    identically and an auditor reading the cards cannot tell them apart —
    ``docs/regen_2026-09.md`` §12 was run as ``--latent-mode grid`` against a
    deployment whose YAML says ``particle`` and carded the plain YAML's hash.

    Substituting the effective block fixes that and changes nothing else: with
    no override in force ``traj`` round-trips to the same JSON the YAML dump
    already carries, so every card written before this is reproduced exactly.
    A non-model ``config`` (the ``str(cfg)`` fallback) and a missing ``traj``
    pass straight through.

    The YAML's own hash is not discarded: :func:`_build_score_card` stamps it
    as ``provenance.source_config_hash``. The effective hash identifies the run
    but not the deployment file it belongs to, and ``docs/regen_2026-09.md``
    §11's speed_min sweep is five runs of one file.
    """
    ...

def _build_score_card(*, run_id: str, degeneracy: dict | None, channel: dict | None, binding: dict | None, config, timestamp: str, detachment: dict | None=None, end_anchor: dict | None=None, n_steps: int, traj=None, heading_gate=None, smoother_diagnostics: dict | None=None, **stamp_extra) -> ScoreCard:
    """The ledger's record of one deployment run (design §1, §3.5 row 12).

    The G-degeneracy gate is re-scored from the filter's own diagnostics
    through :func:`anchor.validation.ledger.evaluate_degeneracy_gate`, rather
    than trusting the driver's copy of the verdict: the filter and the ledger
    then agree on nothing but the names of the five scalars, which is the
    point of exporting them.

    ``detachment`` is :meth:`DetachmentResult.to_dict`: which rule cut the
    track, both candidate moments, and the regime table. It is a diagnostic
    and not a gate — no floor is scored from it — but a card that reports
    ``n_steps`` without saying what the steps end at is reporting half a
    number (§17.4).

    ``end_anchor`` is :func:`_end_anchor_metadata`: which end-anchor model the
    run used, why ``auto`` chose it, and the anchor's position, σ and step. It
    is a diagnostic on the same terms — a card that reports an endpoint without
    saying what boundary condition produced it is reporting half a number in
    the other direction.

    ``smoother_diagnostics`` is
    :func:`~anchor.trajectory.particle_filter.smoother_cube_diagnostics`: how
    many distinct ancestries and latent pairs the FFBS cube carries, and — when
    the run asked for it — the backward sweep's own effective sample size. It
    is a **diagnostic**, on the same terms as ``detachment`` and ``end_anchor``:
    ``GATE_TABLE`` is untouched, no floor is scored from it, and the ``§3.7``
    numbers stay pre-registered. It is carried because ``n_founders_final``
    measures the *forward* filter's stored paths and every positional number
    the report prints comes from this cube instead
    (``docs/regen_2026-09.md`` §19.6.3, option 3).

    ``traj`` is the effective :class:`TrajectoryConfig`; see
    :func:`_card_config_dump` for why the provenance hash is taken over it
    rather than over the YAML alone. The YAML's hash rides along as
    ``provenance.source_config_hash``, so a reader can tell "same file,
    different flag" from "different deployment" — which neither hash settles
    on its own.
    """
    ...

def _end_anchor_metadata(choice, end_anchor, recovery_anchor, detach_result, *, creep_sigma_m: float | None, label: str) -> dict:
    """What the run says about its end anchor, once, for every consumer.

    The parquet footer, the ledger card's ``diagnostics.end_anchor`` and the
    report's end-anchor section all read this dict, so a reader comparing a
    card against a report is comparing one set of numbers rather than three
    formatters' opinions of them. ``choice`` is
    :class:`~anchor.trajectory.end_anchor.EndAnchorChoice` or None on the path
    where no detachment was found and the recovery point is used unmodelled.

    ``step`` is where the anchor is applied — the end of the attached span,
    which under ``detach_rule="stationary"`` is the stationary onset and not
    the water exit. Reporting σ without it reports half a number: a 27 m σ at
    9.333 h and a 27 m σ at 16.942 h are different claims about the animal.
    """
    ...

def _print_regime_table(detach_result, base_hz: float) -> None:
    """Console form of the record's regime table (§17.4.2's three records).

    Printed whether or not the stationary rule fired, and before the line that
    says where the track was cut: which span the truncation lands in is the
    fact a reader of a run log needs, and on ``BR_260318_S3`` the shipped
    answer was "the water exit, 7.617 h after the animal record ended".
    """
    ...

def _print_polygon_rejections(filter_state: dict | None) -> None:
    """Console line for steps at which the whole cloud was out of the water.

    Under the old hard constraint this fact arrived as a weight collapse and
    as a breached ``ess_min`` floor. The finite ``polygon_penalty_nats`` leaves
    the relative weights alone, so neither fires any more and the disclosure
    would otherwise vanish from the run's surface — which is the failure mode
    ``docs/regen_2026-09.md`` §12.4 is about, in reverse.
    """
    ...

def _print_degeneracy(degeneracy: dict | None) -> None:
    """Console verdict for the standing G-degeneracy gate (design §3.7)."""
    ...

def _print_latent_grid(grid: dict | None, *, stage: str='') -> None:
    """Console summary of the outer latent grid (design §3.5).

    The two axis marginals are the point of the mode: in particle mode the
    same two numbers are a moment of a cloud that ancestral degeneracy has
    already collapsed, and on the flagship run ``k_speed`` reduced to a single
    atom with sd exactly 0. Here they are a posterior over grid nodes, which
    resampling never touches.

    Printed twice on a run with an end anchor, ``stage`` naming which weights
    are on show: the filter can only produce ``p(node | forward observations)``,
    and the anchor is folded in later (see
    :func:`~anchor.trajectory.particle_filter.apply_end_anchor_to_latent_grid`).
    The two are different distributions and the second is the one to read, so
    neither is printed unlabelled.
    """
    ...

def _prepare_latent_grid_for_smoothing(filter_state: dict, end_anchor, *, n_smooth: int, seed: int):
    """Make the grid's node weights condition on the end anchor, then hand the
    smoother one forward history at a time.

    Two things have to be true for the FFBS ensemble to be a sample from the
    latent mixture, and neither is true of what the filter returns.

    1. **The node weights must condition on the end anchor.** Every path drawn
       inside a node is conditioned on it; the forward filter never saw it (it
       is back-propagated from the recovery position at stage 6b, *after* the
       filter at stage 6). Pairing weights ``p(node | y)`` with paths from
       ``p(x | y, anchor, node)`` is not a sample from anything. So score
       :func:`~anchor.trajectory.particle_filter.end_anchor_log_evidence` on
       each node's terminal cloud and fold it in. If that moves the MAP node,
       the forward history ``filter_state`` carries — the one the report, the
       animation and the binding check read — is re-run for the new MAP.
    2. **The drawn nodes' histories must not all be held at once.** One is
       ``T_snap × N × 4`` float64 (1.3 GB on the flagship), and the diffuse
       posterior this mode exists to produce can draw from every node on the
       grid, which is the tens of gigabytes the mode's *success* case would
       otherwise need. Each node is re-run as the smoother reaches it and
       dropped again: peak memory is one history — the MAP node's, which the
       report holds regardless — and the cost is one filter pass per other
       drawn node.

    Returns ``(drawn_nodes, node_runs)``, the second a generator suitable for
    :func:`~anchor.trajectory.particle_filter.ffbs_smoother_over_grid`.
    """
    ...

def _degeneracy_metadata(degeneracy: dict | None) -> dict:
    """JSON-safe view of the degeneracy record (see
    :data:`_DEGENERACY_METADATA_DROP` for what it leaves out)."""
    ...

def _print_smoother_diagnostics(cube: dict | None) -> None:
    """One console line for the smoothed cube's degeneracy (§19.6.3 option 3).

    Printed beside the G-degeneracy banner and never inside it: the founder
    count is the *forward* filter's and this is the cube's, and the report
    would be lying if it let one stand for the other.
    """
    ...

def _latent_grid_metadata(grid: dict | None) -> dict:
    """JSON-safe view of the outer latent grid, minus the per-step arrays.

    Everything a reader needs to reproduce or audit the latent posterior — the
    two axes, every node's log prior, log marginal and posterior weight, the
    axis marginals, the FFBS draw counts and each node's §3.7 verdict — and
    nothing that scales with the record length. ``degeneracy_per_node`` goes
    through :func:`_degeneracy_metadata` for exactly that reason: the raw
    records carry five arrays per node, which on the flagship is 25 × 5 × 61 000
    numbers.
    """
    ...

def _polygon_metadata(filter_state: dict | None) -> dict:
    """How the water constraint entered this run, and what it cost.

    ``polygon_mode`` and the proposal's per-step accounting reach
    ``filter_state`` but nothing else, so a completed
    ``anchor track --polygon-mode soft`` run used to be indistinguishable in
    its own artefacts from a shipped-indicator run except through a 16-hex
    ``config_hash``. This is the exported view: the mode, the two knobs, and
    the proposal's totals. The three ``*_at_step`` arrays are dropped the way
    ``_degeneracy_metadata`` drops ``per_step``.
    """
    ...

def _latent_grid_summary(grid: dict | None) -> dict:
    """The short form of :func:`_latent_grid_metadata`, for the parquet footer.

    A track parquet handed to ``anchor export`` carries no report; when the
    reconstruction is a latent mixture, "which latents?" is part of what the
    coordinates mean.
    """
    ...

def _write_track_parquet(track_df, path: Path, metadata: dict) -> None:
    """Write the tidy track parquet with ``metadata`` in the schema footer.

    The σ columns in this file are only as good as the gate verdict travelling
    with them, and a parquet handed to ``anchor export`` / ``anchor spaceuse``
    carries no report. Keys are namespaced ``anchor:*`` and the pandas
    metadata pyarrow writes is left untouched.

    Values go through the ledger's own coercion, which maps a non-finite float
    to ``null`` — ``var_log_w`` peaks at ``inf`` on a collapsed run, and
    Python's lenient ``json`` would otherwise write a bare ``Infinity`` that
    ``JSON.parse``, ``serde_json`` and ``encoding/json`` all reject.
    ``allow_nan=False`` makes anything that escapes the coercion raise here
    rather than reach the file.
    """
    ...

def _qc_findings(cfg, config_path):
    """Data-health findings for the report's QC section, or None.

    Prefers the JSON ``anchor doctor`` / ``anchor run-all`` already wrote
    (``data/interim/<id>_qc.json``), which costs a file read — but only when
    that file's freshness stamp says it was computed from *this* config and
    *this* raw CSV (:func:`anchor.qc.stamp_is_current`). Otherwise it runs
    :func:`anchor.qc.run_doctor` over the deployment YAML, which re-probes the
    raw CSV (a fraction of a second on most records, ~30 s on the largest).
    Findings are returned as plain dicts or ``Finding`` objects
    interchangeably — :func:`~anchor.trajectory.report.qc_section` is
    duck-typed on ``.check`` / ``.level`` / ``.message``.

    The stamp check is the whole point of this function's cache: the report
    leads with the health verdict, and a superseded verdict is worse than none
    at all. ``docs/regen_2026-09.md`` §10 is the case — the deployment's
    ``length_cm`` was promoted to a measured value, every number in the report
    was computed from it, and §0 still carried the ``config.animal_length``
    FAIL from a JSON written before the edit. Whichever branch runs is printed
    with its reason, so the artefact's provenance is readable off the console.

    Deliberately non-fatal: a reconstruction is not worth abandoning because
    its health report could not be built, so every failure is reported on
    stdout and returns None (the report is then assembled without the
    section). A stale cache is *not* a fallback for a doctor that will not
    run — no section beats a wrong one.
    """
    ...

def _with_qc_section(sections, cfg, config_path, findings=None):
    """Prepend the ``anchor doctor`` data-health section to *sections*.

    The reconstruction figures below it say nothing about whether the record
    behind them is sound, so the report leads with the health verdict. A
    deployment whose findings cannot be produced simply gets no section:
    :func:`_qc_findings` reports the reason and returns None.

    ``findings`` lets the caller pass a report it has already built. The
    driver does, because the standing G-heading gate is scored from the same
    findings before the track parquet is written, and running the doctor twice
    on one reconstruction would be a second probe of the raw CSV for no gain.
    """
    ...

class _SiteDefaultDeclination(float):
    """The site's declination, carried as a float that can be recognised.

    ``--declination-deg`` cannot default to None: ``args.declination_deg`` is
    read as a number by ``ingest_deployment`` and by every caller that drives
    this module's argparser (``scripts/diagnose_polygon_exits.build_bundle``
    among them). It also cannot default to a plain float, because
    :func:`_effective_traj` would then be unable to tell "the operator asked
    for 12.7°" from "nobody said anything and the site constant applied" — and
    that is exactly the distinction ``docs/regen_2026-09.md`` §18.6.1 needs,
    where two runs 5.35 million nats apart shared ``config_hash``
    ``c22bdee634b63476``.

    A float subclass is both: arithmetic, formatting and ``float()`` behave
    identically, and ``isinstance`` answers the provenance question.
    """
    __slots__ = ()

def _polygon_penalty_arg(text: str):
    """Parse ``--polygon-penalty-nats``: a number of nats, or ``none``/``hard``.

    Which numbers are legal is ``TrajectoryConfig.polygon_penalty_nats``'s
    business — its validator demands a positive, finite value — so this only
    turns the text into a float and leaves the rule where it lives; a zero,
    negative or infinite number exits through :func:`_traj_with` carrying that
    validator's own message and the flag's name.
    """
    ...

def _latent_axis_arg(text: str):
    """Parse a ``--latent-grid-*`` flag: a value list, or ``n:min:max``.

    ``"0.8,1.0,1.2"`` is the explicit list; ``"5:0.6:1.4"`` is the five-point
    regular axis from 0.6 to 1.4 inclusive, the same shape the YAML writes as
    ``{n: 5, min: 0.6, max: 1.4}``. Both go through ``TrajectoryConfig``'s
    validation, so a malformed axis exits naming the flag rather than
    producing a grid nobody asked for.
    """
    ...

def _traj_with(base_traj, updates, labels, *, prefix):
    """``base_traj`` with ``updates`` applied, re-validated against its schema.

    The single place a ``TrajectoryConfig`` is altered from the command line —
    by an override flag or by a ``--sensitivity`` grid point. Rebuilding the
    model rather than assigning onto a ``model_copy()`` is what makes the
    declared bounds apply: ``TrajectoryConfig`` does not set
    ``validate_assignment``, so pydantic checks nothing on ``setattr`` and a
    field like ``bathymetry_off_bottom_factor`` (``gt=0, le=1``) would accept
    from the CLI a value the same YAML rejects. Any bound added to the schema
    later is enforced on both CLI paths automatically.

    ``updates`` maps field name -> new value and ``labels`` maps the same field
    names to what the operator actually typed, so the error can name it.
    A validation error on a field this call did *not* touch means the config
    itself is at fault; it propagates verbatim rather than being misattributed
    to a flag.
    """
    ...

def _effective_traj(cfg, args):
    """The deployment's TrajectoryConfig with any CLI hyperparameter overrides.

    Every hyperparameter flag — ``--n-particles`` and ``--bathy-extra-sigma-m``
    included — defaults to None and overrides the YAML only when set, so a
    deployment's ``trajectory:`` block is authoritative unless the operator
    says otherwise on the command line. Out-of-range flags exit with the
    offending flag named (see :func:`_traj_with`), not with a silently
    meaningless likelihood.

    Three flags are not plain value overrides. ``--no-bathymetry`` is a
    ``store_true``, so "absent" reads as False rather than as None: it clears
    ``enable_bathymetry_constraint`` when given and stays out of the way when
    not, which leaves a YAML block that sets the field False free to disable
    the depth likelihood on its own. ``--polygon-penalty-nats none`` overrides
    *with* None — the hard ``-inf`` polygon — and arrives as
    :data:`_HARD_POLYGON` because None is already the absent flag.
    ``--bathymetry-tide-term`` takes the words ``on``/``off`` and is
    translated to the field's bool for the same reason: its None is
    already spent on "no instruction".
    ``--declination-deg`` defaults to the *site's* declination rather than to
    None, so its "absent" value is a number; it is recognised by type
    (:class:`_SiteDefaultDeclination`) and only an operator-supplied value
    reaches the effective block, which is what keeps the site default out of
    the hash.
    """
    ...

def _apply_wet_threshold(polygon, traj, args):
    """The water constraint the run will use, and the threshold it stands on.

    The tidal stack bakes its wet predicate — ``(bed(MLLW) + η) > threshold`` —
    at build time, and the baked number reaches nothing that a reader of a
    finished run can see. Two things happen here. The baked threshold is read
    off the loaded stack and printed, so the console says what the water was
    taken to be; and, when ``trajectory.wet_threshold_m`` (or
    ``--wet-threshold-m``) names a different one, the stack is rebuilt in
    memory at that threshold before the filter sees it
    (:meth:`~anchor.trajectory.polygon_constraint.TidalPolygonConstraint.with_threshold`).

    The threshold in force, the baked one and where the one in force came from
    are stamped on ``args`` — the way ``release_x`` and ``n_particles`` already
    are — because the report's header table and the card's provenance both need
    them and neither is handed the polygon. ``null`` is dropped from the
    effective-config dump, so a run that names no threshold cards the hash it
    always did and the stamp is the only thing distinguishing it from one that
    named 0.05 explicitly.

    A run whose water constraint is the *static* MLLW outline — ``--tide-source
    none`` — has no wet-mask stack and no threshold to move; naming one there
    is a CLI misuse and exits saying so, rather than being silently ignored.

    The rebuild reads the pair the *loaded* stack was baked from, which
    :func:`~anchor.trajectory.elkhorn_demo.load_tide_aware_polygon` records on
    the object as ``source_raster_path`` / ``source_outline_path`` — not
    ``--depth`` / ``--polygon``, which agree with it only because they are the
    argparse defaults. A run passing ``--depth`` with a same-shaped raster
    would otherwise rebuild against a source the stack was never baked from,
    and
    :meth:`~anchor.trajectory.polygon_constraint.TidalPolygonConstraint.with_threshold`'s
    shape check cannot see that. A constraint carrying no such record — the
    static outline, or a stack a test built — falls back to the flags.
    """
    ...

def _effective_endpoint(cfg_endpoint, lon, lat, sigma_m, *, default_sigma_m=10.0):
    """Resolve one deployment endpoint: CLI flag wins, then the YAML block.

    ``cfg_endpoint`` is an ``EndpointConfig`` (``cfg.release`` / ``cfg.recovery``)
    or None. Each component resolves independently, so ``--release-sigma-m`` can
    widen a configured position without restating its coordinates. Returns
    ``(lon, lat, sigma_m)``, or None when neither source supplies a position —
    which for the release anchor is a hard error and for the recovery anchor
    simply means "no bidirectional smoothing".
    """
    ...

def _effective_body_length_m(cfg, arg_value):
    """Body length: ``--body-length-m`` > ``animal.length_cm`` > species default.

    Mirrors ``anchor.pipeline._resolve_body_length_m`` so the reconstructed
    speed scale U = K·L·TBF uses the same L the rest of the pipeline does; the
    trailing 0.9 m only fires for a config that declares neither.

    Returns ``(length_m, source)``. The source label is carried into the report
    rather than re-derived from the config: L scales every reconstructed metre,
    so an operator-supplied ``--body-length-m`` must not be reported under the
    config's ``animal.length_cm_source`` provenance, which describes a number
    that did not run.
    """
    ...

def _warn_stale_states(args) -> None:
    """Warn when the behaviour-state parquet predates the configs behind it.

    ``INGEST_FINGERPRINT_FIELDS`` covers the deployment identity, the raw CSV,
    the rate, the calibration, the clip, the window, the timezone and the tag —
    and **not** the species ``tailbeat`` block, which sets the peak picker the
    speed channel is built from. A states file therefore stays "valid" across a
    prominence change that moves every speed in the record, which is exactly
    what happened on 2026-09-06 (§19.4.5). Nothing here can verify the file; it
    can only compare modification times and say what it sees.
    """
    ...

def _effective_states_parquet(cfg, arg_value):
    """Behaviour-state parquet: ``--states-parquet`` > the config's own id.

    Keyed off ``cfg.deployment_id`` and never off ``--deployment``: the latter
    is an *output*-file stem, so renaming a second run's outputs must not
    silently repoint this *input* at a file that does not exist and drop the
    behaviour-state-conditioned process noise.
    """
    ...

def _sweep_value_cast(base_traj, param):
    """The type a ``--sensitivity`` grid value is cast to before validation.

    ``type(getattr(base_traj, param))`` is the obvious answer and is wrong for
    an ``Optional`` field whose *current* value is ``None``: ``type(None)`` is
    ``NoneType`` and ``NoneType(400.0)`` raises a bare ``TypeError``, which is
    not how this module reports a sweep it cannot build — the grid is meant to
    fail through :func:`_traj_with` carrying the field validator's own
    sentence. ``polygon_penalty_nats`` reaches that state whenever the
    effective config carries the hard (``-inf``) polygon, from a YAML or from
    ``--polygon-penalty-nats none``. Fall back to the declared annotation's
    first concrete member there, and keep the value's own type otherwise, so a
    ``Literal`` field (``bathymetry_mode``) still casts through ``str``.
    """
    ...

def _run_sensitivity(spec, base_traj, track, bathy, polygon, release, noise_per_step, enable_bathy, tide_series, current_field, verified_positions, args, n_steps):
    """Sweep one trajectory hyperparameter and print a sensitivity table."""
    ...

def _argparser(prog: str | None=None) -> argparse.ArgumentParser:
    ...

def main(argv: list[str] | None=None, prog: str | None=None) -> None:
    ...
