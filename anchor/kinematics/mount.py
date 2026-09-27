"""Tag frame -> body frame: the fixed mount rotation.

Design ``docs/design/leopard_shark_digital_twin.md`` section 3.5 row 1, Phase 0
R1 ("frame closure"). ``TagInfo.axes_rotation_deg`` was declared in every
deployment YAML and read by no code outside ``sim/``; this module is where it is
read.

The convention, stated once
---------------------------
``axes_rotation_deg`` is ``(roll, pitch, yaw)`` in degrees, composed
**intrinsic ZYX**, describing the orientation of the **tag** in the **body**
frame::

    R_body_tag = Rz(yaw) @ Ry(pitch) @ Rx(roll)
    v_body     = R_body_tag @ v_tag

so :func:`apply_mount_rotation` maps a tag-frame reading to the body frame by
applying ``R_body_tag`` directly, not its inverse. Both frames are the tag
convention the rest of ``anchor`` uses: **X forward, Y right, Z down**, with
gravity reading ``+1 g`` on ``accZ`` at rest
(:func:`anchor.kinematics.core.add_pitch_roll`). ``[0, 0, 0]`` means the tag is
mounted body-aligned and this step is a no-op.

This is the same convention the forward simulator writes, and it is now the
only one in the tree: ``sim/axy_forward_sim.make_mount`` builds the nominal
mount as ``Rot.from_euler("ZYX", [yaw, pitch, roll])`` and
``sim/axy5_export._readout`` projects the body-frame signal into the tag with
its inverse. In SciPy terms the intrinsic ``"ZYX"`` sequence with
``[yaw, pitch, roll]`` and the extrinsic ``"xyz"`` sequence with
``[roll, pitch, yaw]`` are the same rotation; the intrinsic spelling is used
here because it is the one the simulator uses.

Measured against the simulator
------------------------------
``tests/kinematics/test_mount.py::test_mount_rotation_collapses_sim_pitch_bias``
generates a slip-free AXY-5 record with a known ``(5, -12, 20) deg`` mount,
runs it through the real ingest and :func:`anchor.kinematics.core.add_pitch_roll`,
and compares against the simulator's own body-pitch label:

===============================  ==================  =================
pitch error vs truth             mean                std
===============================  ==================  =================
no mount rotation (today)        -9.58 deg           9.75 deg
full ZYX, yaw included           **-0.08 deg**       **0.84 deg**
pitch and roll only, yaw dropped +0.29 deg           9.19 deg
===============================  ==================  =================

On the default record, which carries the simulator's slip process on top of the
fixed mount, the same correction moves the pitch bias from ``-11.75 deg`` to
``-5.39 deg`` at seed 7; the remainder is slip, a random walk that a *fixed*
rotation cannot remove by construction and that the design routes to the
reference-tag channel instead.

What happens to the yaw part
----------------------------
Design 3.5 says **pitch and roll** are what this correction buys, and that is
true of the information it adds — but the whole ZYX rotation is applied, yaw
included, and the table above is why. ``Rz(yaw)`` is the *outermost* factor of
the composition, so dropping it does not leave a pitch-and-roll correction: it
leaves the pitch-and-roll correction itself rotated by the mount yaw, which is
worth 11x the per-sample pitch error here even where the mean happens to come
out near zero.

What applying it does *not* buy is heading. Rotating ``magX/magY`` by a constant
``yaw`` shifts every tag-derived heading by exactly that constant, and a
constant heading offset is precisely what the particle filter's ``psi_bias``
latent absorbs. So the constant part of the mount yaw is **exactly aliased with
``psi_bias``**: applying it re-parameterises that latent's zero point and adds
no information. Per design 3.5 it is declared aliased and never freed. The
*time-varying* part of the mount yaw is the slip process, which is not this
function's business at all.
"""
from __future__ import annotations
import logging
import math
from typing import Sequence
import numpy as np
import pandas as pd
AXES_ROTATION_LIMIT_DEG = 180.0

def normalize_axes_rotation_deg(values: Sequence[float]) -> tuple[float, float, float]:
    """Validate ``axes_rotation_deg`` and return it as ``(roll, pitch, yaw)`` floats.

    Three finite numbers, each within ``[-180, 180]``. Raises ``ValueError``
    otherwise — this is the single validator behind both
    :class:`anchor.ingest.config.TagInfo` and :func:`apply_mount_rotation`, so a
    config that loads is a config this module can act on.
    """
    ...

def is_body_aligned(axes_rotation_deg: Sequence[float]) -> bool:
    """True when the declared mount is exactly ``[0, 0, 0]`` (rotation is a no-op)."""
    ...

def mount_rotation(axes_rotation_deg: Sequence[float]):
    """``R_body_tag`` as a :class:`scipy.spatial.transform.Rotation`.

    ``R.apply(v_tag)`` is ``v_body``. See the module docstring for the
    convention; ``scipy`` is imported here rather than at module scope so that
    importing this module stays as cheap as the rest of ``anchor.kinematics``.
    """
    ...

def apply_mount_rotation(df: pd.DataFrame, axes_rotation_deg: Sequence[float]) -> pd.DataFrame:
    """Rotate ``accX/Y/Z`` and ``magX/Y/Z`` from the tag frame into the body frame.

    ``axes_rotation_deg`` is the deployment's ``tag.axes_rotation_deg``:
    ``(roll, pitch, yaw)`` degrees, intrinsic ZYX, tag-in-body. Returns *df*
    itself, unmodified, for the body-aligned default ``[0, 0, 0]`` — the 605 MB
    APT record must not be copied to multiply by the identity. Otherwise returns
    a copy with the rotated columns overwritten in place and
    ``attrs["mount_rotation_deg"]`` set to the applied ``[roll, pitch, yaw]``.
    The attribute is therefore the record of what happened: absent means the
    frame is still the tag's, present means it is the body's.

    Call it *after* :func:`anchor.ingest.calibrate.apply_calibration` — the
    calibration is a per-axis property of the sensor and only means anything in
    the tag's own axes — and *before* any kinematics, so pitch, roll, heading
    and every dynamic-acceleration channel downstream are body-frame quantities.
    """
    ...
