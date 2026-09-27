"""Deployment data-health checks — the engine behind ``anchor doctor``.

Every check here is calibrated against a defect that exists in this repository's
own configs today, and every one of them is cheap: nothing in this module loads
a whole raw CSV. :func:`probe_raw_csv` reads a few thousand rows from the head,
the middle and the tail of the file plus a byte-level newline count, so the
605 MB white-shark export and the 980 MB AXY-Depth export are both triaged in
seconds.

Deliberately *not* routed through :func:`anchor.ingest.io.load_deployment`:
that function applies calibration and writes ``data/interim/<id>.parquet`` as a
side effect, which is exactly what a read-only health check must not do.

Threshold provenance
--------------------
The WARN/FAIL cut points below follow the minimum reporting checklist of Payne
et al. (2026), *Animal Biotelemetry* (https://doi.org/10.1186/s40317-025-00438-w):
a deployment record must report its sampling rate, its time base, its sensor
calibration and the animal's measured body size, and a value that is absent or
inconsistent with the record is a reporting defect rather than a matter of
taste. Each constant names the specific consequence it guards against.

Levels are ``PASS`` / ``WARN`` / ``FAIL``. ``FAIL`` means "a published number
computed from this deployment is wrong"; ``WARN`` means "a number may be wrong
and nothing in the record settles it".
"""
from __future__ import annotations
import hashlib
import json
import math
from dataclasses import dataclass, field, asdict
from io import StringIO
from pathlib import Path
from typing import Any, Literal, Optional
import numpy as np
import pandas as pd
from anchor.ingest import io as _io
from anchor.ingest.config import DeploymentConfig, load_config
TIME_AXIS_FAIL = 0.05
TIME_AXIS_WARN = 0.01
SAMPLING_RATE_FAIL = 0.05
SAMPLING_RATE_WARN = 0.01
GAP_FACTOR = 2.5
GAP_MISSING_FRACTION_FAIL = 0.01
DEPTH_OFFSET_WARN = 0.5
DEPTH_OFFSET_FAIL = 2.0
DETACH_SURFACE_DEPTH_M = 0.5
DETACH_SUSTAINED_MIN = 10.0
DEPTH_DRIFT_WARN = 0.5
DEPTH_DRIFT_FAIL = 2.0
CALIB_COND_FAIL = 1000.0
CALIB_BIAS_RATIO_FAIL = 5.0
CALIB_ACCEL_BIAS_RATIO_FAIL = 0.5
HEADING_MAG_RATE_FAIL_HZ = 0.5
HEADING_MAG_RATE_WARN_FACTOR = 2.0
HEADING_HARD_IRON_WARN = 1.0
HEADING_HARD_IRON_FAIL = 5.0
HEADING_DIP_MAD_FAIL_DEG = 10.0
HEADING_DIP_MAD_WARN_DEG = 5.0
HEADING_DIP_OFFSET_FAIL_DEG = 15.0
HEADING_DIP_OFFSET_WARN_DEG = 5.0
HEADING_MAPPING_MARGIN_FAIL_DEG = 3.0
HEADING_COVERAGE_FRACTION_FAIL = 0.25
HEADING_COVERAGE_EIGENVALUE_FAIL = 0.05
HEADING_MAX_CSV_ROWS = 4000000
HEADING_CSV_CHUNK_ROWS = 500000
DEFAULT_PROBE_ROWS = 5000

@dataclass(frozen=True)
class Finding:
    """One check's verdict.

    ``check`` is a stable dotted identifier (so downstream tooling can key on
    it), ``message`` is the human sentence, and ``value`` carries the numbers
    the verdict was made from so a reader can audit the threshold.
    """
    check: str
    level: Level
    message: str

    def to_dict(self) -> dict[str, Any]:
        ...

@dataclass
class QCReport:
    deployment_id: str
    config_path: str
    findings: list[Finding]

    @property
    def worst_level(self) -> Level:
        ...

    @property
    def failed(self) -> bool:
        ...

    def to_dict(self) -> dict[str, Any]:
        ...

    def to_table(self) -> str:
        """Fixed-width table, one row per finding."""
        ...
QC_STAMP_VERSION = 4

