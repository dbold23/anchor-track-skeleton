"""HTTP server for ``anchor dashboard``: static front end + a small JSON API.

Standard library only (:class:`http.server.ThreadingHTTPServer`). It binds to
127.0.0.1 and refuses requests whose ``Host`` header is not a loopback name
(DNS-rebinding guard); state-changing endpoints additionally require a JSON
body and a same-origin ``Origin`` when the browser sends one.

API (all JSON)::

    GET  /api/health
    GET  /api/deployments
    GET  /api/deployment?config=configs/deployments/<file>.yaml
    GET  /api/runs
    GET  /api/run?dir=<reports/...>&id=<deployment id>
    GET  /api/track?dir=...&id=...[&max_points=N]
    GET  /api/series?id=<deployment id>
    GET  /api/site?name=<site>
    GET  /api/claims
    GET  /api/jobs                      current job + history
    GET  /api/jobs/log?since=N[&job=ID]
    GET  /api/jobs/preview?action=...&config=...&options={json}
                                        the shell command a job would run
    POST /api/jobs                      {"action", "config", "options"}
    POST /api/jobs/cancel
    GET  /files/<path>                  a report/figure under reports/ or data/processed/
"""
from __future__ import annotations
import json
import mimetypes
import os
import threading
import traceback
import webbrowser
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Callable, Optional
from urllib.parse import parse_qs, unquote, urlsplit
from anchor.dashboard import data as D
from anchor.dashboard.jobs import JobBusy, JobError, JobManager, build_command
DEFAULT_PORT = 8750

class DashboardServer(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True

    def __init__(self, root: Path, port: int, jobs: Optional[JobManager]=None):
        ...

    @property
    def port(self) -> int:
        ...

class Handler(BaseHTTPRequestHandler):
    server: DashboardServer

    def log_message(self, format: str, *args: Any) -> None:
        ...

    def _send(self, status: int, body: bytes, ctype: str, extra: Optional[dict[str, str]]=None) -> None:
        ...

    def _json(self, payload: Any, status: int=200) -> None:
        ...

    def _error(self, status: int, message: str) -> None:
        ...

    def _host_ok(self) -> bool:
        ...

    def _origin_ok(self) -> bool:
        ...

    def _query(self) -> dict[str, str]:
        ...

    def _body(self) -> dict:
        ...

    def _dispatch(self, routes: dict[str, Callable[[], None]]) -> None:
        ...

    def do_GET(self) -> None:
        ...

    def do_POST(self) -> None:
        ...

    def _serve_static(self, path: str) -> None:
        ...

    def _serve_file(self, rel_path: str) -> None:
        ...

def preview_command(root: Path, q: dict[str, str]) -> dict:
    """The terminal equivalent of a job, validated exactly as a real start is.

    ``python -u -m anchor.cli`` is shown as ``anchor``; a track job's default
    output label is stamped at start time, so it is shown as a placeholder.
    """
    ...

def make_server(root: Path | str='.', port: int=DEFAULT_PORT, jobs: Optional[JobManager]=None) -> DashboardServer:
    """A bound (not yet serving) dashboard server on 127.0.0.1:``port``."""
    ...

def _quietly(fn, *args) -> None:
    ...

def serve(root: Path | str='.', port: int=DEFAULT_PORT, open_browser: bool=True) -> None:
    """Run the dashboard until interrupted (the ``anchor dashboard`` command)."""
    ...
