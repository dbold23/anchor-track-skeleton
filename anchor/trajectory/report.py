"""Self-contained HTML report builder for an end-to-end deployment run.

The report is one ``.html`` file with every figure embedded as base64 PNG and
the animation embedded as a base64 ``<video>`` (h264 MP4). The Folium track
map is referenced as a sibling iframe to keep the report file size sane.

No Jinja, no external CSS — minimal f-string template so the report can be
opened anywhere with no asset path resolution.
"""
from __future__ import annotations
import base64
import io
import math
from dataclasses import dataclass, field
from html import escape
from pathlib import Path
from typing import Optional
import matplotlib.pyplot as plt

@dataclass
class Section:
    title: str
    body_html: str
    fig_b64: Optional[str] = None

def fig_to_png_b64(fig: plt.Figure, dpi: int=110) -> str:
    """Serialize a matplotlib Figure to a base64 PNG suitable for inline <img>."""
    ...

def file_to_b64(path: Path) -> str:
    ...

def qc_section(findings, *, title: str='0. Data health (anchor doctor)') -> Section:
    """Render ``anchor.qc`` findings as a report section.

    Duck-typed on ``.check`` / ``.level`` / ``.message`` so ``report`` keeps no
    import dependency on ``anchor.qc`` (and so a JSON-round-tripped finding
    renders identically). Pass ``QCReport.findings`` straight in.
    """
    ...

def end_anchor_block(meta: dict | None) -> str:
    """The end-anchor section: which model, why, where, and at what σ.

    ``meta`` is ``run_deployment._end_anchor_metadata``'s dict, which is also
    what the parquet footer and the ledger card's ``diagnostics.end_anchor``
    carry, so the three agree by construction. Returns an empty string when
    there is no end anchor, so a caller can concatenate it unconditionally.

    The σ decomposition is printed for the grounded model because the whole
    claim is arithmetic on two stated numbers — a recovery fix's own σ and a
    bottom-creep allowance — and a reader who disagrees with the allowance can
    see exactly what it contributed.
    """
    ...

def regime_table(detachment: dict | None, *, base_hz: float=1.0) -> str:
    """The record's regime table, as HTML.

    ``detachment`` is :meth:`DetachmentResult.to_dict` — which rule cut the
    track, both candidate moments, and one row per regime. Returns an empty
    string when there is nothing to show, so a caller can concatenate it
    unconditionally.

    The table exists because the shipped answer to "what span did the filter
    reconstruct?" was a single number, and on ``BR_260318_S3`` that number
    (16.942 h) covered 7.617 h of a tag lying on a slough bottom
    (``docs/regen_2026-09.md`` §17.4). A row is marked as the cut so a reader
    can see which regime the reconstruction actually ends in.
    """
    ...

def degeneracy_banner(degeneracy: dict | None) -> str:
    """The G-degeneracy verdict, as a banner for the top of a section body.

    ``degeneracy`` is what
    :func:`anchor.trajectory.particle_filter.evaluate_degeneracy` returns.
    A pass renders one green line; a failure names every floor that failed,
    with the value that failed it and the step it failed at, and states that
    the run's credible intervals are suppressed. Returns ``""`` when there is
    no degeneracy record at all (an older run, or a caller that does not
    collect one), so the caller can concatenate it unconditionally.
    """
    ...

def gate_banner(gate: dict | None) -> str:
    """A banner for any scored gate, from its :meth:`GateResult.to_dict` payload.

    :func:`degeneracy_banner` renders G-degeneracy from the filter's own
    diagnostics dict; this renders any *gate* dict off the score card, which is
    how **G-heading** reaches the report. Returns ``""`` for ``None`` so the
    caller can concatenate it unconditionally, and it deliberately prints on a
    pass as well as on a failure: a reader who cannot see that the heading was
    checked has no way to tell a checked heading from an unchecked one.
    """
    ...

def suppressed(value_html: str, *, is_suppressed: bool) -> str:
    """Mark one credible-interval figure as suppressed, keeping it legible."""
    ...

def _fmt(value) -> str:
    """A number for a card table cell; anything else escaped as-is.

    ``None`` is rendered "not finite" rather than "None". Inside a score card
    a null number is never an absent one — the card's JSON coercion maps a
    non-finite float to null and leaves absent keys absent — so ``var(log w)``
    peaking at ``inf`` arrives here as ``None`` and "None" would read as
    "unmeasured", which is the opposite of what happened.
    """
    ...

