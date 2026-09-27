"""typer-based CLI: ``anchor <command>``."""
from __future__ import annotations
from pathlib import Path
from typing import Optional
import typer
from anchor.ingest import calibrate as CAL
from anchor.ingest import io
from anchor import pipeline
from anchor import plot as P
from anchor import qc as QC
from anchor.ingest.config import load_config

@calibrate_app.callback(invoke_without_command=True)
def calibrate(ctx: typer.Context, spins: Optional[Path]=typer.Option(None, help='Dir containing calibration spin CSVs'), out: Path=typer.Option(Path('data/interim/calib'), help='Where to save the JSON calibration'), schema: str=typer.Option('axy5', help='Source schema for the spin CSVs')):
    """Fit accel (and, if present, mag) ellipsoid calibration from spin CSVs.

    Behaviour of ``anchor calibrate --spins <dir>`` is unchanged; the options
    moved onto a group callback only so that ``anchor calibrate mag`` can exist
    beside them.
    """
    ...

@calibrate_app.command('mag')
def calibrate_mag(config: Path=typer.Option(..., help='Deployment YAML'), out: Optional[Path]=typer.Option(None, '--out', help='Where to write the calibration JSON (default: data/interim/calib/<id>/mag_inflight.json)'), in_flight: bool=typer.Option(False, '--in-flight', help="Fit the magnetometer on the animal's own record (the only mode)."), dip_deg: Optional[float]=typer.Option(None, '--dip-deg', help="Magnetic inclination at the site, positive downward. Overrides the per-site constant selected by the config's `site:` field.")):
    """In-flight magnetometer fit, validated by the dip-angle test.

    Fits the ellipsoid to the magnetometer samples taken *on the animal* (which
    cover the sphere, because the animal rolls), searches the 48 signed axis
    permutations for the one whose field-to-gravity angle matches the site's
    magnetic inclination, folds that mapping into ``A`` and writes the result
    in the on-disk calibration format with a ``validation`` block.

    The written file is a candidate, not a promotion: pointing a deployment's
    ``calibration.mag`` at it is a separate, deliberate edit.
    """
    ...

@app.command()
def doctor(config: Path=typer.Option(..., help='Deployment YAML'), json_out: Optional[Path]=typer.Option(None, '--json', '--out', help='Where to write the QC JSON (default: data/interim/<id>_qc.json)'), probe_rows: int=typer.Option(QC.DEFAULT_PROBE_ROWS, help='Rows sampled from each of the head/middle/tail of the raw CSV'), heading: bool=typer.Option(True, '--heading/--no-heading', help='Run the heading.* family (the dip-angle test). --no-heading is the cheap triage: it skips the only check that reads the record in bulk')):
    """Data-health triage for one deployment. Exits 1 on any FAIL.

    Every check but one reads only the head, middle and tail of the raw CSV
    plus a byte-level row count, so a 600 MB export is triaged in seconds and
    nothing is cached or calibrated as a side effect.

    The exception is the ``heading.*`` family (design §3.7's G-heading,
    amendment 2026-09-05), which needs the whole record: it reads six IMU
    columns out of the interim parquet when the cache is valid for this config,
    and otherwise streams up to ``QC.HEADING_MAX_CSV_ROWS`` rows of the raw
    CSV, then fits an ellipsoid to the magnetometer in memory. That costs a few
    seconds to about half a minute per deployment (regen §16.14.3), still
    writes nothing, and ``--no-heading`` drops it when the cheap triage is what
    is wanted.
    """
    ...

@app.command()
def process(config: Path=typer.Option(..., help='Deployment YAML')):
    """Raw CSV → processed parquet with VeDBA/ODBA/jerk/tailbeat."""
    ...

@app.command()
def events(config: Path=typer.Option(..., help='Deployment YAML')):
    """Extract high-activity events from a processed deployment."""
    ...

@app.command()
def features(config: Path=typer.Option(..., help='Deployment YAML')):
    """Sliding-window feature table."""
    ...

@app.command()
def classify(config: Path=typer.Option(..., help='Deployment YAML')):
    """Fit GMM + post-hoc labeling; save model + states."""
    ...

