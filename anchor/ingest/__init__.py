"""Ingest + calibration: raw CSV to calibrated parquet.

Paper section 4.2. Handles three CSV schemas (axy5, axy_depth, cats), accel
ellipsoid calibration, and pydantic deployment-config loading with
`inherits:` species-level merging.
"""
from anchor.ingest.io import detect_sampling_rate, iter_csv_chunks, load_deployment, normalize_schema, parse_datetime, read_flexible_csv, read_parquet, write_parquet
from anchor.ingest.calibrate import apply_calibration, calibration_from_spins, fit_accel_ellipsoid, fit_ellipsoid, fit_mag_ellipsoid, load_calibration, save_calibration
from anchor.ingest.config import DeploymentConfig, load_config
__all__ = ['DeploymentConfig', 'apply_calibration', 'calibration_from_spins', 'detect_sampling_rate', 'fit_accel_ellipsoid', 'fit_ellipsoid', 'fit_mag_ellipsoid', 'iter_csv_chunks', 'load_calibration', 'load_config', 'load_deployment', 'normalize_schema', 'parse_datetime', 'read_flexible_csv', 'read_parquet', 'save_calibration', 'write_parquet']