def config_fingerprint(cfg: Any, length: int=16) -> str:
    """Short content hash of the *whole* deployment config.

    Deliberately not :func:`anchor.ingest.io.ingest_fingerprint`: that hash
    covers only the fields that change the interim parquet's *contents*, and
    ``animal`` is not among them — so keying a QC report on it would be blind
    to a ``length_cm`` promotion, which is exactly the edit whose doctor
    verdict went stale in ``docs/regen_2026-09.md`` §10. The checks in this
    module read the config broadly (``animal``, ``release``/``recovery``,
    ``timezone``, ``sampling_rate_hz``, ``calibration``, ``raw_csv``), so the
    honest key is the config in full: a field this module does not read yet
    costs a spare re-run, a field it reads and the hash misses ships a wrong
    table.

    Same 16-hex, sorted-keys, ``default=str`` convention as
    ``ingest_fingerprint`` and ``anchor.validation.ledger.card.config_hash``,
    computed locally rather than imported so ``anchor doctor`` keeps its cheap
    imports (``anchor.validation`` pulls in the pose/drone stack). Non-pydantic
    objects — a stub in a test, a ``SimpleNamespace`` — hash their ``__dict__``
    so this is total over whatever a caller holds.
    """
    ...

def file_fingerprint(path: str | Path, length: int=16) -> str:
    """Short content hash of one file, read in chunks.

    Same 16-hex convention as :func:`config_fingerprint`. Chunked because the
    same helper is the obvious one to reach for on a raw CSV, and this module's
    contract is that nothing in it reads a 605 MB file into memory.
    """
    ...

def calibration_fingerprints(cfg: Any) -> dict[str, Optional[str]]:
    """Content hash of each calibration JSON the config references.

    ``None`` for a kind the config does not reference at all and
    :data:`CALIBRATION_ABSENT` for one it references that is not on disk: the
    three states carry different verdicts in :func:`check_calibration` (WARN,
    FAIL, and a real gate result), so a stamp that collapsed any two of them
    would outlive the edit that moved between them.

    Hashing the *contents* is the point. :func:`config_fingerprint` covers the
    calibration **paths**, and re-running the ellipsoid fit rewrites the same
    path in place — every path identical, every byte different, and
    ``calibration.mag`` moving from FAIL to PASS under a cached report that
    still looks fresh.
    """
    ...

def qc_stamp(cfg: Any) -> dict[str, Any]:
    """Identity of the inputs a QC report was computed from.

    ``raw_csv_bytes`` is ``None`` when the file is absent, and that is a state
    worth recording rather than skipping: the doctor's verdict on a missing raw
    CSV is a FAIL, and it must not outlive the file reappearing. The mtime
    rides along for diagnosis by eye only and is never compared — copying or
    syncing ``data/raw`` rewrites every mtime without changing a byte (see
    :func:`anchor.ingest.io.raw_csv_stat`).

    A config with no ``raw_csv`` at all is stamped as "no raw CSV" rather than
    handed to :func:`~anchor.ingest.io.raw_csv_stat`, whose ``Path("")``
    resolves to the working directory and would stamp *its* size.

    ``calibration_hashes`` is the third input (see
    :func:`calibration_fingerprints`): the paths already ride inside
    ``config_hash``, but a re-fit that rewrites a calibration JSON in place
    moves no path and would otherwise leave a cached FAIL looking current.
    """
    ...

def _raw_csv_desc(n_bytes: Optional[int]) -> str:
    ...

def _calibration_desc(hashes: Any) -> str:
    ...

def stamp_is_current(stamp: Any, cfg: Any) -> tuple[bool, str]:
    """``(fresh, reason)`` for a stamp read back from a cached QC report.

    The reason is returned rather than logged so the caller can put it in front
    of whoever is looking at the artefact — a cache that silently rebuilt and a
    cache that silently did not look identical otherwise. A report with no
    stamp is never current: every ``<id>_qc.json`` written before this gate
    carries none, and nothing in it ties it to the config in hand.
    """
    ...

def write_report(report: QCReport, out: Optional[str | Path]=None) -> Path:
    """Serialize ``report`` to JSON; default ``data/interim/<id>_qc.json``."""
    ...

