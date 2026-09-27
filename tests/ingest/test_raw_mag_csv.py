"""``raw_mag_csv``: the second CSV a deployment may take its magnetometer from.

Three deployments in this repository read a vendor ``*_CLEAN.csv`` whose
magnetometer has been wrapped into ``[0, 360)`` and is therefore destroyed
(``docs/regen_2026-09.md`` §16.13), while the primary file is still the right
accelerometer record. ``raw_mag_csv`` names the tag's own export and the
magnetometer triple alone is joined back on the sample timestamp.

The fixtures here are synthetic on purpose: every number the join is asserted
against is one this file wrote, so a failure is a defect in the join and not a
change in a 779 MB export. The one test that reads the shipped configs asserts
only what those configs declare.
"""
from __future__ import annotations
from pathlib import Path
import numpy as np
import pandas as pd
import pytest
from anchor.ingest import io
from anchor.ingest.config import DeploymentConfig, load_config
FS_HZ = 25
N_SECONDS = 40

def _primary(path: Path, *, wrap: bool=True, sep: str=',') -> np.ndarray:
    """Write a cleaned-export lookalike: 25 Hz accel, 1 Hz mag, mag folded mod 360.

    Returns the ``(N_SECONDS, 3)`` array of *unfolded* counts it folded, so a
    test can assert that the fold really is unrecoverable from this file.
    """
    ...

def _secondary(path: Path, truth: np.ndarray, *, offset_s: float=0.0, sep: str=';', drop: int=0, sub_ms: bool=False) -> None:
    """Write a vendor-export lookalike: ``Date`` + ``Time``, ``MagX/MagY/MagZ``.

    Capitalised differently from the primary, ``;``-delimited, and carrying the
    same 1 Hz grid inside a 25 Hz record — i.e. the shape of the file this
    field exists to read.
    """
    ...

def _cfg(primary: Path, secondary: Path | None, **extra) -> DeploymentConfig:
    ...

def test_the_reader_finds_a_differently_capitalised_mag_triple(tmp_path):
    """``MagX`` and ``magX`` are the same channel; the two exports disagree."""
    ...

def test_the_reader_refuses_a_file_with_no_magnetometer(tmp_path):
    ...

def test_the_reader_refuses_a_file_with_no_time_axis(tmp_path):
    ...

def test_the_join_replaces_the_wrapped_triple_and_leaves_every_other_row_nan(tmp_path):
    """The point of the field, in one assertion.

    The primary's magnetometer is the truth folded into ``[0, 360)`` and the
    fold is lossy — the folded value is not the truth on any row. After the
    join the 1 Hz rows carry the second file's signed counts exactly, and the
    24 rows between them are still NaN: the join replaces a channel, it does
    not interpolate one onto a grid it was never sampled on.
    """
    ...

def test_the_join_is_a_no_op_when_no_second_source_is_declared(tmp_path):
    ...

def test_a_clock_offset_fails_the_join_loudly_and_names_itself(tmp_path):
    """A 400 ms offset is a diagnosis, not a tolerance to absorb.

    Matching is exact, so a sub-sample offset takes the match fraction to zero
    rather than quietly pairing each row with its neighbour. The message has to
    carry the measured offset, because that number is what tells the operator
    which of the two exports has the wrong clock.
    """
    ...

def test_a_whole_second_offset_is_caught_by_the_floor_and_not_by_luck(tmp_path):
    """A 3 s offset still pairs 37 of 40 rows with the *wrong* sample.

    On a 1 Hz grid a whole-second offset is exactly the case an exact match
    cannot see: every row but the three at the boundary finds a partner, and
    the partner is three seconds of the animal's swimming away. 92.50% is what
    stops it, which is the reason :data:`io.RAW_MAG_MATCH_MIN` is 0.95 and not
    something comfortable.
    """
    ...

def test_a_partial_second_file_fails_the_floor_rather_than_leaving_a_hole(tmp_path):
    """Dropping a tenth of the second file's rows is below the 95% floor.

    The failure mode this guards is a magnetometer that is NaN over part of the
    record and finite over the rest, which no downstream check distinguishes
    from a sensor that stopped.
    """
    ...