@app.command()
def evaluate(deployments: list[str]=typer.Argument(..., help='Deployment IDs with labeled feature parquets in --features-dir'), features_dir: Path=typer.Option(Path('data/features'), help='Dir of <id>.parquet feature tables'), estimator: str=typer.Option('random_forest', help='random_forest | xgboost'), label_col: str=typer.Option('label', help='Window-label column (from `anchor labels`)'), min_confidence: float=typer.Option(0.0, help='Drop windows below this label_confidence'), no_balance: bool=typer.Option(False, '--no-balance', help='Disable balanced class weighting'), out_dir: Optional[Path]=typer.Option(None, help='Write metrics.json + pooled_confusion.parquet here')):
    """Subject-level LOSO evaluation with per-class metrics.

    Pools labeled windows across DEPLOYMENTS, runs leave-one-subject-out CV
    (the split that avoids pseudo-replication), and reports per-class
    precision/recall/F1, macro-F1, balanced accuracy, and Cohen's κ — surfacing
    rare-behaviour failure that overall accuracy hides.
    """
    ...

@app.command()
def demo(out_dir: Path=typer.Option(Path('demo_out'), help='Where to write the synthetic deployment + outputs'), minutes: float=typer.Option(5.0, help='Minutes of synthetic 25 Hz data'), seed: int=typer.Option(0, help='RNG seed'), no_spaceuse: bool=typer.Option(False, '--no-spaceuse', help='Skip the energy-seascape step')):
    """Run the whole pipeline on synthetic data — no private data needed.

    Fabricates a plausible AXY-5 accelerometer record (rest/cruise/active/burst
    regimes with a tail-beat), runs ingest → kinematics → behaviour, then the
    energy-seascape analysis. A zero-setup tour of anchor end-to-end.
    """
    ...

@app.command()
def gallery(out_dir: Path=typer.Option(Path('gallery'), help='Where to write the PNGs'), minutes: float=typer.Option(40.0, help='Length of the synthetic deployment'), seed: int=typer.Option(7, help='RNG seed for the synthetic scene'), no_dark: bool=typer.Option(False, '--no-dark', help='Skip the dark-theme render')):
    """Render Anchor's figure style on a synthetic deployment.

    The signature track figure (uncertainty lens pinned at release and
    recovery, path coloured by behaviour, linked uncertainty / depth /
    ethogram strips) in light and dark, plus the ethogram and sensor
    overview. No field data needed; no number in it is a result.
    """
    ...

@app.command()
def export(track: Path=typer.Option(..., help='Track parquet with lon/lat (or x/y + --crs)'), fmt: str=typer.Option('geojson', '--format', help='geojson | movebank | netcdf'), out: Path=typer.Option(..., help='Output path'), crs: Optional[str]=typer.Option(None, help='Source CRS if track has x/y (e.g. EPSG:32610)'), t0_utc: Optional[str]=typer.Option(None, help='Deployment start UTC (ISO) — required for movebank/netcdf time'), individual_id: str=typer.Option('unknown', help='Animal/tag id for movebank/netcdf'), stride: int=typer.Option(1, help='Keep every Nth point in geojson point features')):
    """Export a reconstructed track to a standard interchange format.

    GeoJSON (QGIS/web), Movebank CSV (move2/ctmm/aniMotum), or CF-1.8 NetCDF
    (archival). Reads the tidy track parquet written by the trajectory pipeline
    (or any parquet with lon/lat or x/y columns).
    """
    ...

@app.command()
def spaceuse(samples: Path=typer.Option(..., help='FFBS trajectory samples .npy of shape (T, K, >=2) in --crs'), crs: str=typer.Option(..., help='Projected CRS of the samples (e.g. EPSG:32610)'), out_dir: Path=typer.Option(..., help='Output dir for ud.tif + isopleths.geojson'), energy_parquet: Optional[Path]=typer.Option(None, help='Parquet with a per-timestep energy proxy (len T)'), energy_col: str=typer.Option('vedba_mean', help='Energy column in --energy-parquet'), cell_size_m: float=typer.Option(10.0, help='UD raster cell size (m)'), bandwidth_m: float=typer.Option(30.0, help='KDE smoothing bandwidth (m)'), levels: str=typer.Option('0.5,0.95', help='Comma-separated isopleth levels')):
    """Uncertainty-propagated utilization distribution / energy seascape.

    Consumes the K joint FFBS trajectory samples (so the home range integrates
    over reconstruction uncertainty), optionally weighting occupancy by a
    per-timestep energy proxy (VeDBA/ODBA) to map *where the animal spent
    energy*. Writes a GeoTIFF density + GeoJSON isopleths and prints areas.
    """
    ...

