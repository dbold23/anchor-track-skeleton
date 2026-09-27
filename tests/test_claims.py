"""The paper-claims registry stays parseable, complete, and runnable.

``docs/claims.yaml`` is only useful if every entry keeps its shape and every
``computed_by`` still points at something that exists, so these tests guard the
registry itself rather than any single number in it.
"""
from __future__ import annotations
import importlib.util
import json
import re
import sys
from pathlib import Path
import pytest

def _load_module():
    ...

@pytest.fixture(scope='module')
def claims():
    ...

def _resolve_dotted(dotted: str) -> int:
    """How many components of a dotted path resolve to real files/dirs."""
    ...

def test_registry_parses_and_is_nonempty(claims):
    ...

def test_every_entry_has_the_required_keys(claims):
    ...

def test_every_claim_line_is_inside_its_document(claims):
    ...

def test_computed_by_targets_exist(claims):
    """Every file or module a `computed_by` names is present in the tree."""
    ...

def test_check_specs_reference_real_methods_and_inputs(claims):
    ...

def test_generated_markers_are_present_in_the_drafts(claims):
    """A claim declaring a marker must actually own that token in its document."""
    ...

def test_marker_claims_quote_the_regenerated_number_in_their_own_text(claims):
    """The registry's own quote must not drift away from the number it records.

    ``text`` is quoted verbatim from the document, so for a generated claim it
    carries the same marker token; if regeneration rewrote only ``value`` the
    registry would slowly start misquoting the manuscript it exists to police.
    """
    ...

def test_drafts_no_longer_promise_bit_identical_reproduction():
    ...

def test_check_run_executes_and_reports(capsys):
    """`--check` runs end to end and returns a real exit status."""
    ...

def test_contradicted_claims_make_check_fail(tmp_path, capsys):
    """A registry holding a contradicted claim must exit non-zero."""
    ...

def test_malformed_registry_is_rejected(tmp_path, capsys):
    ...

def test_pytest_count_refuses_a_partial_collection(tmp_path, monkeypatch):
    """A failed collection must raise, not write an undercount into the paper.

    Collection errors are the realistic failure (an optional dependency missing
    in CI, a half-saved module): pytest still reports the tests it did find and
    exits non-zero. That number is the one the script writes into both drafts,
    so it has to refuse rather than guess.
    """
    ...

def test_pytest_count_is_the_whole_suite_on_a_healthy_tree(tmp_path, monkeypatch):
    """The happy path still counts, so the guard above is not just refusing."""
    ...

def test_every_numeral_in_the_drafts_is_registered_or_declared_a_label():
    """The registry's completeness claim is checked, not asserted.

    Every numeral in the swept drafts must be either recorded by a claim on its
    line or blanked by a declared label rule. A new number in the manuscript
    fails here until someone writes down what produces it.
    """
    ...

def test_every_sweep_ignore_rule_compiles_and_says_why():
    ...

def test_covers_must_be_numbers(tmp_path):
    """`covers` feeds the sweep, so a stray string has to be rejected loudly."""
    ...

def test_bathymetry_note_is_scoped_per_condition(claims):
    """The note a co-author reads before cutting the headline must be scoped.

    The simulation it cites is a variant x perturbation-condition table, not a
    single number, and which configuration wins depends on the condition. A
    note written from the noise-free baseline alone would tell a co-author to
    delete a headline the same simulation supports, so both relationships the
    note asserts are re-read from the file here rather than quoted into prose.
    """
    ...