def test_a_primary_with_no_magnetometer_at_all_is_joined_and_not_refused(tmp_path):
    """The case ``raw_mag_csv`` exists for: the primary carries no mag column.

    The floor then cannot be scored against the primary's magnetometer rows,
    because there are none. Scoring against every parsed primary row instead —
    which is what the branch did until 2026-09-06 — makes the floor unreachable
    by construction: a 1 Hz secondary inside a 25 Hz primary matches 4 % of it
    and is refused for being sampled at the rate it was sampled at. The
    denominator is the second file's own samples inside the primary's span.
    """
    ...

def test_a_primary_with_no_magnetometer_still_catches_a_clock_offset(tmp_path):
    """The rescored floor is a floor, not a licence.

    The guard it exists for — two exports whose clocks disagree — still fires
    when the primary carries no magnetometer, and still names the measured
    offset. Two things it does *not* see, both stated here rather than
    asserted: a second file covering only part of the primary's span (its own
    samples are the denominator, so 36 s of second file inside a 40 s primary
    score 100 %), and an offset that is a whole multiple of the primary's own
    sample period, which lands on a primary row by construction once every row
    is a candidate. Both are coverage questions rather than join questions.
    """
    ...

def test_the_join_matches_at_millisecond_resolution(tmp_path):
    """400 microseconds is not a clock offset; it is a rounding of the same stamp.

    :data:`io.RAW_MAG_JOIN_RESOLUTION` is the reason: both AXY exports stamp
    their 1 Hz rows at whole milliseconds, and comparing nanoseconds would turn
    an exact match into a total miss.
    """
    ...

def test_declaring_the_field_does_not_restate_an_existing_config_hash(tmp_path):
    """A null ``raw_mag_csv`` contributes nothing to the ingest fingerprint.

    :data:`io.INGEST_FINGERPRINT_OPTIONAL_FIELDS` exists for this: had the
    field been folded in as ``null``, adding it to the schema would have made
    every interim parquet in the tree stale at once, the flagship's included.
    """
    ...

def test_setting_the_field_changes_the_config_hash(tmp_path):
    ...

def test_the_cache_is_keyed_on_the_second_files_content_and_not_only_its_path(tmp_path, monkeypatch):
    """Rewriting the second file in place must invalidate the parquet.

    ``calibration`` is fingerprinted by path alone and §16 found that a re-fit
    written to the same path therefore served a stale record. The second
    magnetometer source does not repeat it: the sidecar carries a SHA-256, the
    primary CSV is untouched, and the cache still goes stale.
    """
    ...

def test_a_sidecar_written_before_this_field_existed_is_stale(tmp_path, monkeypatch):
    ...

def test_load_deployment_caches_the_joined_magnetometer_and_records_the_join(tmp_path, monkeypatch):
    ...

def test_the_doctors_streamed_read_takes_the_same_magnetometer_as_ingest(tmp_path, monkeypatch):
    """The one coherence the whole change turns on.

    ``anchor doctor`` falls back to a streamed read of the raw CSV whenever no
    valid interim parquet exists, which is the state all three affected
    deployments are in. Were that reader to ignore ``raw_mag_csv``, promoting a
    calibration fitted to the second file's signed counts would make the doctor
    apply it to the primary file's wrapped ones and report a heading failure
    that is an artefact of reading the wrong column.
    """
    ...

def test_the_shipped_configs_declare_what_the_2026_09_06_pass_decided():
    """LS_260415_S3 gains a second source; S2 gains a fit; S8 gains a null.

    Read as a table, this is the whole of §17's ingest pass:

    ==============  ==========================  ==========================
    deployment      raw_mag_csv                 calibration.mag
    ==============  ==========================  ==========================
    LS_260415_S3    the vendor export           null (the fit fails the floors)
    LS_250326_S2    none needed (signed counts) its own in-flight fit
    LS_250326_S8    none exists                 null (the record is destroyed)
    ==============  ==========================  ==========================
    """
    ...

def test_the_degenerate_2025_fit_is_still_refused_where_it_now_sits(tmp_path):
    """The file the two 2025 configs used to point at is still gated.

    Asserted here from the ingest side, on a synthetic deployment that names the
    file directly; ``tests/test_qc.py`` asserts the same refusal from the
    doctor's side. Neither reaches it through a shipped config any more.
    """
    ...