@app.command()
def plot(config: Path=typer.Option(..., help='Deployment YAML'), kind: str=typer.Option('ts', help='ts | event | ethogram | calib | tailbeat'), out: Optional[Path]=typer.Option(None, help='PNG output path')):
    """Render a plot for this deployment."""
    ...

@app.command(name='run-all')
def run_all(config: Path=typer.Option(..., help='Deployment YAML'), no_doctor: bool=typer.Option(False, '--no-doctor', help='Skip the stage-zero `anchor doctor` health check')):
    """doctor → process → events → features → classify, in one shot.

    The stage-zero health check reports but never aborts: run `anchor doctor`
    on its own for a non-zero exit code on FAIL.
    """
    ...

@app.command(context_settings={'allow_extra_args': True, 'ignore_unknown_options': True, 'help_option_names': []})
def track(ctx: typer.Context):
    """Reconstruct one deployment's trajectory (particle filter + FFBS smoother).

    A thin delegate to ``python -m anchor.trajectory.run_deployment``: every
    argument is forwarded verbatim, so ``anchor track --help`` prints that
    module's own flag list. ``--config`` is the one required flag: it selects
    the deployment YAML that supplies the endpoints, site, body length and
    sway axis, and every other flag overrides that YAML rather than replacing
    it.
    """
    ...

@labels_app.command(name='import')
def labels_import(config: Path=typer.Option(..., help='Deployment YAML with video_sync + labels fields'), out: Optional[Path]=typer.Option(None, help='Output parquet (default: data/processed/{id}_labels.parquet)')):
    """Parse BORIS/VIA export → align to accel → project onto feature windows.

    Reads the label-source path and format from the deployment config's
    ``labels:`` block. Produces a parquet with one row per feature window
    and columns ``label`` + ``label_confidence``.
    """
    ...

@round_app.command(name='bootstrap')
def labels_round_bootstrap(config: Path=typer.Option(..., help='Deployment YAML'), n: int=typer.Option(50, help='Number of uncertain windows to surface'), method: str=typer.Option('entropy', help='entropy | margin | least_confident'), notes: str=typer.Option('', help='Free-text notes for the round')):
    """Run query → auto-clip in one step, registering the round in the manifest.

    Calls into ``anchor.behavior.labels.select_uncertain_windows`` and
    ``anchor.validation.auto_clip.clip_uncertain_windows`` then records
    the round at ``data/labels/rounds/{deployment_id}/round_{N:03d}/``.
    """
    ...

@round_app.command(name='complete')
def labels_round_complete(config: Path=typer.Option(..., help='Deployment YAML'), round_id: int=typer.Option(..., help='Round id to complete'), boris_export: Path=typer.Option(..., help='BORIS / VIA export to ingest')):
    """Promote a round to LABELED and ingest the BORIS export into a labels parquet."""
    ...

@round_app.command(name='status')
def labels_round_status(config: Path=typer.Option(..., help='Deployment YAML')):
    """Print the active-learning round history for a deployment."""
    ...

@labels_app.command(name='query')
def labels_query(config: Path=typer.Option(..., help='Deployment YAML'), n: int=typer.Option(200, help='Number of windows to surface for annotation'), method: str=typer.Option('entropy', help='entropy | margin | least_confident'), out: Optional[Path]=typer.Option(None, help='CSV of suggested windows')):
    """Phase B: surface the top-N most uncertain feature windows for labeling.

    Reads ``data/processed/{id}_states.parquet`` (emitted by ``anchor
    classify``) which now carries ``state_prob_*`` columns, and writes a
    CSV ranked by posterior uncertainty. The annotator opens each row's
    video segment (using ``start_t`` + deployment video offset) in BORIS
    and labels it — those labels feed back into the next classifier round.
    """
    ...

@pose_app.command(name='kinematics')
def pose_kinematics(keypoints: Path=typer.Option(..., help='DLC CSV or SLEAP H5 export'), species: str=typer.Option(..., help='leopard_shark | bat_ray | thresher_shark | white_shark'), body_length_m: float=typer.Option(..., help='Body length (m) for L scale'), fps: float=typer.Option(30.0, help='Video fps (only used for DLC CSV)'), out: Path=typer.Option(..., help='Output parquet (per-cycle TBF / amplitude / A/L)')):
    """Pose keypoints → per-tailbeat-cycle kinematic features (TBF, A/L)."""
    ...

