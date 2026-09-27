"""Pydantic config models + YAML loader with simple ``inherits:`` merging."""
from __future__ import annotations
import copy
import datetime as _dt
import math
from pathlib import Path
from typing import Literal, Optional
import logging
import yaml
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_serializer, model_validator
from anchor.events import JERK_SCALE_FACTOR, VEDBA_SCALE_FACTOR, ThresholdMethod
SMOOTH_SIGMA_RTOL = 0.05
DEFAULT_STROUHAL_K = 0.4

class TailbeatConfig(BaseModel):
    min_period_s: float = 0.3
    prominence: Optional[float] = None

class EventConfig(BaseModel):
    """Which event-threshold rule to use, and its parameters.

    ``method="robust_scale"`` (the default, and what the pipeline used before
    this field existed) puts each channel's threshold at ``median + factor *
    1.4826 * MAD`` of the record; ``vedba_pct`` / ``jerk_pct`` are then unused.
    ``method="percentile"`` restores the pre-N5 within-deployment percentile
    rule and ignores the scale factors instead. See :mod:`anchor.events` for
    what the robust-scale rule does and does not give you — in particular it is
    *not* an absolute or cross-animal-comparable threshold.
    """
    vedba_pct: float = 99.5
    jerk_pct: float = 99.9
    min_gap_s: float = 1.0

class FeaturesConfig(BaseModel):
    window_s: float = 2.0
    step_s: float = 1.0
    include_depth: bool = False

class ClassifierConfig(BaseModel):
    n_states: int = 4

class LatentAxisSpec(BaseModel):
    """One axis of the outer latent grid, as a count and inclusive endpoints.

    ``n=1`` collapses the axis to the single value ``min`` (``max`` is then
    required to equal it), which is how a one-node grid is written.
    """

    @model_validator(mode='after')
    def _check_span(self):
        ...

    def values(self) -> list[float]:
        """The ``n`` grid points, endpoints included."""
        ...

class TrajectoryConfig(BaseModel):
    """Particle-filter + smoother hyperparameters for trajectory reconstruction.

    These were previously hardcoded in ``run_filter_with_snapshots``; surfacing
    them here makes runs reproducible and enables sensitivity analysis (vary one
    field over a grid, see ``anchor.trajectory.sensitivity``) without code edits.
    Defaults reproduce the prior hardcoded behaviour. Angles are in degrees for
    readability and converted to radians at the filter boundary.
    """

    @model_serializer(mode='wrap')
    def _drop_unset_optionals(self, handler):
        """Serialise, then drop the :data:`TRAJECTORY_OMIT_FROM_DUMP_WHEN_NULL`
        nulls, so a run that gave no instruction on one of those fields hashes
        exactly as it did before the field existed."""
        ...
    n_particles: int = 4000
    process_noise_xy_m: float = 2.5
    resample_threshold: float = 0.5
    init_x_std_m: float = 20.0
    init_bias_std_deg: float = 10.0
    init_speed_std: float = 0.2
    bias_walk_std_deg_per_s: float = 0.0
    speed_walk_std_per_s: float = 0.0
    speed_min: float = 0.5
    speed_max: float = 1.8
    bathymetry_extra_sigma_m: float = 1.0
    smoother_process_noise_xy_m: Optional[float] = None
    smoother_n_samples: int = 200

    @field_validator('polygon_penalty_nats')
    @classmethod
    def _penalty_is_positive(cls, v):
        """A zero or negative penalty would *reward* leaving the water, and a
        non-finite one is spelt ``None`` (the explicit hard mode)."""
        ...

    @field_validator('wet_threshold_m')
    @classmethod
    def _wet_threshold_is_finite(cls, v):
        """A NaN threshold makes every comparison False and every cell dry.

        Negative values stay legal on purpose -- a threshold below the bed
        admits cells above the waterline and is the loosened-mask control -- but
        NaN and +/-inf are not thresholds. NaN in particular is silent: the
        rebuilt stack is dry at every cell and every level, and the filter then
        charges ``polygon_penalty_nats`` on every particle at every step.
        """
        ...

