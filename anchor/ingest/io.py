"""Loading and normalization of AXY-family CSV exports.

Three raw schemas are supported:

- ``axy5``      AXY-5, ``;`` delimiter, ``accX/Y/Z`` in g, ``Timestamp`` column.
- ``axy_depth`` AXY-Depth, ``,`` delimiter, ``X/Y/Z`` in g, separate ``Date``
                + ``Time`` columns (DD/MM/YYYY), no magnetometer.
- ``cats``      CATS/APT clamp, ``,`` delimiter, accelerometer in m/s^2
                (converted to g), gyro + mag + depth + camera + speed; European
                ``DD.MM.YYYY`` dates.
"""
from __future__ import annotations
import hashlib
import json
import logging
from pathlib import Path
from typing import Any, Literal, Iterator
import numpy as np
import pandas as pd
GRAVITY = 9.80665
FS_MISMATCH_TOL = 0.05
FS_DETECT_ROWS = 100000
INGEST_SCHEMA_VERSION = 3
TIMESTAMP_AGREEMENT_TOL_S = 1.0
TIMESTAMP_DISAGREEMENT_FRAC = 0.01
SPAN_ROWS_MAX_RATIO = 5.0
SPAN_CHECK_MIN_EXPECTED_S = 60.0
RAW_MAG_MATCH_MIN = 0.95
RAW_MAG_CHUNK_ROWS = 2000000

def read_flexible_csv(filepath: str | Path, **kwargs) -> pd.DataFrame:
    """Read a CSV with unknown delimiter and tolerant encoding.

    Tries the Python-engine sniffer first, then falls back through ``,``,
    ``\\t``, ``;``. Tries UTF-8 then Latin-1 — CATS/APT exports include non-ASCII
    unit symbols (``°``, ``²``, ``µ``) as raw cp1252 bytes.
    """
    ...

def iter_csv_chunks(filepath: str | Path, chunksize: int=1000000, sep: str | None=None, **kwargs) -> Iterator[pd.DataFrame]:
    """Yield DataFrame chunks; used by the large WS loader."""
    ...

def _sniff_delimiter(filepath: str) -> str:
    ...

def _datetime_columns(df: pd.DataFrame) -> tuple[str | None, str | None, str | None]:
    """Return ``(timestamp_col, date_col, time_col)``; any may be ``None``.

    Kept identical to ``anchor.qc._datetime_columns`` on purpose: the doctor's
    ``time.timestamp_consistency`` verdict is only evidence about the loader if
    both look at the same pair of columns.
    """
    ...

def _span_str(parsed: pd.Series) -> str:
    """``"52.75 h (2024-07-02 22:16:45 .. 2024-07-05 03:01:44)"`` for a warning.

    Min-to-max, not first-to-last: a column that has to be described in a
    warning is one that may not be monotonic.
    """
    ...

def _reconcile_datetime_columns(from_ts: pd.Series, from_pair: pd.Series) -> tuple[pd.Series, str]:
    """Choose between a vendor ``Timestamp`` column and ``Date`` + ``Time``.

    They are redundant, so when they agree the choice does not matter and
    ``Timestamp`` is kept (it is the column this loader has always used). When
    they disagree on more than :data:`TIMESTAMP_DISAGREEMENT_FRAC` of rows,
    ``Date`` + ``Time`` wins: those are the tag's own written fields, whereas
    ``Timestamp`` is a derived convenience column that at least one export
    writes with month and day transposed (``APT_240702_S2``, whose ``Timestamp``
    turns a 52.75 h record into a 2140.75 h one). Both spans are named in the
    warning so the choice is auditable from the log alone.
    """
    ...

def parse_datetime(df: pd.DataFrame) -> pd.DataFrame:
    """Return a copy with standardized ``datetime``, ``Date``, ``Time`` columns.

    Handles a combined ``Timestamp`` column, separate ``Date`` + ``Time``
    columns, or both. Tries multiple date conventions (US, EU dot, EU slash)
    before falling back to pandas' inference.

    When the file carries *both*, both are parsed and cross-checked; see
    :func:`_reconcile_datetime_columns` for which one wins and why. Which
    column the returned axis came from is recorded in
    ``df.attrs["datetime_source"]`` (``"timestamp"`` or ``"date_time"``).
    """
    ...

