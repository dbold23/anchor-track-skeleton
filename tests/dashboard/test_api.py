"""The dashboard's JSON API, against a live server on an ephemeral port."""
from __future__ import annotations
import json
import math
import time
from urllib.parse import quote
import pytest
from anchor.dashboard import data as D
from anchor.dashboard.jobs import JobError, build_command
from .conftest import DEP, fake_builder

def _q(s: str) -> str:
    ...

def test_static_pages_served(client):
    ...

def test_health_reports_root(client, repo):
    ...

def test_unknown_api_route_is_404(client):
    ...

def test_deployments_list_lint_qc_and_runs(client):
    ...

def test_deployment_detail(client):
    ...

def test_run_detail_failing_ledger(client):
    ...

def test_run_detail_passing_ledger_is_quotable(client):
    ...

def test_legacy_run_is_unverified_never_quotable(client):
    ...

def test_verdict_from_footer_without_ledger():
    ...

def test_track_payload(client):
    ...

def test_track_strict_json_has_no_nan(client):
    ...

def test_series_depth_and_states(client):
    ...

def test_series_missing_products_explained(client):
    ...

def test_site_geometry_and_claims(client):
    ...

def test_files_endpoint_serves_reports_sandboxed(client):
    ...

@pytest.mark.parametrize('config', ['../escape.yaml', 'outside.yaml', 'configs/../outside.yaml', 'configs/deployments/../../outside.yaml', 'configs/deployments/../../../escape.yaml', '/etc/passwd', 'configs/notes.txt', 'configs/deployments/missing.yaml', 'configs\\deployments\\DASH_T1.yaml'])
def test_deployment_rejects_paths_outside_configs(client, config):
    ...

@pytest.mark.parametrize('path', ['/files/pyproject.toml', '/files/reports/../outside.yaml', '/files/reports/%2e%2e/outside.yaml', f'/files/{FAIL_RUN}/{DEP}_track.parquet', '/files/data/interim/DASH_T1_qc.json'])
def test_files_endpoint_rejects_outside_or_unservable(client, path):
    ...

@pytest.mark.parametrize('run_dir,dep', [('../repo', DEP), ('configs', DEP), ('reports/legacy', '../x'), ('reports/legacy', 'NOPE')])
def test_run_endpoints_reject_bad_run_refs(client, run_dir, dep):
    ...

def test_job_rejects_config_traversal_and_unknown_input(serve_repo):
    ...

def test_host_and_origin_guards(client):
    ...

def test_build_command_track_whitelist(repo):
    ...

def _wait_done(client, timeout=20.0):
    ...

def test_job_streams_log_and_writes_run_log(serve_repo, repo):
    ...

def test_one_job_at_a_time_and_cancel(serve_repo):
    ...

def test_failing_job_reports_exit_code(serve_repo):
    ...

def test_job_preview_matches_build_command(client):
    ...

def test_job_preview_rejects_what_start_rejects(client):
    ...

def test_health_flags_demo_workspace(client, repo):
    ...

def test_demo_workspace_reads_through_the_normal_api(tmp_path):
    ...