@dataclass
class RawProbe:
    """Head / middle / tail slices of a raw CSV plus its exact row count.

    Each slice is schema-normalized and carries a ``datetime`` column parsed
    from :attr:`datetime_source`, and (when the file has both a ``Timestamp``
    column and separate ``Date`` + ``Time`` columns) a second ``datetime_ts``
    column parsed from ``Timestamp`` alone. Keeping the two apart is the point:
    ``io.parse_datetime`` returns one *reconciled* axis (since 3354f0f,
    ``Date`` + ``Time`` wins a wide disagreement and ``Timestamp`` is kept
    otherwise), so a check that reused it would see one column and could not
    report the disagreement between them at all.
    """
    path: Path
    sep: str
    n_rows: int
    head: pd.DataFrame
    mid: Optional[pd.DataFrame]
    tail: pd.DataFrame
    datetime_source: str
    has_timestamp_pair: bool

    def parts(self) -> list[tuple[str, pd.DataFrame]]:
        """The distinct probed chunks.

        When the file is small enough that the head chunk already covers every
        row, :func:`probe_raw_csv` makes ``tail`` the *same object* as ``head``;
        yielding it twice would double-count every gap and reversal found in it.
        """
        ...

def count_csv_rows(path: str | Path, block_bytes: int=8 << 20) -> int:
    """Data rows in a CSV, counted by streaming newlines. Never loads the file."""
    ...

def _decode(raw: bytes) -> str:
    ...

def _read_lines_at(path: Path, offset: int, nbytes: int, *, skip_partial_first: bool) -> list[str]:
    """Complete lines from ``[offset, offset + nbytes)``.

    ``skip_partial_first`` must be False when ``offset`` is known to land
    exactly on a line boundary (the head chunk, which starts one byte past the
    header's newline) and True when the offset was chosen by byte arithmetic
    and therefore lands mid-line.
    """
    ...

def _frame_from_lines(header: str, lines: list[str], sep: str) -> pd.DataFrame:
    ...

def _datetime_columns(df: pd.DataFrame) -> tuple[Optional[str], Optional[str], Optional[str]]:
    """Return ``(timestamp_col, date_col, time_col)``; any may be None."""
    ...

def _attach_datetimes(df: pd.DataFrame) -> tuple[pd.DataFrame, str, bool]:
    """Add ``datetime`` (authoritative) and, when redundant, ``datetime_ts``.

    ``Date`` + ``Time`` are the tag's own written fields and are treated as
    authoritative; ``Timestamp`` is a derived convenience column that some
    exports write with month and day transposed (``APT_240702_S2``).
    """
    ...

def probe_raw_csv(path: str | Path, schema: str, probe_rows: int=DEFAULT_PROBE_ROWS) -> RawProbe:
    """Read the head, middle and tail of a raw CSV plus its exact row count.

    The returned chunks are guaranteed disjoint: when the head and tail byte
    blocks overlap, the shared rows are trimmed off the front of the tail so
    that gaps and reversals inside them are counted once.

    Raises
    ------
    ValueError
        If the file has a header but no data rows (a truncated or failed
        export). :func:`run_doctor` turns that into a ``raw_csv`` FAIL.
    """
    ...

def check_timestamp_consistency(probe: RawProbe) -> Optional[Finding]:
    """Compare the ``Date`` + ``Time`` columns against ``Timestamp`` directly.

    Returns ``None`` when the file carries only one of the two, so the caller
    can leave the check out of the table rather than reporting a vacuous PASS.
    """
    ...

def check_time_axis(cfg: DeploymentConfig, probe: RawProbe) -> Finding:
    """``|(t_max - t_min) * fs - n_rows| / n_rows`` against the configured fs."""
    ...

def check_sampling_rate(cfg: DeploymentConfig, probe: RawProbe) -> Finding:
    """Detected fs (``io.detect_sampling_rate`` on the head) vs configured fs.

    ``load_deployment`` never calls ``detect_sampling_rate``, so a species
    default that does not match the tag's programmed rate propagates silently
    into every frequency and every dead-reckoned distance.
    """
    ...

def check_time_continuity(cfg: DeploymentConfig, probe: RawProbe, gap_factor: float=GAP_FACTOR) -> Finding:
    """Gaps and time reversals in the probed chunks, with segment boundaries."""
    ...

def check_depth_reference(probe: RawProbe, depth_col: str='Depth') -> Optional[Finding]:
    """Surface-referenced depth offset and start-to-end drift.

    ``None`` when the schema carries no depth channel. The shallowest depth the
    tag reports is estimated by the 1st percentile of a chunk rather than the
    minimum, so a single spike does not define the surface.
    """
    ...