def _try_datetime_formats(raw: pd.Series) -> pd.Series:
    ...

def detect_sampling_rate(df: pd.DataFrame) -> float:
    """Detect Hz from timestamps.

    Strategy:

    - If the timestamp column has sub-second resolution (i.e., most adjacent
      rows have different timestamps), ``fs = 1 / median positive delta``.
    - Otherwise the timestamp is stamped only once per second (common in the
      AXY-5 exports where 25 samples share the same ``HH:MM:SS.000``), and we
      count duplicates of the first timestamp value — that count IS fs.
    """
    ...

def normalize_schema(df: pd.DataFrame, source: Schema) -> pd.DataFrame:
    """Rename + unit-convert so downstream code sees ``accX/Y/Z``, ``magX/Y/Z``,
    ``Depth``, ``TempC``, ``Battery`` regardless of vendor.
    """
    ...

def _rename_by_contains(df: pd.DataFrame, mapping: dict[str, str]) -> pd.DataFrame:
    """Rename columns whose name contains one of the mapping keys. First match wins."""
    ...

def _mag_columns(columns) -> tuple[str, str, str] | None:
    """The frame's ``magX/magY/magZ`` columns under any capitalisation, or ``None``.

    Case- and space-insensitive, because the two exports of one AXY record
    spell the same channel differently: the cleaned file writes ``magX`` and
    the tag's own export writes ``MagX``. Only an exact triple counts — a file
    carrying two of the three axes is not a magnetometer source.
    """
    ...

def chunk_datetime(chunk: pd.DataFrame) -> pd.Series:
    """The parsed time axis of one raw chunk, without normalising anything else.

    :func:`parse_datetime` in one line, for callers that stream a raw CSV
    themselves and need the timestamps to join on but not the ``Date_str`` /
    ``Time_str`` columns it adds. Rows whose timestamp did not parse come back
    ``NaT`` rather than being dropped, so the returned series is positionally
    aligned with *chunk* and can index arrays built from it.
    """
    ...

def read_raw_mag_csv(source: str | Path, *, chunksize: int=RAW_MAG_CHUNK_ROWS) -> pd.DataFrame:
    """Stream *source* and return only its magnetometer triples, timestamped.

    Returns a frame with ``datetime``, ``magX``, ``magY``, ``magZ`` and nothing
    else, one row per sample that carries a finite triple. Rows without one are
    dropped as they are read, so a 779 MB, 10.8 M-row export whose magnetometer
    runs at 1 Hz inside a 25 Hz record costs one streaming pass and leaves
    ~433 k rows resident.

    Three columns of the file are read and the rest is never materialised. The
    time axis is parsed by :func:`chunk_datetime`, i.e. the same reconciliation
    the primary record gets, so a secondary whose vendor ``Timestamp`` column
    disagrees with its own ``Date`` + ``Time`` is resolved the same way as a
    primary that does.
    """
    ...

def _join_keys(when) -> np.ndarray:
    """Timestamps as integer milliseconds, the join's only comparison.

    Unparseable rows come back as :data:`_NAT` rather than being dropped, so
    the result stays positionally aligned with the frame it came from.
    """
    ...

