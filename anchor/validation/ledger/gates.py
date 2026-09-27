"""Section 3.7's gate table, encoded as data, plus the standing G-degeneracy check.

"A pre-registration whose thresholds are deferred is not a pre-registration."
Every row of the table in section 3.7 of
``docs/design/leopard_shark_digital_twin.md`` is transcribed here verbatim, so
the numbers a run is judged against live in code that CI executes rather than
in prose nobody diffs. :data:`GATE_TABLE_VERSION` is bumped by any amendment,
and the design document requires that amendment to be dated and reasoned in
the document itself.

Two rows are evaluated here, and they are the two **standing** gates.
**G-degeneracy** is computed from filter diagnostics on every run, needs no
external data, and its failure suppresses every calibration number in that run.
**G-heading** (amendment 2026-09-05) is computed from ``anchor doctor``'s
heading family on every run and asks whether the magnetometer chain the run is
using is a measurement of azimuth at all; its failure suppresses every
positional number. The other nine are phase gates scored by their own
experiments; they are carried as data so the score card can print the table it
is being judged against.

The suppression consequence belongs to the row, not to the idea of a gate:
:attr:`GateSpec.suppresses_calibration` is true only for G-degeneracy and for
G-field, whose clause (i) withdraws every published interval. G-phantom is
"diagnostic only, no programme stop rule" and a failed G-phantom therefore
leaves every number on the card printing.
"""
from __future__ import annotations
from dataclasses import asdict, dataclass, field
from typing import Mapping, Sequence
import numpy as np
__all__ = ['DEGENERACY_FLOORS', 'DEGENERACY_KEYS', 'GATE_TABLE', 'GATE_TABLE_VERSION', 'GateCheck', 'GateResult', 'GateSpec', 'HEADING_CHECK_PREFIX', 'evaluate_degeneracy_gate', 'evaluate_heading_gate', 'gate_by_name', 'gate_suppressed_numbers', 'gate_suppressed_score_prefixes', 'gate_suppresses_calibration']

@dataclass(frozen=True)
class GateSpec:
    """One row of section 3.7: what is measured, the fixed floor, the rule."""
    name: str
    phase: str
    metric: str
    floor: str
    rule: str
    suppresses_calibration: bool = False

    def to_dict(self) -> dict:
        ...

def gate_by_name(name: str) -> GateSpec:
    ...

def gate_suppressed_numbers(name: str) -> str:
    """What failing the gate called ``name`` withdraws, for the banner."""
    ...

def gate_suppressed_score_prefixes(name: str) -> tuple[str, ...]:
    """Score-name prefixes that failing the gate called ``name`` withdraws.

    A gate the table does not name withdraws nothing, for the reason
    :func:`gate_suppresses_calibration` gives.
    """
    ...

def gate_suppresses_calibration(name: str) -> bool:
    """Whether failing the gate called ``name`` withdraws calibration numbers.

    A gate the table does not name suppresses nothing: an ad-hoc check invented
    by a caller cannot acquire a stop rule the pre-registration never granted
    it.
    """
    ...

@dataclass(frozen=True)
class GateCheck:
    """One floor within a gate, and whether the run cleared it."""
    key: str
    value: float
    floor: float
    comparison: str
    passed: bool

    def to_dict(self) -> dict:
        ...

@dataclass(frozen=True)
class GateResult:
    """The verdict for one gate, with every constituent check kept."""
    gate: str
    passed: bool
    suppresses_calibration: bool | None = None

    @property
    def failed_checks(self) -> tuple[GateCheck, ...]:
        ...

    @property
    def suppresses(self) -> bool:
        """Whether failing *this* gate withdraws the run's calibration numbers."""
        ...

    @property
    def banner(self) -> str:
        """The one line the ledger prints above the run's numbers.

        The suppression clause is appended only for a gate whose own section
        3.7 row carries that consequence. A failed G-phantom prints
        ``G-phantom FAIL (...)`` and nothing more, because its row reads
        "diagnostic only, no programme stop rule".
        """
        ...

    def to_dict(self) -> dict:
        ...

def evaluate_degeneracy_gate(degeneracy: Mapping[str, float], floors: Mapping[str, float] | None=None) -> GateResult:
    """Score the standing G-degeneracy gate from the filter's diagnostics.

    Parameters
    ----------
    degeneracy
        Exactly the keys in :data:`DEGENERACY_KEYS`:
        ``n_founders_final`` (surviving distinct time-zero ancestors),
        ``min_unique_ancestor_fraction`` (minimum over ``t`` of the fraction of
        distinct ancestors), ``max_norm_weight`` (largest normalised weight
        seen), ``ess_min`` (minimum effective sample size, **absolute**, not a
        fraction), ``var_log_w`` (variance of the log incremental weights) and
        ``n_particles``.
    floors
        Override for :data:`DEGENERACY_FLOORS`; the shipped values are the
        section 3.7 numbers and changing them is an amendment, not a knob.

    Raises
    ------
    ValueError
        If a key is missing or ``n_particles`` is not a positive integer. A
        non-finite diagnostic is not an error — it fails its check, because
        ``nan`` means the filter could not measure the thing the gate is about.
    """
    ...

def _check(key: str, value, floor: float, comparison: str, detail: str) -> GateCheck:
    ...

def _finding_field(finding, name: str, default=None):
    """``finding[name]`` for a dict, ``finding.name`` for a Finding, else default.

    Duck-typed on purpose: ``anchor.trajectory.run_deployment`` hands this
    module either ``anchor.qc.Finding`` objects (fresh doctor run) or the plain
    dicts read back from a cached ``data/interim/<id>_qc.json``, and the two
    must score identically.
    """
    ...

def evaluate_heading_gate(findings: Sequence) -> GateResult | None:
    """Score the standing G-heading gate from ``anchor doctor``'s heading family.

    Returns ``None`` when the findings carry no ``heading.*`` check at all —
    an older cached QC report, or a doctor run with ``heading=False``. That is
    deliberately not a failure: a gate scored from an input that does not exist
    would be a verdict about the report's age, not about the deployment.

    The floors are **not** duplicated here. Each heading finding carries its own
    ``value["gates"]`` list of ``{key, value, floor, comparison}`` entries,
    written by :mod:`anchor.qc` from the constants documented there, so the
    ledger's floors and the doctor's constants are the same numbers by
    construction and cannot drift apart. A heading finding at level ``FAIL``
    that carries no numeric entry still fails the gate, through a synthetic
    check named after it: a family that could not run is not a family that
    passed.
    """
    ...

def evaluate_gates(degeneracy: Mapping[str, float] | None=None, extra: Sequence[GateResult]=()) -> tuple[GateResult, ...]:
    """G-degeneracy (when diagnostics are available) plus any externally scored gates."""
    ...