def check_config_sanity(cfg: DeploymentConfig) -> list[Finding]:
    """Config fields whose absence silently changes a published number."""
    ...

def calibration_degeneracy(cal: dict) -> dict[str, float]:
    """Degeneracy diagnostics for one ellipsoid fit from ``calibrate.fit_ellipsoid``.

    Two independent failure modes, both present on disk:

    ``cond_A``
        Condition number of the 3x3 upper-triangular ``A``. A collapsed axis
        (``LS_250326/mag.json`` has ``A[2][2] = 1.35e-08``) makes the
        calibrated vector effectively two-dimensional.
    ``bias_ratio``
        ``||A @ b|| / target``. When the fitted bias runs away from the data
        cloud, ``||A(m - b)||`` is dominated by the constant ``||A(-b)||`` and
        the residual is flat: the fit reports a low cost while encoding no
        orientation information. The runaways measured in this archive sit at
        9.23 and 11.48 (``docs/regen_2026-09.md`` section 16.13.3) and the
        least-squares fitter's silent runaways at 10^3 to 10^4.

    Neither is a *soundness* statistic, and this function is the reason the
    distinction has to be made somewhere else. Both are functions of the fit
    alone, and the refused dry-spin fit ``BR_260318/mag.json`` beats the
    validated in-flight fit of the same tag on both of them -- ``cond_A``
    67.68 against 1.32, ``bias_ratio`` 0.9997 against 1.7405 -- while occupying
    1 of 48 direction cells against 48 of 48. What separates them is coverage,
    which is a function of the *data*; see :func:`mag_coverage_verdict`.
    """
    ...

def mag_coverage_verdict(cal: dict) -> tuple[Optional[str], dict[str, Any]]:
    """The direction coverage a magnetometer calibration carries, and its verdict.

    Returns ``(reason, value)``: ``reason`` is ``None`` when the file's own
    record of the fit's coverage clears :data:`HEADING_COVERAGE_FRACTION_FAIL`
    and :data:`HEADING_COVERAGE_EIGENVALUE_FAIL`, and a failure clause
    otherwise. ``value`` is what the finding should carry either way.

    Three things this deliberately does not do.

    It does not *recompute* anything. The coverage is read out of the
    ``validation`` block that ``anchor calibrate mag --in-flight`` writes
    (:func:`anchor.ingest.mag_inflight.coverage_stats` computed it, on the data
    the fit was made from). Recomputing it here would need the record, would
    cost a bulk read in a check whose whole contract is that it reads a JSON
    file, and would put a second opinion with different numbers next to the
    ``heading.coverage`` finding.

    It does not gate the dip statistics, though it reports them. The dip test
    belongs to the heading family, which scores **the calibration in use** and
    not the file in isolation: ``heading.dip_spread``, ``heading.dip_offset``
    and ``heading.axis_mapping`` carry those verdicts and the G-heading gate
    reads its floors off them.

    It does not let an unrecorded fit through. A magnetometer calibration with
    no ``validation`` block is a fit whose coverage was never measured, and
    ``docs/regen_2026-09.md`` section 16.10 is the case for refusing it: the
    fit-only statistics rank the archive's refused dry-spin fit *ahead* of its
    validated in-flight fit, so "passes ``cond_A`` and ``bias_ratio``" is not
    evidence of soundness and never was. Both unvalidated magnetometer fits on
    disk in this repository are degenerate; one of them (``BR_260318/mag.json``,
    1 cell of 48, a 2.60 deg cap) clears both fit-only floors.
    """
    ...

def check_calibration(cfg: DeploymentConfig) -> list[Finding]:
    """Load each referenced calibration JSON and gate it on degeneracy.

    The two branches ask different questions, because the two instruments fail
    differently. The accelerometer branch is the original one and is unchanged:
    ``cond_A`` and a bias-runaway floor at
    :data:`CALIB_ACCEL_BIAS_RATIO_FAIL`. The magnetometer branch keeps
    ``cond_A``, raises the runaway floor to :data:`CALIB_BIAS_RATIO_FAIL` --
    because a hard iron of the order of the field radius is the norm on these
    tags and not a defect -- and adds the statistic that actually separates a
    sound fit from a degenerate one, the recorded direction coverage
    (:func:`mag_coverage_verdict`).
    """
    ...