def score_card_panel(card: dict | None, *, is_suppressed: bool=False) -> str:
    """Render a :class:`~anchor.validation.ledger.ScoreCard` for the report.

    ``card`` is the card's ``to_dict()`` — the same payload written to
    ``<id>_ledger.json``. Duck-typed on that JSON layout rather than on the
    class, so ``report`` keeps no import dependency on the ledger and a card
    read back from disk renders identically.

    The panel does **not** restate the gate verdict: :func:`degeneracy_banner`
    is the one banner in the report and this sits directly beneath it. What
    the panel adds is the record needed to check that verdict — provenance,
    every §3.7 floor with the value measured against it, the reported scores
    (§3.7 has the ledger print the failed gate's *name* in place of a
    suppressed number, which is what ``reported_scores`` already does), and
    the along/cross decomposition. Channel σ figures are credible intervals
    like any other and carry the same :func:`suppressed` mark.

    Returns ``""`` for ``None``, so a caller with no card concatenates it
    unconditionally.
    """
    ...

def latent_grid_unscored_bias(grid: dict | None) -> dict:
    """How far the grid's log-marginal ranking is contaminated by lost steps.

    An *unscored* step contributes exactly zero to that node's log marginal
    rather than the negative number an honest likelihood would have supplied
    (see ``animate_filter.run_filter_with_snapshots``), so the bias is signed:
    it favours whichever node leans on the fallback hardest. It cannot be
    waved away as "conservative". On the flagship the node that took 100% of
    the posterior had skipped 25 989 of 60 992 steps while four nodes sharing
    its ``k_speed`` skipped none, and the ranking is only defensible there
    because the MAP node also wins per *scored* step.

    Since the polygon rejects with a finite ``polygon_penalty_nats`` (§12.4's
    fix), a cloud driven out of the water is *charged* rather than excused, so
    on a default run these counts are zero and ``penalised_total`` carries the
    steps instead. What is left here is the hard mode
    (``polygon_penalty_nats=None``) and genuine numerical underflow — the
    cases where the marginal still cannot score a step at all.

    Returns the grid total, the MAP node's count, the smallest count on the
    grid, ``map_is_favoured`` — True exactly when the MAP node skipped more
    steps than some other node did, i.e. when the comparison that picked it
    was not made on common data — and, beside them, the penalised counts that
    are *in* the marginals.
    """
    ...

def _as_list(values) -> list:
    """``list(values)``, tolerating ``None`` and a NumPy array alike.

    ``grid`` arrives as NumPy arrays from the filter and as plain lists after
    a JSON round trip, and ``x or []`` raises on the former.
    """
    ...

def _anchor_note(grid: dict, nodes: list, anchored: bool) -> str:
    """What the node weights condition on — never left to the reader to guess.

    The forward filter cannot see the end anchor, so the grid driver can only
    produce ``p(node | y)``. Every path the smoother draws inside a node *is*
    conditioned on the anchor, so pairing those paths with forward weights
    would not sample the mixture at all. The fix folds
    ``log p(anchor | y, node)`` in before the node draw; this note says whether
    it happened and how much it moved, because on a real deployment it is
    hundreds of nats and reorders the grid.
    """
    ...

def latent_grid_table(grid: dict | None, *, is_suppressed: bool=False, max_rows: int=40) -> str:
    """Render the outer latent grid's posterior (design §3.5).

    ``grid`` is ``filter_state["latent_grid"]``. Returns ``""`` when the run
    was in particle mode, so a caller concatenates it unconditionally.

    Three things, in the order a reader needs them: the two axis marginals
    (which is where "did ``k_speed`` land near 1.0 or on the floor?" is
    answered), then the node table with each node's log marginal likelihood and
    posterior weight, then the per-node §3.7 verdict. The posterior mean ± sd
    of each latent is a run-produced credible interval like any other and
    carries the same :func:`suppressed` mark the banner promises — the
    marginal likelihoods are estimated by the same particle clouds the gate
    scored, so a failed gate is a caveat on them too.
    """
    ...

def build_html(*, title: str, subtitle: str, param_table: list[tuple[str, str]], sections: list[Section], animation_mp4_path: Optional[Path]=None, folium_map_path: Optional[Path]=None, trailing_sections: Optional[list[Section]]=None, output_path: Path) -> Path:
    """Compose the report HTML and write it to ``output_path``.

    ``param_table`` is a list of (label, value) pairs displayed at the top.
    ``sections`` are rendered in order. Pass ``animation_mp4_path`` and
    ``folium_map_path`` (sibling files in the report's directory) to embed
    them as a <video> and an <iframe> respectively.
    """
    ...
