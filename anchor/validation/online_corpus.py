"""Online video corpus → DLC pose → species K calibration.

Used for bat ray now (drone is killed by Elkhorn turbidity; aquarium is
future MBA work). Caveat: published video has no synced accel, so this
path is K-only — it does NOT validate behavior states.

Workflow:
  1. Curate 3-5 published clips with body-length scale references
     (MBA exhibit cams, BBC/NatGeo, research footage).
  2. Annotate ~100-300 frames per clip per species in DLC.
  3. ``extract_keypoints_dlc`` → :class:`anchor.validation.pose.Keypoints`.
  4. ``keypoints_to_kinematics`` → per-cycle (TBF, A/L, L_pix).
  5. Combine with a known swim-speed observation (in-frame fiducial
     velocity, tank current measurement, or back-calculation from
     reference-bar pixel speed) → ``compute_k_from_kinematics`` →
     species K with bootstrap CI.

Reference K anchors — the shipped species values a corpus estimate is
scored against. Ported 2026-09-04 from the 2026-07-10 stride-length audit;
derivations and citations in ``docs/strouhal_calibration.md``:
  - LS K = 0.75 (Triakis stride 1.0-1.7 BL/cycle, Donley & Shadwick 2003,
    2007; conservative pick against the 0.5-0.9 general sub-carangiform band)
  - WS K = 0.65 (lamnid stride; shortfin mako ~0.90 BL/cycle direct,
    10.1111/jfb.15475)
  - BR K = 0.85 (myliobatid stride 1.47 disc-lengths/cycle, Chen 2021
    10.1088/1748-3190/abf5ba, converted to this pipeline's disc-WIDTH basis)
  - TS K = 0.40 (**unaudited** — read across from the white shark before the
    audit, and the white shark has since moved to 0.65)

The pre-audit anchors this block used to list (LS/TS/WS 0.40, BR 0.25, sourced
to Bainbridge 1958 + Webb 1975 + Triantafyllou 1993, Watanabe et al. 2019 *MEPS*
621:221-227, and Moored et al. 2011 *J R Soc Interface* 8:1041-1057) are
superseded in both value and citation; paper §4.5.2 still states them
(``docs/claims.yaml: traj_k_*``, contradicted).
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional
import numpy as np
import pandas as pd

@dataclass
class OnlineCorpusEntry:
    """Provenance + measurement metadata for one published-video sample."""
    source_url: str
    species: str
    body_length_m: float
    swim_speed_m_s: Optional[float] = None

def compute_k_from_kinematics(kinematics: pd.DataFrame, swim_speed_m_s: float | np.ndarray) -> pd.DataFrame:
    """Per-cycle K = U / (L · TBF).

    ``kinematics`` is the output of :func:`anchor.validation.pose.keypoints_to_kinematics`
    (must carry ``tbf_hz`` and ``body_length_m`` columns). ``swim_speed_m_s``
    is either a scalar (constant cruise) or an array aligned with cycles.

    Returns the input frame with an added ``k`` column. Drops rows where
    TBF or U is non-positive.
    """
    ...

def bootstrap_k(k_samples: np.ndarray, n_bootstrap: int=1000, ci: float=0.95, rng: Optional[np.random.Generator]=None) -> dict[str, float]:
    """Bootstrap median K with percentile CI.

    Online-corpus samples have noisy body-length scale references and
    per-clip swim-speed uncertainty; report median + CI rather than a
    point estimate.
    """
    ...

def aggregate_corpus(per_clip_dfs: list[pd.DataFrame], weight_by: str='uniform') -> dict[str, float]:
    """Combine per-clip K samples and bootstrap aggregate.

    ``weight_by="uniform"`` pools all per-cycle K values equally;
    ``"per_clip"`` first medians within each clip, then bootstraps over
    clips (more conservative when one long clip dominates the cycle count).
    """
    ...
