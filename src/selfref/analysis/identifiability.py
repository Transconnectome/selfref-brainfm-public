"""Moment-specific identifiability Δ_id (PLAN §5 B).

For subject i, run r, window w the feature is the parcel x TR activity block,
z-scored per parcel within the window and flattened.

    s_ij(w, w') = atanh(corr(x_i^1(w), x_j^2(w')))
    I(w, w')    = mean_i s_ii(w, w') - mean_{i != j} s_ij(w, w')
    I_lock(w)   = I(w, w)
    I_shift(w)  = mean over w' with |start(w') - start(w)| >= min_gap of I(w, w')
    Δ_id(w)     = I_lock(w) - I_shift(w);  Δ̄_id = mean_w Δ_id(w)

Per-subject decomposition (used for the subject-cluster bootstrap CI, a prereg choice):
    d_i = mean_w [ s_ii(w,w) - mean_{j != i} s_ij(w,w) ]
          - mean_w mean_{w'} [ s_ii(w,w') - mean_{j != i} s_ij(w,w') ]
so that mean_i d_i = Δ̄_id.
"""
from __future__ import annotations

import numpy as np


def window_starts(n_tr: int, window: int, step: int) -> np.ndarray:
    return np.arange(0, n_tr - window + 1, step)


def window_features(run: np.ndarray, starts: np.ndarray, window: int) -> np.ndarray:
    """run: TRs x parcels -> windows x (window * parcels), unit-norm rows of z-scored blocks."""
    feats = []
    for s in starts:
        block = run[s : s + window]
        block = (block - block.mean(0)) / np.maximum(block.std(0), 1e-12)
        v = block.ravel()
        v = v - v.mean()
        feats.append(v / np.linalg.norm(v))
    return np.asarray(feats)


def similarity_tensor(run1: np.ndarray, run2: np.ndarray, window: int, step: int) -> tuple[np.ndarray, np.ndarray]:
    """runs: subjects x TRs x parcels. Returns S[i, j, w, w'] (Fisher z) and window starts."""
    starts = window_starts(run1.shape[1], window, step)
    f1 = np.stack([window_features(r, starts, window) for r in run1])
    f2 = np.stack([window_features(r, starts, window) for r in run2])
    r = np.einsum("iwd,jvd->ijwv", f1, f2)
    return np.arctanh(np.clip(r, -0.999999, 0.999999)), starts


def per_subject_delta(S: np.ndarray, starts: np.ndarray, min_gap: int) -> np.ndarray:
    n = S.shape[0]
    same = S[np.arange(n), np.arange(n)]  # i, w, w'
    off = (S.sum(axis=1) - same) / (n - 1)  # mean over j != i
    I_i = same - off  # i, w, w'
    lock = np.einsum("iww->iw", I_i)
    far = np.abs(starts[:, None] - starts[None, :]) >= min_gap
    shift = (I_i * far).sum(-1) / np.maximum(far.sum(-1), 1)
    valid = far.any(-1)
    return (lock - shift)[:, valid].mean(axis=1)


def delta_id(run1: np.ndarray, run2: np.ndarray, window: int, step: int, min_gap: int) -> np.ndarray:
    """Per-subject d_i; the group estimate Δ̄_id is its mean."""
    S, starts = similarity_tensor(run1, run2, window, step)
    return per_subject_delta(S, starts, min_gap)


def min_gap_trs(window: int, tr: float, extra_s: float = 15.0) -> int:
    """PLAN §5 B: shifted windows are at least one window length plus 15 s apart."""
    return int(window + np.ceil(extra_s / tr))


def hrf_controlled_delta(
    run1: np.ndarray,
    run2: np.ndarray,
    checker: np.ndarray,
    checker_design: np.ndarray,
    tr: float,
    window: int,
    step: int,
    rng: np.random.Generator,
) -> dict[str, np.ndarray]:
    """Per-subject d_i, d_i^HRF and their difference e_i (PLAN §5 B, main estimand = mean e_i).

    Subject HRF lag comes from the checker block run (mean of its parcels), never from
    simulation ground truth. Surrogate amplitude is fitted per parcel on the movie run
    itself (see `hrf_surrogate`), so the checker gain is estimated but unused.
    """
    from selfref.analysis.hrf import estimate_lag_gain, hrf_surrogate

    est = [estimate_lag_gain(c.mean(axis=1), checker_design, tr) for c in checker]
    lags = np.array([e[0] for e in est])
    gains = np.array([e[1] for e in est])
    gap = min_gap_trs(window, tr)
    d = delta_id(run1, run2, window, step, gap)
    s1 = hrf_surrogate(run1, lags, gains, tr, rng)
    s2 = hrf_surrogate(run2, lags, gains, tr, rng)
    d_hrf = delta_id(s1, s2, window, step, gap)
    return {"d": d, "d_hrf": d_hrf, "e": d - d_hrf, "lag_hat": lags, "gain_hat": gains}
