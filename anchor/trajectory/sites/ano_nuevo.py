"""Año Nuevo Island, central California — white shark hotspot.

Año Nuevo is a documented seasonal white shark aggregation site studied by
Hopkins Marine Station / Stanford / MBARI / Jorgensen et al. The 2019 WS
deployment CC0704 has no GPS or acoustic anchor, so this site config is a
plausible *placeholder* release point near the island's NE flank, used to
exercise the bathymetry-constrained trajectory pipeline on real depth data.
Replace with the actual deployment lat/lon if/when it becomes available.

Declination from NOAA WMM 2025 at the island for 2019 epoch is approximately
+13.0° E (recompute for the deployment date if the absolute heading matters
to your downstream analysis).
"""
from __future__ import annotations
from pathlib import Path
from anchor.trajectory.sites import BBox
ANO_NUEVO_DECLINATION_DEG_2019 = 13.0
ANO_NUEVO_DECLINATION_DEG_2026 = 12.7
ANO_NUEVO_DEFAULT_RELEASE_LON = -122.33
ANO_NUEVO_DEFAULT_RELEASE_LAT = 37.11
