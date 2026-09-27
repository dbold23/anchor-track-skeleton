"""Shared pytest fixtures."""
from __future__ import annotations
from pathlib import Path
import numpy as np
import pytest

@pytest.fixture(scope='session')
def ls_csv() -> Path:
    ...

@pytest.fixture(scope='session')
def br_csv() -> Path:
    ...

@pytest.fixture(scope='session')
def ws_axy_csv() -> Path:
    ...

@pytest.fixture(scope='session')
def ws_cats_csv() -> Path:
    ...

@pytest.fixture(scope='session')
def calib_spin_csv() -> Path:
    ...

@pytest.fixture(scope='session')
def test_deploy_csv() -> Path:
    ...

@pytest.fixture(autouse=True)
def _seed():
    ...
