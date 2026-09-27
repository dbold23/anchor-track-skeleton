"""End-to-end CLI smoke test on fixture data.

Writes a tiny deployment config pointing at the LS fixture slice and runs
``anchor run-all`` via the typer CliRunner. Confirms the four output files
exist.
"""
from __future__ import annotations
import yaml
from typer.testing import CliRunner
from anchor.cli import app

def test_run_all_on_ls_fixture(tmp_path, monkeypatch, ls_csv):
    ...

def test_run_all_with_hmm_on_ls_fixture(tmp_path, monkeypatch, ls_csv):
    ...

def _mini_configs(tmp_path):
    """A self-contained configs/ tree so `inherits:` resolves inside tmp_path."""
    ...

def test_config_lint_passes_on_a_clean_config(tmp_path):
    ...

def test_config_lint_flags_a_misspelt_key_with_a_hint(tmp_path):
    """A closed schema is only useful if the error says what was meant."""
    ...

def _clean_axy_csv(path, n: int=600, fs: float=25.0):
    """A synthetic 25 Hz AXY-5 record with a self-consistent time axis."""
    ...

def _doctor_config(tmp_path, csv, **deploy):
    ...

def test_doctor_exits_1_on_a_fail(tmp_path, monkeypatch, ls_csv):
    ...

def test_doctor_exits_0_when_nothing_fails(tmp_path, monkeypatch):
    ...

def test_doctor_writes_to_the_json_override(tmp_path, monkeypatch, ls_csv):
    ...

def test_run_all_stage_zero_reports_but_never_aborts(tmp_path, monkeypatch, ls_csv):
    """A FAILing doctor must not change `run-all`'s exit code or its outputs."""
    ...

def test_run_all_no_doctor_skips_stage_zero(tmp_path, monkeypatch, ls_csv):
    ...

def test_track_help_delegates_to_run_deployment():
    """`anchor track --help` is run_deployment's own argparse help, exit 0.

    The Typer command owns no flag list of its own — the roadmap's four-stage
    sequence ends in `anchor track`, and it has to be the same command the
    module-level entry point is, not a second copy that drifts from it.
    """
    ...

def test_track_carries_the_provenance_flags_of_regen_section_13():
    """`--no-bathymetry` and `--polygon-penalty-nats` are the two switches
    `docs/regen_2026-09.md` §13.6-13.7 asks the run's `config_hash` to see.
    Both override a `TrajectoryConfig` field, and both have to be reachable
    from the command the roadmap's four-stage sequence ends in — not only
    from `python -m anchor.trajectory.run_deployment`."""
    ...

def test_track_forwards_the_polygon_penalty_flag_verbatim(monkeypatch):
    """Typer owns no flag list of its own, so the value must arrive at
    `run_deployment.main` unparsed — `none` included, which is the literal
    that means the hard -inf polygon."""
    ...

def test_track_without_a_config_errors_instead_of_running_one_bat_ray():
    """A bare `anchor track` must not launch a run of a hardwired deployment.

    `--config` used to default to `configs/deployments/BR_260318_S3.yaml`, so
    `anchor track` with no arguments started a real full-length particle-filter
    run of one bat ray at Elkhorn — the same hardwired-single-animal default
    the endpoint flags dropped, and now ~74,000 steps rather than 7,200.
    """
    ...

def test_track_forwards_unknown_options_verbatim(monkeypatch):
    """Extra args reach run_deployment.main untouched, in order."""
    ...
