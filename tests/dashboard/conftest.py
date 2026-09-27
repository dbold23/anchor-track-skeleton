"""Fixtures for the dashboard API tests: a tiny synthetic repo + a live server."""
from __future__ import annotations
import json
import shutil
import sys
import threading
import urllib.error
import urllib.request
from pathlib import Path
import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import pytest
from anchor.dashboard.jobs import JobManager, build_command
from anchor.dashboard.server import make_server

def _gate(name: str, passed: bool) -> dict:
    ...

def _ledger(passed: bool) -> dict:
    ...

def _write_track(path: Path, footer: dict | None=None, n: int=200) -> None:
    ...

@pytest.fixture()
def repo(tmp_path: Path) -> Path:
    ...

def fake_builder(script: str):
    """A JobManager builder that runs ``python -c script`` but validates like the real one."""
    ...

class Client:

    def __init__(self, base: str):
        ...

    def request(self, path: str, method: str='GET', body: bytes | None=None, headers: dict | None=None):
        ...

    def get(self, path: str, **kw):
        ...

    def post(self, path: str, payload: dict, headers: dict | None=None):
        ...

@pytest.fixture()
def serve_repo(repo: Path):
    """Factory: start a server on an ephemeral port with an optional job builder."""
    ...

@pytest.fixture()
def client(serve_repo) -> Client:
    ...