def substitute_mag_on_timestamps(when, mag: 'np.ndarray | None', source: str | Path, *, match_min: float=RAW_MAG_MATCH_MIN, chunksize: int=RAW_MAG_CHUNK_ROWS, label: str='') -> tuple['np.ndarray', dict[str, Any]]:
    """Replace *mag* with the triples *source* carries at the same timestamps.

    The one implementation behind both the ingest path
    (:func:`join_raw_mag`, which feeds ``data/interim/<id>.parquet``) and the
    doctor's streamed read, so a heading measured by ``anchor doctor`` and a
    heading reconstructed by ``anchor track`` are measured on the same numbers.

    *when* is the primary record's time axis (anything :func:`pandas.to_datetime`
    accepts, one entry per row) and *mag* its current ``(n, 3)`` magnetometer,
    or ``None`` when the primary carries none. Matching is **exact** on
    timestamps rounded to :data:`RAW_MAG_JOIN_RESOLUTION`: the two files are two
    exports of one record, so the right answer is an exact match on every row
    and anything else is a clock offset to be diagnosed rather than absorbed by
    a nearest-neighbour tolerance.

    Rows of the primary that carried a finite triple are the *targets* — the
    1 Hz grid inside the 25 Hz record. When at least *match_min* of them find a
    partner the join is applied; below it :class:`ValueError` names the measured
    offset. Every other row comes back NaN, exactly as it went in: the point is
    to replace one channel, not to interpolate it onto a grid it was never
    sampled on.

    When the primary carries **no** magnetometer at all — the case
    ``raw_mag_csv`` exists for — it supplies no target grid, and the floor is
    scored the other way round: against the second file's own samples that fall
    inside the primary's span. Scoring against every parsed primary row instead
    would make the floor unreachable by construction, since a 1 Hz secondary
    inside a 25 Hz primary can never match more than 4 % of it. ``report`` names
    the denominator in ``target_basis``.

    Returns ``(mag, report)``. The report is JSON-serialisable and is what the
    interim sidecar and ``df.attrs["raw_mag_join"]`` carry.
    """
    ...

def join_raw_mag(df: pd.DataFrame, cfg) -> tuple[pd.DataFrame, dict[str, Any] | None]:
    """Apply ``cfg.raw_mag_csv`` to a parsed frame; a no-op when it is null.

    Replaces ``magX/magY/magZ`` in place and leaves every other column alone.
    Returns ``(df, report)`` with ``report`` ``None`` when the config declares
    no second source.
    """
    ...

def write_parquet(df: pd.DataFrame, path: str | Path) -> None:
    ...

def read_parquet(path: str | Path) -> pd.DataFrame:
    """Read a parquet written by :func:`write_parquet`.

    Parquet does not round-trip ``DataFrame.attrs``, so when the interim
    sidecar written by :func:`write_interim_sidecar` sits beside the file its
    ``analysis_window`` block is restored into ``df.attrs``. A frame read back
    from the cache therefore carries the same provenance as one returned
    straight from :func:`load_deployment`.
    """
    ...

def window_bound(value, timezone: str | None) -> pd.Timestamp:
    """Coerce one ``deploy_window`` endpoint to a naive wall-clock timestamp.

    An endpoint written with an explicit UTC offset is converted into
    ``timezone`` — the clock the raw CSV's Date/Time columns are written in —
    and then stripped of its offset, so the comparison against the naive
    ``datetime`` column is like-for-like. Converting an offset-aware endpoint
    without a declared ``timezone`` is an error rather than a guess.
    """
    ...

