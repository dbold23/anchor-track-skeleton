# Architecture

`anchor` is organized around the four sections of the paper's Methods chapter.
Each subpackage has clear ownership and tests.

## Module map (paper section to code path)

```
Paper §4.2 Ingest + calibration
    anchor/ingest/
        io.py              CSV schema dispatch (axy5, axy_depth, cats)
        calibrate.py       Ellipsoid fit (NXP AN4246), degenerate-fit gate
        config.py          Pydantic deployment YAML + species inheritance

Paper §4.3 Kinematics
    anchor/kinematics/
        core.py            ODBA, VeDBA, jerk, rotation-corrected DBA, pitch/roll, tailbeat peaks
        locomotion.py      Axial undulator vs. pectoral oscillator dispatch
        features.py        Sliding-window summary metrics + standardization
        mount.py           Tag frame -> body frame: the declared fixed mount rotation
        stats.py           Mahalanobis change detection + rotation test (tagtools parity)

Paper §4.4 Behavior inference
    anchor/behavior/
        _base.py           FittedClassifier dataclass + persistence
        hmm.py             Unsupervised: GMM + GMM-warm-started HMM
        supervised.py      Supervised: RF/XGB + isotonic CalibratedClassifierCV
        labels.py          BORIS / VIA video-label importer
        cv.py              Subject-LOSO + stratified k-fold splitters
        resample.py        Cross-species feature pooling

Paper §4.5 Trajectory reconstruction
    anchor/trajectory/
        axy_ingest.py      Bridge: kinematics to filter input
        imu.py             Mag ellipsoid + tilt-comp heading        §4.5.2
        particle_filter.py SMC + FFBS smoother                      §4.5.3, §4.5.4
        two_filter.py      Bidirectional smoother (diagnostic)      §4.5.4
        release_anchor.py  Release-point Gaussian prior
        end_anchor.py      Recovery-point Gaussian likelihood
        bathymetry.py      Topobathy raster lookup
        polygon_constraint.py Tide-aware water-mask hard constraint §4.5.1
        site_geometry/     NHD-consensus polygon derivation         §4.5.1
        tides.py / tide_fetch.py   NOAA CO-OPS station 9413450
        currents.py        Tidal-prism backward propagation
        wind.py / wind_fetch.py    NOAA NDBC + Allen 1999 leeway
        detachment.py      Whitney 2016 + regime segmentation       §4.5.5
        animate_filter.py  Particle-filter MP4/GIF
        report.py          Self-contained HTML report
        run_deployment.py  Single-CLI end-to-end orchestrator
        sites/elkhorn.py, sites/ano_nuevo.py  Site constants

Validation (external ground truth, no paper section of its own)
    anchor/validation/
        pose.py            DeepLabCut / SLEAP keypoints -> TBF, amplitude, body-length scale
        drone.py           UAS video ingest + pixel->world georeferencing
        drone_corpus.py    Manifest of UAS overflights; world-coordinate K calibration
        corpus.py          Per-species online clip manifest + end-to-end K from pose
        online_corpus.py   Online video -> pose -> species K (bat ray; no synced accel)
        paired_tag.py      CATS + AXY clock alignment and feature harmonization
        paired_tag_runner.py  End-to-end paired-tag orchestrator (§C3 figure)
        pose_overlay.py    Keypoints, skeleton and per-cycle metrics burned onto video
        auto_clip.py       Cuts uncertain-window clips from source video (active learning)
        stream_kinematics.py  Single-camera aquarium-stream kinematics: MOG2
                              tracking, centroid-locked motion-energy tail-beat
                              frequency, close-pass mining, MobileSAM
                              single-animal segmentation, body-frame tail
                              excursion, body-as-ruler speed -> K.
                              See docs/stream_kinematics.md
        ledger/            R0 score card and gate table (design §3.5, §3.7, Phase 0)
            channel.py     Along-/cross-channel decomposition against a centreline
            scores.py      RMSE, ensemble CRPS, variogram score, rank histograms, containment
            gates.py       §3.7's ten gate rows as data + the standing G-degeneracy check
            card.py        Versioned ScoreCard: provenance, banner, suppression rule, strict JSON
            linear_gaussian.py  Kalman/RTS/FFBS control arm for the harness itself
                           See docs/ledger.md
```

## Cross-section flow

```
raw CSV ─┐
         ├─> ingest.io.load_deployment ─┐
config ──┘                              ├─> kinematics.core.add_* (DBA family)
                                        ├─> kinematics.locomotion.dispatch (tailbeat axis)
                                        ├─> kinematics.features.summarize_window_metrics
                                        ├─> behavior.fit_hmm / fit_supervised
                                        └─> trajectory.axy_ingest (heading, speed, depth)
                                                ├─> trajectory.particle_filter (forward)
                                                ├─> trajectory.particle_filter.ffbs_smoother (with end-anchor)
                                                ├─> trajectory.detachment (post-detach drift)
                                                └─> trajectory.report (HTML)
```

## Top-level files

- `anchor/cli.py` — `anchor <command>` entry point (Typer); thin wrapper around
  `pipeline.py` orchestration.
- `anchor/pipeline.py` — v1/v2 orchestration glue tying ingest, kinematics, and
  behavior stages. Driven by `cli.py` (`anchor process|events|features|classify|
  run-all`). A DVC pipeline wrapping these stages is planned but not yet
  configured (no `dvc.yaml` in the repo).
- `anchor/qc.py` — the engine behind `anchor doctor`: read-only deployment
  data-health checks (time axis vs row count, Date+Time vs Timestamp, detected
  vs configured sampling rate, gaps and reversals, depth zero drift, config
  sanity, degenerate calibration fit). Probes only the head, middle and tail of
  the raw CSV, so a 600 MB export is triaged in seconds.
- `anchor/events.py` — high-activity event detection via VeDBA + jerk thresholds.
- `anchor/export.py` — CF/ACDD NetCDF and Movebank-shaped archival export.
- `anchor/spaceuse.py` — utilization distributions and the energy seascape,
  propagated through the FFBS trajectory samples.
- `anchor/demo.py` — the zero-data `anchor demo` end-to-end run.
- `anchor/plot.py` — shared plotting helpers (matplotlib).

## Tests

`tests/` mirrors the source tree:

```
tests/
├── conftest.py
├── fixtures/
├── ingest/      4 test files
├── kinematics/  5 test files
├── behavior/    7 test files
├── trajectory/  28 test files
├── trajectory/site_geometry/  3 test files
└── validation/  11 test files (incl. test_ledger.py, test_stream_kinematics.py)
```

Plus the top-level `tests/test_*.py` covering the CLI, `anchor doctor`, export,
space-use, the demo, the claims registry and window reconciliation.

Run a section's tests: `pytest tests/<section>/`.

## Data + configs

- `configs/species/` — per-species defaults (locomotion mode, body length,
  Strouhal K, accel cutoff, tailbeat axis).
- `configs/deployments/` — per-deployment YAMLs with `inherits: <species>`.
- `data/` and `reports/` are gitignored and produced locally (the canonical
  `data/` lives in the sibling `AXY+/data` and is symlinked in). DVC-based data
  versioning is planned but not yet set up.