def _block_nanmean(values: np.ndarray, block: int) -> np.ndarray:
    """Block mean ignoring NaN, the way ``axy_ingest._block_mean`` does it.

    Restated rather than imported so this check does not pull the trajectory
    ingest into ``anchor doctor``; the point is only to put the depth channel
    on the same 1 Hz grid the detachment detector runs on, so its answer here
    is the answer the driver would get.
    """
    ...

class _DepthOnlyTrack:
    """The three attributes ``detect_tag_detachment`` reads, and nothing else."""

    def __init__(self, depth_m: np.ndarray, base_hz: float=1.0):
        ...

    def __len__(self) -> int:
        ...

def check_detachment(cfg: DeploymentConfig) -> list[Finding]:
    """``detachment.stationary_span`` — is the "attached" span partly a
    motionless tag?

    The shipped truncation rule cuts a track where the depth channel says the
    tag reached the surface. A tag that comes off on the bottom, or an animal
    that stops, leaves the depth channel flat and near its last value for as
    long as it takes the float to work the tag up: on ``BR_260318_S3`` that is
    7.617 h, and the accelerometer sees it immediately — the one-minute median
    dynamic-acceleration norm falls 4.6x in sixty seconds and never recovers
    (``docs/regen_2026-09.md`` §17.4.2). This check runs the same rule the
    driver runs (:func:`anchor.trajectory.detachment.detect_stationary_onset`)
    and WARNs when a stationary span of at least 60 min lies inside what the
    water-exit rule would call attached, with the hours and the fraction.

    It needs no filter and no reconstruction — only the interim parquet's
    accelerometer and depth columns, read once (0.35 s on the flagship's
    1.87 M rows, 0.16 s to segment). It returns **no finding at all** when
    that parquet is absent or was written from a different config: a check
    that could not run must not read as a check that passed. A missing
    accelerometer is the same case.
    """
    ...

def _gate_entry(key: str, value: float, floor: float, comparison: str, detail: str) -> dict[str, Any]:
    """One numeric floor, in the shape :mod:`anchor.validation.ledger.gates` reads.

    The ledger scores G-heading from exactly these entries rather than from its
    own copy of the thresholds, so the gate's floors *are* the doctor's
    constants and cannot drift apart from them.
    """
    ...

def _heading_finding(check: str, level: Level, message: str, value: dict[str, Any], gates: list[dict[str, Any]] | None=None) -> Finding:
    ...

def _uncalibrate_mag(mag: np.ndarray, cal: dict) -> tuple[np.ndarray, str]:
    """Recover raw counts from a calibrated magnetometer column.

    ``apply_calibration`` writes ``A (m_raw - b)`` into the interim parquet, so
    the raw record is ``A^-1 m_cal + b`` exactly. Inverting is preferred over
    re-reading the raw CSV: it is one 3x3 solve against a 130 MB to 605 MB
    streamed parse, and it is exact. It is refused when ``A`` is too
    ill-conditioned to invert without amplifying the parquet's own float noise
    past the signal -- which is the state ``data/interim/calib/LS_250326/mag.json``
    leaves its deployments in (``A[2][2] = 1.35e-08``, calibrated mag a
    constant), and where the honest answer is that the raw record is gone from
    the cache and must come from the CSV.
    """
    ...

def _heading_from_parquet(cfg) -> Optional[dict[str, Any]]:
    """Accel plus the in-use and raw magnetometer from ``data/interim/<id>.parquet``.

    ``None`` unless the cache is valid for *this* config
    (:func:`anchor.ingest.io.interim_cache_is_valid`): a parquet written from a
    different clip or a different calibration would answer a question about a
    record that is not the one the YAML describes.

    The parquet holds the magnetometer **as the pipeline uses it** — raw counts
    when ``calibration.mag`` is null, calibrated otherwise — so it is the in-use
    column by construction, and the raw column is recovered from it by
    inversion.
    """
    ...

def _heading_from_csv(cfg) -> dict[str, Any]:
    """The same two columns, streamed from the raw CSV and capped.

    The fallback when no valid interim parquet exists. Two caveats, both
    reported in the finding rather than hidden: the read is capped at
    :data:`HEADING_MAX_CSV_ROWS` so a doctor pass stays inside a minute on the
    largest export, and the raw CSV is *unwindowed*, so off-animal handling and
    post-recovery float are included where the parquet route would have
    excluded them.

    ``cfg.raw_mag_csv``, when set, is honoured here through the same
    :func:`anchor.ingest.io.substitute_mag_on_timestamps` the ingest path uses,
    so the magnetometer this function returns is the one
    ``data/interim/<id>.parquet`` will hold.
    """
    ...