@pose_app.command(name='overlay')
def pose_overlay_cmd(video: Path=typer.Option(..., help='Source video (MP4)'), keypoints: Path=typer.Option(..., help='DLC CSV or SLEAP H5 export'), out: Path=typer.Option(..., help='Output MP4 with keypoint + skeleton overlay'), species: Optional[str]=typer.Option(None, help='Species for default skeleton'), metrics: Optional[Path]=typer.Option(None, help='Optional pose-kinematics parquet for per-cycle metric overlay'), fps: float=typer.Option(30.0, help='Video fps (DLC CSV only)'), show_names: bool=typer.Option(False, help='Print keypoint names next to dots'), confidence_threshold: float=typer.Option(0.5, help='Below this confidence, dot turns red'), n_frames: Optional[int]=typer.Option(None, help='Render only the first N frames')):
    """Render keypoints + skeleton + per-cycle metrics on top of source video."""
    ...

@validation_app.command(name='drone')
def validation_drone(video_srt: Path=typer.Option(..., help='DJI .SRT telemetry file beside the MP4'), keypoints: Path=typer.Option(..., help='DLC/SLEAP keypoints export'), body_kp: str=typer.Option('centroid', help='Keypoint name to track in world coords'), fov_deg: float=typer.Option(84.0, help='Camera horizontal FOV (deg)'), image_w: int=typer.Option(3840, help='Image width (px)'), image_h: int=typer.Option(2160, help='Image height (px)'), out: Path=typer.Option(..., help='Output parquet (per-frame lat/lon/mpp)')):
    """Drone footage + pose → per-frame world-coord trajectory."""
    ...

@paired_tag_app.command(name='matrix')
def paired_tag_matrix(cats: Path=typer.Option(..., help='CATS-derived state parquet (with t + state column)'), axy: Path=typer.Option(..., help='AXY-derived state parquet (with t + state column)'), state_col: str=typer.Option('state', help='State column name in both parquets'), out: Path=typer.Option(..., help='Output parquet (confusion matrix; kappa in metadata)')):
    """Low-level: agreement matrix from two pre-computed state parquets.

    Assumes both parquets already share a common time grid. For
    end-to-end clock-aligning + harmonization + κ in one step, use
    ``paired-tag run``.
    """
    ...

@paired_tag_app.command(name='run')
def paired_tag_run(axy_features: Path=typer.Option(..., help='AXY feature parquet from `anchor features`'), cats_features: Path=typer.Option(..., help='CATS feature parquet from `anchor features`'), axy_model: Path=typer.Option(..., help='AXY-trained classifier (.pkl from `anchor classify`)'), cats_model: Optional[Path]=typer.Option(None, help='CATS-trained supervised classifier; omit to use AXY model on both (HMM-consistency mode)'), out_dir: Path=typer.Option(..., help='Output directory for confusion matrix + state predictions'), align_signal: str=typer.Option('vedba_mean', help='Feature column to cross-correlate'), common_align_fs: float=typer.Option(1.0, help='Common rate for clock-alignment xcorr (Hz)'), max_offset_s: float=typer.Option(600.0, help='Max plausible clock offset between tags (s)'), window_match_dt_s: float=typer.Option(2.0, help='Window-pairing time tolerance (s)')):
    """End-to-end: clock-align CATS+AXY, predict states, emit κ + confusion."""
    ...

@paired_tag_app.command(name='aggregate')
def paired_tag_aggregate(reports_dir: Path=typer.Option(..., help='Directory containing per-deployment subdirs from `paired-tag run`'), out_dir: Path=typer.Option(..., help='Where to write the species-level summary + confusion'), n_bootstrap: int=typer.Option(1000, help='Bootstrap resamples over deployments'), ci: float=typer.Option(0.95, help='Bootstrap CI level')):
    """Aggregate per-deployment paired-tag rounds into a species-level κ + CI.

    Walks ``reports_dir/*/`` for subdirectories containing ``summary.json``,
    ``axy_states.parquet``, and ``cats_states.parquet`` (the layout written
    by ``paired-tag run``). Produces a species-level confusion matrix +
    pooled κ + bootstrap-over-deployments κ with CI.
    """
    ...