def apply_analysis_window(df: pd.DataFrame, cfg) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Restrict a parsed deployment frame to its declared analysis window.

    Two independent declarations, either or both of which may be null:

    ``cfg.clip``
        ``[start_sample, end_sample]``, a half-open **row** range as logged by
        the operator in ``AXY_DeploymentMetadata.xlsx``. Applied positionally
        to ``df``. Note that :func:`parse_datetime` has already dropped rows
        whose timestamp failed to parse, so the indices are exact only when the
        raw record parses cleanly; that is the case for every deployment in
        this repo, and any drop is reported in the returned ``n_rows_in``.
    ``cfg.deploy_window``
        ``[start, end]`` wall-clock bounds, applied inclusively against the
        ``datetime`` column and interpreted in ``cfg.timezone``.

    Both are applied when both are set — clip first, then the time window —
    which is also the cheapest way to detect that they disagree: the result is
    their intersection, and an empty intersection raises.

    One exception, and it is the reason ``timezone`` exists. When ``timezone``
    is null the window is compared against the raw file's own *unlabelled*
    clock, so "the window selects nothing" is at least as likely to mean "the
    two are written in different clocks" as "the record is wrong". When that
    happens and no ``clip`` was applied, the window is skipped with a loud
    warning and the full record is returned
    (``window["deploy_window_skipped"]`` records it) rather than raising,
    because a declared-but-unresolvable window must not take a deployment from
    loading to ``ValueError``. Two neighbouring cases stay hard errors: a
    disjoint window under a *declared* timezone, and an empty result when a
    clip was also applied, which is a clip/window contradiction no clock can
    explain away. A window that selects some but not all rows is always
    applied; under a null ``timezone`` the drop is warned about, naming the
    fraction.

    Returns ``(windowed_df, window)`` where ``window`` is a JSON-serialisable
    record of what was applied, suitable for ``df.attrs["analysis_window"]``
    and for the interim-cache sidecar.
    """
    ...

def check_sampling_rate(df: pd.DataFrame, cfg) -> float | None:
    """Compare the rate detected from the time axis with the configured one.

    Warns — loudly, naming both numbers — when they differ by more than
    :data:`FS_MISMATCH_TOL`, and returns the detected rate (``None`` when the
    time axis is too degenerate to detect one). The configured rate is
    deliberately **not** overridden: silently switching sampling rates would
    change every dead-reckoned metre without an audit trail. ``anchor doctor``
    promotes this warning to a FAIL.
    """
    ...

def check_time_axis_span(df: pd.DataFrame, cfg) -> float | None:
    """Refuse a time axis that cannot be reconciled with ``n_rows / fs``.

    A record of ``n`` rows sampled at ``fs`` accounts for ``n / fs`` seconds.
    When the parsed axis spans more than :data:`SPAN_ROWS_MAX_RATIO` times that
    (or less than its reciprocal), the axis is not a time base for this record
    and building an analysis grid on it is meaningless: gaps, resampling, event
    durations and every dead-reckoned metre inherit the error. ``APT_240702_S2``
    parsed from its transposed ``Timestamp`` column spanned 2140.75 h against
    26.4 h of samples — 81x — and still wrote an interim parquet.

    Deliberately loose, and deliberately not a sampling-rate check: a merely
    wrong ``sampling_rate_hz`` (50 configured over a 25 Hz record) is 2x and
    stays the warning :func:`check_sampling_rate` emits. Returns the observed
    span in seconds, or ``None`` when there is too little record to judge
    (fewer than two rows, no configured rate, or less than
    :data:`SPAN_CHECK_MIN_EXPECTED_S` of expected record).
    """
    ...

def interim_path_for(cfg) -> Path:
    """Canonical interim-parquet path for a deployment."""
    ...

def interim_sidecar_path(interim: str | Path) -> Path:
    """Sidecar JSON path for an interim parquet (``<id>.window.json``)."""
    ...

def ingest_fingerprint(cfg) -> str:
    """Short content hash of the config fields that determine the interim parquet.

    A pure function of *cfg* and :data:`INGEST_SCHEMA_VERSION`: it covers
    :data:`INGEST_FINGERPRINT_FIELDS` and nothing else, so a repointed
    calibration, a changed ``clip`` or a changed ``deploy_window`` all produce a
    different fingerprint, and the same config hashes identically whether or not
    the raw CSV happens to be on disk. The schema version is folded in so that a
    change to *this module* — a parser fix that makes the same config produce a
    different parquet — invalidates existing caches too.

    The raw file's own identity is deliberately *not* hashed here — see
    :func:`raw_csv_stat`, which :func:`interim_cache_is_valid` consults only
    when the file exists. Folding it in would make the fingerprint
    presence-dependent, and a tree that ships ``data/interim`` without
    ``data/raw`` would then invalidate its own cache and fall through to a
    re-ingest that cannot possibly succeed.

    :data:`INGEST_FINGERPRINT_OPTIONAL_FIELDS` are folded in only when set, so
    declaring a new optional field does not restate every existing config's
    hash. ``raw_mag_csv``, unlike ``calibration``, is additionally keyed by
    *content* — see :func:`raw_mag_stat`, which
    :func:`interim_cache_is_valid` compares.
    """
    ...

def raw_csv_stat(cfg) -> dict[str, int] | None:
    """Size and mtime of the deployment's raw CSV, or ``None`` when it is absent.

    Size is what :func:`interim_cache_is_valid` compares; ``raw_csv_mtime_ns``
    is recorded for diagnostics only. Copying or syncing ``data/raw`` rewrites
    every mtime without changing a byte, and treating that as a content change
    would force a full re-parse of the 605 MB APT record for nothing.
    """
    ...

def raw_mag_stat(cfg) -> dict[str, Any] | None:
    """Size and content hash of ``raw_mag_csv``, or ``None`` when unset/absent.

    Keyed by content, not by path. ``calibration`` is fingerprinted by path
    alone — docs/regen_2026-09.md §16 found that a re-fitted ``mag.json``
    written to the same path therefore served a stale parquet — and the second
    magnetometer source is exactly the kind of file that gets re-exported in
    place, so it carries a full SHA-256 as well as its size. The hash costs one
    streaming read (0.4 s warm, a few seconds cold on the 779 MB export it
    exists for) against the ~25 s that reading the same file for the join costs,
    so paying it on every cache check buys a correct answer cheaply.
    """
    ...

def write_interim_sidecar(cfg, interim: str | Path, window: dict[str, Any], raw_mag_join: dict[str, Any] | None=None) -> Path:
    """Record which config and analysis window produced an interim parquet."""
    ...

def read_interim_sidecar(interim: str | Path) -> dict[str, Any] | None:
    """Read an interim sidecar; ``None`` when absent or unreadable."""
    ...

def interim_cache_is_valid(cfg, interim: str | Path | None=None) -> bool:
    """True when ``data/interim/<id>.parquet`` was written from *this* config.

    Callers that short-circuit :func:`load_deployment` with a cached parquet
    must gate on this, otherwise a changed ``clip``, ``deploy_window`` or
    calibration path silently serves the old file: calibration is baked in at
    write time and the window is applied before it, so nothing downstream can
    tell a stale cache from a fresh one. A parquet with no sidecar predates
    this keying and is always treated as stale.

    Two checks, deliberately asymmetric. The config fingerprint is compared
    always. The raw CSV's size is compared only when the raw file is on disk:
    on a tree that carries ``data/interim`` but not ``data/raw`` a re-ingest is
    impossible, so declaring the cache stale would turn a working read into a
    ``FileNotFoundError`` from :func:`load_deployment`. There the cache is
    accepted on its config hash alone and the unverifiable raw stat is warned
    about. Only the recorded size is compared, never the mtime — see
    :func:`raw_csv_stat`.
    """
    ...

def _raw_mag_cache_is_valid(cfg, sidecar: dict[str, Any], path: Path) -> bool:
    """The ``raw_mag_csv`` half of :func:`interim_cache_is_valid`.

    Symmetric with the raw CSV's check in shape and asymmetric in strength: an
    absent second source is accepted on the config hash alone for the same
    reason (a re-ingest is impossible without the file), but a present one is
    compared by SHA-256 and not only by size, because the whole point of the
    field is that the magnetometer's bytes are the record.
    """
    ...

def load_deployment(cfg) -> pd.DataFrame:
    """Load + normalize a raw CSV per a DeploymentConfig.

    Chunked when the file is big. In order: parse, check the detected sampling
    rate against the configured one, check that the parsed time axis can be
    this record's at all (:func:`check_time_axis_span`, which raises), restrict
    to the declared analysis window (``clip`` / ``deploy_window``), take the
    magnetometer from ``raw_mag_csv`` when one is declared
    (:func:`join_raw_mag`), apply calibration, rotate the tag frame into the
    body frame, then write
    ``data/interim/<deployment_id>.parquet`` plus the ``<id>.window.json``
    sidecar that keys that cache to this config.

    The window is applied *before* calibration and before any downstream
    kinematics, so off-animal handling and post-recovery surface float never
    reach the event detector, the classifier or the particle filter. What was
    applied is recorded in ``df.attrs["analysis_window"]``.

    The mount rotation (``tag.axes_rotation_deg``, see
    :mod:`anchor.kinematics.mount`) goes *after* calibration, because a
    calibration is a per-axis property of the sensor and only means anything in
    the tag's own axes, and *before* anything kinematic, so pitch, roll and
    heading are body-frame quantities everywhere downstream. It is a no-op for
    the body-aligned default ``[0, 0, 0]``; when it is not, the applied
    ``[roll, pitch, yaw]`` is recorded in ``df.attrs["mount_rotation_deg"]``.
    """
    ...

def _load_chunked(path: Path, schema: Schema) -> pd.DataFrame:
    """Streamed read for large CSVs (>500 MB)."""
    ...