class EndpointConfig(BaseModel):
    """A georeferenced deployment endpoint (tag-on release, or recovery pickup).

    These replace the unversioned ``--release-lon/--release-lat`` shell history
    that ``run_deployment.py`` currently carries as argparse defaults, so the
    particle filter's release anchor travels with the deployment YAML.
    """

class CalibrationPaths(BaseModel):
    accel: Optional[str] = None
    mag: Optional[str] = None

class VideoSyncConfig(BaseModel):
    offset_s: Optional[float] = None
    reference_event: Optional[str] = None

class LabelsConfig(BaseModel):
    path: Optional[str] = None
    format: Optional[Literal['boris', 'via']] = None

class AnimalInfo(BaseModel):
    id: Optional[str] = None
    length_cm: Optional[float] = None
    sex: Optional[str] = None

class TagInfo(BaseModel):
    model: Optional[str] = None
    mount: Optional[str] = None

    @field_validator('axes_rotation_deg')
    @classmethod
    def _check_axes_rotation(cls, v):
        """Three finite degrees in [-180, 180], validated by the code that uses them.

        Deferred import: ``anchor.kinematics`` pulls in scipy.signal, and the
        config module is imported by the CLI's ``--help`` path.
        """
        ...

class DeploymentConfig(BaseModel):
    """Merged species + deployment view. This is what the pipeline consumes."""

    @model_serializer(mode='wrap')
    def _drop_unset_optionals(self, handler):
        """Serialise, then drop the :data:`OMIT_FROM_DUMP_WHEN_NULL` nulls."""
        ...
    species: str
    source_schema: SourceSchema
    sampling_rate_hz: float
    lowpass_cutoff_hz: float
    tailbeat: TailbeatConfig
    event_thresholds: EventConfig
    features: FeaturesConfig
    classifier: ClassifierConfig
    body_length_m_default: Optional[float] = None
    deployment_id: str
    raw_csv: str
    deploy_window: Optional[list[str]] = None
    video_dir: Optional[str] = None

    @field_validator('deploy_window', mode='before')
    @classmethod
    def _coerce_window(cls, v):
        """PyYAML parses ISO datetimes into datetime objects — stringify them."""
        ...

    @model_validator(mode='after')
    def _check_smooth_sigma_matches_the_band(self) -> 'DeploymentConfig':
        """Warn when ``tailbeat.smooth_sigma`` is not the value ``fs`` implies.

        ``gaussian_filter1d``'s sigma is in samples, so a value copied between
        a 25 Hz and a 50 Hz tag silently moves the smoother's corner by an
        octave — and when it lands *inside* the species' own tail-beat band it
        caps reported tail-beat frequency, which then propagates through
        ``U = K * L * TBF`` into every reconstructed metre. This is a warning
        and not an error because ``smooth_sigma`` is legitimately a tuning knob
        (a deliberately narrower band is a valid choice); what is never
        legitimate is *not noticing*.
        """
        ...

    @model_validator(mode='after')
    def _check_lowpass_below_the_slowest_beat(self) -> 'DeploymentConfig':
        """Warn when the static/dynamic split swallows the slowest tail beat.

        ``lowpass_cutoff_hz`` splits the specific force into posture and
        motion. A cutoff above the slowest beat classes that beat as posture:
        TBF is then picked on the faster remainder (biased up), VeDBA loses
        the beat's energy (biased down) and pitch/roll oscillate at the beat.
        A warning, like the smooth_sigma check, because the cutoff is a
        judgement; ``anchor doctor`` reports the same number as a finding.
        """
        ...

    @field_validator('clip')
    @classmethod
    def _check_clip(cls, v):
        """A clip range must be a non-negative, strictly increasing sample pair."""
        ...

def _deep_merge(base: dict, override: dict) -> dict:
    """Dict-merge ``override`` into ``base``; override wins at leaves."""
    ...

def load_config(path: str | Path, configs_root: Optional[str | Path]=None) -> DeploymentConfig:
    """Load a deployment YAML; if it carries ``inherits:`` resolve against the
    sibling species folder (or ``configs_root`` if given).
    """
    ...
