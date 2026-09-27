"""The versioned score card: numbers, gates, provenance, one JSON file.

Section 1 of the design document asks for "a ledger [that] prints the lowest
tier feeding every reported interval". This is the container for that: one
immutable record per scored run, carrying

- a **schema version** (:data:`SCORECARD_VERSION`), so a card written today is
  still readable when the score set changes;
- the **scores** as a flat ``{name: float}`` mapping, normally the output of
  :func:`anchor.validation.ledger.scores.score_paths`;
- the **gate table** of section 3.7 as data, and the :class:`GateResult` for
  every gate actually scored;
- a **provenance stamp** — git SHA and dirtiness, hashes of the effective
  configuration and of the file it was resolved from, the caller's timestamp
  and the installed package version.

The suppression rule is enforced by the card, not by its readers:
:meth:`ScoreCard.report` returns the failed gate's *name* in place of any
calibration number, which is exactly what the G-degeneracy row prescribes.
It is scoped to the rows that prescribe it — G-degeneracy, and G-field's
clause (i) — because section 3.7 gives every other row its own consequence and
G-phantom's is explicitly "diagnostic only, no programme stop rule". A failed
gate that carries no suppression rule appears in :attr:`ScoreCard.failed_gates`
and in the banner, and changes no number.
"""
from __future__ import annotations
import hashlib
import json
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping, Sequence
from anchor.validation.ledger.gates import GATE_TABLE, GATE_TABLE_VERSION, GateResult, GateSpec, gate_suppressed_score_prefixes
__all__ = ['SCORECARD_VERSION', 'Provenance', 'ScoreCard', 'config_hash', 'git_sha', 'jsonable', 'package_version', 'write_json']

def config_hash(config: Any, length: int=16) -> str:
    """Stable short SHA-256 of a configuration object.

    The object is canonicalised as JSON with sorted keys and a ``str`` fallback
    for anything not natively serialisable, so two runs with the same effective
    configuration hash identically regardless of dict ordering. Matches the
    16-hex convention already used by ``anchor.ingest.io``.
    """
    ...

def git_sha(repo_root: Path | str | None=None) -> tuple[str, bool]:
    """``(sha, dirty)`` for the working tree, or ``("unknown", False)``.

    Read-only: ``rev-parse`` and ``status --porcelain``, nothing else. Returns
    the sentinel rather than raising when git is absent, when the tree is not a
    repository, or when the call times out — a score card must still be
    writable from an installed wheel.
    """
    ...

def package_version() -> str:
    """Installed ``anchor-track`` version, or ``"unknown"``."""
    ...

@dataclass(frozen=True)
class Provenance:
    """Where a number came from. Everything here is cheap and always available."""
    timestamp: str
    git_dirty: bool = False

    @classmethod
    def stamp(cls, timestamp: str, config: Any=None, repo_root: Path | str | None=None, source_config: Any=None, **extra: Any) -> 'Provenance':
        """Build a stamp. ``timestamp`` is passed in so cards are reproducible.

        Nothing here reads the clock: the caller owns the time, which is what
        makes a card byte-reproducible from the same run.

        ``config`` is the effective configuration and ``source_config``, when a
        caller has one, the file it was resolved from. Recording only the first
        loses which deployment YAML a card belongs to; recording only the
        second gives every point of a one-flag sweep the same hash, which is
        what ``docs/regen_2026-09.md`` §11 and §12 hit.
        """
        ...

    def to_dict(self) -> dict:
        """JSON-ready mapping. ``extra`` is coerced like every other payload.

        ``extra`` is where a caller stamps run metadata — the variogram stride,
        a member count, a thinning factor — and those arrive as numpy scalars
        far more often than as Python ints. Coercing here rather than in
        :meth:`ScoreCard.to_dict` keeps a stamp serialisable wherever it is
        used, and keeps the JSON strict: a non-finite float becomes ``null``,
        never a bare ``NaN`` literal.
        """
        ...

@dataclass(frozen=True)
class ScoreCard:
    """One scored run: numbers, gates, provenance, and the rule joining them."""
    run_id: str
    provenance: Provenance

    @property
    def failed_gates(self) -> tuple[str, ...]:
        """Every gate that failed, whatever its consequence."""
        ...

    @property
    def suppressing_gates(self) -> tuple[str, ...]:
        """The failed gates whose own section 3.7 row withdraws the numbers.

        A subset of :attr:`failed_gates`. G-degeneracy is in it; G-phantom,
        whose row reads "diagnostic only, no programme stop rule", never is.
        """
        ...

    @property
    def suppressed(self) -> bool:
        """True when a gate that *carries* a suppression rule failed.

        Not the same as "a gate failed": section 3.7 gives each row its own
        consequence, and only G-degeneracy and G-field clause (i) withdraw
        calibration numbers.
        """
        ...

    @property
    def banner(self) -> str:
        """The line printed above the run.

        Passing runs get one ``PASS`` line per gate; a failing run gets the
        failed gate's name, which is what the reader sees instead of a number.
        """
        ...

    def report(self, name: str) -> Any:
        """The value of score ``name``, or the failed gate's name if suppressed.

        Section 3.7, G-degeneracy: "Any failure suppresses every calibration
        number in that run; the ledger prints the failed gate's name in place
        of the number." G-heading's row says the same of every *positional*
        number, which is a different set of score names — so the prefixes are
        read off the failing rows rather than from one global tuple, and the
        gate named in place of the number is the one whose own rule covers it.
        """
        ...

    def reported_scores(self) -> dict[str, Any]:
        """Every score put through :meth:`report`."""
        ...

    def to_dict(self) -> dict:
        """The whole card as JSON types.

        The coercion is applied to the *entire* payload, not field by field:
        numpy scalars and non-finite floats reach the card through the scores,
        the diagnostics, a gate check's measured value and the provenance
        stamp's ``extra`` alike, and a writer that coerces only some of those
        fails at ``write_json`` time — after the run it exists to record.
        """
        ...

    def to_json(self, indent: int=2) -> str:
        ...

    def write_json(self, path: Path | str, indent: int=2) -> Path:
        ...

def write_json(card: ScoreCard, path: Path | str, indent: int=2) -> Path:
    """Write ``card`` to ``path`` atomically (temp file then replace)."""
    ...

def jsonable(value: Any) -> Any:
    """Coerce numpy scalars/arrays, paths and nested containers into JSON types.

    Public because it is the ledger's single definition of what "strict JSON"
    means here -- non-finite floats become ``null``, numpy scalars become
    Python scalars, ``Path`` becomes ``str`` -- and any writer that stamps a
    sidecar next to a score card has to agree with the card, not reimplement it.
    """
    ...