@validation_app.command(name='online')
def validation_online(keypoints: Path=typer.Option(..., help='DLC/SLEAP keypoints from a published clip'), species: str=typer.Option(..., help='leopard_shark | bat_ray | thresher_shark | white_shark'), body_length_m: float=typer.Option(..., help='Body length scale (m)'), swim_speed_m_s: float=typer.Option(..., help='Known swim speed for the clip (m/s)'), fps: float=typer.Option(30.0, help='Video fps (only used for DLC CSV)'), out: Path=typer.Option(..., help='Output parquet (per-cycle K)')):
    """Published-video pose → species K calibration (no synced accel)."""
    ...

@validation_app.command(name='auto-clip')
def validation_auto_clip(query_csv: Path=typer.Option(..., help='Output of `anchor labels query`'), video: Path=typer.Option(..., help='Source video to clip from'), out_dir: Path=typer.Option(..., help='Where to drop the per-window MP4 clips'), pad_s: float=typer.Option(0.0, help='Pad each window by this many seconds')):
    """Cut every uncertain window from the source video into per-clip MP4s."""
    ...

@corpus_app.command(name='add')
def corpus_add(species: str=typer.Option(..., help='leopard_shark | bat_ray | thresher_shark | white_shark'), body_length_m: float=typer.Option(..., help='Known body length in metres (scale ref)'), url: str=typer.Option('', help='Source URL'), local_path: str=typer.Option('', help='Local path to the downloaded clip'), source_credit: str=typer.Option('', help='Cite-able credit (MBA exhibit cam, BBC, etc.)'), license: str=typer.Option('fair_use_research', help='License/usage classification'), swim_speed: Optional[float]=typer.Option(None, help='Externally known swim speed (m/s)'), swim_speed_method: str=typer.Option('pose_displacement', help='pose_displacement | fiducial | tank_current'), body_length_method: str=typer.Option('', help='How body length was determined'), notes: str=typer.Option('', help='Free-text notes')):
    """Register a new clip in the per-species corpus manifest."""
    ...

@corpus_app.command(name='list')
def corpus_list(species: str=typer.Option(..., help='Species to list')):
    """Show every clip in the per-species manifest."""
    ...

@corpus_app.command(name='remove')
def corpus_remove(species: str=typer.Option(...), clip_id: str=typer.Option(...)):
    """Drop a clip from the manifest. Local files are NOT deleted."""
    ...

@corpus_app.command(name='prep')
def corpus_prep(species: str=typer.Option(...), clip_id: str=typer.Option(...), n_frames: int=typer.Option(100, help='Frames to extract for hand-labeling'), method: str=typer.Option('uniform', help='uniform')):
    """Extract evenly-spaced frames from a clip for DLC hand-labeling."""
    ...

@corpus_app.command(name='calibrate')
def corpus_calibrate(species: str=typer.Option(...), weight_by: str=typer.Option('per_clip', help='per_clip | uniform'), out: Optional[Path]=typer.Option(None, help='Output parquet for per-cycle K table')):
    """End-to-end species K calibration from every clip with inferred keypoints."""
    ...

@drone_corpus_app.command(name='add')
def drone_corpus_add(species: str=typer.Option(..., help='leopard_shark | bat_ray | thresher_shark | white_shark'), body_length_m: float=typer.Option(..., help='Known body length in metres'), video: Path=typer.Option(..., help='Path to MP4'), srt: Path=typer.Option(..., help='Path to DJI SRT telemetry file'), fov_deg: float=typer.Option(84.0, help='Camera horizontal FOV (deg)'), image_w: int=typer.Option(3840, help='Image width (px)'), image_h: int=typer.Option(2160, help='Image height (px)'), deployment_id: str=typer.Option('', help='Linked AXY deployment id (paired mode)'), video_offset_s: Optional[float]=typer.Option(None, help='AXY clock offset (paired mode)'), site: str=typer.Option('', help='Site identifier'), flight_date: str=typer.Option('', help='Flight date YYYY-MM-DD'), pilot: str=typer.Option('', help='Pilot / operator credit'), notes: str=typer.Option('')):
    """Register a new drone overflight in the species manifest."""
    ...

@drone_corpus_app.command(name='list')
def drone_corpus_list(species: str=typer.Option(...)):
    """Show every drone clip in the per-species manifest."""
    ...

@drone_corpus_app.command(name='remove')
def drone_corpus_remove(species: str=typer.Option(...), clip_id: str=typer.Option(...)):
    """Drop a drone clip from the manifest. Local files are NOT deleted."""
    ...

