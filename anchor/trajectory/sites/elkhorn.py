"""Elkhorn Slough, Monterey Bay, California — site constants.

The slough is a turbid mixed-tide estuary, ~7 mi long, max depth ~5 m at the
mouth. Leopard shark, bat ray, and sea otter habitat. CSUMB / MLML / Hopkins
have an established research presence; bathymetry is published.

Declination is **not** restated here. It is re-exported from
:mod:`anchor.trajectory.imu`, which fetched it from WMM2025 on 2026-09-06 and
records the request and the saved JSON. Until then this module carried its own
12.7 from memory while ``imu`` carried 12.580, and because ``run_deployment``
takes ``--declination-deg``'s default from *this* module, every ``anchor track``
run used the stale value while the doctor and the forensics scripts used the
fetched one — a silent 0.12 deg disagreement inside one package. Re-exporting is
what stops the two diverging again.
"""
from __future__ import annotations
from pathlib import Path
from anchor.trajectory.imu import ELKHORN_DECLINATION_DEG_2026 as ELKHORN_DECLINATION_DEG_2026
from anchor.trajectory.sites import BBox
import numpy as _np
ELKHORN_CURRENT_DECAY_PROFILE = ((0.0, 1.0), (1500.0, 0.7), (3000.0, 0.5), (5000.0, 0.3), (7000.0, 0.2), (9500.0, 0.1))
ELKHORN_TIDAL_PRISM_K_M = 10000.0
