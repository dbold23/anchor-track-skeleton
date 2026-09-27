"""Local web dashboard for anchor (``anchor dashboard``).

Stdlib-only server (:mod:`http.server`) plus a static single-page front end
shipped as package data. It reads what the CLI already writes to disk (configs,
``anchor doctor`` JSON, track parquets, ledger cards) and can spawn the CLI as a
subprocess; it never computes a reconstruction itself.
"""
from anchor.dashboard.server import make_server, serve
__all__ = ['make_server', 'serve']
