"""Smoke tests for the HTML report builder.

Don't run the full deployment pipeline — that takes minutes and depends on
real data. Just verify the HTML composer assembles a valid file with all
the expected anchors (param table, sections, optional video/iframe).
"""
from __future__ import annotations
from pathlib import Path
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from anchor.trajectory.report import Section, build_html, fig_to_png_b64, qc_section

def _dummy_fig() -> plt.Figure:
    ...

def test_build_html_minimal(tmp_path: Path):
    ...

def test_build_html_with_video_and_map(tmp_path: Path):
    ...

def test_section_without_figure_renders(tmp_path: Path):
    ...

def test_qc_section_renders_into_the_report_html(tmp_path: Path):
    """Findings → section → written HTML, the whole path run_deployment uses."""
    ...

def test_qc_section_has_no_failure_banner_when_nothing_fails():
    ...

def test_qc_section_accepts_finding_objects(tmp_path: Path):
    """run_deployment passes ``QCReport.findings`` straight in when no cached
    JSON exists, so the duck-typing must cover the dataclass too."""
    ...

def _card(*, n_founders=1, run_id='BR_260318_S3', channel=None, source_config_hash='feedfacecafe0002'):
    ...

def test_score_card_panel_is_empty_without_a_card():
    ...

def test_score_card_panel_shows_every_floor_with_the_value_measured_against_it():
    ...

def test_score_card_panel_does_not_restate_the_verdict():
    """One banner per report. The panel evidences the verdict rendered above
    it by ``degeneracy_banner``; a second banner would be a second claim."""
    ...

def test_score_card_panel_carries_the_provenance_a_reader_needs():
    ...

def test_score_card_panel_distinguishes_the_two_provenance_hashes():
    """Card 1.1.0 carries both hashes and one unlabelled ``config`` cannot
    say which is which: the effective configuration identifies the *run*
    (CLI overrides resolved) and the source hash the deployment *file*, so
    "same file, different flag" is only readable when both are labelled."""
    ...

def test_score_card_panel_omits_the_deployment_hash_on_a_1_0_0_card():
    """A 1.0.0 card has no ``source_config_hash``; the panel drops that part
    rather than printing an empty ``<code>``, and the effective hash keeps
    its label so the two renderings do not read as the same field."""
    ...

def test_score_card_panel_prints_the_gate_name_in_place_of_a_suppressed_score():
    """§3.7: "the ledger prints the failed gate's name in place of the
    number". ``reported_scores`` already does it; the panel must render that
    field rather than the raw ``scores``."""
    ...

def test_score_card_panel_marks_channel_sigmas_when_the_gate_fails():
    ...

def test_score_card_panel_leaves_channel_sigmas_plain_when_the_gate_passes():
    ...

def test_score_card_panel_does_not_print_a_step_count_in_scientific_notation():
    """A 60,992-step run is the flagship. ``.4g`` would render it 6.099e+04."""
    ...

def test_score_card_panel_escapes_text_from_the_card():
    ...

def test_score_card_panel_says_not_finite_where_the_card_holds_a_null():
    """``var(log w)`` peaked at ``inf`` on the flagship run. JSON has no inf,
    so the card carries null — and "None" in the Measured column would read as
    "we did not measure it", which is the opposite of what happened."""
    ...