def heading_inputs(cfg) -> dict[str, Any]:
    """Accelerometer, the magnetometer the pipeline uses, and the raw counts.

    Prefers the interim parquet, which is columnar, read-only and costs under a
    second on the flagship's 1.87 M rows; falls back to a capped streamed read
    of the raw CSV. Never writes anything: the module's contract is that
    ``anchor doctor`` caches nothing and calibrates nothing.
    """
    ...

def _site_dip(cfg, dip_deg: Optional[float]) -> tuple[float, float, str]:
    """``(dip_deg, tolerance_deg, provenance)`` for a deployment.

    Raises rather than defaulting when neither an override nor a known site
    supplies a value: a wrong dip moves the test's offset by exactly its error
    and would be read as a calibration defect.
    """
    ...

def inflight_mag_calibration(cfg, *, dip_deg: Optional[float]=None, data: Optional[dict[str, Any]]=None) -> dict:
    """Fit and validate an in-flight magnetometer calibration for ``cfg``.

    The shared body behind ``anchor calibrate mag --in-flight`` and the
    doctor's heading family, so the numbers the CLI writes to disk and the
    numbers the gate is scored from come from one code path.

    ``data`` is a :func:`heading_inputs` result the caller already holds.
    :func:`heading_diagnostics` passes its own, because the record is the
    expensive part -- 8.3 s of streamed CSV on the largest deployment against
    a fraction of a second for the fit -- and reading it twice per doctor pass
    would double the family's cost for nothing.
    """
    ...

def _mag_rate_hz(n_mag: int, n_rows: int, fs_hz: float) -> float:
    """Finite magnetometer triples per second of record."""
    ...

def heading_diagnostics(cfg, *, dip_deg: Optional[float]=None) -> dict[str, Any]:
    """Everything the heading family reports, in one read of the record.

    Two blocks, and the distinction between them is the point.

    ``in_use``
        The dip-angle test and the coverage of the field directions **the
        pipeline computes today** — raw counts when ``calibration.mag`` is
        null, calibrated otherwise, with the identity axis mapping the
        pipeline assumes. This is what the gate is scored on: it measures the
        heading that is actually being fed to the filter.
    ``inflight``
        A fresh in-flight fit on the same record, with the 48-mapping search.
        It is the counterfactual: the hard-iron ratio, the conditioning, and
        whether the data prefer a frame other than the identity. A record can
        fail ``in_use`` and still carry a perfectly good magnetometer, and that
        is the case the operator needs told apart from a dead sensor.
    """
    ...

def check_heading(cfg: DeploymentConfig) -> list[Finding]:
    """The heading family: magnetometer rate, hard iron, dip test, mapping, coverage.

    Scored on **the calibration the YAML references** — raw counts when
    ``calibration.mag`` is null — and not on the in-flight fit, which is
    reported beside it as the counterfactual. That distinction is the whole
    check: on ``BR_260318_S3`` the shipped chain holds the field-to-DOWN angle
    to a MAD of 39 deg and an in-flight fit of the same record holds it to
    2.4 deg, and a family scored on the fit would have called the deployment
    healthy while the filter was being fed a measurement of posture.

    Every finding carries a ``gates`` list of ``{key, value, floor,
    comparison}`` entries, which is what
    :func:`anchor.validation.ledger.gates.evaluate_heading_gate` scores
    **G-heading** from. A family that cannot run at all still emits one finding
    with a failing ``mag_rate_hz`` entry, so a deployment with no magnetometer
    fails the gate rather than silently skipping it.
    """
    ...

def run_doctor(cfg_path: str | Path, probe_rows: int=DEFAULT_PROBE_ROWS, heading: bool=True) -> QCReport:
    """Assemble the full health report for one deployment YAML.

    ``heading=False`` drops the :func:`check_heading` family, which is the one
    check in this module that reads bulk sensor data rather than a probe. It
    reads the interim parquet's six IMU columns when a valid cache exists (0.8 s
    on the flagship's 1.87 M rows) and streams a capped slice of the raw CSV
    otherwise; both are read-only and neither writes a cache.
    """
    ...