@drone_corpus_app.command(name='prep')
def drone_corpus_prep(species: str=typer.Option(...), clip_id: str=typer.Option(...), n_frames: int=typer.Option(100)):
    """Extract evenly-spaced frames from a drone clip for DLC labeling."""
    ...

@drone_corpus_app.command(name='cross-validate')
def drone_corpus_cross_validate(species: str=typer.Option(...), clip_id: str=typer.Option(..., help='Drone clip id (must have video_offset_s set)'), axy_processed: Path=typer.Option(..., help='AXY processed parquet (output of `anchor process`)'), species_k: float=typer.Option(..., help='Species default Strouhal K to test against'), out: Optional[Path]=typer.Option(None, help='Output parquet for per-cycle comparison')):
    """Paired drone+AXY: drone-derived speed vs accel-derived Strouhal speed.

    Empirically validates the literature-derived K against drone-measured
    swim speed. Produces a per-cycle comparison table + bootstrap-medianed
    empirical K with CI.
    """
    ...

@drone_corpus_app.command(name='calibrate')
def drone_corpus_calibrate(species: str=typer.Option(...), weight_by: str=typer.Option('per_clip', help='per_clip | uniform'), out_dir: Optional[Path]=typer.Option(None, help='Where to save per-cycle K + trajectories')):
    """End-to-end species K + per-frame world-coord trajectory from drone footage."""
    ...

@stream_app.command(name='extract')
def stream_extract(clip: Path=typer.Option(..., help='Captured video file (MP4/MKV/TS)'), out: Path=typer.Option(..., help='Output directory for tracks, manifest and overlays'), min_px: float=typer.Option(200.0, help='Minimum apparent body length (px) for a close pass. 200 = amplitude grade, 100 = frequency grade'), min_duration_s: float=typer.Option(3.0, help='Shortest track and close pass to keep'), overlay: bool=typer.Option(False, help='Also write one verification PNG per close pass'), max_overlays: int=typer.Option(12, help='Cap on overlay PNGs (largest passes first)'), source_credit: str=typer.Option('', help='Credit recorded in the manifest')):
    """Track a captured clip, mine close passes, write the curated-segment manifest.

    Writes ``tracks.csv`` (per-track, per-frame), ``close_passes.json`` (the
    curated-segment manifest, flags included) and, with ``--overlay``, one
    verification PNG per pass. Nothing is downloaded and nothing is published.
    """
    ...

@stream_app.command(name='manifest')
def stream_manifest(dir: Path=typer.Option(..., '--dir', help='Dated capture directory, e.g. data/external/media/leopard_shark/mba_stream/20260710'), cam: str=typer.Option('', help='Cam label for new entries: shark | kelp_forest'), out: Optional[Path]=typer.Option(None, help='Manifest path (default: <dir>/manifest.json)')):
    """Inventory a dated capture directory into ``manifest.json`` (ffprobe if available).

    ``live_verified`` and per-file notes already in the manifest are preserved:
    they are the Phase 0 human check that the feed was live and not the
    off-hours loop, and no probe can recover them.
    """
    ...

def _nested_model(annotation):
    """The BaseModel subclass inside an annotation, unwrapping Optional/unions."""
    ...

def _model_at(loc: tuple) -> Optional[type]:
    """Resolve a pydantic error location to the model class that owns its last key."""
    ...

def _lint_config(path: Path) -> tuple[str, list[str]]:
    """Validate one deployment YAML. Returns ``(id, errors)``; empty errors = OK."""
    ...

@app.command(name='config-lint')
def config_lint(paths: Optional[list[Path]]=typer.Argument(None, help='Deployment YAMLs or directories (default: configs/deployments)')):
    """Validate deployment configs against the schema; exits non-zero on any failure."""
    ...

@app.command()
def dashboard(port: int=typer.Option(8750, help='Port on 127.0.0.1'), no_browser: bool=typer.Option(False, '--no-browser', help='Do not open a browser'), root: Path=typer.Option(Path('.'), help='Repository root (holds configs/, reports/)'), demo: bool=typer.Option(False, '--demo', help='Open a synthetic demo workspace (three animals) instead of --root; written once to ~/.cache/anchor/dashboard-demo'), reset_demo: bool=typer.Option(False, '--reset-demo', help='With --demo: rebuild the demo workspace from scratch')):
    """Local web dashboard: deployments, runs, track viewer, QC and gates."""
    ...
