"""Synthetic Spacetop alignvideo relevance ratings for task A (metadata path).

Structure from stage 0 (V2): 116 subjects, 49 distinct clips shown once each, in the
same order for everyone (so clip and presentation position are confounded), 13 runs of
3-4 clips. Missingness has two layers: whole runs lost (540 of 1,360 runs) and
within-run nonresponse (20.6% of the remaining ratings). Person features are age and
sex (the only ones in the dataset); clip features stand for staff-coded content codes.
No variance parameter comes from real data (PLAN §12.1).

rating_ic = mu + person_i + clip_c + drift * position_c
            + meta_amp * (person_feat_i @ W @ clip_feat_c)   (interaction explained by metadata)
            + free_amp * eta_ic                              (interaction metadata cannot see)
            + noise_amp * eps_ic
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass
class AParams:
    n_sub: int = 116
    n_clip: int = 49
    n_run: int = 13
    n_clip_feat: int = 6
    person_sd: float = 1.0
    clip_sd: float = 1.0
    drift: float = 0.0
    meta_amp: float = 0.0
    free_amp: float = 0.0
    noise_amp: float = 1.0
    p_run_lost: float = 540 / 1360
    p_nonresponse: float = 0.206


def simulate(p: AParams, rng: np.random.Generator) -> tuple[pd.DataFrame, np.ndarray, np.ndarray, dict]:
    """Return (long table of observed ratings, person features, clip features, truth)."""
    n, C = p.n_sub, p.n_clip
    run_of_clip = np.repeat(np.arange(p.n_run), int(np.ceil(C / p.n_run)))[:C]
    position = np.arange(C)  # identical order for everyone
    age = rng.normal(0, 1, n)
    sex = rng.integers(0, 2, n) * 2.0 - 1
    person_feat = np.column_stack([age, sex])
    clip_feat = rng.standard_normal((C, p.n_clip_feat))
    W = rng.standard_normal((person_feat.shape[1], p.n_clip_feat))
    W /= np.linalg.norm(W)

    person = p.person_sd * rng.standard_normal(n)
    clip = p.clip_sd * rng.standard_normal(C)
    pos_z = (position - position.mean()) / position.std()
    meta = person_feat @ W @ clip_feat.T
    meta = meta / meta.std()
    y = (
        person[:, None]
        + clip[None, :]
        + p.drift * pos_z[None, :]
        + p.meta_amp * meta
        + p.free_amp * rng.standard_normal((n, C))
        + p.noise_amp * rng.standard_normal((n, C))
    )
    lost_run = rng.random((n, p.n_run)) < p.p_run_lost
    observed = ~lost_run[:, run_of_clip] & (rng.random((n, C)) >= p.p_nonresponse)
    ii, cc = np.nonzero(observed)
    df = pd.DataFrame({"subject": ii, "clip": cc, "position": position[cc], "rating": y[ii, cc]})
    truth = {"clip": clip, "drift_by_clip": p.drift * pos_z, "meta": meta}
    return df, person_feat, clip_feat, truth
